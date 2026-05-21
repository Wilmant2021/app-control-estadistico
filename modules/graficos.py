import plotly.graph_objs as go
import pandas as pd


def crear_grafico_xbar_r(datos_xbar: list[float], datos_r: list[float], xbar_bar: float, r_bar: float, lcs_xbar: float, lci_xbar: float, lcs_r: float, lci_r: float):
    x = list(range(1, len(datos_xbar) + 1))
    colores_xbar = ['red' if i in [idx for idx, valor in enumerate(datos_xbar) if valor > lcs_xbar or valor < lci_xbar] else 'blue' for i in range(len(datos_xbar))]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=datos_xbar, mode='lines+markers', name='X̄', marker=dict(color=colores_xbar, size=10)))
    fig.add_hline(y=xbar_bar, line_dash='dash', line_color='black', annotation_text='X̄-bar', annotation_position='top left')
    fig.add_hline(y=lcs_xbar, line_dash='dot', line_color='red', annotation_text='UCL', annotation_position='top right')
    fig.add_hline(y=lci_xbar, line_dash='dot', line_color='red', annotation_text='LCL', annotation_position='bottom right')
    fig.update_layout(title='Gráfico X̄', xaxis_title='Subgrupo', yaxis_title='Media')

    colores_r = ['red' if i in [idx for idx, valor in enumerate(datos_r) if valor > lcs_r or valor < lci_r] else 'blue' for i in range(len(datos_r))]
    fig_r = go.Figure()
    fig_r.add_trace(go.Scatter(x=x, y=datos_r, mode='lines+markers', name='Rango', marker=dict(color=colores_r, size=10)))
    fig_r.add_hline(y=r_bar, line_dash='dash', line_color='black', annotation_text='R-bar', annotation_position='top left')
    fig_r.add_hline(y=lcs_r, line_dash='dot', line_color='red', annotation_text='UCL', annotation_position='top right')
    fig_r.add_hline(y=lci_r, line_dash='dot', line_color='red', annotation_text='LCL', annotation_position='bottom right')
    fig_r.update_layout(title='Gráfico R', xaxis_title='Subgrupo', yaxis_title='Rango')
    return fig, fig_r


def crear_grafico_xbar_s(datos_xbar: list[float], datos_s: list[float], xbar_bar: float, s_bar: float, lcs_xbar: float, lci_xbar: float, lcs_s: float, lci_s: float):
    x = list(range(1, len(datos_xbar) + 1))
    colores_xbar = ['red' if i in [idx for idx, valor in enumerate(datos_xbar) if valor > lcs_xbar or valor < lci_xbar] else 'blue' for i in range(len(datos_xbar))]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=datos_xbar, mode='lines+markers', name='X̄', marker=dict(color=colores_xbar, size=10)))
    fig.add_hline(y=xbar_bar, line_dash='dash', line_color='black', annotation_text='X̄-bar', annotation_position='top left')
    fig.add_hline(y=lcs_xbar, line_dash='dot', line_color='red', annotation_text='UCL', annotation_position='top right')
    fig.add_hline(y=lci_xbar, line_dash='dot', line_color='red', annotation_text='LCL', annotation_position='bottom right')
    fig.update_layout(title='Gráfico X̄', xaxis_title='Subgrupo', yaxis_title='Media')

    colores_s = ['red' if i in [idx for idx, valor in enumerate(datos_s) if valor > lcs_s or valor < lci_s] else 'blue' for i in range(len(datos_s))]
    fig_s = go.Figure()
    fig_s.add_trace(go.Scatter(x=x, y=datos_s, mode='lines+markers', name='S', marker=dict(color=colores_s, size=10)))
    fig_s.add_hline(y=s_bar, line_dash='dash', line_color='black', annotation_text='S-bar', annotation_position='top left')
    fig_s.add_hline(y=lcs_s, line_dash='dot', line_color='red', annotation_text='UCL', annotation_position='top right')
    fig_s.add_hline(y=lci_s, line_dash='dot', line_color='red', annotation_text='LCL', annotation_position='bottom right')
    fig_s.update_layout(title='Gráfico S', xaxis_title='Subgrupo', yaxis_title='Desviación estándar')
    return fig, fig_s


def crear_grafico_p(indices: list[int], p: list[float], p_bar: float, lcs: list[float], lci: list[float], fuera: list[int]):
    x = [i + 1 for i in indices]
    colores = ['red' if i in fuera else 'blue' for i in indices]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=x, y=p, name='p', marker=dict(color=colores)))
    fig.add_hline(y=p_bar, line_dash='dash', line_color='black', annotation_text='p-bar', annotation_position='top left')
    for valor in lcs:
        fig.add_hline(y=valor, line_dash='dot', line_color='red')
    for valor in lci:
        fig.add_hline(y=valor, line_dash='dot', line_color='red')
    fig.update_layout(title='Gráfico P', xaxis_title='Muestra', yaxis_title='Proporción defectuosa')
    return fig


def crear_grafico_np(indices: list[int], np_values: list[int], np_bar: float, lcs: float, lci: float):
    x = [i + 1 for i in indices]
    colores = ['red' if valor > lcs or valor < lci else 'blue' for valor in np_values]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=x, y=np_values, name='Np', marker=dict(color=colores)))
    fig.add_hline(y=np_bar, line_dash='dash', line_color='black', annotation_text='Np-bar', annotation_position='top left')
    fig.add_hline(y=lcs, line_dash='dot', line_color='red', annotation_text='UCL', annotation_position='top right')
    fig.add_hline(y=lci, line_dash='dot', line_color='red', annotation_text='LCL', annotation_position='bottom right')
    fig.update_layout(title='Gráfico Np', xaxis_title='Muestra', yaxis_title='Número defectuoso')
    return fig


def crear_grafico_c(indices: list[int], c_values: list[int], c_bar: float, lcs: float, lci: float):
    x = [i + 1 for i in indices]
    colores = ['red' if valor > lcs or valor < lci else 'blue' for valor in c_values]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=x, y=c_values, name='C', marker=dict(color=colores)))
    fig.add_hline(y=c_bar, line_dash='dash', line_color='black', annotation_text='C-bar', annotation_position='top left')
    fig.add_hline(y=lcs, line_dash='dot', line_color='red', annotation_text='UCL', annotation_position='top right')
    fig.add_hline(y=lci, line_dash='dot', line_color='red', annotation_text='LCL', annotation_position='bottom right')
    fig.update_layout(title='Gráfico C', xaxis_title='Muestra', yaxis_title='Defectos por unidad')
    return fig


def crear_grafico_u(indices: list[int], u_values: list[float], u_bar: float, lcs: list[float], lci: list[float]):
    x = [i + 1 for i in indices]
    colores = ['red' if valor > lcs[idx] or valor < lci[idx] else 'blue' for idx, valor in enumerate(u_values)]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=x, y=u_values, name='U', marker=dict(color=colores)))
    fig.add_hline(y=u_bar, line_dash='dash', line_color='black', annotation_text='U-bar', annotation_position='top left')
    for valor in lcs:
        fig.add_hline(y=valor, line_dash='dot', line_color='red')
    for valor in lci:
        fig.add_hline(y=valor, line_dash='dot', line_color='red')
    fig.update_layout(title='Gráfico U', xaxis_title='Muestra', yaxis_title='Defectos por unidad')
    return fig


def crear_histograma(datos: list[float], bins: int = 10, titulo: str = 'Histograma'):
    fig = go.Figure(data=[go.Histogram(x=datos, nbinsx=bins)])
    fig.update_layout(title=titulo, xaxis_title='Valor', yaxis_title='Frecuencia')
    return fig


def crear_grafico_pareto(categorias: list[str], frecuencias: list[int], titulo: str = 'Diagrama de Pareto'):
    df = pd.DataFrame({'categoria': categorias, 'frecuencia': frecuencias})
    df = df.sort_values('frecuencia', ascending=False)
    acumulado = df['frecuencia'].cumsum() / df['frecuencia'].sum() * 100
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df['categoria'], y=df['frecuencia'], name='Frecuencia', marker=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df['categoria'], y=acumulado, mode='lines+markers', name='Acumulado (%)', yaxis='y2', marker=dict(color='red')))
    fig.add_hline(y=80, line_dash='dash', line_color='green', annotation_text='80%', annotation_position='top right', yref='y2')
    fig.update_layout(
        title=titulo,
        xaxis_title='Categoría',
        yaxis_title='Frecuencia',
        yaxis2=dict(title='Acumulado (%)', overlaying='y', side='right', rangemode='tozero', range=[0, 100])
    )
    return fig


