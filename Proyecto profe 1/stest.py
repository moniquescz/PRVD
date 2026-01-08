import pandas as pd
import folium
import requests
import json
import re
import unicodedata

# 1. TABLA DE CONVERSIÓN (Basada en los datos que proporcionaste)
# Mapeamos el código TX (01, 02...) al nombre real para el buscador
# IMPORTANTE: Los nombres deben coincidir EXACTAMENTE con el GeoJSON
distrito_map = {
    "01": "Centro", "02": "Arganzuela", "03": "Retiro", "04": "Salamanca",
    "05": "Chamartin", "06": "Tetuan", "07": "Chamberi", "08": "Fuencarral-El Pardo",
    "09": "Moncloa-Aravaca", "10": "Latina", "11": "Carabanchel", "12": "Usera",
    "13": "Puente de Vallecas", "14": "Moratalaz", "15": "Ciudad Lineal", "16": "Hortaleza",
    "17": "Villaverde", "18": "Villa de Vallecas", "19": "Vicalvaro", "20": "San Blas",
    "21": "Barajas"
}

def limpiar_nombre_distrito(texto):
    """
    Extrae el código numérico de cadenas como 'Madrid distrito 01' 
    y devuelve el nombre oficial del distrito.
    """
    # Buscamos dos dígitos en el texto (ej: 01, 08, 12...)
    match = re.search(r'(\d{2})', str(texto))
    if match:
        codigo = match.group(1)
        # Normalizamos a título (ej: "CENTRO" -> "Centro") por si acaso
        nombre = distrito_map.get(codigo, texto)
        return nombre
    return texto 

def normalize_name(name):
    """
    Normaliza un nombre de distrito eliminando acentos, 
    convirtiendo a minúsculas y normalizando espacios/guiones.
    """
    # Eliminar acentos
    name = ''.join(
        c for c in unicodedata.normalize('NFD', str(name))
        if unicodedata.category(c) != 'Mn'
    )
    # Convertir a minúsculas
    name = name.lower()
    # Normalizar espacios y guiones (eliminar espacios alrededor de guiones)
    name = re.sub(r'\s*-\s*', '-', name)
    # Eliminar espacios múltiples
    name = re.sub(r'\s+', ' ', name)
    # Eliminar espacios al principio y final
    name = name.strip()
    return name 

# --- CONFIGURACIÓN DE ARCHIVOS ---
FILE_PATH = r'C:\Users\Eric\Desktop\Master\PRVD\Practicas\Practica_Final\PRVD\Proyecto profe 1\resultados\viajes_madrid.csv'
COLUMN_NAME = 'name' 
GEOJSON_URL = "https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/madrid-districts.geojson"

# 2. CARGA DE DATOS
try:
    df = pd.read_csv(FILE_PATH, sep=None, engine='python', encoding='latin-1', on_bad_lines='skip')
    print(f"✅ CSV cargado. Procesando conversiones...")
except Exception as e:
    print(f"❌ Error al abrir el archivo: {e}")
    exit()

# 3. PROCESAR NOMBRES ÚNICOS CON LA CONVERSIÓN
nombres_en_csv = set(df[COLUMN_NAME].dropna())
municipios_encontrados = set()

for nombre in nombres_en_csv:
    nombre_limpio = limpiar_nombre_distrito(nombre)
    municipios_encontrados.add(nombre_limpio)

print(f"📍 Distritos identificados tras conversión en CSV ({len(municipios_encontrados)}): {municipios_encontrados}")

# 4. DESCARGAR GEOJSON DE DISTRITOS
print("\n⬇️  Descargando GeoJSON de distritos...")
try:
    response = requests.get(GEOJSON_URL)
    response.raise_for_status()
    geojson_data = response.json()
    print("✅ GeoJSON descargado correctamente.")
except Exception as e:
    print(f"❌ Error al descargar GeoJSON: {e}")
    exit()

# 5. INICIALIZAR MAPA
# Centrado en Madrid
mapa = folium.Map(location=[40.4167, -3.7033], zoom_start=11)

# 6. FILTRAR Y PINTAR EL GEOJSON
# Recorremos cada "Feature" del GeoJSON para ver si coincide con nuestros datos

def style_function(feature):
    # Intentamos casar el nombre del GeoJSON con nuestros nombres limpios
    # El GeoJSON tiene el nombre en feature['properties']['name']
    nombre_geojson = feature['properties'].get('name', '')
    
    # Normalizar el nombre del GeoJSON
    nombre_geojson_norm = normalize_name(nombre_geojson)
    
    # Buscar coincidencia con los distritos encontrados
    encontrado = False
    for m in municipios_encontrados:
        m_norm = normalize_name(m)
        if nombre_geojson_norm == m_norm:
            encontrado = True
            break
    
    if encontrado:
        return {
            'fillColor': '#3186cc', # Azul para los encontrados
            'color': 'blue',
            'weight': 2,
            'fillOpacity': 0.4
        }
    else:
        return {
            'fillColor': '#gray',   # Gris para los NO encontrados (si hubiera)
            'color': 'gray',
            'weight': 1,
            'fillOpacity': 0.1
        }

# Añadimos el GeoJSON al mapa con la función de estilo dinámica
folium.GeoJson(
    geojson_data,
    style_function=style_function,
    tooltip=folium.GeoJsonTooltip(fields=['name'], aliases=['Distrito:'])
).add_to(mapa)

# Contar cuántos distritos fueron encontrados
distritos_geojson = set()
distritos_mapeados = 0

for feature in geojson_data['features']:
    nombre_geo = feature['properties'].get('name', '')
    distritos_geojson.add(nombre_geo)
    
    # Verificar si este distrito fue encontrado
    nombre_geo_norm = normalize_name(nombre_geo)
    for m in municipios_encontrados:
        if normalize_name(m) == nombre_geo_norm:
            distritos_mapeados += 1
            break

print(f"\n📊 Resumen:")
print(f"   - Distritos en el GeoJSON: {len(distritos_geojson)}")
print(f"   - Distritos encontrados en CSV: {len(municipios_encontrados)}")
print(f"   - Distritos mapeados correctamente: {distritos_mapeados}")

print(f"\n✅ Distritos encontrados en CSV:")
for distrito in sorted(municipios_encontrados):
    print(f"   - {distrito}")

# Mostrar distritos del GeoJSON que NO fueron encontrados
distritos_no_encontrados = []
for nombre_geo in distritos_geojson:
    nombre_geo_norm = normalize_name(nombre_geo)
    encontrado = False
    for m in municipios_encontrados:
        if normalize_name(m) == nombre_geo_norm:
            encontrado = True
            break
    if not encontrado:
        distritos_no_encontrados.append(nombre_geo)

if distritos_no_encontrados:
    print(f"\n⚠️  Distritos en GeoJSON NO encontrados en CSV:")
    for distrito in sorted(distritos_no_encontrados):
        print(f"   - {distrito}")
else:
    print(f"\n✨ ¡Todos los distritos del GeoJSON fueron encontrados en el CSV!")

# 7. GUARDAR
output_file = "mapa_distritos_madrid.html"
mapa.save(output_file)
print(f"✨ Mapa generado correctamente como '{output_file}'")