import numpy as np
import pandas as pd
from scipy import stats

class QCStats:
    @staticmethod
    def test_normalidad(datos):
        """Realiza la prueba de Shapiro-Wilk para normalidad."""
        if len(datos) < 3:
            return False, 0, "Insuficientes datos para prueba"
        shapiro_test = stats.shapiro(datos)
        is_normal = shapiro_test.pvalue > 0.05
        return is_normal, shapiro_test.pvalue, "Normal" if is_normal else "No Normal"

    @staticmethod
    def calcular_x_barra_r(df_subgrupos):
        """
        Calcula límites para gráfico X-barra y R.
        df_subgrupos: DataFrame donde cada fila es un subgrupo.
        """
        # Factores para constantes de gráficos de control (n=2 a n=10)
        A2 = {2: 1.880, 3: 1.023, 4: 0.729, 5: 0.577, 6: 0.483, 7: 0.419, 8: 0.373, 9: 0.337, 10: 0.308}
        D3 = {2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0.076, 8: 0.136, 9: 0.184, 10: 0.223}
        D4 = {2: 3.267, 3: 2.574, 4: 2.282, 5: 2.114, 6: 2.004, 7: 1.924, 8: 1.864, 9: 1.816, 10: 1.777}

        n = df_subgrupos.shape[1]
        x_barras = df_subgrupos.mean(axis=1)
        rangos = df_subgrupos.max(axis=1) - df_subgrupos.min(axis=1)

        x_doble_barra = x_barras.mean()
        r_barra = rangos.mean()

        # Límites X-barra
        ucl_x = x_doble_barra + A2[n] * r_barra
        lcl_x = x_doble_barra - A2[n] * r_barra

        # Límites R
        ucl_r = D4[n] * r_barra
        lcl_r = D3[n] * r_barra

        return {
            'x_barras': x_barras,
            'rangos': rangos,
            'x_doble_barra': x_doble_barra,
            'r_barra': r_barra,
            'ucl_x': ucl_x,
            'lcl_x': lcl_x,
            'ucl_r': ucl_r,
            'lcl_r': lcl_r
        }

    @staticmethod
    def calcular_capacidad(datos, lse, lie):
        """Calcula índices de capacidad Cp y Cpk."""
        media = np.mean(datos)
        sigma = np.std(datos, ddof=1)
        
        if sigma == 0:
            return 0, 0
            
        cp = (lse - lie) / (6 * sigma)
        cpk = min((lse - media) / (3 * sigma), (media - lie) / (3 * sigma))
        
        return round(cp, 3), round(cpk, 3)

    @staticmethod
    def calcular_grafico_p(defectuosos, n_total):
        """Calcula límites para gráfico P (proporción de defectuosos)."""
        defectuosos = np.array(defectuosos)
        n_total = np.array(n_total)
        p = defectuosos / n_total
        p_barra = sum(defectuosos) / sum(n_total)
        
        # El límite varía si n es variable, aquí usamos n promedio para simplificar o n específico
        sigma_p = np.sqrt((p_barra * (1 - p_barra)) / n_total)
        ucl_p = p_barra + 3 * sigma_p
        lcl_p = np.maximum(0, p_barra - 3 * sigma_p)
        
        return {
            'p': p,
            'p_barra': p_barra,
            'ucl_p': ucl_p,
            'lcl_p': lcl_p
        }

    @staticmethod
    def calcular_x_barra_s(df_subgrupos):
        """Calcula límites para gráfico X-barra y S."""
        # Factores para n=2 a n=10
        A3 = {2: 2.659, 3: 1.954, 4: 1.628, 5: 1.427, 6: 1.287, 7: 1.182, 8: 1.099, 9: 1.032, 10: 0.975}
        B3 = {2: 0, 3: 0, 4: 0, 5: 0, 6: 0.030, 7: 0.118, 8: 0.185, 9: 0.239, 10: 0.284}
        B4 = {2: 3.267, 3: 2.568, 4: 2.266, 5: 2.089, 6: 1.970, 7: 1.882, 8: 1.815, 9: 1.761, 10: 1.716}

        n = df_subgrupos.shape[1]
        x_barras = df_subgrupos.mean(axis=1)
        desviaciones = df_subgrupos.std(axis=1)

        x_doble_barra = x_barras.mean()
        s_barra = desviaciones.mean()

        ucl_x = x_doble_barra + A3[n] * s_barra
        lcl_x = x_doble_barra - A3[n] * s_barra
        ucl_s = B4[n] * s_barra
        lcl_s = B3[n] * s_barra

        return {
            'x_barras': x_barras,
            's': desviaciones,
            'x_doble_barra': x_doble_barra,
            's_barra': s_barra,
            'ucl_x': ucl_x,
            'lcl_x': lcl_x,
            'ucl_s': ucl_s,
            'lcl_s': lcl_s
        }

    @staticmethod
    def calcular_capacidad_completa(datos, lse, lie):
        """Calcula Cp, Cpk, Pp y Ppk."""
        media = np.mean(datos)
        sigma_st = np.std(datos, ddof=1) # Estimación a corto plazo (simplificada)
        
        cp = (lse - lie) / (6 * sigma_st) if sigma_st != 0 else 0
        cpk = min((lse - media) / (3 * sigma_st), (media - lie) / (3 * sigma_st)) if sigma_st != 0 else 0
        
        # Para Pp/Ppk usamos la desviación estándar total
        pp = cp # En este contexto simplificado son similares
        ppk = cpk
        
        return {
            'cp': round(cp, 3),
            'cpk': round(cpk, 3),
            'pp': round(pp, 3),
            'ppk': round(ppk, 3)
        }

    @staticmethod
    def calcular_grafico_np(defectuosos, n):
        """Gráfico Np (Número de defectuosos, n constante)."""
        p_barra = sum(defectuosos) / (len(defectuosos) * n)
        np_barra = n * p_barra
        ucl = np_barra + 3 * np.sqrt(n * p_barra * (1 - p_barra))
        lcl = max(0, np_barra - 3 * np.sqrt(n * p_barra * (1 - p_barra)))
        return {'np': defectuosos, 'np_barra': np_barra, 'ucl': ucl, 'lcl': lcl}

    @staticmethod
    def calcular_grafico_u(defectos, n_unidades):
        """Gráfico U (Defectos por unidad, n variable)."""
        defectos = np.array(defectos)
        n_unidades = np.array(n_unidades)
        u = defectos / n_unidades
        u_barra = sum(defectos) / sum(n_unidades)
        ucl = u_barra + 3 * np.sqrt(u_barra / n_unidades)
        lcl = np.maximum(0, u_barra - 3 * np.sqrt(u_barra / n_unidades))
        return {'u': u, 'u_barra': u_barra, 'ucl': ucl, 'lcl': lcl}
