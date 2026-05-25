import re
import streamlit as st
import pandas as pd
from datetime import datetime
from database import queries
from ui import section_card


def _normalize_header(header):
    if isinstance(header, str):
        return header.strip().lower().replace(' ', '_')
    return ''


def _normalize_value(value):
    if pd.isna(value):
        return ''
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _get_header_map(columns):
    return {_normalize_header(col): col for col in columns}


def _get_cell(row, header_map, aliases):
    for alias in aliases:
        normalized = _normalize_header(alias)
        if normalized in header_map:
            return row[header_map[normalized]]
    return None


def _parse_number_list(value, dtype=float):
    if pd.isna(value):
        return []
    if isinstance(value, (list, tuple, pd.Series)):
        return [dtype(x) for x in value if x is not None and str(x).strip() != '']
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return [dtype(value)]
    text = str(value)
    text = text.replace(',', ' ').replace(';', ' ').replace('\n', ' ').replace('|', ' ')
    parts = [p.strip().strip('[]()') for p in text.split() if p.strip()]
    parsed = []
    for part in parts:
        try:
            parsed.append(dtype(part))
        except ValueError:
            continue
    return parsed


def _build_metadata_from_row(row, header_map, productos, analistas):
    producto = _normalize_value(_get_cell(row, header_map, ['producto', 'nombre_producto', 'producto_nombre']))
    analista = _normalize_value(_get_cell(row, header_map, ['analista', 'nombre_analista', 'analista_nombre']))
    tipo_control = _normalize_value(_get_cell(row, header_map, ['tipo_control', 'tipo', 'control']))
    fecha_hora = _get_cell(row, header_map, ['fecha_hora', 'fecha', 'fecha_muestra'])
    num_subgrupo = _get_cell(row, header_map, ['num_subgrupo', 'subgrupo', 'tam_subgrupo'])
    lote = _normalize_value(_get_cell(row, header_map, ['lote']))
    origen = _normalize_value(_get_cell(row, header_map, ['origen']))
    observaciones = _normalize_value(_get_cell(row, header_map, ['observaciones', 'observacion']))

    if isinstance(fecha_hora, str) and fecha_hora.strip():
        try:
            fecha_str = fecha_hora.strip()
            return {
                'producto': producto,
                'analista': analista,
                'tipo_control': tipo_control,
                'fecha_hora': fecha_str,
                'num_subgrupo': int(num_subgrupo) if num_subgrupo not in (None, '', float('nan')) else None,
                'lote': lote,
                'origen': origen,
                'observaciones': observaciones,
            }
        except Exception:
            pass

    if isinstance(fecha_hora, pd.Timestamp):
        fecha_hora = fecha_hora.to_pydatetime()
    if isinstance(fecha_hora, datetime):
        fecha_hora = fecha_hora.strftime('%Y-%m-%d %H:%M:%S')
    elif fecha_hora is None or (isinstance(fecha_hora, str) and fecha_hora.strip() == ''):
        fecha_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        fecha_hora = str(fecha_hora)

    return {
        'producto': producto,
        'analista': analista,
        'tipo_control': tipo_control,
        'fecha_hora': fecha_hora,
        'num_subgrupo': int(num_subgrupo) if num_subgrupo not in (None, '', float('nan')) else None,
        'lote': lote,
        'origen': origen,
        'observaciones': observaciones,
    }


def _parse_variable_values(row, header_map):
    known_keys = {
        'producto', 'nombre_producto', 'analista', 'nombre_analista', 'tipo_control', 'tipo', 'control',
        'fecha_hora', 'fecha', 'fecha_muestra', 'num_subgrupo', 'subgrupo', 'tam_subgrupo',
        'lote', 'origen', 'observaciones', 'observacion',
        'nombre_variable', 'tipo_dato', 'lci', 'lcs', 'valor_nominal'
    }
    explicit = _get_cell(row, header_map, ['valores', 'datos', 'valores_muestra'])
    valores = _parse_number_list(explicit, float)
    if valores:
        return valores

    valores = []
    for normalized, original in header_map.items():
        if normalized in known_keys:
            continue
        if normalized.startswith('valor') or normalized.startswith('dato'):
            valores.extend(_parse_number_list(row[original], float))
            continue
        cell = row[original]
        if isinstance(cell, (int, float)) and not isinstance(cell, bool):
            valores.append(float(cell))
        elif isinstance(cell, str) and cell.strip():
            valores.extend(_parse_number_list(cell, float))
    return valores


def _parse_attribute_values(row, header_map):
    inspeccionados = _get_cell(row, header_map, ['n_inspeccionados', 'inspeccionados'])
    defectuosos = _get_cell(row, header_map, ['n_defectuosos', 'defectuosos'])
    inspect_list = _parse_number_list(inspeccionados, int)
    defect_list = _parse_number_list(defectuosos, int)
    if inspect_list and defect_list and len(inspect_list) == len(defect_list):
        return inspect_list, defect_list

    inspect_list = []
    defect_list = []
    for normalized, original in header_map.items():
        if normalized.startswith('n_inspeccionado') or normalized.startswith('inspeccionado'):
            inspect_list.extend(_parse_number_list(row[original], int))
        if normalized.startswith('n_defectuoso') or normalized.startswith('defectuoso'):
            defect_list.extend(_parse_number_list(row[original], int))
    if inspect_list and defect_list and len(inspect_list) == len(defect_list):
        return inspect_list, defect_list

    return [], []


def _resolve_product_id(producto, productos):
    if not producto:
        return None
    producto = producto.strip().lower()
    matches = productos[productos['nombre'].str.strip().str.lower() == producto]
    if not matches.empty:
        return int(matches.iloc[0]['id_producto'])
    return None


def _resolve_analista_id(analista, analistas):
    if not analista:
        return None
    nombre = analista.strip().lower()
    candidates = analistas.copy()
    candidates['full_name'] = candidates['nombre'].str.strip().str.lower() + ' ' + candidates['apellido'].str.strip().str.lower()
    matches = candidates[candidates['full_name'] == nombre]
    if not matches.empty:
        return int(matches.iloc[0]['id_analista'])
    return None


def _get_numeric_columns(df):
    numeric_columns = []
    for col in df.columns:
        if pd.to_numeric(df[col], errors='coerce').notna().any():
            numeric_columns.append(col)
    return numeric_columns


def _get_text_columns(df):
    return [col for col in df.columns if df[col].astype(str).str.strip().any()]


def _parse_column_values(series, dtype=float):
    values = []
    for value in series:
        if pd.isna(value):
            continue
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            values.append(dtype(value))
            continue
        text = str(value).strip()
        if not text:
            continue
        if dtype is float:
            try:
                values.append(float(text))
                continue
            except ValueError:
                pass
        try:
            values.append(dtype(text))
        except ValueError:
            continue
    return values


def _resolve_or_create_product(nombre_producto, productos, crear_nuevo=False, nuevo_producto=None):
    nombre = _normalize_value(nombre_producto)
    if not nombre:
        return None
    existing = productos[productos['nombre'].str.strip().str.lower() == nombre.lower()]
    if not existing.empty:
        return int(existing.iloc[0]['id_producto'])
    if crear_nuevo and nuevo_producto is not None:
        tipo = nuevo_producto.get('tipo', '').strip().lower()
        if tipo not in ('fruta', 'hortaliza', 'planta_medicinal'):
            tipo = 'planta_medicinal'
        return queries.insert_producto(
            nuevo_producto.get('nombre', nombre).strip(),
            tipo,
            nuevo_producto.get('variedad', ''),
            nuevo_producto.get('unidad_medida', 'unidad'),
            nuevo_producto.get('descripcion', '')
        )
    if crear_nuevo:
        return queries.insert_producto(nombre, 'planta_medicinal', '', 'unidad', '')
    return None


def _resolve_or_create_analista(nombre_analista, analistas, crear_nuevo=False, nuevo_analista=None):
    nombre_completo = _normalize_value(nombre_analista)
    if not nombre_completo:
        return None
    existing = analistas.copy()
    existing['full_name'] = existing['nombre'].str.strip().str.lower() + ' ' + existing['apellido'].str.strip().str.lower()
    matches = existing[existing['full_name'] == nombre_completo.lower()]
    if not matches.empty:
        return int(matches.iloc[0]['id_analista'])
    if crear_nuevo:
        if nuevo_analista is not None and nuevo_analista.get('nombre'):
            nombre = nuevo_analista.get('nombre').strip()
            apellido = nuevo_analista.get('apellido', '').strip() or nombre
            cargo = nuevo_analista.get('cargo', '')
            contacto = nuevo_analista.get('contacto', '')
        else:
            partes = nombre_completo.split()
            nombre = partes[0]
            apellido = ' '.join(partes[1:]) if len(partes) > 1 else nombre
            cargo = ''
            contacto = ''
        return queries.insert_analista(nombre, apellido, cargo, contacto)
    return None


def _sheet_type_from_headers(header_map, sheet_name):
    normalized = set(header_map.keys())
    if 'nombre_variable' in normalized or 'valores' in normalized or any(h.startswith('valor') for h in normalized):
        return 'variable'
    if 'nombre_atributo' in normalized or 'n_inspeccionados' in normalized or 'n_defectuosos' in normalized:
        return 'atributo'
    if sheet_name and 'atributo' in sheet_name.lower():
        return 'atributo'
    return 'variable'


def _parse_excel_sheet(df, sheet_name, productos, analistas):
    header_map = _get_header_map(df.columns)
    sheet_type = _sheet_type_from_headers(header_map, sheet_name)
    rows = []
    errors = []

    for index, row in df.iterrows():
        metadata = _build_metadata_from_row(row, header_map, productos, analistas)
        producto_id = _resolve_product_id(metadata['producto'], productos)
        analista_id = _resolve_analista_id(metadata['analista'], analistas)
        tipo_control = metadata['tipo_control'].strip().lower()
        if not tipo_control:
            tipo_control = sheet_type

        if producto_id is None:
            errors.append(f'Fila {index + 2}: producto "{metadata["producto"]}" no existe.')
            continue
        if analista_id is None:
            errors.append(f'Fila {index + 2}: analista "{metadata["analista"]}" no existe.')
            continue

        num_subgrupo = metadata['num_subgrupo'] or 1
        tipo_control = 'variable' if tipo_control.startswith('v') else 'atributo'

        if tipo_control == 'variable':
            nombre_variable = _normalize_value(_get_cell(row, header_map, ['nombre_variable', 'variable']))
            tipo_dato = _normalize_value(_get_cell(row, header_map, ['tipo_dato', 'tipo_de_dato'])) or 'continua'
            lcs = _get_cell(row, header_map, ['lcs', 'limite_control_superior'])
            lci = _get_cell(row, header_map, ['lci', 'limite_control_inferior'])
            valor_nominal = _get_cell(row, header_map, ['valor_nominal', 'nominal'])
            valores = _parse_variable_values(row, header_map)
            if not nombre_variable:
                errors.append(f'Fila {index + 2}: falta nombre_variable.')
                continue
            if len(valores) < 2:
                errors.append(f'Fila {index + 2}: debe haber al menos dos valores numéricos para la variable.')
                continue
            rows.append({
                'tipo_control': 'variable',
                'producto_id': producto_id,
                'analista_id': analista_id,
                'fecha_hora': metadata['fecha_hora'],
                'num_subgrupo': num_subgrupo,
                'lote': metadata['lote'],
                'origen': metadata['origen'],
                'observaciones': metadata['observaciones'],
                'nombre_variable': nombre_variable,
                'tipo_dato': tipo_dato,
                'lcs': float(lcs) if lcs not in (None, '', float('nan')) else 0.0,
                'lci': float(lci) if lci not in (None, '', float('nan')) else 0.0,
                'valor_nominal': float(valor_nominal) if valor_nominal not in (None, '', float('nan')) else 0.0,
                'valores': valores,
            })
        else:
            nombre_atributo = _normalize_value(_get_cell(row, header_map, ['nombre_atributo', 'atributo']))
            tipo_grafico = _normalize_value(_get_cell(row, header_map, ['tipo_grafico', 'grafico'])) or 'P'
            tam_subgrupo = _get_cell(row, header_map, ['tam_subgrupo', 'tamanio_subgrupo', 'tam'])
            inspeccionados, defectuosos = _parse_attribute_values(row, header_map)
            if not nombre_atributo:
                errors.append(f'Fila {index + 2}: falta nombre_atributo.')
                continue
            if not inspeccionados or not defectuosos:
                errors.append(f'Fila {index + 2}: falta n_inspeccionados o n_defectuosos con igual cantidad de valores.')
                continue
            rows.append({
                'tipo_control': 'atributo',
                'producto_id': producto_id,
                'analista_id': analista_id,
                'fecha_hora': metadata['fecha_hora'],
                'num_subgrupo': num_subgrupo,
                'lote': metadata['lote'],
                'origen': metadata['origen'],
                'observaciones': metadata['observaciones'],
                'nombre_atributo': nombre_atributo,
                'tipo_grafico': tipo_grafico,
                'tam_subgrupo': int(tam_subgrupo) if tam_subgrupo not in (None, '', float('nan')) else num_subgrupo,
                'inspeccionados': inspeccionados,
                'defectuosos': defectuosos,
            })
    return rows, errors


def _register_excel_samples(rows):
    registered = []
    for item in rows:
        if item['tipo_control'] == 'variable':
            configs = pd.DataFrame(queries.get_variables_by_producto(item['producto_id']))
            existing = configs[
                configs['nombre_variable'].str.strip().str.lower() == item['nombre_variable'].strip().lower()
            ]
            if not existing.empty:
                id_variable = int(existing.iloc[0]['id_variable'])
            else:
                id_variable = queries.insert_variable_config(
                    item['producto_id'], item['nombre_variable'], item['tipo_dato'], item['lcs'], item['lci'], item['valor_nominal'], item['num_subgrupo']
                )

            id_muestra = queries.insert_muestra(
                item['producto_id'], item['analista_id'], item['num_subgrupo'], item['lote'], item['origen'], item['observaciones'], item['fecha_hora']
            )
            for idx, valor in enumerate(item['valores'], start=1):
                queries.insert_medicion_variable(id_muestra, id_variable, idx, valor)
            registered.append(item)
        else:
            configs = pd.DataFrame(queries.get_atributos_by_producto(item['producto_id']))
            existing = configs[
                configs['nombre_atributo'].str.strip().str.lower() == item['nombre_atributo'].strip().lower()
            ]
            if not existing.empty:
                id_atributo = int(existing.iloc[0]['id_atributo'])
            else:
                id_atributo = queries.insert_atributo_config(
                    item['producto_id'], item['nombre_atributo'], item['tipo_grafico'], item['tam_subgrupo']
                )

            id_muestra = queries.insert_muestra(
                item['producto_id'], item['analista_id'], item['num_subgrupo'], item['lote'], item['origen'], item['observaciones'], item['fecha_hora']
            )
            for n, d in zip(item['inspeccionados'], item['defectuosos']):
                queries.insert_medicion_atributo(id_muestra, id_atributo, int(n), int(d))
            registered.append(item)
    return registered


def render_page():
    st.header('04 - Registro de Muestras')
    st.write('Registra muestras variables y atributos para el control estadístico.')

    productos = pd.DataFrame(queries.get_productos())
    analistas = pd.DataFrame(queries.get_analistas())

    with section_card('Carga masiva desde Excel', 'Sube un archivo Excel para registrar varias muestras en bloque.'):
        excel_file = st.file_uploader('Selecciona un archivo Excel (.xlsx)', type=['xlsx'])
        if excel_file is not None:
            try:
                sheets = pd.read_excel(excel_file, sheet_name=None)
            except Exception as error:
                st.error(f'No se pudo leer el archivo Excel: {error}')
                sheets = None

            if sheets is not None:
                sheet_names = list(sheets.keys())
                sheet_name = st.selectbox('Selecciona la hoja', sheet_names)
                df_sheet = sheets[sheet_name]

                if df_sheet.empty:
                    st.warning('La hoja seleccionada está vacía.')
                else:
                    column_list = list(df_sheet.columns)
                    st.markdown('**Columnas detectadas en la hoja:**')
                    st.write(column_list)

                    producto_column = st.selectbox('Columna de producto (opcional)', ['<No usar>'] + column_list)
                    analista_column = st.selectbox('Columna de analista (opcional)', ['<No usar>'] + column_list)
                    control_type_excel = st.radio('Tipo de control en el Excel', ['Variable', 'Atributo'])

                    numeric_columns = _get_numeric_columns(df_sheet)
                    if not numeric_columns:
                        st.warning('No se detectaron columnas numéricas en esta hoja. Revisa el archivo.')

                    if control_type_excel == 'Variable':
                        value_column = st.selectbox('Columna con valores de la variable', [''] + numeric_columns)
                        nombre_variable = st.text_input('Nombre de la variable')
                        tipo_dato = st.selectbox('Tipo de dato', ['continua', 'discreta'])
                        lci = st.number_input('Límite de control inferior (LCI)', value=0.0)
                        lcs = st.number_input('Límite de control superior (LCS)', value=0.0)
                        valor_nominal = st.number_input('Valor nominal', value=0.0)
                    else:
                        inspeccionados_column = st.selectbox('Columna N° inspeccionados', [''] + numeric_columns)
                        defectuosos_column = st.selectbox('Columna N° defectuosos', [''] + numeric_columns)
                        nombre_atributo = st.text_input('Nombre del atributo')
                        tipo_grafico = st.selectbox('Tipo de gráfico', ['P', 'NP', 'C', 'U'])
                        tam_subgrupo = st.number_input('Tamaño del subgrupo para atributo', min_value=1, max_value=1000, value=5)

                    if producto_column == '<No usar>':
                        producto_origen = st.radio('Producto destino', ['Producto existente', 'Crear producto nuevo'])
                        if producto_origen == 'Producto existente':
                            producto_seleccionado_excel = st.selectbox('Producto', [''] + productos['nombre'].tolist())
                            nuevo_producto_nombre = ''
                            nuevo_producto_tipo = ''
                            nuevo_producto_variedad = ''
                            nuevo_producto_unidad = ''
                            nuevo_producto_descripcion = ''
                        else:
                            nuevo_producto_nombre = st.text_input('Nombre del nuevo producto')
                            nuevo_producto_tipo = st.selectbox('Tipo de producto', ['fruta', 'hortaliza', 'planta_medicinal'])
                            nuevo_producto_variedad = st.text_input('Variedad')
                            nuevo_producto_unidad = st.text_input('Unidad de medida')
                            nuevo_producto_descripcion = st.text_area('Descripción del nuevo producto')
                            producto_seleccionado_excel = ''
                    else:
                        producto_seleccionado_excel = ''
                        nuevo_producto_nombre = ''
                        nuevo_producto_tipo = 'planta_medicinal'
                        nuevo_producto_variedad = ''
                        nuevo_producto_unidad = ''
                        nuevo_producto_descripcion = ''

                    if analista_column == '<No usar>':
                        analista_origen = st.radio('Analista destino', ['Analista existente', 'Crear analista nuevo'])
                        if analista_origen == 'Analista existente':
                            analista_seleccionado_excel = st.selectbox('Analista', [''] + (analistas['nombre'] + ' ' + analistas['apellido']).tolist())
                        else:
                            nuevo_analista_nombre = st.text_input('Nombre del analista')
                            nuevo_analista_apellido = st.text_input('Apellido del analista')
                            nuevo_analista_cargo = st.text_input('Cargo')
                            nuevo_analista_contacto = st.text_input('Contacto')
                    else:
                        analista_seleccionado_excel = ''
                        nuevo_analista_nombre = ''
                        nuevo_analista_apellido = ''
                        nuevo_analista_cargo = ''
                        nuevo_analista_contacto = ''

                    crear_productos_nuevos = st.checkbox('Crear productos nuevos automáticamente si no existen', value=True)
                    crear_analistas_nuevos = st.checkbox('Crear analistas nuevos automáticamente si no existen', value=True)

                    if st.button('Registrar muestras desde Excel'):
                        errors = []
                        rows_to_register = []
                        product_cache = {}
                        analyst_cache = {}

                        def get_product_id_for_name(product_name):
                            normalized = _normalize_value(product_name)
                            if not normalized:
                                return None
                            if normalized in product_cache:
                                return product_cache[normalized]
                            product_id = _resolve_or_create_product(
                                normalized,
                                productos,
                                crear_nuevo=crear_productos_nuevos,
                                nuevo_producto={
                                    'nombre': normalized,
                                    'tipo': nuevo_producto_tipo,
                                    'variedad': nuevo_producto_variedad,
                                    'unidad_medida': nuevo_producto_unidad,
                                    'descripcion': nuevo_producto_descripcion,
                                }
                            )
                            if product_id:
                                product_cache[normalized] = product_id
                            return product_id

                        def get_analyst_id_for_name(analyst_name):
                            normalized = _normalize_value(analyst_name)
                            if not normalized:
                                return None
                            if normalized in analyst_cache:
                                return analyst_cache[normalized]
                            analyst_id = _resolve_or_create_analista(
                                normalized,
                                analistas,
                                crear_nuevo=crear_analistas_nuevos,
                                nuevo_analista={
                                    'nombre': nuevo_analista_nombre or normalized.split()[0],
                                    'apellido': nuevo_analista_apellido or ' '.join(normalized.split()[1:]) if len(normalized.split()) > 1 else normalized,
                                    'cargo': nuevo_analista_cargo,
                                    'contacto': nuevo_analista_contacto,
                                }
                            )
                            if analyst_id:
                                analyst_cache[normalized] = analyst_id
                            return analyst_id

                        if producto_column == '<No usar>':
                            if producto_origen == 'Producto existente' and not producto_seleccionado_excel:
                                errors.append('Debes seleccionar un producto destino.')
                            if producto_origen == 'Crear producto nuevo' and not nuevo_producto_nombre.strip():
                                errors.append('Debes ingresar el nombre del nuevo producto.')
                            if producto_origen == 'Producto existente':
                                default_product_id = _resolve_or_create_product(producto_seleccionado_excel, productos, crear_nuevo=False)
                            else:
                                default_product_id = _resolve_or_create_product(nuevo_producto_nombre, productos, crear_nuevo=True, nuevo_producto={
                                    'nombre': nuevo_producto_nombre,
                                    'tipo': nuevo_producto_tipo,
                                    'variedad': nuevo_producto_variedad,
                                    'unidad_medida': nuevo_producto_unidad,
                                    'descripcion': nuevo_producto_descripcion,
                                })
                        else:
                            default_product_id = None

                        if analista_column == '<No usar>':
                            if analista_origen == 'Analista existente' and not analista_seleccionado_excel:
                                errors.append('Debes seleccionar un analista destino.')
                            if analista_origen == 'Crear analista nuevo' and not nuevo_analista_nombre.strip():
                                errors.append('Debes ingresar el nombre del nuevo analista.')
                            if analista_origen == 'Analista existente':
                                default_analyst_id = _resolve_or_create_analista(analista_seleccionado_excel, analistas, crear_nuevo=False)
                            else:
                                default_analyst_id = _resolve_or_create_analista(
                                    f'{nuevo_analista_nombre} {nuevo_analista_apellido}',
                                    analistas,
                                    crear_nuevo=True,
                                    nuevo_analista={
                                        'nombre': nuevo_analista_nombre,
                                        'apellido': nuevo_analista_apellido,
                                        'cargo': nuevo_analista_cargo,
                                        'contacto': nuevo_analista_contacto,
                                    }
                                )
                        else:
                            default_analyst_id = None

                        if control_type_excel == 'Variable':
                            if not value_column:
                                errors.append('Debes seleccionar la columna de valores de la variable.')
                            if not nombre_variable.strip():
                                errors.append('Debes ingresar el nombre de la variable para la importación.')
                        else:
                            if not inspeccionados_column:
                                errors.append('Debes seleccionar la columna de inspeccionados.')
                            if not defectuosos_column:
                                errors.append('Debes seleccionar la columna de defectuosos.')
                            if not nombre_atributo.strip():
                                errors.append('Debes ingresar el nombre del atributo para la importación.')

                        if errors:
                            for error in errors:
                                st.error(error)
                        else:
                            if control_type_excel == 'Variable':
                                if producto_column == '<No usar>':
                                    product_id = default_product_id
                                    if product_id is None:
                                        st.error('No existe el producto destino.')
                                        return
                                else:
                                    product_id = None

                                if analista_column == '<No usar>':
                                    analyst_id = default_analyst_id
                                    if analyst_id is None:
                                        st.error('No existe el analista destino.')
                                        return
                                else:
                                    analyst_id = None

                                if producto_column == '<No usar>' and analista_column == '<No usar>':
                                    values = _parse_column_values(df_sheet[value_column], float)
                                    if len(values) < 2:
                                        st.error('La columna seleccionada no tiene suficientes valores numéricos.')
                                    else:
                                        rows_to_register.append({
                                            'tipo_control': 'variable',
                                            'producto_id': product_id,
                                            'analista_id': analyst_id,
                                            'fecha_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                            'num_subgrupo': 1,
                                            'lote': '',
                                            'origen': '',
                                            'observaciones': '',
                                            'nombre_variable': nombre_variable.strip(),
                                            'tipo_dato': tipo_dato,
                                            'lcs': lcs,
                                            'lci': lci,
                                            'valor_nominal': valor_nominal,
                                            'valores': values,
                                        })
                                else:
                                    grouped = df_sheet.groupby(producto_column) if producto_column != '<No usar>' else [('__fixed__', df_sheet)]
                                    for product_name, group in grouped:
                                        if producto_column == '<No usar>':
                                            product_id = default_product_id
                                        else:
                                            product_id = get_product_id_for_name(product_name)
                                            if not product_id:
                                                errors.append(f'Producto "{product_name}" no existe y no se puede crear.')
                                                continue
                                        if analista_column == '<No usar>':
                                            analyst_id = default_analyst_id
                                        else:
                                            first_analyst = group[analista_column].astype(str).str.strip()
                                            first_analyst = first_analyst[first_analyst != '']
                                            analyst_id = get_analyst_id_for_name(first_analyst.iloc[0]) if not first_analyst.empty else default_analyst_id
                                        if analyst_id is None:
                                            errors.append(f'No se pudo resolver el analista para producto "{product_name}".')
                                            continue
                                        values = _parse_column_values(group[value_column], float)
                                        if len(values) < 2:
                                            errors.append(f'Producto "{product_name}" no tiene suficientes valores numéricos en la columna seleccionada.')
                                            continue
                                        rows_to_register.append({
                                            'tipo_control': 'variable',
                                            'producto_id': product_id,
                                            'analista_id': analyst_id,
                                            'fecha_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                            'num_subgrupo': 1,
                                            'lote': '',
                                            'origen': '',
                                            'observaciones': '',
                                            'nombre_variable': nombre_variable.strip(),
                                            'tipo_dato': tipo_dato,
                                            'lcs': lcs,
                                            'lci': lci,
                                            'valor_nominal': valor_nominal,
                                            'valores': values,
                                        })
                            else:
                                if producto_column == '<No usar>':
                                    product_id = default_product_id
                                    if product_id is None:
                                        st.error('No existe el producto destino.')
                                        return
                                else:
                                    product_id = None
                                if analista_column == '<No usar>':
                                    analyst_id = default_analyst_id
                                    if analyst_id is None:
                                        st.error('No existe el analista destino.')
                                        return
                                else:
                                    analyst_id = None
                                if producto_column == '<No usar>':
                                    inspected = _parse_column_values(df_sheet[inspeccionados_column], int)
                                    defected = _parse_column_values(df_sheet[defectuosos_column], int)
                                    if len(inspected) == 0 or len(inspected) != len(defected):
                                        st.error('Las columnas seleccionadas no tienen juegos válidos de inspeccionados y defectuosos.')
                                    else:
                                        rows_to_register.append({
                                            'tipo_control': 'atributo',
                                            'producto_id': product_id,
                                            'analista_id': analyst_id,
                                            'fecha_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                            'num_subgrupo': tam_subgrupo,
                                            'lote': '',
                                            'origen': '',
                                            'observaciones': '',
                                            'nombre_atributo': nombre_atributo.strip(),
                                            'tipo_grafico': tipo_grafico,
                                            'tam_subgrupo': tam_subgrupo,
                                            'inspeccionados': inspected,
                                            'defectuosos': defected,
                                        })
                                else:
                                    grouped = df_sheet.groupby(producto_column)
                                    for product_name, group in grouped:
                                        product_id = get_product_id_for_name(product_name)
                                        if not product_id:
                                            errors.append(f'Producto "{product_name}" no existe y no se puede crear.')
                                            continue
                                        if analista_column != '<No usar>':
                                            first_analyst = group[analista_column].astype(str).str.strip()
                                            first_analyst = first_analyst[first_analyst != '']
                                            analyst_id = get_analyst_id_for_name(first_analyst.iloc[0]) if not first_analyst.empty else default_analyst_id
                                        else:
                                            analyst_id = default_analyst_id
                                        if analyst_id is None:
                                            errors.append(f'No se pudo resolver el analista para producto "{product_name}".')
                                            continue
                                        inspected = _parse_column_values(group[inspeccionados_column], int)
                                        defected = _parse_column_values(group[defectuosos_column], int)
                                        if len(inspected) == 0 or len(inspected) != len(defected):
                                            errors.append(f'Producto "{product_name}" no tiene juegos válidos de inspeccionados y defectuosos.')
                                            continue
                                        rows_to_register.append({
                                            'tipo_control': 'atributo',
                                            'producto_id': product_id,
                                            'analista_id': analyst_id,
                                            'fecha_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                            'num_subgrupo': tam_subgrupo,
                                            'lote': '',
                                            'origen': '',
                                            'observaciones': '',
                                            'nombre_atributo': nombre_atributo.strip(),
                                            'tipo_grafico': tipo_grafico,
                                            'tam_subgrupo': tam_subgrupo,
                                            'inspeccionados': inspected,
                                            'defectuosos': defected,
                                        })
                            if errors:
                                for error in errors:
                                    st.error(error)
                            elif rows_to_register:
                                registered = _register_excel_samples(rows_to_register)
                                st.success(f'Se registraron {len(registered)} muestras desde Excel.')
                                st.experimental_rerun()
                            else:
                                st.info('No se registraron muestras. Revisa los datos y selecciona las columnas correctas.')

    with section_card('Datos de muestra', 'Selecciona producto, analista y configura la muestra antes de registrarla.'):
        if productos.empty or analistas.empty:
            st.warning('Necesitas al menos un producto y un analista para registrar muestras.')
            return

        producto_seleccionado = st.selectbox('Producto', [''] + productos['nombre'].tolist())
        analista_seleccionado = st.selectbox('Analista', [''] + (analistas['nombre'] + ' ' + analistas['apellido']).tolist())

        if not producto_seleccionado or not analista_seleccionado:
            st.info('Selecciona un producto y un analista.')
            return

        id_producto = int(productos.loc[productos['nombre'] == producto_seleccionado, 'id_producto'].iloc[0])
        id_analista = int(analistas.loc[(analistas['nombre'] + ' ' + analistas['apellido']) == analista_seleccionado, 'id_analista'].iloc[0])

        tipo_control = st.radio('Tipo de control', ['Variable', 'Atributo'])
        fecha_hora = st.datetime_input('Fecha y hora de la muestra', value=datetime.now())
        num_subgrupo = st.number_input('Tamaño del subgrupo', min_value=1, max_value=50, value=5)
        lote = st.text_input('Lote')
        origen = st.text_input('Origen')
        observaciones = st.text_area('Observaciones')

        if tipo_control == 'Variable':
            configs = pd.DataFrame(queries.get_variables_by_producto(id_producto))
            opcions = ['<Nueva configuración>'] + [f"{row['id_variable']} - {row['nombre_variable']}" for _, row in configs.iterrows()]
            seleccion = st.selectbox('Configuración de variable', opcions)

            if seleccion != '<Nueva configuración>':
                id_variable = int(seleccion.split(' - ')[0])
                config = queries.get_variable_config_by_id(id_variable)
                st.markdown(f"**Variable:** {config['nombre_variable']} | Tipo: {config['tipo_dato']} | LCI: {config['lci']} | LCS: {config['lcs']}")
            else:
                nombre_variable = st.text_input('Nombre de la variable')
                tipo_dato = st.selectbox('Tipo de dato', ['continua', 'discreta'])
                lcs = st.number_input('Límite de control superior (LCS)', value=0.0)
                lci = st.number_input('Límite de control inferior (LCI)', value=0.0)
                valor_nominal = st.number_input('Valor nominal', value=0.0)

            valores = st.text_area('Valores de la variable (separados por espacios o comas)')
            if st.button('Guardar muestra de variable'):
                if seleccion == '<Nueva configuración>' and not nombre_variable.strip():
                    st.error('Debes ingresar el nombre de la variable.')
                else:
                    datos = [float(x) for x in valores.replace(',', ' ').split() if x.strip()]
                    if len(datos) < 2:
                        st.error('Ingresa al menos dos valores válidos.')
                    else:
                        if seleccion == '<Nueva configuración>':
                            id_variable = queries.insert_variable_config(id_producto, nombre_variable.strip(), tipo_dato, lcs, lci, valor_nominal, num_subgrupo)
                        muestra_id = queries.insert_muestra(id_producto, id_analista, num_subgrupo, lote.strip(), origen.strip(), observaciones.strip(), fecha_hora.strftime('%Y-%m-%d %H:%M:%S'))
                        for idx, valor in enumerate(datos, start=1):
                            queries.insert_medicion_variable(muestra_id, id_variable, idx, float(valor))
                        st.success('Muestra de variable registrada correctamente.')
                        st.rerun()

        else:
            configs = pd.DataFrame(queries.get_atributos_by_producto(id_producto))
            opcions = ['<Nueva configuración>'] + [f"{row['id_atributo']} - {row['nombre_atributo']}" for _, row in configs.iterrows()]
            seleccion = st.selectbox('Configuración de atributo', opcions)

            if seleccion != '<Nueva configuración>':
                id_atributo = int(seleccion.split(' - ')[0])
                config = queries.get_atributo_by_id(id_atributo)
                st.markdown(f"**Atributo:** {config['nombre_atributo']} | Tipo gráfico: {config['tipo_grafico']} | Tamaño subgrupo: {config['tam_subgrupo']}")
                tipo_grafico = config['tipo_grafico']
                tam_subgrupo = int(config['tam_subgrupo'] or num_subgrupo)
            else:
                nombre_atributo = st.text_input('Nombre del atributo')
                tipo_grafico = st.selectbox('Tipo de gráfico', ['P', 'NP', 'C', 'U'])
                tam_subgrupo = st.number_input('Tamaño del subgrupo para atributo', min_value=1, max_value=1000, value=num_subgrupo)

            inspeccionados = st.text_area('N° inspeccionados por muestra (ejemplo: 100 100 100)')
            defectuosos = st.text_area('N° defectuosos por muestra (ejemplo: 5 4 3)')

            if st.button('Guardar muestra de atributo'):
                if seleccion == '<Nueva configuración>' and not nombre_atributo.strip():
                    st.error('Debes ingresar el nombre del atributo.')
                else:
                    n_inspeccionados = [int(x) for x in inspeccionados.replace(',', ' ').split() if x.strip()]
                    n_defectuosos = [int(x) for x in defectuosos.replace(',', ' ').split() if x.strip()]
                    if len(n_inspeccionados) == 0 or len(n_inspeccionados) != len(n_defectuosos):
                        st.error('Ingresa listas válidas de inspeccionados y defectuosos de igual tamaño.')
                    else:
                        if seleccion == '<Nueva configuración>':
                            id_atributo = queries.insert_atributo_config(id_producto, nombre_atributo.strip(), tipo_grafico, tam_subgrupo)
                        muestra_id = queries.insert_muestra(id_producto, id_analista, num_subgrupo, lote.strip(), origen.strip(), observaciones.strip(), fecha_hora.strftime('%Y-%m-%d %H:%M:%S'))
                        for n, d in zip(n_inspeccionados, n_defectuosos):
                            queries.insert_medicion_atributo(muestra_id, id_atributo, int(n), int(d))
                        st.success('Muestra de atributo registrada correctamente.')
                        st.rerun()
