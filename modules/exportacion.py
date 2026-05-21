import pandas as pd
from openpyxl.utils import get_column_letter


def exportar_a_excel(dataframes: dict[str, pd.DataFrame], nombre_archivo: str = 'exportacion.xlsx') -> str:
    """Exporta múltiples DataFrames a un archivo Excel con hojas separadas."""
    with pd.ExcelWriter(nombre_archivo, engine='openpyxl') as writer:
        for hoja, df in dataframes.items():
            df.to_excel(writer, sheet_name=hoja[:31], index=False)
            _autosize_worksheet_columns(writer.sheets[hoja[:31]])
    return nombre_archivo


def exportar_reporte_control_excel(
    nombre_archivo: str,
    metadata: dict,
    tipo_control: str,
    tipo_grafico: str,
    df_mediciones: pd.DataFrame,
    resultados_control: dict,
    resultados_capacidad: dict | None = None,
    resultado_normalidad: dict | None = None,
    tam_subgrupo: int | None = None,
) -> str:
    """Exporta un reporte CEP estructurado en un archivo Excel con varias hojas."""
    with pd.ExcelWriter(nombre_archivo, engine='openpyxl') as writer:
        _write_resumen_ejecutivo(
            writer,
            metadata,
            tipo_control,
            tipo_grafico,
            resultados_capacidad,
            resultado_normalidad,
            df_mediciones,
            resultados_control,
            tam_subgrupo,
        )
        _write_datos_control(writer, df_mediciones, tipo_control, tipo_grafico, tam_subgrupo)
        _write_limites_control(writer, tipo_control, tipo_grafico, resultados_control)
    return nombre_archivo


def _write_resumen_ejecutivo(
    writer,
    metadata: dict,
    tipo_control: str,
    tipo_grafico: str,
    resultados_capacidad: dict | None,
    resultado_normalidad: dict | None,
    df_mediciones: pd.DataFrame,
    resultados_control: dict,
    tam_subgrupo: int | None,
) -> None:
    sheet = 'Resumen Ejecutivo'[:31]
    metadata_items = [
        ('Producto', metadata.get('producto', 'N/A')),
        ('Analista', metadata.get('analista', 'N/A')),
        ('Variable/Atributo', metadata.get('variable_atributo', 'N/A')),
        ('Tipo de control', tipo_control),
        ('Tipo de gráfico', tipo_grafico),
        ('Fecha/Hora', metadata.get('fecha_hora', 'N/A')),
        ('Tamaño de subgrupo', tam_subgrupo or metadata.get('tam_subgrupo', 'N/A')),
        ('Cantidad de observaciones', len(df_mediciones)),
        ('Subgrupos calculados', metadata.get('subgrupos_calculados', 'N/A')),
    ]
    df_metadata = pd.DataFrame(metadata_items, columns=['Campo', 'Valor'])

    startrow = 0
    df_metadata.to_excel(writer, sheet_name=sheet, index=False, startrow=startrow)
    startrow += len(df_metadata) + 2

    if resultados_capacidad is not None:
        capacidad_items = [
            ('Cp', resultados_capacidad.get('cp', 'N/A')),
            ('Cpk', resultados_capacidad.get('cpk', 'N/A')),
            ('Pp', resultados_capacidad.get('pp', 'N/A')),
            ('Ppk', resultados_capacidad.get('ppk', 'N/A')),
            ('Interpretación de capacidad', resultados_capacidad.get('interpretacion', 'N/A')),
        ]
        df_capacidad = pd.DataFrame(capacidad_items, columns=['Métrica', 'Valor'])
        df_capacidad.to_excel(writer, sheet_name=sheet, index=False, startrow=startrow)
        startrow += len(df_capacidad) + 2

    if resultado_normalidad is not None:
        normalidad_items = [
            ('Estadístico Shapiro-Wilk', resultado_normalidad.get('estadistico', 'N/A')),
            ('p-valor', resultado_normalidad.get('p_valor', 'N/A')),
            ('Resultado', resultado_normalidad.get('interpretacion', 'N/A')),
            ('Normalidad aceptada', resultado_normalidad.get('es_normal', 'N/A')),
        ]
        df_normalidad = pd.DataFrame(normalidad_items, columns=['Métrica', 'Valor'])
        df_normalidad.to_excel(writer, sheet_name=sheet, index=False, startrow=startrow)

    _autosize_worksheet_columns(writer.sheets[sheet])


def _write_datos_control(
    writer,
    df_mediciones: pd.DataFrame,
    tipo_control: str,
    tipo_grafico: str,
    tam_subgrupo: int | None,
) -> None:
    sheet = 'Datos de Control'[:31]
    df_panel = _build_datos_control_df(df_mediciones, tipo_control, tipo_grafico, tam_subgrupo)
    df_panel.to_excel(writer, sheet_name=sheet, index=False)
    _autosize_worksheet_columns(writer.sheets[sheet])


def _write_limites_control(
    writer,
    tipo_control: str,
    tipo_grafico: str,
    resultados_control: dict,
) -> None:
    sheet = 'Límites de Control'[:31]
    df_summary, df_details = _build_limites_control_df(tipo_control, tipo_grafico, resultados_control)
    df_summary.to_excel(writer, sheet_name=sheet, index=False, startrow=0)
    df_details.to_excel(writer, sheet_name=sheet, index=False, startrow=len(df_summary) + 3)
    _autosize_worksheet_columns(writer.sheets[sheet])


def _build_datos_control_df(
    df_mediciones: pd.DataFrame,
    tipo_control: str,
    tipo_grafico: str,
    tam_subgrupo: int | None,
) -> pd.DataFrame:
    if tipo_control.lower() == 'variable':
        if 'num_observacion' not in df_mediciones.columns or 'valor' not in df_mediciones.columns:
            raise ValueError('Los datos de medición variable deben incluir num_observacion y valor')
        df = df_mediciones.copy()
        df = df.sort_values('num_observacion').reset_index(drop=True)
        tam_subgrupo = int(tam_subgrupo or df.get('tam_subgrupo', pd.Series([5])).iloc[0])
        df['Subgrupo'] = ((df['num_observacion'] - 1) // tam_subgrupo) + 1
        agrupado = df.groupby('Subgrupo')['valor']
        df['X-barra'] = agrupado.transform('mean')
        if tipo_grafico.lower() == 'x-barra y s':
            df['S'] = agrupado.transform(lambda grupo: grupo.std(ddof=1))
            df['Rango'] = agrupado.transform(lambda grupo: grupo.max() - grupo.min())
        else:
            df['Rango'] = agrupado.transform(lambda grupo: grupo.max() - grupo.min())
            df['S'] = agrupado.transform(lambda grupo: grupo.std(ddof=1))
        df = df[['Subgrupo', 'num_observacion', 'valor', 'X-barra', 'Rango', 'S']]
        df.columns = ['Subgrupo', 'Observación', 'Valor', 'X-barra', 'Rango', 'Desviación S']
        return df

    if tipo_control.lower() == 'atributo':
        if 'n_inspeccionados' not in df_mediciones.columns or 'n_defectuosos' not in df_mediciones.columns:
            raise ValueError('Los datos de atributos deben incluir n_inspeccionados y n_defectuosos')
        df = df_mediciones.copy()
        df = df.reset_index(drop=True)
        df['Subgrupo'] = df.index + 1
        df['Fracción Defectuosa'] = df['n_defectuosos'] / df['n_inspeccionados']
        df = df[['Subgrupo', 'n_inspeccionados', 'n_defectuosos', 'Fracción Defectuosa']]
        df.columns = ['Subgrupo', 'Inspeccionados', 'Defectuosos', 'Fracción Defectuosa']
        return df

    raise ValueError(f'Tipo de control no reconocido: {tipo_control}')


def _build_limites_control_df(tipo_control: str, tipo_grafico: str, resultados_control: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    if tipo_control.lower() == 'variable':
        if tipo_grafico.lower() == 'x-barra y r':
            df_summary = pd.DataFrame([
                ('Línea central X-barra', resultados_control.get('xbar_bar', 'N/A')),
                ('Línea central Rango', resultados_control.get('r_bar', 'N/A')),
                ('LCS X-barra', resultados_control.get('lcs_xbar', 'N/A')),
                ('LCI X-barra', resultados_control.get('lci_xbar', 'N/A')),
                ('LCS Rango', resultados_control.get('lcs_r', 'N/A')),
                ('LCI Rango', resultados_control.get('lci_r', 'N/A')),
            ], columns=['Métrica', 'Valor'])
            detalle = pd.DataFrame({
                'Subgrupo': list(range(1, len(resultados_control.get('xbars', [])) + 1)),
                'X-barra': resultados_control.get('xbars', []),
                'Rango': resultados_control.get('rangos', []),
                'LCS X-barra': [resultados_control.get('lcs_xbar', pd.NA)] * len(resultados_control.get('xbars', [])),
                'LCI X-barra': [resultados_control.get('lci_xbar', pd.NA)] * len(resultados_control.get('xbars', [])),
                'LCS Rango': [resultados_control.get('lcs_r', pd.NA)] * len(resultados_control.get('rangos', [])),
                'LCI Rango': [resultados_control.get('lci_r', pd.NA)] * len(resultados_control.get('rangos', [])),
            })
            return df_summary, detalle

        if tipo_grafico.lower() == 'x-barra y s':
            df_summary = pd.DataFrame([
                ('Línea central X-barra', resultados_control.get('xbar_bar', 'N/A')),
                ('Línea central S', resultados_control.get('s_bar', 'N/A')),
                ('LCS X-barra', resultados_control.get('lcs_xbar', 'N/A')),
                ('LCI X-barra', resultados_control.get('lci_xbar', 'N/A')),
                ('LCS S', resultados_control.get('lcs_s', 'N/A')),
                ('LCI S', resultados_control.get('lci_s', 'N/A')),
            ], columns=['Métrica', 'Valor'])
            detalle = pd.DataFrame({
                'Subgrupo': list(range(1, len(resultados_control.get('xbars', [])) + 1)),
                'X-barra': resultados_control.get('xbars', []),
                'S': resultados_control.get('s', []),
                'LCS X-barra': [resultados_control.get('lcs_xbar', pd.NA)] * len(resultados_control.get('xbars', [])),
                'LCI X-barra': [resultados_control.get('lci_xbar', pd.NA)] * len(resultados_control.get('xbars', [])),
                'LCS S': [resultados_control.get('lcs_s', pd.NA)] * len(resultados_control.get('s', [])),
                'LCI S': [resultados_control.get('lci_s', pd.NA)] * len(resultados_control.get('s', [])),
            })
            return df_summary, detalle

    if tipo_control.lower() == 'atributo':
        central_label = 'Central'
        metric_name = {
            'p': 'Proporción defectuosa',
            'np': 'Defectos esperados',
            'c': 'Defectos por unidad',
            'u': 'Defectos por unidad por inspección',
        }.get(tipo_grafico.lower(), 'Central')

        if tipo_grafico.upper() == 'P':
            central_value = resultados_control.get('p_bar', 'N/A')
        elif tipo_grafico.upper() == 'NP':
            central_value = resultados_control.get('np_bar', 'N/A')
        elif tipo_grafico.upper() == 'C':
            central_value = resultados_control.get('c_bar', 'N/A')
        else:
            central_value = resultados_control.get('u_bar', 'N/A')

        df_summary = pd.DataFrame([
            (metric_name, central_value),
            ('Límite superior de control', 'Ver detalle por subgrupo'),
            ('Límite inferior de control', 'Ver detalle por subgrupo'),
        ], columns=['Métrica', 'Valor'])
        detalles = {
            'Subgrupo': list(range(1, len(resultados_control.get('lcs', [])) + 1)),
            metric_name: resultados_control.get(tipo_grafico.lower(), []),
            'LCS': resultados_control.get('lcs', []),
            'LCI': resultados_control.get('lci', []),
        }
        detalle = pd.DataFrame(detalles)
        return df_summary, detalle

    raise ValueError(f'Tipo de control no reconocido para límites: {tipo_control}')


def _autosize_worksheet_columns(worksheet) -> None:
    for column_cells in worksheet.columns:
        max_length = 0
        column = column_cells[0].column_letter
        for cell in column_cells:
            try:
                value = str(cell.value)
            except Exception:
                value = ''
            if value is None:
                value = ''
            max_length = max(max_length, len(value))
        adjusted_width = min(max_length + 2, 50)
        worksheet.column_dimensions[column].width = adjusted_width


def crear_dataframe_mediciones_variables(mediciones: list[tuple]) -> pd.DataFrame:
    columnas = [
        'id_medicion', 'id_muestra', 'id_variable', 'num_observacion', 'valor', 'es_atipico'
    ]
    return pd.DataFrame(mediciones, columns=columnas)


def crear_dataframe_mediciones_atributos(mediciones: list[tuple]) -> pd.DataFrame:
    columnas = [
        'id_med_atrib', 'id_muestra', 'id_atributo', 'n_inspeccionados', 'n_defectuosos', 'fuera_control'
    ]
    return pd.DataFrame(mediciones, columns=columnas)


def crear_dataframe_muestras(muestras: list[tuple]) -> pd.DataFrame:
    columnas = [
        'id_muestra', 'id_producto', 'id_analista', 'fecha_hora', 'num_subgrupo', 'lote', 'origen', 'observaciones'
    ]
    return pd.DataFrame(muestras, columns=columnas)


def crear_dataframe_productos(productos: list[tuple]) -> pd.DataFrame:
    columnas = ['id_producto', 'nombre', 'tipo', 'variedad', 'unidad_medida', 'descripcion']
    return pd.DataFrame(productos, columns=columnas)


def crear_dataframe_analistas(analistas: list[tuple]) -> pd.DataFrame:
    columnas = ['id_analista', 'nombre', 'apellido', 'cargo', 'contacto']
    return pd.DataFrame(analistas, columns=columnas)


def crear_dataframe_variables(variable_config: list[tuple]) -> pd.DataFrame:
    columnas = ['id_variable', 'id_producto', 'nombre_variable', 'tipo_dato', 'lcs', 'lci', 'valor_nominal', 'tam_subgrupo']
    return pd.DataFrame(variable_config, columns=columnas)


def crear_dataframe_atributos(atributos: list[tuple]) -> pd.DataFrame:
    columnas = ['id_atributo', 'id_producto', 'nombre_atributo', 'tipo_grafico', 'tam_subgrupo']
    return pd.DataFrame(atributos, columns=columnas)
