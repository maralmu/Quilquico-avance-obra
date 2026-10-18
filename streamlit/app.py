"""Aplicación académica de control de avance físico del Proyecto Quilquico."""
from pathlib import Path
import hashlib
import streamlit as st
from calculos import (AVANCES, cargar_datos, calcular_avance_semanal, estado,
    avance_por_especialidad, avance_por_encargado, partidas_por_encargado,
    resumen_partidas, detectar_atrasos, actualizar_registro)
from graficos import comparar, grafico_desviacion, grafico_partidas_encargado
from reportes import generar_reporte_excel

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title='Quilquico · Control de obra', page_icon='🏗️', layout='wide')
st.markdown('''<style>
.block-container {padding-top:2rem; max-width:1450px}
[data-testid="stMetric"] {background:#edf4f7;border-radius:12px;padding:18px;border-top:3px solid #11a398}
[data-testid="stMetricValue"] {font-size:1.65rem;white-space:normal;overflow:visible}
[data-testid="stMetricValue"] div {white-space:normal;overflow:visible;text-overflow:clip}
h1,h2,h3 {color:#17324d}
</style>''', unsafe_allow_html=True)


def tabla(d):
    formatos = {c: '{:.2%}' for c in d.columns if c in [*AVANCES, 'peso_partida', 'planificado_acumulado', 'real_acumulado', 'desviacion', 'diferencia']}
    st.dataframe(d.style.format(formatos), width='stretch')


def indicadores(a):
    f = a.iloc[-1]
    cols = st.columns(4)
    cols[0].metric('Planificado acumulado', f'{f.planificado_acumulado:.2%}')
    cols[1].metric('Real acumulado', f'{f.real_acumulado:.2%}')
    cols[2].metric('Desviación acumulada', f'{f.desviacion * 100:+.2f} pp')
    cols[3].metric('Estado de la obra', estado(f.desviacion))


st.sidebar.title('QUILQUICO')
st.sidebar.caption('Control de avance físico de obra')
fuente = st.sidebar.radio('Fuente de datos', ['Base original', 'Cargar CSV'])
archivo = st.sidebar.file_uploader('Seleccionar archivo CSV', type=['csv']) if fuente == 'Cargar CSV' else None
try:
    if fuente == 'Cargar CSV':
        if archivo is None:
            st.info('Seleccione un CSV en el panel lateral para comenzar.')
            st.stop()
        contenido = archivo.getvalue()
    else:
        contenido = (ROOT / 'datos' / 'Caso_2_Quilquico_Base_Completa.csv').read_bytes()
    firma = fuente + hashlib.sha256(contenido).hexdigest()
    if st.session_state.get('firma') != firma:
        st.session_state['datos'] = cargar_datos(contenido)
        st.session_state['firma'] = firma
        st.session_state['editado'] = False
except (ValueError, OSError) as exc:
    st.error(f'No se cargaron los datos: {exc}')
    st.stop()

if st.sidebar.button('Restablecer datos de la fuente'):
    st.session_state['datos'] = cargar_datos(contenido)
    st.session_state['editado'] = False
    st.rerun()
d = st.session_state['datos']
semana = st.sidebar.selectbox('Semana de control', sorted(d.semana.unique()), index=d.semana.nunique()-1)
seccion = st.sidebar.radio('Sección', ['Panel principal', 'Avance general', 'Especialidades', 'Encargados', 'Partidas y alertas', 'Reportes'])
corte = d[d.semana <= semana]
a = calcular_avance_semanal(corte)
proyecto = 'Proyecto Quilquico' if fuente == 'Base original' else 'Proyecto del CSV cargado'
st.title(proyecto)
st.caption(f'CONTROL DE OBRA · Semana {semana} de {d.semana.max()} · {"Datos editados en esta sesión" if st.session_state.editado else fuente}')
st.sidebar.caption('Los cambios manuales duran esta sesión. Descargue el CSV para conservarlos.')

if seccion == 'Panel principal':
    st.subheader('Resumen de avance')
    indicadores(a)
    cols = st.columns(3)
    for col, etiqueta, campo in zip(cols, ['Partidas', 'Especialidades', 'Encargados'], ['codigo_partida', 'especialidad', 'encargado']):
        col.metric(etiqueta, d[campo].nunique())
    st.plotly_chart(comparar(a, 'Curva S · visión general', acumulado=True), width='stretch')
    st.progress(min(1., max(0., float(a.real_acumulado.iloc[-1]))), text='Avance real sobre el total de obra')
    atrasos = resumen_partidas(d, semana).estado.eq('ATRASADA').sum()
    st.info(f'{atrasos} partidas con atraso acumulado al corte. Los pesos únicos suman {d.drop_duplicates("codigo_partida").peso_partida.sum():.0%}.')
    with st.expander('Cómo funciona la aplicación · infografía'):
        st.image(str(ROOT / 'docs' / 'infografia.png'), width='stretch')

elif seccion == 'Avance general':
    indicadores(a)
    st.plotly_chart(comparar(a, 'Curva S · acumulado desde semana 1', acumulado=True), width='stretch')
    st.plotly_chart(comparar(a, 'Avance semanal · planificado y real', barras=True), width='stretch')
    st.plotly_chart(grafico_desviacion(a), width='stretch')
    vista = a.copy()
    vista['estado'] = vista.desviacion.map(estado)
    tabla(vista)

elif seccion == 'Especialidades':
    st.subheader('Avance por especialidad')
    especialidad = st.selectbox('Especialidad', ['Todas', *sorted(d.especialidad.unique())])
    resumen = avance_por_especialidad(corte)[AVANCES]
    st.plotly_chart(comparar(resumen, 'Comparación acumulada por especialidad', barras=True), width='stretch')
    seleccion = corte if especialidad == 'Todas' else corte[corte.especialidad.eq(especialidad)]
    st.plotly_chart(comparar(calcular_avance_semanal(seleccion), f'Avance semanal · {especialidad}'), width='stretch')
    resumen['desviacion'] = resumen[AVANCES[1]] - resumen[AVANCES[0]]
    vista = resumen if especialidad == 'Todas' else resumen.loc[[especialidad]]
    tabla(vista.rename(columns={AVANCES[0]: 'planificado_acumulado', AVANCES[1]: 'real_acumulado'}))
    st.caption('Porcentajes de contribución al total de la obra; no son porcentajes de ejecución interna de cada especialidad.')

elif seccion == 'Encargados':
    st.subheader('Seguimiento por encargado')
    encargado = st.selectbox('Encargado', sorted(d.encargado.unique()))
    seleccion = corte[corte.encargado.eq(encargado)]
    ac = calcular_avance_semanal(seleccion)
    cols = st.columns(3)
    cols[0].metric('Partidas asignadas', seleccion.codigo_partida.nunique())
    cols[1].metric('Planificado acumulado', f'{ac.planificado_acumulado.iloc[-1]:.2%}')
    cols[2].metric('Real acumulado', f'{ac.real_acumulado.iloc[-1]:.2%}')
    st.plotly_chart(comparar(ac, f'Avance acumulado · {encargado}', acumulado=True), width='stretch')
    st.plotly_chart(grafico_partidas_encargado(partidas_por_encargado(corte)), width='stretch')
    st.plotly_chart(comparar(avance_por_encargado(corte), 'Comparación acumulada entre encargados', barras=True), width='stretch')
    tabla(ac)
    st.caption('Avances expresados como contribución al total de obra.')

elif seccion == 'Partidas y alertas':
    st.subheader('Partidas y alertas')
    c1, c2 = st.columns(2)
    esp = c1.selectbox('Filtrar especialidad', ['Todas', *sorted(d.especialidad.unique())])
    enc = c2.selectbox('Filtrar encargado', ['Todos', *sorted(d.encargado.unique())])
    modo = st.radio('Tipo de revisión', ['Acumulado al corte', 'Solo semana seleccionada'], horizontal=True)
    solo = st.checkbox('Mostrar solo partidas atrasadas')
    p = resumen_partidas(d, semana).reset_index() if modo == 'Acumulado al corte' else d[d.semana.eq(semana)].copy()
    if modo != 'Acumulado al corte':
        p['desviacion'] = p[AVANCES[1]] - p[AVANCES[0]]
        p['estado'] = p.desviacion.map(estado)
    if esp != 'Todas':
        p = p[p.especialidad.eq(esp)]
    if enc != 'Todos':
        p = p[p.encargado.eq(enc)]
    cantidad = p.estado.eq('ATRASADA').sum()
    st.warning(f'{cantidad} partidas atrasadas en esta selección. Diferencia = real − planificado.') if cantidad else st.success('No hay partidas atrasadas en esta selección.')
    if solo:
        p = p[p.estado.eq('ATRASADA')]
    tabla(p)
    st.caption('Un atraso semanal puede coexistir con un acumulado según programa. El modo seleccionado define la comparación.')
    with st.expander('Carga manual · actualizar registro existente'):
        st.write('Seleccione una partida y semana. Los avances son aportes al total de obra en %. Especialidad y encargado se actualizan para todas las semanas de esa partida.')
        c1, c2 = st.columns(2)
        cod = c1.selectbox('Partida a actualizar', sorted(d.codigo_partida.unique()), key='manual_codigo')
        sem = c2.number_input('Semana del registro', min_value=1, max_value=int(d.semana.max()), value=int(semana), step=1, key='manual_semana')
        fila = d[d.codigo_partida.eq(cod) & d.semana.eq(sem)].iloc[0]
        with st.form(f'editar_{cod}_{sem}'):
            st.caption(f'{fila.partida} · Peso: {fila.peso_partida:.2%}')
            plan = st.number_input('Avance planificado semanal (%)', min_value=0., max_value=100., value=float(fila[AVANCES[0]] * 100), step=0.1, format='%.3f')
            real = st.number_input('Avance real semanal (%)', min_value=0., max_value=100., value=float(fila[AVANCES[1]] * 100), step=0.1, format='%.3f')
            especialidades = sorted(d.especialidad.unique())
            encargados = sorted(d.encargado.unique())
            nueva_esp = st.selectbox('Especialidad asignada', especialidades, index=especialidades.index(fila.especialidad))
            nuevo_enc = st.selectbox('Encargado asignado', encargados, index=encargados.index(fila.encargado))
            if st.form_submit_button('Validar y aplicar cambios'):
                try:
                    actualizado = actualizar_registro(d, sem, cod, plan / 100, real / 100, nueva_esp, nuevo_enc)
                    st.session_state['datos'] = actualizado
                    st.session_state['editado'] = True
                    st.rerun()
                except ValueError as exc:
                    st.error(f'No se aplicaron cambios: {exc}')

elif seccion == 'Reportes':
    st.subheader('Resultados y descargas')
    indicadores(a)
    st.write(f'El Excel y el avance procesado incluyen las semanas 1 a {semana}. El CSV de base conserva todas las semanas y las ediciones de la sesión.')
    tabla(a)
    if st.button('Generar reporte Excel', type='primary'):
        try:
            st.session_state['excel'] = generar_reporte_excel(d, semana, proyecto)
            st.session_state['excel_firma'] = (hashlib.sha256(d.to_csv(index=False).encode()).hexdigest(), int(semana))
        except Exception:
            st.error('No se pudo generar el reporte. Restablezca los datos o revise la instalación de OpenPyXL.')
    firma_actual = (hashlib.sha256(d.to_csv(index=False).encode()).hexdigest(), int(semana))
    if st.session_state.get('excel_firma') == firma_actual:
        st.download_button('Descargar reporte Excel', st.session_state['excel'], f'Reporte_Quilquico_S{semana}.xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    st.download_button('Descargar avance procesado CSV', a.to_csv().encode('utf-8-sig'), f'Avance_S{semana}.csv', 'text/csv')
    st.download_button('Descargar base completa de esta sesión', d.to_csv(index=False).encode('utf-8-sig'), 'Base_Quilquico_sesion.csv', 'text/csv')
    st.image(str(ROOT / 'docs' / 'infografia.png'), width='stretch')

st.divider()
st.caption('AECODE · Python + IA para Programación · Entregable 2 · Martín Muñoz Hernandez | Desviaciones en puntos porcentuales (pp).')
