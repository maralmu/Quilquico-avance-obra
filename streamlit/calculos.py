"""Cálculos originales de avance ponderado y validación de su contrato de datos."""
from io import BytesIO
import numpy as np
import pandas as pd

AVANCES = ['avance_planificado_semanal', 'avance_real_semanal']
TEXTOS = ['codigo_partida', 'partida', 'especialidad', 'encargado']
COLUMNAS = ['semana', *TEXTOS, 'peso_partida', *AVANCES]
TOL = 1e-9


def validar_datos(datos):
    """Exige matriz partida-semana completa y aportes expresados como fracciones."""
    faltan = set(COLUMNAS) - set(datos.columns)
    if faltan:
        raise ValueError('Faltan columnas obligatorias: ' + ', '.join(sorted(faltan)))
    d = datos[COLUMNAS].copy()
    if d.empty:
        raise ValueError('El archivo no contiene registros.')
    if d.isna().any().any():
        raise ValueError('Hay valores vacíos. Complete todas las columnas obligatorias.')
    for c in TEXTOS:
        d[c] = d[c].astype(str).str.strip()
        if d[c].eq('').any():
            raise ValueError(f'La columna {c} contiene textos vacíos.')
    for c in ['semana', 'peso_partida', *AVANCES]:
        d[c] = pd.to_numeric(d[c], errors='coerce')
        if not np.isfinite(d[c].to_numpy(dtype=float)).all():
            raise ValueError(f'La columna {c} requiere números finitos, sin texto ni vacíos.')
    if (d.semana < 1).any() or (d.semana % 1 != 0).any():
        raise ValueError('Las semanas deben ser enteros positivos desde 1.')
    d['semana'] = d.semana.astype(int)
    semanas = sorted(d.semana.unique())
    if semanas != list(range(1, len(semanas) + 1)):
        raise ValueError('Las semanas deben ser consecutivas desde 1, sin saltos.')
    if d.duplicated(['semana', 'codigo_partida']).any():
        raise ValueError('Hay registros duplicados de una partida en la misma semana.')
    if not d.groupby('codigo_partida').size().eq(len(semanas)).all():
        raise ValueError('Cada partida debe aparecer en todas las semanas. Registre cero si no hubo avance.')
    for c in ['partida', 'especialidad', 'encargado', 'peso_partida']:
        if d.groupby('codigo_partida')[c].nunique().gt(1).any():
            raise ValueError(f'{c} debe mantenerse constante para cada código de partida.')
    pesos = d.drop_duplicates('codigo_partida').peso_partida
    if (pesos <= 0).any() or not np.isclose(pesos.sum(), 1, atol=TOL, rtol=0):
        raise ValueError('Los pesos por partida única deben ser positivos y sumar 1 (100 %).')
    if (d[AVANCES] < 0).any().any():
        raise ValueError('Los avances semanales no pueden ser negativos.')
    por_partida = d.groupby('codigo_partida')[AVANCES].sum()
    limite = d.groupby('codigo_partida').peso_partida.first()
    if por_partida.gt(limite + TOL, axis=0).any().any():
        raise ValueError('El avance acumulado de una partida supera su peso. Use aportes ponderados, no porcentajes internos.')
    return d.sort_values(['semana', 'codigo_partida']).reset_index(drop=True)


def cargar_datos(archivo):
    """Lee CSV UTF-8 (con o sin BOM), separado por coma; no cambia unidades."""
    try:
        if isinstance(archivo, bytes):
            archivo = BytesIO(archivo)
        d = pd.read_csv(archivo, encoding='utf-8-sig')
    except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeError, OSError) as exc:
        raise ValueError('No se pudo leer el CSV. Use UTF-8, coma como separador y punto decimal.') from exc
    return validar_datos(d)


def estado(desviacion):
    if abs(desviacion) <= TOL:
        return 'SEGÚN PROGRAMA'
    return 'ATRASADA' if desviacion < 0 else 'ADELANTADA'


def calcular_avance_semanal(datos):
    avance = datos.groupby('semana')[AVANCES].sum().sort_index()
    avance['planificado_acumulado'] = avance[AVANCES[0]].cumsum()
    avance['real_acumulado'] = avance[AVANCES[1]].cumsum()
    avance['desviacion'] = avance.real_acumulado - avance.planificado_acumulado
    return avance


def detectar_atrasos(datos):
    d = datos.copy()
    d['diferencia'] = d[AVANCES[1]] - d[AVANCES[0]]
    return d[d.diferencia < -TOL].copy()


def avance_por_grupo(datos, grupo):
    avance = datos.groupby(grupo)[AVANCES].sum()
    avance['planificado_porcentaje'] = avance[AVANCES[0]] * 100
    avance['real_porcentaje'] = avance[AVANCES[1]] * 100
    return avance


def avance_por_especialidad(datos):
    return avance_por_grupo(datos, 'especialidad')


def avance_por_encargado(datos):
    return avance_por_grupo(datos, 'encargado')


def partidas_por_encargado(datos):
    return datos.groupby('encargado').codigo_partida.nunique()


def resumen_partidas(datos, semana):
    d = datos[datos.semana <= semana]
    meta = d.drop_duplicates('codigo_partida').set_index('codigo_partida')[['partida', 'especialidad', 'encargado', 'peso_partida']]
    r = meta.join(d.groupby('codigo_partida')[AVANCES].sum()).rename(columns={AVANCES[0]: 'planificado_acumulado', AVANCES[1]: 'real_acumulado'})
    r['desviacion'] = r.real_acumulado - r.planificado_acumulado
    r['estado'] = r.desviacion.map(estado)
    return r


def actualizar_registro(datos, semana, codigo, plan, real, especialidad, encargado):
    """Edición transaccional: conserva el original si el conjunto deja de ser válido."""
    d = datos.copy()
    objetivo = d.semana.eq(semana) & d.codigo_partida.eq(codigo)
    if objetivo.sum() != 1:
        raise ValueError('No existe la combinación de semana y partida seleccionada.')
    d.loc[objetivo, AVANCES] = [plan, real]
    d.loc[d.codigo_partida.eq(codigo), ['especialidad', 'encargado']] = [especialidad, encargado]
    return validar_datos(d)
