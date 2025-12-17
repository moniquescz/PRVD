import pandas as pd
import folium
from folium.plugins import MarkerCluster, HeatMap
from pyproj import Transformer
import numpy as np
import os

# Configuración
DATA_PATH = '../data'
RESULTADOS_PATH = '../resultados'
OUTPUT_MAP = '../resultados/mapa_cobertura.html'

def cargar_y_procesar_metro():
    print("Cargando Metro...")
    try:
        df = pd.read_csv(os.path.join(DATA_PATH, 'Metro/stops.txt'))
        df = df[['stop_id', 'stop_name', 'stop_lat', 'stop_lon']].copy()
        df['mode'] = 'metro'
        return df
    except Exception as e:
        print(f"Error cargando Metro: {e}")
        return pd.DataFrame()

def cargar_y_procesar_autobuses():
    print("Cargando Autobuses...")
    try:
        # Cargar con separador ,
        df = pd.read_csv(os.path.join(DATA_PATH, 'AUTOBUSES/stopsemt.csv'), sep=',', quotechar='"')
        
        # Conversión de coordenadas UTM 30N a WGS84
        transformer = Transformer.from_crs("EPSG:25830", "EPSG:4326", always_xy=True)
        lon, lat = transformer.transform(df['posX'].values, df['posY'].values)
        
        df['stop_lat'] = lat
        df['stop_lon'] = lon
        df['stop_name'] = df['description'] if 'description' in df.columns else 'Bus Stop'
        df['stop_id'] = df['stopId']
        
        df = df[['stop_id', 'stop_name', 'stop_lat', 'stop_lon']].copy()
        df['mode'] = 'bus'
        return df
    except Exception as e:
        print(f"Error cargando Autobuses: {e}")
        return pd.DataFrame()

def cargar_y_procesar_bicimad():
    print("Cargando BiciMAD...")
    try:
        # Separador ; y posibles comas en números
        df = pd.read_csv(os.path.join(DATA_PATH, 'BICIMAD/bikestationbicimad_csv.csv'), sep=';')
        
        # Corregir coordenadas si vienen con coma
        for col in ['POINT_X', 'POINT_Y']:
            if df[col].dtype == object:
                df[col] = df[col].astype(str).str.replace(',', '.').astype(float)
        
        df = df.rename(columns={
            'POINT_Y': 'stop_lat',
            'POINT_X': 'stop_lon',
            'Name': 'stop_name',
            'OBJECTID': 'stop_id'
        })
        
        df = df[['stop_id', 'stop_name', 'stop_lat', 'stop_lon']].copy()
        df['mode'] = 'bicimad'
        return df
    except Exception as e:
        print(f"Error cargando BiciMAD (check header?): {e}")
        return pd.DataFrame()

def calcular_densidad(df_all):
    print("\nCalculando densidad de estaciones...")
    # Grid de aprox 500m (0.0045 grados lat/lon aprox en Madrid)
    STEP = 0.0045
    
    df_all['lat_bin'] = (df_all['stop_lat'] / STEP).round().astype(int)
    df_all['lon_bin'] = (df_all['stop_lon'] / STEP).round().astype(int)
    
    density = df_all.groupby(['lat_bin', 'lon_bin']).size().reset_index(name='count')
    density['lat_center'] = density['lat_bin'] * STEP
    density['lon_center'] = density['lon_bin'] * STEP
    
    # Top densidades
    print("Top 10 zonas con mayor densidad de transporte:")
    print(density.sort_values('count', ascending=False).head(10))
    return density

def crear_mapa(metro, bus, bici):
    print("\nGenerando mapa...")
    m = folium.Map(location=[40.416775, -3.703790], zoom_start=12, tiles='CartoDB positron')
    
    # Capas
    layer_metro = folium.FeatureGroup(name='Metro (Azul)')
    layer_bus = folium.FeatureGroup(name='Autobús (Verde)')
    layer_bici = folium.FeatureGroup(name='BiciMAD (Rojo)')
    
    # Añadir puntos Metro
    for idx, row in metro.iterrows():
        folium.CircleMarker(
            location=[row['stop_lat'], row['stop_lon']],
            radius=4,
            color='blue',
            fill=True,
            fill_opacity=0.7,
            popup=f"Metro: {row['stop_name']}"
        ).add_to(layer_metro)
        
    # Añadir puntos Bus (Cluster para rendimiento, son muchos)
    bus_cluster = MarkerCluster(name='Autobús (Cluster)').add_to(m)
    # Si se prefiere sin cluster, usar FeatureGroup pero será lento
    # Usamos FeatureGroup para visualización directa si son < 2000, pero son 12k.
    # El usuario pidió "Mapear todos", así que usaremos circles pero con cuidado.
    # Para cumplir "verde", usaremos CircleMarker en el cluster o feature group.
    # Dado el volumen, mejor submuestrear o cluster.
    # Pero el usuario pidió colores específicos. Haremos FeatureGroup pero aviso que puede pesar.
    
    for idx, row in bus.iterrows():
        folium.CircleMarker(
            location=[row['stop_lat'], row['stop_lon']],
            radius=2,
            color='green',
            fill=True,
            fill_opacity=0.5,
            popup=f"Bus: {row['stop_name']}"
        ).add_to(layer_bus)
        
    # Añadir puntos Bici
    for idx, row in bici.iterrows():
        folium.CircleMarker(
            location=[row['stop_lat'], row['stop_lon']],
            radius=3,
            color='red',
            fill=True,
            fill_opacity=0.6,
            popup=f"Bici: {row['stop_name']}"
        ).add_to(layer_bici)

    layer_metro.add_to(m)
    layer_bus.add_to(m)
    layer_bici.add_to(m)
    
    folium.LayerControl().add_to(m)
    
    m.save(OUTPUT_MAP)
    print(f"Mapa guardado en: {OUTPUT_MAP}")

def main():
    metro = cargar_y_procesar_metro()
    bus = cargar_y_procesar_autobuses()
    bici = cargar_y_procesar_bicimad()
    
    print(f"Registros Metro: {len(metro)}")
    print(f"Registros Bus: {len(bus)}")
    print(f"Registros Bici: {len(bici)}")
    
    df_all = pd.concat([metro, bus, bici])
    
    calcular_densidad(df_all)
    crear_mapa(metro, bus, bici)
    print("Análisis completado.")

if __name__ == "__main__":
    main()
