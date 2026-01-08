import pandas as pd
import numpy as np
from scipy.spatial import distance

# Rutas de los archivos
viajes_path = r'C:\Users\Eric\Desktop\Master\PRVD\Practicas\Practica_Final\PRVD\Proyecto profe 1\data\viajes_madrid.csv'
transporte_path = r'C:\Users\Eric\Desktop\Master\PRVD\Practicas\Practica_Final\PRVD\Proyecto profe 1\resultados\transporte_madrid_consolidado.csv'
output_path = r'C:\Users\Eric\Desktop\Master\PRVD\Practicas\Practica_Final\PRVD\Proyecto profe 1\resultados\transporte_madrid_con_distritos.csv'

print("=" * 80)
print("SCRIPT DE ASIGNACIÓN DE DISTRITOS A PARADAS DE TRANSPORTE")
print("=" * 80)

# Mapeo de códigos de distrito a nombres reales de Madrid
nombres_distritos_madrid = {
    2807901: "Centro",
    2807902: "Arganzuela",
    2807903: "Retiro",
    2807904: "Salamanca",
    2807905: "Chamartín",
    2807906: "Tetuán",
    2807907: "Chamberí",
    2807908: "Fuencarral-El Pardo",
    2807909: "Moncloa-Aravaca",
    2807910: "Latina",
    2807911: "Carabanchel",
    2807912: "Usera",
    2807913: "Puente de Vallecas",
    2807914: "Moratalaz",
    2807915: "Ciudad Lineal",
    2807916: "Hortaleza",
    2807917: "Villaverde",
    2807918: "Villa de Vallecas",
    2807919: "Vicálvaro",
    2807920: "San Blas-Canillejas",
    2807921: "Barajas"
}

print("\n1. Distritos de Madrid configurados:")
for codigo, nombre in sorted(nombres_distritos_madrid.items()):
    num_distrito = str(codigo)[-2:]
    print(f"   Distrito {num_distrito}: {nombre}")

print("\n2. Leyendo archivo de transporte consolidado...")
df_transporte = pd.read_csv(transporte_path, sep=';', encoding='utf-8')
print(f"   ✓ Total de registros en transporte: {len(df_transporte)}")

# Limpiar espacios en blanco de las columnas
df_transporte.columns = df_transporte.columns.str.strip()

print("\n3. Configurando centroides de cada distrito...")

# Centroides aproximados de los 21 distritos de Madrid (lat, lon)
centroides_distritos = {
    2807901: (40.4200, -3.7050),  # Centro
    2807902: (40.4000, -3.6950),  # Arganzuela
    2807903: (40.4100, -3.6750),  # Retiro
    2807904: (40.4300, -3.6700),  # Salamanca
    2807905: (40.4650, -3.6800),  # Chamartín
    2807906: (40.4550, -3.6950),  # Tetuán
    2807907: (40.4350, -3.7050),  # Chamberí
    2807908: (40.4900, -3.7100),  # Fuencarral-El Pardo
    2807909: (40.4450, -3.7250),  # Moncloa-Aravaca
    2807910: (40.3900, -3.7150),  # Latina
    2807911: (40.3700, -3.7250),  # Carabanchel
    2807912: (40.3800, -3.7000),  # Usera
    2807913: (40.3900, -3.6600),  # Puente de Vallecas
    2807914: (40.4050, -3.6450),  # Moratalaz
    2807915: (40.4450, -3.6550),  # Ciudad Lineal
    2807916: (40.4700, -3.6550),  # Hortaleza
    2807917: (40.3500, -3.7000),  # Villaverde
    2807918: (40.3700, -3.6250),  # Villa de Vallecas
    2807919: (40.3950, -3.6100),  # Vicálvaro
    2807920: (40.4250, -3.6350),  # San Blas-Canillejas
    2807921: (40.4750, -3.5800),  # Barajas
}

print(f"   ✓ Centroides de {len(centroides_distritos)} distritos configurados")

def asignar_distrito_cercano(lat, lon, centroides, nombres):
    """
    Asigna el distrito más cercano basándose en la distancia euclidiana
    a los centroides de los distritos.
    """
    if pd.isna(lat) or pd.isna(lon):
        return None, None, None
    
    punto = np.array([lat, lon])
    distancias = {}
    
    for codigo_distrito, centroide in centroides.items():
        centroide_array = np.array(centroide)
        dist = distance.euclidean(punto, centroide_array)
        distancias[codigo_distrito] = dist
    
    # Encontrar el distrito más cercano
    distrito_cercano = min(distancias, key=distancias.get)
    nombre_distrito = nombres.get(distrito_cercano, "Desconocido")
    num_distrito = str(distrito_cercano)[-2:]
    
    return distrito_cercano, nombre_distrito, f"Distrito {num_distrito}"

print("\n4. Asignando distritos a cada parada de transporte...")
print("   (Esto puede tardar un momento...)")

# Aplicar la función a cada fila
resultados = df_transporte.apply(
    lambda row: asignar_distrito_cercano(
        row['stop_lat'], 
        row['stop_lon'], 
        centroides_distritos,
        nombres_distritos_madrid
    ),
    axis=1
)

# Separar los resultados en tres columnas
df_transporte['codigo_distrito'] = resultados.apply(lambda x: x[0])
df_transporte['nombre_distrito'] = resultados.apply(lambda x: x[1])
df_transporte['distrito_num'] = resultados.apply(lambda x: x[2])

print(f"   ✓ Distritos asignados correctamente")

# Mostrar estadísticas
print("\n5. Estadísticas de asignación:")
distrito_counts = df_transporte.groupby(['distrito_num', 'nombre_distrito']).size().reset_index(name='count')
distrito_counts = distrito_counts.sort_values('distrito_num')

print("\n   Distribución de paradas por distrito:")
for _, row in distrito_counts.iterrows():
    if pd.notna(row['distrito_num']):
        print(f"      {row['distrito_num']} ({row['nombre_distrito']}): {row['count']} paradas")

print(f"\n6. Guardando archivo en: {output_path}")
df_transporte.to_csv(output_path, sep=';', index=False, encoding='utf-8')

print("\n" + "=" * 80)
print("¡PROCESO COMPLETADO EXITOSAMENTE!")
print("=" * 80)
print(f"\nArchivo generado: {output_path}")
print(f"Total de registros: {len(df_transporte)}")
print(f"Columnas agregadas:")
print(f"  - codigo_distrito: Código completo del distrito (ej: 2807901)")
print(f"  - nombre_distrito: Nombre real del distrito (ej: Centro)")
print(f"  - distrito_num: Número de distrito (ej: Distrito 01)")

# Crear también un archivo separado solo con la información de distritos
distritos_ref = pd.DataFrame([
    {'codigo_distrito': codigo, 'nombre_distrito': nombre, 'distrito_num': f"Distrito {str(codigo)[-2:]}"}
    for codigo, nombre in sorted(nombres_distritos_madrid.items())
])

distritos_output_path = r'C:\Users\Eric\Desktop\Master\PRVD\Practicas\Practica_Final\PRVD\Proyecto profe 1\resultados\distritos_madrid.csv'
distritos_ref.to_csv(distritos_output_path, sep=';', index=False, encoding='utf-8')
print(f"\nArchivo de referencia de distritos guardado en: {distritos_output_path}")

# Mostrar una muestra de los datos
print("\n7. Muestra de los primeros registros con distrito asignado:")
muestra = df_transporte[['stop_name', 'stop_lat', 'stop_lon', 'nombre_distrito', 'distrito_num']].head(15)
for idx, row in muestra.iterrows():
    nombre_parada = row['stop_name'].strip()[:40]
    print(f"   {nombre_parada:40} -> {row['nombre_distrito']:25} ({row['distrito_num']})")

print("\n" + "=" * 80)
