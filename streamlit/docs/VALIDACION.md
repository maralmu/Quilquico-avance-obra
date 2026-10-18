# Registro de validación

Fecha de ejecución: 17 de octubre de 2026. Entorno: Windows, Python 3.14, Streamlit 1.66.0, Pandas 3.0.3, NumPy 2.4.6, Plotly 6.9.0, OpenPyXL 3.1.5.

## Comprobaciones ejecutadas

- Compilación de `app.py`, `calculos.py`, `graficos.py` y `reportes.py`: correcta.
- `python -m unittest discover -s tests -v`: seis pruebas aprobadas. Incluyen múltiples casos internos.
- Regresión: igualdad de DataFrames/Series para avance semanal, atrasos, especialidades, encargados y cantidad de partidas, comparados con las funciones extraídas del script original mediante AST.
- Valores de control: semana 8 = 87 % planificado y 81,50 % real; semana 12 = 100 % en ambos. Los resúmenes por partida concilian con el general.
- Archivos inválidos: vacío, columnas faltantes, duplicados, semana omitida, fila omitida, semana decimal/cero, peso incorrecto, avances negativos/excesivos/infinitos, textos vacíos y nulos. Todos rechazados con ValueError controlado.
- Edición: rechazo de valores incompatibles sin modificar el original; aplicación de una modificación válida en copia.
- Gráficos: construcción y serialización de cinco tipos de figuras.
- Excel: generación en memoria, reapertura, seis hojas, dos gráficos nativos, cortes y formato porcentual verificados. Se renderizaron las seis hojas con Artifact Tool y se revisaron visualmente; se corrigieron anchos, textos y rótulos acumulados.
- Streamlit AppTest: pantalla inicial, cambio a semana 8, navegación por las seis secciones, botón de generación de Excel y estado de carga CSV sin archivo. Sin excepciones.
- Servidor real: `python -m streamlit run app.py --server.headless true --server.address 127.0.0.1 --server.port 8501` inició y el navegador mostró el panel y la Curva S. Se revisó la disposición estrecha y de escritorio.
- Infografía: SVG y PNG revisados visualmente, con datos originales contrastados.

La primera ejecución restringida no pudo completar la prueba de Streamlit por permisos del entorno. Se repitió fuera de la restricción y pasó. La advertencia `missing ScriptRunContext` aparece al iniciar AppTest fuera del servidor y no produjo una falla de prueba.

## Límites de lo verificado

- No se ha publicado una aplicación remota ni verificado una URL de Streamlit Community Cloud. Se requiere la cuenta del estudiante y un repositorio GitHub.
- No se realizó el envío a Classroom.
- No se abrió el Excel en Microsoft Excel de escritorio; se verificó mediante OpenPyXL y renderización de Artifact Tool.
- La carga de CSV se comprobó en la capa de lectura/validación y la interfaz de carga sin archivo; no se automatizó una transferencia real mediante el selector de archivos del navegador.
- La edición manual se probó en su función transaccional; no se automatizaron todas las combinaciones del formulario.
- No se proporcionó notebook para contrastarlo. La regresión se basa en el script original completo aportado.

## Evaluación final de cumplimiento

Las funcionalidades locales de los criterios de 7, 5 y 4 puntos están implementadas y tienen evidencia de prueba. Para el último criterio de 4 puntos existen estructura e infografía, pero falta acreditar publicación remota. No se asegura una nota ni cumplimiento total de ese criterio hasta publicar y probar la URL. El ZIP incluye código completo, datos, reporte, documentación e infografía.
