import numpy as np
from scipy import stats

CONSTANTES = {
    'd2': {
        2: 1.128, 3: 1.693, 4: 2.059, 5: 2.326, 6: 2.534, 7: 2.704, 8: 2.847, 9: 2.970, 10: 3.078,
        11: 3.173, 12: 3.258, 13: 3.336, 14: 3.407, 15: 3.472, 16: 3.532, 17: 3.588, 18: 3.640, 19: 3.689, 20: 3.735,
        21: 3.778, 22: 3.819, 23: 3.858, 24: 3.895, 25: 3.931
    },
    'c4': {
        2: 0.7979, 3: 0.8862, 4: 0.9213, 5: 0.9400, 6: 0.9515, 7: 0.9594, 8: 0.9650, 9: 0.9693, 10: 0.9727,
        11: 0.9754, 12: 0.9776, 13: 0.9794, 14: 0.9810, 15: 0.9823, 16: 0.9834, 17: 0.9843, 18: 0.9851, 19: 0.9858, 20: 0.9864,
        21: 0.9869, 22: 0.9874, 23: 0.9877, 24: 0.9881, 25: 0.9884
    },
    'A2': {
        2: 1.880, 3: 1.023, 4: 0.729, 5: 0.577, 6: 0.483, 7: 0.419, 8: 0.373, 9: 0.337, 10: 0.308,
        11: 0.285, 12: 0.266, 13: 0.249, 14: 0.235, 15: 0.223, 16: 0.212, 17: 0.203, 18: 0.194, 19: 0.187, 20: 0.180,
        21: 0.173, 22: 0.167, 23: 0.162, 24: 0.157, 25: 0.153
    },
    'D3': {
        2: 0.000, 3: 0.000, 4: 0.000, 5: 0.000, 6: 0.000, 7: 0.076, 8: 0.136, 9: 0.184, 10: 0.223,
        11: 0.256, 12: 0.283, 13: 0.307, 14: 0.328, 15: 0.347, 16: 0.363, 17: 0.378, 18: 0.391, 19: 0.403, 20: 0.415,
        21: 0.425, 22: 0.434, 23: 0.443, 24: 0.451, 25: 0.459
    },
    'D4': {
        2: 3.267, 3: 2.574, 4: 2.282, 5: 2.114, 6: 2.004, 7: 1.924, 8: 1.864, 9: 1.816, 10: 1.777,
        11: 1.744, 12: 1.717, 13: 1.693, 14: 1.672, 15: 1.654, 16: 1.637, 17: 1.622, 18: 1.608, 19: 1.597, 20: 1.585,
        21: 1.575, 22: 1.566, 23: 1.557, 24: 1.548, 25: 1.541
    },
    'A3': {
        2: 2.659, 3: 1.954, 4: 1.628, 5: 1.427, 6: 1.287, 7: 1.182, 8: 1.099, 9: 1.032, 10: 0.975,
        11: 0.927, 12: 0.886, 13: 0.850, 14: 0.817, 15: 0.789, 16: 0.763, 17: 0.739, 18: 0.718, 19: 0.697, 20: 0.678,
        21: 0.661, 22: 0.646, 23: 0.631, 24: 0.617, 25: 0.604
    },
    'B3': {
        2: 0.000, 3: 0.000, 4: 0.000, 5: 0.000, 6: 0.030, 7: 0.118, 8: 0.185, 9: 0.239, 10: 0.284,
        11: 0.321, 12: 0.354, 13: 0.383, 14: 0.409, 15: 0.432, 16: 0.452, 17: 0.470, 18: 0.486, 19: 0.500, 20: 0.513,
        21: 0.525, 22: 0.535, 23: 0.545, 24: 0.554, 25: 0.563
    },
    'B4': {
        2: 3.267, 3: 2.568, 4: 2.266, 5: 2.089, 6: 1.970, 7: 1.882, 8: 1.815, 9: 1.761, 10: 1.716,
        11: 1.679, 12: 1.648, 13: 1.622, 14: 1.602, 15: 1.583, 16: 1.567, 17: 1.553, 18: 1.539, 19: 1.526, 20: 1.515,
        21: 1.504, 22: 1.494, 23: 1.485, 24: 1.476, 25: 1.468
    }
}


def prueba_normalidad(datos: list[float]) -> dict:
    """Aplica Shapiro-Wilk sobre los datos."""
    datos = np.array(datos, dtype=float)
    if len(datos) < 3:
        return {
            'estadistico': np.nan,
            'p_valor': np.nan,
            'es_normal': False,
            'interpretacion': 'Insuficientes datos para prueba'
        }
    estadistico, p_valor = stats.shapiro(datos)
    es_normal = p_valor > 0.05
    return {
        'estadistico': float(estadistico),
        'p_valor': float(p_valor),
        'es_normal': bool(es_normal),
        'interpretacion': 'Normal' if es_normal else 'No normal'
    }


def detectar_atipicos(datos: list[float], metodo: str = 'iqr') -> dict:
    """Detecta atípicos usando IQR o Z-score."""
    datos = np.array(datos, dtype=float)
    if metodo == 'zscore':
        z = np.abs(stats.zscore(datos, nan_policy='omit'))
        indices = np.where(z > 3)[0].tolist()
        valores = datos[indices].tolist()
        limites = {'z_limite': 3.0}
    else:
        q1 = np.percentile(datos, 25)
        q3 = np.percentile(datos, 75)
        iqr = q3 - q1
        limite_inferior = q1 - 1.5 * iqr
        limite_superior = q3 + 1.5 * iqr
        indices = np.where((datos < limite_inferior) | (datos > limite_superior))[0].tolist()
        valores = datos[indices].tolist()
        limites = {
            'limite_inferior': float(limite_inferior),
            'limite_superior': float(limite_superior),
            'iqr': float(iqr)
        }
    return {
        'indices_atipicos': indices,
        'valores_atipicos': valores,
        'limites': limites
    }


def estadisticas_descriptivas(datos: list[float]) -> dict:
    """Retorna estadísticas descriptivas básicas."""
    datos = np.array(datos, dtype=float)
    n = len(datos)
    if n == 0:
        return {
            'n': 0, 'media': np.nan, 'mediana': np.nan,
            'desv_std': np.nan, 'varianza': np.nan,
            'minimo': np.nan, 'maximo': np.nan,
            'q1': np.nan, 'q3': np.nan, 'rango': np.nan, 'cv': np.nan
        }
    media = float(np.mean(datos))
    desv_std = float(np.std(datos, ddof=1)) if n > 1 else 0.0
    varianza = float(np.var(datos, ddof=1)) if n > 1 else 0.0
    minimo = float(np.min(datos))
    maximo = float(np.max(datos))
    q1 = float(np.percentile(datos, 25))
    q3 = float(np.percentile(datos, 75))
    rango = float(maximo - minimo)
    cv = float(desv_std / media * 100) if media != 0 else np.nan
    return {
        'n': n,
        'media': media,
        'mediana': float(np.median(datos)),
        'desv_std': desv_std,
        'varianza': varianza,
        'minimo': minimo,
        'maximo': maximo,
        'q1': q1,
        'q3': q3,
        'rango': rango,
        'cv': cv
    }


def calcular_xbar_r(subgrupos: list[list[float]]) -> dict:
    """Calcula límites y puntos para el gráfico X̄-R."""
    if not subgrupos:
        raise ValueError('No hay subgrupos para calcular X-barra R')
    subgrupos = [np.array(s, dtype=float) for s in subgrupos if len(s) > 0]
    n = len(subgrupos[0])
    if len(subgrupos) < 2 or n < 2:
        raise ValueError('Se requieren al menos 2 subgrupos de tamaño mínimo 2')
    if n not in CONSTANTES['A2']:
        raise ValueError(f'No hay constantes definidas para n={n}')
    xbars = np.array([float(np.mean(s)) for s in subgrupos])
    rangos = np.array([float(np.max(s) - np.min(s)) for s in subgrupos])
    xbar_bar = float(np.mean(xbars))
    r_bar = float(np.mean(rangos))
    lcs_xbar = xbar_bar + CONSTANTES['A2'][n] * r_bar
    lci_xbar = xbar_bar - CONSTANTES['A2'][n] * r_bar
    lcs_r = CONSTANTES['D4'][n] * r_bar
    lci_r = CONSTANTES['D3'][n] * r_bar
    puntos_fuera_xbar = np.where((xbars > lcs_xbar) | (xbars < lci_xbar))[0].tolist()
    puntos_fuera_r = np.where((rangos > lcs_r) | (rangos < lci_r))[0].tolist()
    return {
        'xbars': xbars.tolist(),
        'rangos': rangos.tolist(),
        'xbar_bar': xbar_bar,
        'r_bar': r_bar,
        'lcs_xbar': lcs_xbar,
        'lci_xbar': lci_xbar,
        'lcs_r': lcs_r,
        'lci_r': lci_r,
        'puntos_fuera_xbar': puntos_fuera_xbar,
        'puntos_fuera_r': puntos_fuera_r
    }


def calcular_xbar_s(subgrupos: list[list[float]]) -> dict:
    """Calcula límites y puntos para el gráfico X̄-S."""
    if not subgrupos:
        raise ValueError('No hay subgrupos para calcular X-barra S')
    subgrupos = [np.array(s, dtype=float) for s in subgrupos if len(s) > 0]
    n = len(subgrupos[0])
    if len(subgrupos) < 2 or n < 2:
        raise ValueError('Se requieren al menos 2 subgrupos de tamaño mínimo 2')
    if n not in CONSTANTES['A3']:
        raise ValueError(f'No hay constantes definidas para n={n}')
    xbars = np.array([float(np.mean(s)) for s in subgrupos])
    s = np.array([float(np.std(s, ddof=1)) for s in subgrupos])
    xbar_bar = float(np.mean(xbars))
    s_bar = float(np.mean(s))
    lcs_xbar = xbar_bar + CONSTANTES['A3'][n] * s_bar
    lci_xbar = xbar_bar - CONSTANTES['A3'][n] * s_bar
    lcs_s = CONSTANTES['B4'][n] * s_bar
    lci_s = CONSTANTES['B3'][n] * s_bar
    puntos_fuera_xbar = np.where((xbars > lcs_xbar) | (xbars < lci_xbar))[0].tolist()
    puntos_fuera_s = np.where((s > lcs_s) | (s < lci_s))[0].tolist()
    return {
        'xbars': xbars.tolist(),
        's': s.tolist(),
        'xbar_bar': xbar_bar,
        's_bar': s_bar,
        'lcs_xbar': lcs_xbar,
        'lci_xbar': lci_xbar,
        'lcs_s': lcs_s,
        'lci_s': lci_s,
        'puntos_fuera_xbar': puntos_fuera_xbar,
        'puntos_fuera_s': puntos_fuera_s
    }


def calcular_grafico_p(n_inspeccionados: list[int], n_defectuosos: list[int]) -> dict:
    """Calcula límites para gráfico P con n variable."""
    n_inspeccionados = np.array(n_inspeccionados, dtype=float)
    n_defectuosos = np.array(n_defectuosos, dtype=float)
    p = n_defectuosos / n_inspeccionados
    p_bar = float(n_defectuosos.sum() / n_inspeccionados.sum())
    sigma = np.sqrt((p_bar * (1 - p_bar)) / n_inspeccionados)
    lcs = p_bar + 3 * sigma
    lci = np.maximum(0, p_bar - 3 * sigma)
    fuera_control = np.where((p > lcs) | (p < lci))[0].tolist()
    return {
        'p': p.tolist(),
        'p_bar': p_bar,
        'lcs': lcs.tolist(),
        'lci': lci.tolist(),
        'puntos_fuera': fuera_control
    }


def calcular_grafico_np(n_inspeccionados: list[int], n_defectuosos: list[int]) -> dict:
    """Calcula límites para gráfico Np con n constante."""
    n_inspeccionados = np.array(n_inspeccionados, dtype=float)
    n_defectuosos = np.array(n_defectuosos, dtype=float)
    if not np.all(n_inspeccionados == n_inspeccionados[0]):
        raise ValueError('N debe ser constante para gráfico Np')
    n = n_inspeccionados[0]
    p_bar = float(n_defectuosos.sum() / (n * len(n_defectuosos)))
    np_bar = float(n * p_bar)
    sigma = np.sqrt(n * p_bar * (1 - p_bar))
    lcs = np_bar + 3 * sigma
    lci = max(0, np_bar - 3 * sigma)
    fuera_control = np.where((n_defectuosos > lcs) | (n_defectuosos < lci))[0].tolist()
    return {
        'np': n_defectuosos.tolist(),
        'np_bar': np_bar,
        'lcs': lcs,
        'lci': lci,
        'puntos_fuera': fuera_control
    }


def calcular_grafico_c(defectos_por_unidad: list[int]) -> dict:
    """Calcula límites para gráfico C con n constante."""
    c = np.array(defectos_por_unidad, dtype=float)
    c_bar = float(np.mean(c))
    lcs = c_bar + 3 * np.sqrt(c_bar)
    lci = max(0, c_bar - 3 * np.sqrt(c_bar))
    fuera_control = np.where((c > lcs) | (c < lci))[0].tolist()
    return {
        'c': c.tolist(),
        'c_bar': c_bar,
        'lcs': lcs,
        'lci': lci,
        'puntos_fuera': fuera_control
    }


def calcular_grafico_u(n_inspeccionados: list[int], total_defectos: list[int]) -> dict:
    """Calcula límites para gráfico U con n variable."""
    n_inspeccionados = np.array(n_inspeccionados, dtype=float)
    total_defectos = np.array(total_defectos, dtype=float)
    u = total_defectos / n_inspeccionados
    u_bar = float(total_defectos.sum() / n_inspeccionados.sum())
    sigma = np.sqrt(u_bar / n_inspeccionados)
    lcs = u_bar + 3 * sigma
    lci = np.maximum(0, u_bar - 3 * sigma)
    fuera_control = np.where((u > lcs) | (u < lci))[0].tolist()
    return {
        'u': u.tolist(),
        'u_bar': u_bar,
        'lcs': lcs.tolist(),
        'lci': lci.tolist(),
        'puntos_fuera': fuera_control
    }


def calcular_capacidad(datos: list[float], lcs: float, lci: float, valor_nominal: float = None) -> dict:
    """Calcula Cp, Cpk, Pp y Ppk para un conjunto de datos."""
    datos = np.array(datos, dtype=float)
    n = len(datos)
    if n < 2:
        return {
            'cp': np.nan,
            'cpk': np.nan,
            'pp': np.nan,
            'ppk': np.nan,
            'media': np.nan,
            'desv_corto': np.nan,
            'desv_largo': np.nan,
            'proceso_capaz': False,
            'interpretacion': 'Insuficientes datos'
        }
    media = float(np.mean(datos))
    desv_corto = float(np.std(datos, ddof=1))
    desv_largo = float(np.std(datos, ddof=0))
    cp = float((lcs - lci) / (6 * desv_corto)) if desv_corto > 0 else np.nan
    cpk = float(min((lcs - media) / (3 * desv_corto), (media - lci) / (3 * desv_corto))) if desv_corto > 0 else np.nan
    pp = float((lcs - lci) / (6 * desv_largo)) if desv_largo > 0 else np.nan
    ppk = float(min((lcs - media) / (3 * desv_largo), (media - lci) / (3 * desv_largo))) if desv_largo > 0 else np.nan
    proceso_capaz = bool(cpk >= 1.33) if not np.isnan(cpk) else False
    interpretacion = 'Proceso capaz' if proceso_capaz else 'Proceso no capaz'
    return {
        'cp': cp,
        'cpk': cpk,
        'pp': pp,
        'ppk': ppk,
        'media': media,
        'desv_corto': desv_corto,
        'desv_largo': desv_largo,
        'proceso_capaz': proceso_capaz,
        'interpretacion': interpretacion
    }


def calcular_pareto(nombres_defectos: list[str], frecuencias: list[int]) -> dict:
    """Calcula datos ordenados para un diagrama de Pareto."""
    df = np.array(frecuencias, dtype=float)
    nombres = list(nombres_defectos)
    if len(nombres) != len(df):
        raise ValueError('Las listas de nombres y frecuencias deben tener la misma longitud')
    indices = np.argsort(df)[::-1]
    frecuencias_ordenadas = df[indices].tolist()
    nombres_ordenados = [nombres[i] for i in indices]
    porcentaje = [(f / float(df.sum()) * 100) for f in frecuencias_ordenadas]
    porcentaje_acumulado = np.cumsum(porcentaje).tolist()
    return {
        'categorias': nombres_ordenados,
        'frecuencias': frecuencias_ordenadas,
        'porcentaje': porcentaje,
        'porcentaje_acumulado': porcentaje_acumulado
    }
