# Diagnóstico y matriz de cumplimiento

## Fuentes revisadas antes de programar

Pauta `Entregable 2.pdf`, 13 páginas, revisadas visualmente; script original completo; CSV original de 240 filas y 8 columnas; ambas imágenes de evaluación (16,5/20). No se proporcionó notebook. Se aplica el Caso 2 (páginas 6 y 7) y las condiciones generales (páginas 11 y 12). El caso adicional y su presentación de hasta ocho diapositivas no corresponden a este trabajo.

## Diagnóstico de datos y decisiones

- 20 partidas, 12 semanas consecutivas, 5 especialidades y 5 encargados. Una fila por partida y semana.
- Los pesos se repiten cada semana: se suman una sola vez por código. Suman 1, equivalente a 100 %. Sumarlos en las 240 filas produciría 12 y sería incorrecto.
- En cada partida, la suma de los avances planificados semanales coincide con su peso. Son contribuciones ponderadas al total de la obra. No se vuelven a multiplicar por el peso.
- Se conservan `groupby().sum()`, acumulación cronológica, real menos planificado y conteo único de partidas. Los gráficos de grupos muestran contribución al total de la obra, no porcentaje de ejecución interno de cada grupo.
- Se añade tolerancia de 1e-9 a la clasificación del estado para evitar falsos atrasos por redondeo binario. Se documenta como ajuste numérico, sin alterar los avances.
- La alerta original compara avance semanal; se conserva y se añade una vista de atraso acumulado al corte, claramente identificada.
- El script original ejecuta carga, gráficos y exportación al importarse. Se extraen sus funciones en módulos sin efectos de importación y se comparan mediante AST, sin ejecutar su bloque principal.
- Se aceptan archivos con semanas desde 1 hasta el corte, con todas las partidas presentes en cada semana y pesos totales de 100 %. Se rechazan matrices incompletas para no interpretar ausencias como cero.
- Los datos originales se mantienen intactos. La edición manual modifica una copia en la sesión y valida el conjunto antes de aplicarla.

## Diseño previsto

`app.py` controla seis secciones y formularios. `calculos.py` valida y procesa; `graficos.py` devuelve figuras Plotly; `reportes.py` devuelve un Excel en memoria con OpenPyXL, como en el trabajo original. No hay autenticación ni base de datos. La información de sesión se pierde al reiniciar.

## Matriz de la pauta (20 puntos)

| Criterio de la pauta | Puntos | Evidencia prevista | Verificación |
|---|---:|---|---|
| Página Streamlit, widgets, botones, tablas, desplegables, gráficos y exportación | 7 | `app.py`, seis secciones, CSV y Excel | Pruebas de aplicación y exportación |
| Funciones Python importadas para análisis, cálculos y gráficos | 5 | `calculos.py`, `graficos.py`, `reportes.py` | Comparación con funciones originales |
| Parámetros editables, carga manual y carga de archivos | 4 | Formulario con semana, partida, planificado, real, especialidad y encargado; carga CSV | Validación previa a cambios |
| Publicación en Streamlit, estructura ordenada e infografía con IA sobre el código | 4 | Estructura modular; `docs/infografia.svg`; guía de publicación | Publicación remota pendiente de acceso y URL real |

La pauta exige también cinco entradas manuales como mínimo, un control de carga, cuatro gráficos, exportación y una imagen de infografía que explique el código y muestre resultados. Se implementarán explícitamente. La distribución interna de puntos del último criterio no está especificada: no se atribuye una nota garantizada.

## Condiciones de envío y certificación

Carpeta comprimida con nombre `ET2_PYTHON_Martin-Muñoz-Hernandez`, código, reportes e infografía; envío por Classroom. La pauta indica domingo 18/10/2026 a las 23:59, hora Perú (en Punta Arenas: lunes 19/10/2026 a las 01:59). No se realiza envío a Classroom automáticamente.

La certificación suma los tres entregables, cada uno sobre 20; requiere al menos 40 puntos totales. El tercer entregable es un formulario de 20 preguntas. Son condiciones académicas, no funcionalidades de la aplicación.
