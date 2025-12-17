# GUÍA DEL PROYECTO PRVD
## Procesamiento y Recuperación de Datos No Estructurados y Visualización

**Autora**: Mónica Sánchez Bellido  
**Máster en Ciencia de Datos**

---

## 📊 DATOS DISPONIBLES

### Fuentes de Datos

#### 1. **Metro de Madrid** (Formato GTFS - General Transit Feed Specification)
- **Ubicación**: `data/Metro/`
- **Archivos**:
  - `agency.txt` - Información de la agencia de transporte
  - `routes.txt` - Líneas/rutas del metro
  - `stops.txt` - Paradas/estaciones
  - `stop_times.txt` - Horarios de parada
  - `trips.txt` - Viajes programados
  - `calendar.txt` / `calendar_dates.txt` - Fechas de servicio
  - `shapes.txt` - Formas geográficas de las rutas
  - `frequencies.txt` - Frecuencias de servicio
  - `fare_attributes.txt` / `fare_rules.txt` - Tarifas
  - `feed_info.txt` - Metadatos del feed

#### 2. **Autobuses EMT Madrid**
- **Ubicación**: `data/AUTOBUSES/`
- **Archivos**:
  - `linesemt.csv` - Líneas de autobús (~398 registros)
  - `stopsemt.csv` - Paradas de autobús (~12,433 registros)
- **Campos clave**:
  - Líneas: identificadores, nombres, origen/destino, fechas vigencia, depósito
  - Paradas: secuencia, distancias, coordenadas (posX, posY), nombres, sentido

#### 3. **BiciMAD**
- **Ubicación**: `data/BICIMAD/`
- **Archivo**: `bikestationbicimad_csv.csv` (~633 estaciones)
- **Campos**: ID, nombre, dirección, coordenadas (lat/long), estado, bases totales, disponibilidad, iluminación

#### 4. **Parkings**
- **Ubicación**: `data/Parkings/`
- **Archivo**: `parkings.csv` (~95 parkings)
- **Campos**: ID, nombre, dirección, email, coordenadas, estado, plazas estándar, plazas PMR, gestión EMT

#### 5. **Fuentes**
- Archivo: `data/DATOSFUENTES.txt`
- **Origen datos**:
  - Autobuses/BiciMAD: https://datos.emtmadrid.es/
  - Metro: https://datos.crtm.es/

---

## 🎯 OBJETIVOS DEL PROYECTO

### Objetivos de Análisis Propuestos

Basándose en los datos disponibles, se proponen los siguientes objetivos de análisis:

#### **Objetivo 1: Análisis de Cobertura del Sistema de Transporte Público en Madrid**
**Pregunta de investigación**: ¿Cuál es la distribución espacial y cobertura del transporte público (Metro, Autobús, BiciMAD) en Madrid?

**Requisitos de las fuentes**:
- ✅ **Fiabilidad a nivel individual**: ALTA - Datos oficiales de EMT y CRTM
- ✅ **Extracción**: UNA SOLA VEZ - Los datos son estáticos (infraestructura)
- ✅ **Completitud geoespacial**: Necesaria - Todas las fuentes tienen coordenadas
- ✅ **Actualización**: No crítica para análisis estructural

**Análisis específicos**:
1. Densidad de estaciones de metro por distrito
2. Cobertura de paradas de autobús
3. Distribución de estaciones BiciMAD
4. Áreas con mejor/peor conectividad multimodal

#### **Objetivo 2: Integración Multimodal - Facilidad de Conexión**
**Pregunta de investigación**: ¿Qué tan bien integrados están los diferentes modos de transporte? ¿Dónde hay parkings cerca de estaciones de metro?

**Requisitos de las fuentes**:
- ✅ **Precisión geoespacial**: CRÍTICA - Necesitamos calcular distancias precisas
- ✅ **Consistencia de formatos**: Media - Diferentes formatos CSV pero con coordenadas
- ✅ **Completitud**: Alta - Necesitamos todos los puntos de interés

**Análisis específicos**:
1. Distancia media entre estaciones BiciMAD y paradas de metro
2. Parkings dentro de 500m de estaciones de metro
3. Puntos de transferencia multimodal (autobús-metro-bici)
4. Zonas con gaps de integración

#### **Objetivo 3: Análisis de Accesibilidad (PMR - Personas con Movilidad Reducida)**
**Pregunta de investigación**: ¿Qué tan accesible es el sistema de transporte para personas con movilidad reducida?

**Requisitos de las fuentes**:
- ✅ **Datos específicos de accesibilidad**: Disponibles en parkings (Plazas_PMR)
- ⚠️ **Limitación**: No tenemos datos PMR para Metro y Autobús en las fuentes actuales
- ✅ **Fiabilidad**: Alta para los datos disponibles

**Análisis específicos**:
1. Distribución de plazas PMR en parkings
2. Ratio plazas PMR / plazas totales por parking
3. Cobertura geográfica de parkings con facilidades PMR

#### **Objetivo 4: Análisis Temporal de Servicios de Autobús**
**Pregunta de investigación**: ¿Cómo ha evolucionado la red de autobuses? ¿Qué líneas han cambiado/sido añadidas/eliminadas?

**Requisitos de las fuentes**:
- ✅ **Datos temporales**: Disponibles - `dateIni`, `dateEnd` en linesemt.csv
- ✅ **Granularidad temporal**: Buena - Fechas precisas
- ✅ **Extracción**: UNA VEZ - Datos históricos

**Análisis específicos**:
1. Líneas activas por período temporal
2. Cambios en rutas (origen/destino) de líneas existentes
3. Líneas especiales (SE*) vs. líneas regulares
4. Evolución de depósitos operativos

#### **Objetivo 5: Análisis de Estado y Disponibilidad de Infraestructura**
**Pregunta de investigación**: ¿Cuál es el estado actual de la infraestructura de movilidad?

**Requisitos de las fuentes**:
- ✅ **Datos de estado**: Disponibles en BiciMAD (`State`, `NoAvailable`)
- ✅ **Actualización**: Depende - BiciMAD puede requerir actualización continua para tiempo real
- ⚠️ **Para proyecto**: Snapshot única suficiente

**Análisis específicos**:
1. Porcentaje de estaciones BiciMAD en servicio vs. fuera de servicio
2. Capacidad (TotalBases) vs. disponibilidad real
3. Estaciones con iluminación nocturna

---

## 🔧 HERRAMIENTAS Y TECNOLOGÍAS

### Stack Tecnológico (Basado en Prácticas del Curso)

#### **1. Apache Hop** - Preprocesamiento ETL ⭐ **NUEVO**
- **Archivo principal**: `proyecto.hpl`
- **Función**: Extracción, transformación y carga (ETL) de datos
- **Ventajas**: 
  - Interfaz visual para diseñar pipelines de datos
  - Procesamiento robusto de múltiples formatos (CSV, TXT, etc.)
  - Transformaciones sin código (filtros, joins, cálculos)
  - Genera datasets limpios y listos para análisis
- **Ubicación**: Carpeta raíz del proyecto
- **Referencia**: Similar a prácticas P1, P2

#### **2. Python** - Análisis y Visualización
- Versión recomendada: Python 3.8+
- **Rol**: Procesamiento post-ETL y análisis estadístico

#### **3. Librerías de Procesamiento de Datos**
```python
import pandas as pd              # Lectura y manipulación de datos procesados
import numpy as np               # Operaciones numéricas
```

#### **4. Visualización**
```python
import matplotlib.pyplot as plt  # Gráficos básicos
import seaborn as sns           # Visualizaciones estadísticas
from scipy import stats         # Análisis estadístico
from scipy.stats import spearmanr, pearsonr  # Correlaciones
```

#### **5. Procesamiento Geoespacial**
```python
# Librerías necesarias para análisis espacial
import folium                   # Mapas interactivos
# o alternativamente:
import geopandas as gpd         # DataFrames geoespaciales
from shapely.geometry import Point  # Geometrías
```

#### **6. Entorno de Desarrollo**
- **Apache Hop GUI** - Para diseñar y ejecutar pipelines ETL
- **Jupyter Notebook** - Para análisis y visualizaciones
- Permite combinar código, gráficos y documentación

---

## 📋 CRITERIOS DE SELECCIÓN DE FUENTES

### Evaluación de Requisitos por Objetivo

| Objetivo | Fiabilidad Individual | Extracción Continua | Precisión Geoespacial | Completitud | Actualización |
|----------|----------------------|---------------------|----------------------|-------------|---------------|
| Cobertura Transporte | **ALTA** ✅ | NO (única) ✅ | **CRÍTICA** ✅ | **ALTA** ✅ | Baja |
| Integración Multimodal | **ALTA** ✅ | NO (única) ✅ | **CRÍTICA** ✅ | **ALTA** ✅ | Media |
| Accesibilidad PMR | **ALTA** ✅ | NO (única) ✅ | MEDIA | PARCIAL ⚠️ | Baja |
| Evolución Temporal | **ALTA** ✅ | NO (única) ✅ | BAJA | **ALTA** ✅ | NO necesaria |
| Estado Infraestructura | MEDIA ⚠️ | IDEALMENTE SÍ* | BAJA | **ALTA** ✅ | Alta* |

**Notas**:
- ⚠️ Accesibilidad PMR: Datos limitados a parkings
- * Estado Infraestructura: Para análisis de snapshot, extracción única es suficiente. Para monitoreo en tiempo real, se necesitaría extracción continua.

### Justificación de Selección de Fuentes

#### ✅ **Fuentes Seleccionadas**:
1. **Metro (GTFS)** - Estándar internacional, muy fiable, completo
2. **Autobuses EMT** - Datos oficiales, gran cobertura, información temporal rica
3. **BiciMAD** - Complementa transporte motorizado, datos de estado
4. **Parkings** - Esencial para Park&Ride, datos de accesibilidad

#### ✅ **Ventajas de estas fuentes**:
- Todas son **oficiales** (EMT Madrid, CRTM)
- **Formato consistente** (CSV/TXT tabulares)
- **Coordenadas geográficas** en todas
- **Complementarias** (cubren diferentes modos de transporte)
- **No requieren extracción continua** para análisis estructural

#### ⚠️ **Limitaciones identificadas**:
- No hay datos de **flujo de pasajeros** (occupancy, demand)
- No hay datos de **horarios en tiempo real**
- Información de **accesibilidad PMR limitada**
- No hay datos de **calidad de servicio** (retrasos, incidencias)

---

## 📝 ESTRUCTURA DEL PROYECTO

### Organización Recomendada

```
Proyecto/
├── data/                          # Datos originales (DO NOT MODIFY)
│   ├── Metro/
│   ├── AUTOBUSES/
│   ├── BICIMAD/
│   └── Parkings/
├── proyecto.hpl                   # ⭐ Pipeline Apache Hop (ETL)
├── notebooks/                     # Jupyter notebooks
│   ├── 01_exploracion_datos_procesados.ipynb
│   ├── 02_analisis_cobertura.ipynb
│   ├── 03_integracion_multimodal.ipynb
│   ├── 04_visualizaciones.ipynb
│   └── 05_conclusiones.ipynb
├── scripts/                       # Scripts Python reutilizables
│   ├── load_processed_data.py
│   ├── geo_utils.py
│   └── visualization.py
├── resultados/                    # ⭐ Datos procesados por HOP y outputs
│   ├── metro_procesado.csv       # Generado por HOP
│   ├── autobuses_procesado.csv   # Generado por HOP
│   ├── bicimad_procesado.csv     # Generado por HOP
│   ├── parkings_procesado.csv    # Generado por HOP
│   ├── transporte_madrid_consolidado.csv  # Dataset integrado
│   ├── figuras/
│   ├── mapas/
│   └── estadisticas/
├── GUIA_PROYECTO_PRVD.md         # Este documento
└── memoria.pdf                    # Memoria final (a entregar)
```

### **Nota Importante: Arquitectura de Dos Fases**

 Este proyecto sigue una arquitectura de **ETL + Análisis**:

1. **Fase ETL (Apache Hop)**: Preprocesamiento, limpieza y consolidación de datos
2. **Fase Análisis (Python/Jupyter)**: Análisis estadístico, cálculos y visualizaciones

Los datos **RAW** (originales) nunca se modifican. Los datos **procesados** se generan en `resultados/`.

---

## 🚀 PLAN DE TRABAJO

### **Fase 0: Preprocesamiento ETL con Apache Hop (1 día)** ⭐ **CRÍTICO - HACER PRIMERO**
**Objetivos**:
- Ejecutar pipeline `proyecto.hpl` en Apache Hop
- Procesar archivos de Metro, Autobuses, BiciMAD y Parkings
- Limpiar, normalizar y estandarizar datos
- Generar datasets procesados en `resultados/`

**Tareas específicas en HOP**:
1. **Flujo 1 - Metro**: 
   - Cargar `stops.txt` (GTFS)
   - Extraer coordenadas y nombres de paradas
   - Filtrar valores nulos
   - Agregar campo `transport_mode = 'metro'`
   
2. **Flujo 2 - Autobuses**:
   - Cargar `stopsemt.csv`
   - Renombrar campos (posX → stop_lon, posY → stop_lat)
   - Filtrar duplicados y nulos
   - Agregar campo `transport_mode = 'bus'`
   
3. **Flujo 3 - BiciMAD**:
   - Cargar `bikestationbicimad_csv.csv`
   - Convertir coordenadas de formato español (coma) a decimal (punto)
   - Filtrar estaciones fuera de servicio
   - Agregar campo `transport_mode = 'bicimad'`
   
4. **Flujo 4 - Parkings**:
   - Cargar `parkings.csv`
   - Calcular ratio PMR (plazas_pmr / plazas_standard)
   - Filtrar coordenadas inválidas
   - Agregar campo `transport_mode = 'parking'`
   
5. **Flujo 5 - Consolidación**:
   - Unir todos los datasets
   - Generar `transporte_madrid_consolidado.csv`

**Entregables**:
- ✅ `resultados/metro_procesado.csv`
- ✅ `resultados/autobuses_procesado.csv`
- ✅ `resultados/bicimad_procesado.csv`
- ✅ `resultados/parkings_procesado.csv`
- ✅ `resultados/transporte_madrid_consolidado.csv`

**Cómo ejecutar**:
```bash
# Abrir Apache Hop GUI
# File → Open → Seleccionar proyecto.hpl
# Run → Execute
# Verificar outputs en carpeta resultados/
```

### Fase 1: Exploración de Datos Procesados (1 día)
**Objetivos**:
- Cargar datasets **procesados** desde `resultados/`
- Verificar calidad del preprocesamiento HOP
- Generar estadísticas descriptivas básicas
- Validar coordenadas y rangos de valores

**Entregables**:
- Notebook `01_exploracion_datos_procesados.ipynb`
- Informe de calidad post-ETL

### Fase 2: Análisis (3-4 días)
**Objetivos**:
- Análisis de cobertura espacial
- Cálculos de distancias entre modos
- Análisis temporal de evolución
- Análisis de accesibilidad PMR
- Estadísticas descriptivas e inferenciales

**Entregables**:
- Notebooks `03_analisis_*.ipynb`
- Tablas de resultados

### Fase 3: Visualización (2-3 días)
**Objetivos**:
- Mapas de cobertura (folium o geopandas)
- Gráficos de distribución y densidad
- Heatmaps de conectividad
- Visualizaciones temporales
- Dashboards integrados

**Entregables**:
- Notebook `05_visualizaciones.ipynb`
- Figuras en alta resolución
- Mapas interactivos HTML

### Fase 4: Conclusiones y Memoria (2 días)
**Objetivos**:
- Sintetizar hallazgos
- Responder a preguntas de investigación
- Documentar limitaciones
- Proponer trabajo futuro
- Redactar memoria final

**Entregables**:
- Notebook `06_conclusiones.ipynb`
- `memoria.pdf`

---

## 🔧 FLUJO DE TRABAJO CON APACHE HOP

### ¿Qué es Apache Hop?

Apache Hop (Hop Orchestration Platform) es una herramienta de integración de datos visual que permite crear **pipelines ETL** (Extract, Transform, Load) sin necesidad de programar. Es similar a otras herramientas ETL como Pentaho Data Integration (Kettle) o Talend.

**Ventajas para este proyecto**:
- ✅ Diseño visual de flujos de datos (drag & drop)
- ✅ Transformaciones robustas para CSV, TXT y otros formatos
- ✅ Filtrado, limpieza y normalización sin código
- ✅ Estandarización garantizada de outputs
- ✅ Reproducibilidad completa del preprocesamiento

### Estructura del Pipeline `proyecto.hpl`

El archivo `proyecto.hpl` ya está creado y contiene:

**5 Flujos de Procesamiento**:
1. **Flujo Metro**: `data/Metro/stops.txt` → `resultados/metro_procesado.csv`
2. **Flujo Autobuses**: `data/AUTOBUSES/stopsemt.csv` → `resultados/autobuses_procesado.csv`
3. **Flujo BiciMAD**: `data/BICIMAD/bikestationbicimad_csv.csv` → `resultados/bicimad_procesado.csv`
4. **Flujo Parkings**: `data/Parkings/parkings.csv` → `resultados/parkings_procesado.csv`
5. **Flujo Consolidación**: Une todos los anteriores → `resultados/transporte_madrid_consolidado.csv`

### Transformaciones Implementadas

#### **Flujo 1: Metro (GTFS)**
```
Cargar stops.txt
  ↓
Seleccionar campos (stop_id, stop_name, stop_lat, stop_lon)
  ↓
Filtrar coordenadas nulas
  ↓
Agregar transport_mode = 'metro'
  ↓
Guardar metro_procesado.csv
```

**Campos output**: `stop_id`, `stop_name`, `stop_lat`, `stop_lon`, `transport_mode`

#### **Flujo 2: Autobuses EMT**
```
Cargar stopsemt.csv
  ↓
Seleccionar y renombrar (stopId→stop_id, description→stop_name, posX→stop_lon, posY→stop_lat)
  ↓
Filtrar coordenadas nulas
  ↓
Agregar transport_mode = 'bus'
  ↓
Guardar autobuses_procesado.csv
```

**Campos output**: `stop_id`, `stop_name`, `stop_lat`, `stop_lon`, `bus_line`, `transport_mode`

#### **Flujo 3: BiciMAD**
```
Cargar bikestationbicimad_csv.csv
  ↓
Seleccionar campos relevantes
  ↓
Reemplazar comas por puntos en coordenadas (formato español → decimal)
  ↓
Convertir a tipo numérico
  ↓
Filtrar solo estaciones IN_SERVICE
  ↓
Agregar transport_mode = 'bicimad'
  ↓
Guardar bicimad_procesado.csv
```

**Campos output**: `station_id`, `station_name`, `stop_lat`, `stop_lon`, `state`, `capacity`, `transport_mode`

#### **Flujo 4: Parkings**
```
Cargar parkings.csv
  ↓
Seleccionar y renombrar campos
  ↓
Calcular pmr_ratio = Plazas_PMR / Plazas_standard
  ↓
Filtrar coordenadas válidas
  ↓
Agregar transport_mode = 'parking'
  ↓
Guardar parkings_procesado.csv
```

**Campos output**: `parking_id`, `parking_name`, `stop_lat`, `stop_lon`, `standard_spaces`, `pmr_spaces`, `pmr_ratio`, `transport_mode`

### Cómo Ejecutar el Pipeline

#### **Opción 1: Apache Hop GUI (Recomendado)**
```bash
# 1. Abrir Hop GUI
# En macOS, ejecutar la aplicación Apache Hop

# 2. Abrir el pipeline
# File → Open → Navegar a: 
# /Users/monica/Desktop/MSc_CienciaDatos/PRVD/Proyecto/proyecto.hpl

# 3. Configurar parámetros (opcional)
# Click derecho en canvas → Pipeline Settings → Parameters
# Verificar Data_Path y Output_Path

# 4. Ejecutar
# Click en botón "Run" (▶️) o F8
# Seleccionar "Local" execution
# Click "Launch"

# 5. Monitorear ejecución
# Ver progreso en tiempo real
# Revisar logs para errores

# 6. Verificar outputs
# Navegar a carpeta resultados/
# Confirmar presencia de 5 archivos CSV
```

#### **Opción 2: Línea de Comandos** (Avanzado)
```bash
# Desde el directorio de instalación de Hop
./hop-run.sh -f /Users/monica/Desktop/MSc_CienciaDatos/PRVD/Proyecto/proyecto.hpl \
  -p Data_Path=/Users/monica/Desktop/MSc_CienciaDatos/PRVD/Proyecto/data \
  -p Output_Path=/Users/monica/Desktop/MSc_CienciaDatos/PRVD/Proyecto/resultados
```

### Verificación de Outputs

Después de ejecutar, verificar:

```bash
cd /Users/monica/Desktop/MSc_CienciaDatos/PRVD/Proyecto/resultados

# Listar archivos generados
ls -lh *.csv

# Debería mostrar:
# metro_procesado.csv
# autobuses_procesado.csv
# bicimad_procesado.csv
# parkings_procesado.csv
# transporte_madrid_consolidado.csv

# Ver primeras líneas de cada archivo
head -5 metro_procesado.csv
head -5 autobuses_procesado.csv
head -5 bicimad_procesado.csv
head -5 parkings_procesado.csv
head -5 transporte_madrid_consolidado.csv
```

### Modificar el Pipeline (Si es necesario)

Si necesitas ajustar transformaciones:

1. **Abrir en Hop GUI**: Doble click en `proyecto.hpl`
2. **Navegar por flujos**: Usa scroll para ver diferentes secciones
3. **Editar transformaciones**: Doble click en cualquier paso
4. **Añadir pasos**: Drag & drop desde panel izquierdo
5. **Conectar pasos**: Click y arrastrar entre pasos
6. **Guardar**: Ctrl+S o File → Save
7. **Re-ejecutar**: F8

**Tips de edición**:
- Los **cuadros amarillos** son notas explicativas - solo documentación
- Los **óvalos azules** son pasos de transformación - estos procesan datos
- Las **flechas verdes** son conexiones (hops) - definen el flujo de datos

### Integración con Python

Una vez ejecutado HOP, cargar datos procesados en Python:

```python
import pandas as pd

# Cargar datasets individuales
metro = pd.read_csv('resultados/metro_procesado.csv', sep=';')
autobuses = pd.read_csv('resultados/autobuses_procesado.csv', sep=';')
bicimad = pd.read_csv('resultados/bicimad_procesado.csv', sep=';')
parkings = pd.read_csv('resultados/parkings_procesado.csv', sep=';')

# O cargar dataset consolidado
transporte_madrid = pd.read_csv('resultados/transporte_madrid_consolidado.csv', sep=';')

# Verificar
print(f"Metro: {len(metro)} paradas")
print(f"Autobuses: {len(autobuses)} paradas")
print(f"BiciMAD: {len(bicimad)} estaciones")
print(f"Parkings: {len(parkings)} parkings")
print(f"Consolidado: {len(transporte_madrid)} registros totales")

# Ver campos disponibles
print(transporte_madrid.columns.tolist())
# ['stop_id', 'stop_name', 'stop_lat', 'stop_lon', 'transport_mode', ...]
```

---

## 📊 ANÁLISIS ESPECÍFICOS SUGERIDOS

### 1. **Análisis de Cobertura**

```python
# Pseudocódigo
# Cargar datos
metro_stops = pd.read_csv('data/Metro/stops.txt')
bus_stops = pd.read_csv('data/AUTOBUSES/stopsemt.csv')
bicimad = pd.read_csv('data/BICIMAD/bikestationbicimad_csv.csv')

# Mapear todos los puntos
import folium
mapa = folium.Map(location=[40.416775, -3.703790])
# Agregar marcadores para cada modo con colores diferentes
# metro -> azul, autobús -> verde, bicimad -> rojo

# Calcular densidad por zona
# Contar puntos en grid de 500m x 500m
```

### 2. **Análisis de Integración Multimodal**

```python
# Calcular distancias entre estaciones BiciMAD y Metro
from scipy.spatial.distance import cdist

# Crear matrices de coordenadas
bicimad_coords = bicimad[['lat', 'long']].values
metro_coords = metro_stops[['stop_lat', 'stop_lon']].values

# Calcular distancias (convertir a metros con fórmula haversine)
# Identificar pares dentro de 500m
```

### 3. **Análisis Temporal de Líneas de Autobús**

```python
# Convertir fechas
lines['dateIni'] = pd.to_datetime(lines['dateIni'])
lines['dateEnd'] = pd.to_datetime(lines['dateEnd'])

# Análisis por año
lines_por_año = lines.groupby(lines['dateIni'].dt.year).size()

# Visualizar evolución
plt.plot(lines_por_año.index, lines_por_año.values)
plt.xlabel('Año')
plt.ylabel('Número de líneas activas')
```

### 4. **Análisis de Accesibilidad PMR**

```python
parkings = pd.read_csv('data/Parkings/parkings.csv')

# Ratio PMR
parkings['ratio_pmr'] = parkings['Plazas_PMR'] / parkings['Plazas_standard']

# Distribución geográfica de parkings con PMR
parkings_pmr = parkings[parkings['Plazas_PMR'] > 0]

# Visualización
sns.scatterplot(data=parkings, x='long', y='lat', 
                size='Plazas_PMR', hue='ratio_pmr')
```

---

## 📐 MÉTRICAS Y KPIs

### Métricas de Cobertura
- **Densidad de estaciones**: Número de estaciones por km²
- **Radio de cobertura**: % de área cubierta en radio de 500m
- **Distancia media a estación más cercana**: Por modo de transporte

### Métricas de Integración
- **Puntos multimodales**: Nº de ubicaciones con 2+ modos en 300m
- **Distancia media inter-modal**: Entre diferentes modos
- **Parkings integrados**: % de parkings en radio de 500m de Metro

### Métricas de Accesibilidad
- **Ratio PMR**: Plazas PMR / Plazas totales (por parking)
- **Cobertura PMR**: % de parkings con plazas PMR
- **Distribución geográfica PMR**: Desviación estándar de distancias

### Métricas Temporales
- **Tasa de cambio**: Líneas añadidas/eliminadas por año
- **Longevidad media**: Duración promedio de líneas
- **Líneas especiales**: % de servicios temporales

---

## 🎓 CRITERIOS DE EVALUACIÓN (Consideraciones)

### Según Especificación del Proyecto

El proyecto debe incluir:

1. ✅ **Selección de fuentes justificada**
   - Objetivos claros de análisis
   - Requisitos de fiabilidad, actualización, completitud
   - Justificación de por qué estas fuentes responden a los objetivos

2. ✅ **Procesamiento adecuado**
   - Limpieza de datos
   - Transformaciones necesarias
   - Integración de múltiples fuentes

3. ✅ **Análisis significativo**
   - Responder a preguntas de investigación
   - Uso de técnicas estadísticas apropiadas
   - Visualizaciones claras y efectivas

4. ✅ **Documentación completa**
   - Código bien comentado
   - Memoria explicativa
   - Justificación de decisiones técnicas

---

## 💡 RECOMENDACIONES FINALES

### DO's ✅
- **Documentar todo**: Cada decisión, cada transformación
- **Validar coordenadas**: Verificar que están en el rango correcto (Madrid)
- **Usar control de versiones**: Git para el proyecto
- **Modularizar código**: Funciones reutilizables en `scripts/`
- **Verificar resultados**: Sanity checks en estadísticas
- **Citar fuentes**: Siempre referenciar origen de datos

### DON'Ts ❌
- **No modificar datos originales**: Trabajar con copias
- **No asumir calidad**: Siempre explorar primero
- **No hardcodear valores**: Usar variables/configuración
- **No ignorar NaNs**: Entender por qué existen antes de eliminar
- **No sobrevisualizar**: Cada gráfico debe tener un propósito

### Consejos Específicos
1. **Coordenadas**: Madrid está aproximadamente en lat=40.4, long=-3.7. Verificar que todos los puntos estén cerca.
2. **GTFS**: El formato es estándar pero complejo. Leer documentación oficial: https://gtfs.org/
3. **Fechas**: Cuidado con formatos mixtos en `linesemt.csv`
4. **Visualizaciones**: Folium es excelente para mapas interactivos web
5. **Performance**: Con 12k+ paradas de autobús, optimizar cálculos de distancias

---

## 📚 RECURSOS ADICIONALES

### Documentación
- **GTFS Reference**: https://gtfs.org/schedule/reference/
- **Pandas Documentation**: https://pandas.pydata.org/docs/
- **Folium Documentation**: https://python-visualization.github.io/folium/
- **GeoPandas Guide**: https://geopandas.org/

### Fuentes de Datos
- **EMT Madrid Open Data**: https://datos.emtmadrid.es/
- **CRTM Open Data**: https://datos.crtm.es/

### Inspiración
- Buscar proyectos similares en GitHub:
  - "GTFS analysis python"
  - "public transport visualization"
  - "multimodal transport integration"

---

## 📧 CONTACTO Y SOPORTE

Para dudas sobre el proyecto:
- Revisar enunciado oficial en `Especificación del proyecto PRVD.pdf`
- Consultar ejemplos en carpeta `practicas/`
- Contactar al profesor/tutor de la asignatura

---

**Última actualización**: Diciembre 2024  
**Versión**: 1.0

---

## ANEXO: Checklist del Proyecto

### Pre-análisis
- [ ] Leer especificación completa del proyecto
- [ ] Explorar todos los archivos de datos
- [ ] Instalar librerías necesarias
- [ ] Configurar entorno Jupyter

### Exploración
- [ ] Cargar todos los datasets
- [ ] Realizar análisis exploratorio
- [ ] Documentar esquemas de datos
- [ ] Identificar problemas de calidad

### Análisis
- [ ] Definir objetivos específicos
- [ ] Limpiar y preparar datos
- [ ] Realizar análisis estadísticos
- [ ] Calcular métricas definidas
- [ ] Validar resultados

### Visualización
- [ ] Crear mapas de cobertura
- [ ] Generar gráficos estadísticos
- [ ] Diseñar visualizaciones integradas
- [ ] Exportar en alta calidad

### Documentación
- [ ] Comentar todo el código
- [ ] Escribir README del proyecto
- [ ] Redactar memoria completa
- [ ] Revisar y corregir

### Entrega
- [ ] Verificar completitud
- [ ] Organizar archivos finales
- [ ] Comprimir si necesario
- [ ] Entregar en plazo

---

**¡Éxito con el proyecto!** 🚀
