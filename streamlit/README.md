# Proyecto Quilquico · Control de avance físico

Aplicación Streamlit para el Entregable 2, Caso 2, de Python + IA para Programación (AECODE). Autor: Martín Muñoz Hernandez. Desarrollo con asistencia de IA a partir del programa y CSV aportados por el autor.

## 1. Instalar Python y abrir en Visual Studio Code (Windows)

1. Descargue Python para Windows desde https://www.python.org/downloads/windows/ e instálelo con la opción de agregar Python al PATH. Este proyecto se comprobó con Python 3.14; las dependencias requieren Python 3.11 o posterior.
2. Instale Visual Studio Code desde https://code.visualstudio.com/ y su extensión Python (Microsoft).
3. Descomprima el ZIP. Abra **Archivo > Abrir carpeta** y seleccione la carpeta que contiene `app.py` y `requirements.txt`.
4. Abra **Terminal > Nuevo terminal** (PowerShell). Compruebe Python:

```powershell
py --version
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

No es necesario activar el entorno, por lo que no hay que cambiar la política de ejecución de PowerShell. Si `py` no está disponible, use `python` en los dos primeros comandos. En VS Code, ejecute **Python: Select Interpreter** y seleccione `.venv\Scripts\python.exe`.

## 2. Iniciar la aplicación

Desde la carpeta del proyecto:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Abra la dirección mostrada por Streamlit, normalmente http://localhost:8501. Mantenga la terminal abierta. Para detener el servidor presione `Ctrl+C`.

## 3. Utilizar las seis secciones

- **Panel principal:** seleccione la semana de control en el lateral. Los indicadores, conteos y Curva S se recalculan desde los datos.
- **Avance general:** consulte Curva S, comparación semanal, desviación y tabla acumulada.
- **Especialidades:** compare aportes al total de obra y seleccione una especialidad para su evolución semanal.
- **Encargados:** seleccione el responsable, consulte sus partidas y acumulados, y compare con los demás.
- **Partidas y alertas:** filtre por especialidad y encargado; elija revisión semanal o acumulada; active “solo atrasadas”. La semana se controla en el lateral.
- **Reportes:** pulse **Generar reporte Excel** y luego **Descargar reporte Excel**. Puede descargar también el avance procesado al corte o toda la base de la sesión.

La imagen de infografía está en el panel principal y en Reportes. Sus resultados corresponden explícitamente a la base original; los indicadores interactivos reflejan los datos activos.

## 4. Carga de CSV y edición manual

Seleccione **Cargar CSV** y elija el archivo. El formato es UTF-8, coma como separador y punto decimal. Debe contener estas columnas:

```text
semana,codigo_partida,partida,especialidad,encargado,peso_partida,avance_planificado_semanal,avance_real_semanal
```

Una fila por partida y semana, semanas consecutivas desde 1, todas las partidas en cada semana y metadatos constantes por código. Los pesos únicos deben sumar 1. Los avances son fracciones **ya ponderadas**: 0.02 significa un aporte de 2 % al total de la obra, no un 2 % interno de la partida. Los acumulados de cada partida no pueden superar su peso.

En **Partidas y alertas > Carga manual**, hay seis entradas: partida, semana, avance planificado, avance real, especialidad y encargado. Los dos avances se ingresan en porcentaje (por ejemplo, 2 para 2 %). La aplicación convierte a fracción. Pulse **Validar y aplicar cambios**; una edición inválida no modifica los datos. La asignación de especialidad/encargado se aplica a todas las semanas del código. No se inventan nuevas partidas ni se solicitan causas del atraso.

Para una prueba segura, seleccione una fila con avance real positivo y redúzcalo temporalmente; compruebe los indicadores y luego pulse **Restablecer datos de la fuente**. Los cambios duran la sesión. Descargue la base completa para conservarlos. El archivo original distribuido no se sobrescribe.

## 5. Convenciones de cálculo

Avance semanal = suma de las contribuciones de las partidas de esa semana. Avance acumulado = suma de avances semanales desde la semana 1. Desviación = real acumulado menos planificado acumulado. Una desviación de −0.055 equivale a **−5.50 puntos porcentuales**.

Los pesos suman 100 % al contar cada partida una sola vez. No se multiplican otra vez por los avances, que ya están ponderados. Especialidades y encargados muestran contribuciones al total de obra. La clasificación usa tolerancia de 1e-9 para absorber redondeo numérico.

## 6. Archivos y pruebas

| Archivo | Función |
|---|---|
| `app.py` | Interfaz, filtros, edición y descargas |
| `calculos.py` | Lectura, validación y cálculo |
| `graficos.py` | Figuras Plotly |
| `reportes.py` | Exportación con OpenPyXL |
| `datos/` | CSV original |
| `referencias/` | Script original sin modificaciones |
| `reportes/Reporte_Proyecto_Quilquico.xlsx` | Ejemplo al corte final |
| `docs/` | Diagnóstico, matriz, informe e infografía |
| `tests/` | Regresión, errores y prueba de aplicación |

Para repetir las comprobaciones:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m compileall -q app.py calculos.py graficos.py reportes.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

El script de referencia tiene ejecución directa y rutas antiguas; no lo use para iniciar la aplicación. Las pruebas extraen únicamente sus funciones mediante AST para compararlas sin abrir gráficos ni crear archivos originales.

## 7. Publicación en Streamlit Community Cloud

La pauta exige publicación. El paquete local no acredita por sí solo ese requisito. Para publicar:

1. Inicie sesión en GitHub y cree un repositorio para este trabajo.
2. Suba el contenido de esta carpeta, incluidos `datos`, `docs`, `.streamlit` y `requirements.txt`. Excluya `.venv`, cachés y archivos personales.
3. Entre a https://share.streamlit.io/ con su cuenta y conecte el repositorio.
4. Cree una aplicación y seleccione el repositorio, la rama y `app.py` como archivo principal.
5. En las opciones avanzadas seleccione una versión de Python compatible (3.11 o posterior; 3.14 fue la comprobada localmente) y pulse **Deploy**.
6. Revise los registros de instalación. Abra la URL real terminada en `.streamlit.app`; pruebe carga, cambio de semana y descarga de Excel.
7. Añada esa URL a su entrega. No se incluye una URL ficticia en este proyecto.

Guías oficiales consultadas: [publicación](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy) y [dependencias](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies).

## 8. Entrega académica

Envíe el ZIP `ET2_PYTHON_Martin-Muñoz-Hernandez.zip` por Classroom junto con la URL publicada. Consulte `docs/DIAGNOSTICO_Y_MATRIZ.md` para los criterios y condiciones de la pauta. El informe se entrega en Markdown, legible directamente desde VS Code. La presentación del Caso 3 no se exige al Caso 2 seleccionado.
