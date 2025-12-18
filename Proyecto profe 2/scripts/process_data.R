# Script de Preprocesamiento para MuxViz -- Proyecto Profe 2

# Función para instalar/cargar paquetes
ensure_package <- function(pkg) {
  if (!require(pkg, character.only = TRUE)) {
    install.packages(pkg, dependencies = TRUE)
    library(pkg, character.only = TRUE)
  }
}

ensure_package("dplyr")
ensure_package("geosphere")
ensure_package("readr")
ensure_package("stringr")

# Definir rutas ABSOLUTAS para evitar errores de directorio de trabajo
# Ajustamos la ruta base al proyecto específico
base_path <- "C:/Users/nicol/Desktop/NICO/AA_universidad/MASTER CIENCIA DE DATOS/1ER CUATRI/PREPROCESO, RECOLECCIÓN Y VISUALIZACION DE DATOS/TRABAJOS/Alejandro/PRVD/Proyecto profe 2"
data_path <- file.path(base_path, "data")
output_path <- file.path(base_path, "output")

if(!dir.exists(output_path)) dir.create(output_path, recursive = TRUE)

# --- 1. Cargar Datos ---
cat("Cargando datos desde:", data_path, "\n")
bus_raw <- read_delim(file.path(data_path, "autobuses_procesado.csv"), delim = ";", show_col_types = FALSE)
metro_raw <- read_delim(file.path(data_path, "metro_procesado.csv"), delim = ";", show_col_types = FALSE)
bicimad_raw <- read_delim(file.path(data_path, "bicimad_procesado.csv"), delim = ";", show_col_types = FALSE)

# --- 2. Unificar Nodos y Asignar IDs ---
# Necesitamos una lista global de nodos para MuxViz (ID 1..N)

# Limpieza y selección de columnas clave
bus_nodes <- bus_raw %>%
  select(original_id = stop_id, name = stop_name, lat = stop_lat, lon = stop_lon) %>%
  mutate(layer = "bus", type = "stop") %>%
  distinct(original_id, .keep_all = TRUE) # Evitar duplicados si hay

# Filtrar solo paradas de metro (ignorar accesos 'acc_' si es necesario, o mantenerlos)
# Asumiremos que 'par_' son las paradas y 'acc_' son accesos. Para la red, usamos paradas.
metro_nodes <- metro_raw %>%
  filter(str_detect(stop_id, "^par_")) %>% # Ajuste corrección syntax
  select(original_id = stop_id, name = stop_name, lat = stop_lat, lon = stop_lon) %>%
  mutate(layer = "metro", type = "station") %>%
  distinct(original_id, .keep_all = TRUE)

# Si el filtro devuelve vacío (por si acaso el formato es distinto), usamos todo
if(nrow(metro_nodes) == 0) {
  metro_nodes <- metro_raw %>%
    select(original_id = stop_id, name = stop_name, lat = stop_lat, lon = stop_lon) %>%
    mutate(layer = "metro", type = "station") %>%
    distinct(original_id, .keep_all = TRUE)
}

bicimad_nodes <- bicimad_raw %>%
  select(original_id = station_id, name = station_name, lat = stop_lat, lon = stop_lon) %>%
  mutate(layer = "bicimad", type = "station") %>%
  distinct(original_id, .keep_all = TRUE)

# Combinar todo
all_nodes <- bind_rows(bus_nodes, metro_nodes, bicimad_nodes) %>%
  mutate(node_id = row_number()) # ID numérico global para MuxViz

cat("Total nodos:", nrow(all_nodes), "\n")

# Guardar layout para MuxViz (nodeID label x y)
# MuxViz espera: id label x y (a veces requiere columnas específicas, suele ser nodeID label lat lon)
layout_df <- all_nodes %>%
  select(nodeID = node_id, label = name, lat, lon)

write_delim(layout_df, file.path(output_path, "layout_muxviz.txt"), delim = " ", col_names = FALSE)
cat("Layout guardado en: output/layout_muxviz.txt\n")

# --- 3. Generar Enlaces (Edges) Intra-capa ---

# A. BUS (Conectar paradas consecutivas de la misma línea)
# Asumimos que el archivo de bus está ordenado o tiene una lógica secuencial.
# Si no, esto es una aproximación.
cols_bus_lines <- bus_raw %>%
  group_by(bus_line) %>%
  group_split()

bus_edges <- list()

for(line_data in cols_bus_lines) {
  if(nrow(line_data) > 1) {
    # Ordenar por sequence si existe, si no, confiar en orden de fila
    # line_data <- line_data %>% arrange(...) 
    
    # Crear enlaces i -> i+1
    ids <- line_data$stop_id
    from_ids <- ids[-length(ids)]
    to_ids <- ids[-1]
    
    # Mapear a node_id global
    from_global <- all_nodes$node_id[match(from_ids, all_nodes$original_id)]
    to_global <- all_nodes$node_id[match(to_ids, all_nodes$original_id)]
    
    # Solo si ambos existen (match no NA)
    valid <- !is.na(from_global) & !is.na(to_global)
    
    if(any(valid)) {
      bus_edges[[length(bus_edges)+1]] <- data.frame(from = from_global[valid], to = to_global[valid], weight = 1)
    }
  }
}
bus_edges_df <- bind_rows(bus_edges) %>% distinct()

# B. METRO (Aproximación: si no hay info de línea, conectar por cercanía o 'line' id si existiera)
# En el head vimos 'par_4_1'. Si '4' es línea, podemos conectar.
# Intentaremos extraer el ID de línea.
metro_edges_df <- data.frame(from=integer(), to=integer(), weight=numeric())

# Intento de extracción de línea: par_LINEA_ORDEN
metro_processed <- metro_raw %>%
  mutate(
    line_guess = str_extract(stop_id, "(?<=par_)\\d+"),
    order_guess = as.numeric(str_extract(stop_id, "(?<=_)\\d+$"))
  ) %>%
  filter(!is.na(line_guess) & !is.na(order_guess))

if(nrow(metro_processed) > 0) {
  metro_lines <- metro_processed %>% group_by(line_guess) %>% arrange(order_guess) %>% group_split()
  
  metro_edges_list <- list()
  for(line_dat in metro_lines) {
    if(nrow(line_dat) > 1) {
      ids <- line_dat$stop_id
      from_ids <- ids[-length(ids)]
      to_ids <- ids[-1]
      
      from_global <- all_nodes$node_id[match(from_ids, all_nodes$original_id)]
      to_global <- all_nodes$node_id[match(to_ids, all_nodes$original_id)]
      
      valid <- !is.na(from_global) & !is.na(to_global)
      if(any(valid)) {
        metro_edges_list[[length(metro_edges_list)+1]] <- data.frame(from = from_global[valid], to = to_global[valid], weight = 1)
      }
    }
  }
  metro_edges_df <- bind_rows(metro_edges_list) %>% distinct()
}

# C. BICIMAD (Geometric Graph: conectar a k-vecinos más cercanos)
# Esto simula que puedes ir de una estación a cualquier otra cercana.
cat("Generando enlaces Bicimad (geométricos)...\n")
bici_indices <- which(all_nodes$layer == "bicimad")
if(length(bici_indices) > 1) {
  coords <- all_nodes[bici_indices, c("lon", "lat")]
  # Matriz de distancias
  dist_mat <- distm(coords, fun = distHaversine)
  
  # Conectar cada nodo con sus 3 más cercanos (ejemplo para evitar red densa completa)
  bici_edges_list <- list()
  k <- 3
  
  for(i in 1:nrow(dist_mat)) {
    # Ordenar distancias (excluyendo el propio 0 en índice i)
    dists <- dist_mat[i, ]
    dists[i] <- Inf # Ignorar self-loop
    nearest <- order(dists)[1:k]
    
    # De indices locales a globales
    from_node <- all_nodes$node_id[bici_indices[i]]
    to_nodes <- all_nodes$node_id[bici_indices[nearest]]
    
    bici_edges_list[[length(bici_edges_list)+1]] <- data.frame(from = from_node, to = to_nodes, weight = 1)
  }
  bici_edges_df <- bind_rows(bici_edges_list) %>% distinct()
} else {
  bici_edges_df <- data.frame(from=integer(), to=integer(), weight=numeric())
}

# --- 4. Generar Enlaces Inter-capa (Transbordos) ---
# Conectar nodos de diferentes capas si están a < 200m
cat("Generando enlaces Inter-capa (costoso computacionalmente para muchos nodos)...\n")

# Para optimizar, podríamos hacerlo solo para subsets, pero aquí haremos fuerza bruta controlada
# o solo Bus <-> Metro y Metro <-> Bici

layers <- unique(all_nodes$layer)
inter_layer_edges <- list()

# Función auxiliar para conectar capa A y capa B
connect_layers <- function(layerA, layerB, threshold=150) {
  idxA <- which(all_nodes$layer == layerA)
  idxB <- which(all_nodes$layer == layerB)
  
  if(length(idxA) == 0 || length(idxB) == 0) return(NULL)
  
  coordsA <- all_nodes[idxA, c("lon", "lat")]
  coordsB <- all_nodes[idxB, c("lon", "lat")]
  
  # Matriz distancias (filas A, cols B)
  dmat <- distm(coordsA, coordsB, fun = distHaversine)
  
  # Encontrar pares < threshold
  pairs <- which(dmat < threshold, arr.ind = TRUE)
  
  if(nrow(pairs) > 0) {
    from_nodes <- all_nodes$node_id[idxA[pairs[,1]]]
    to_nodes <- all_nodes$node_id[idxB[pairs[,2]]]
    return(data.frame(from = from_nodes, to = to_nodes, weight = 1, layer_from = layerA, layer_to = layerB))
  }
  return(NULL)
}

# Autobus <-> Metro
inter_bm <- connect_layers("bus", "metro", 150)
# Metro <-> Bicimad
inter_mb <- connect_layers("metro", "bicimad", 150)
# Bus <-> Bicimad (Opcional, puede ser mucho)
# inter_bb <- connect_layers("bus", "bicimad", 100)

inter_edges_df <- bind_rows(inter_bm, inter_mb) #, inter_bb)

# --- 5. Exportar Edges y Configuración para MuxViz ---

# Para usar buildMultilayerNetworkFromMuxvizFiles (versión GUI/Estándar),
# necesitamos archivos separados por capa y un archivo de configuración.

# A. Guardar edges por capa
write.table(metro_edges_df[,c("from","to","weight")], file.path(output_path, "metro.edges"), row.names=F, col.names=F, quote=F)
write.table(bus_edges_df[,c("from","to","weight")], file.path(output_path, "bus.edges"), row.names=F, col.names=F, quote=F)
write.table(bici_edges_df[,c("from","to","weight")], file.path(output_path, "bicimad.edges"), row.names=F, col.names=F, quote=F)

# B. Guardar layout (id label x y)
# Aseguramos formato correcto: nodeID label x y
layout_export <- all_nodes %>% select(node_id, name, lon, lat)
write.table(layout_export, file.path(output_path, "layout_muxviz.txt"), row.names=F, col.names=F, quote=F)

# C. Crear archivo de Configuración (Config.txt)
# Formato: layerID;layerLabel;path_edges;path_layout
config_data <- data.frame(
  id = 1:3,
  label = c("Metro", "Bus", "Bicimad"),
  edge_path = c("metro.edges", "bus.edges", "bicimad.edges"),
  layout_path = rep("layout_muxviz.txt", 3)
)
# Usamos rutas relativas para el config si lo ejecutamos desde output, o absolutas para seguridad
# MuxViz a veces prefiere absolutas.
config_data$edge_path <- file.path(output_path, config_data$edge_path)
config_data$layout_path <- file.path(output_path, config_data$layout_path)

write.table(config_data, file.path(output_path, "config_muxviz.txt"), sep=";", row.names=F, col.names=F, quote=F)
cat("Archivos de configuración generados en:", output_path, "\n")


# Guardar CSV de nodos para referencia
write_csv(all_nodes, file.path(output_path, "nodos_muxviz_map.csv"))

# --- 6. Integración con MuxViz (Generar objeto .RData) ---
cat("Generando objeto MuxViz...\n")

if(require("muxViz", quietly = TRUE)) {
    # Intentar usar buildMultilayerNetworkFromMuxvizFiles
    if (exists("buildMultilayerNetworkFromMuxvizFiles", where = asNamespace("muxViz"), mode = "function")) {
        tryCatch({
            cat("Usando buildMultilayerNetworkFromMuxvizFiles...\n")
            g.list <- muxViz::buildMultilayerNetworkFromMuxvizFiles(
                config.file = file.path(output_path, "config_muxviz.txt"),
                MultisliceType = "categorical"
            )
            
            # Nota: buildMultilayerNetworkFromMuxvizFiles NO añade automáticamente los edges inter-capa si no están en el config.
            # Pero MuxViz GUI los calcula a menudo dinámicamente o requiere formato extendido.
            # Si queremos forzar los inter-capa manuales que calculamos (inter_edges_df), los añadimos al objeto igraph:
            
            # (Opcional: Añadir inter-links manualmente al objeto graph final si MuxViz lo permite)
            # Por ahora, guardamos el objeto base.
            
            save(g.list, file = file.path(output_path, "muxviz_network.RData"))
            cat("Objeto MuxViz guardado en: output/muxviz_network.RData\n")
            
        }, error = function(e) {
            cat("Error al construir con config file:", e$message, "\n")
        })
    } else {
        cat("Advertencia: No se encuentra la función de construcción de MuxViz.\n")
    }
} else {
  cat("Librería 'muxViz' no encontrada. Instálala para generar el objeto RData.\n")
}

