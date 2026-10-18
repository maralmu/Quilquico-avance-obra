"""Figuras retornadas a Streamlit, sin abrir ventanas al importar."""
import plotly.graph_objects as go
from calculos import AVANCES

COLORES = ['#365C91', '#11A398']


def comparar(tabla, titulo, acumulado=False, barras=False):
    columnas = ['planificado_acumulado', 'real_acumulado'] if acumulado else AVANCES
    fig = go.Figure()
    x = list(tabla.index)
    for c, nombre, color in zip(columnas, ['Planificado', 'Real'], COLORES):
        y = tabla[c].tolist()
        if acumulado and x and isinstance(x[0], (int, float)):
            xx, yy = [0] + x, [0] + y
        else:
            xx, yy = x, y
        if barras:
            fig.add_trace(go.Bar(x=xx, y=yy, name=nombre, marker_color=color))
        else:
            fig.add_trace(go.Scatter(x=xx, y=yy, name=nombre, mode='lines+markers', line=dict(color=color, width=3)))
    fig.update_layout(title=titulo, template='plotly_white', barmode='group', height=390,
                      margin=dict(l=25, r=20, t=65, b=40), legend=dict(orientation='h', y=1.14),
                      yaxis=dict(title='Contribución al total de obra (%)', tickformat='.0%'),
                      xaxis_title='Semana' if tabla.index.name == 'semana' else tabla.index.name,
                      hovermode='x unified')
    fig.update_traces(hovertemplate='%{y:.2%}<extra>%{fullData.name}</extra>')
    return fig


def grafico_desviacion(avance):
    fig = go.Figure(go.Bar(x=avance.index, y=avance.desviacion * 100,
        marker_color=['#CE5C52' if x < -1e-9 else '#11A398' for x in avance.desviacion]))
    fig.update_layout(title='Desviación acumulada', template='plotly_white', height=320,
        xaxis_title='Semana', yaxis_title='Real − planificado (puntos porcentuales)')
    return fig


def grafico_partidas_encargado(cantidad):
    fig = go.Figure(go.Bar(x=cantidad.index, y=cantidad.values, marker_color='#365C91'))
    fig.update_layout(title='Partidas únicas por encargado', template='plotly_white', height=360,
                      yaxis=dict(title='Cantidad de partidas', dtick=1))
    return fig
