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

    with section_card('Carga masiva desde Excel', 'Sube un archivo Excel para registrar varias muestras en bloque.'):
        excel_file = st.file_uploader('Selecciona un archivo Excel (.xlsx)', type=['xlsx'])
        if excel_file is not None:
            try:
                sheets = pd.read_excel(excel_file, sheet_name=None)
            except Exception as error:
                st.error(f'No se pudo leer el archivo Excel: {error}')
                sheets = None

            if sheets is not None:
                all_rows = []
                all_errors = []
                for sheet_name, df_sheet in sheets.items():
                    if df_sheet.empty:
                        continue
                    rows, errors = _parse_excel_sheet(df_sheet, sheet_name, productos, analistas)
                    all_rows.extend(rows)
                    all_errors.extend(errors)

                if all_errors:
                    st.warning('Algunos registros contienen errores y no se importarán:')
                    for error in all_errors:
                        st.write(f'- {error}')

                if all_rows:
                    st.write(f'Se encontraron {len(all_rows)} muestras válidas para importar.')
                    if st.button('Registrar muestras desde Excel'):
                        registered = _register_excel_samples(all_rows)
                        st.success(f'Se registraron {len(registered)} muestras desde Excel.')
                        st.experimental_rerun()
                elif not all_errors:
                    st.info('No se encontraron muestras válidas en el archivo Excel. Revisa los nombres de las columnas y los datos.')
