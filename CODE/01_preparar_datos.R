library(sf)
library(terra)
library(dplyr)

# ============================================================
# Configuración
# ============================================================
input_points <- "DATA/MenM_VdeA_cleaned_9377.gpkg"
input_dem    <- "DATA/DEM_VALLE_2m.tif"
output_data  <- "DATA/datos_entrenamiento.rds"

cat("Cargando puntos de inventario de movimientos en masa...\n")
landslides <- st_read(input_points, quiet = TRUE)
n_positivos <- nrow(landslides)
cat("Puntos en inventario:", n_positivos, "\n")

cat("Cargando DEM (2 m)...\n")
dem <- rast(input_dem)

# Reproyectar puntos al CRS del DEM
cat("Reproyectando puntos al CRS del DEM...\n")
landslides_dem_crs <- st_transform(landslides, crs(dem))

# ============================================================
# Derivados topográficos a 2 m
# ============================================================
cat("Calculando pendiente y aspecto (2 m)...\n")
slope  <- terrain(dem, "slope",  unit = "degrees")
aspect <- terrain(dem, "aspect", unit = "degrees")

# Curvatura: planiforme y de perfil
# Disponible en terra >= 1.7; si falla, se usa un proxy focal.
cat("Calculando curvatura (2 m)...\n")
curvature <- tryCatch({
  curv_plan <- terrain(dem, "planc")
  curv_prof <- terrain(dem, "profc")
  list(plan = curv_plan, prof = curv_prof)
}, error = function(e) {
  cat(
    "  [AVISO] terra no soporta 'planc'/'profc' en esta version.",
    "Usando segunda diferencia central como proxy.\n"
  )
  w <- matrix(c(0, 1, 0, 1, -4, 1, 0, 1, 0), 3, 3)
  curv_total <- focal(dem, w = w, fun = sum, na.rm = TRUE)
  list(plan = curv_total, prof = curv_total)
})

names(curvature$plan) <- "curv_plan"
names(curvature$prof) <- "curv_prof"

# ============================================================
# TWI a 10 m (resolución reducida para eficiencia)
# ============================================================
# Nota: El TWI correcto es ln(A / tan(beta)), donde A es el area
# de contribucion especifica (flow accumulation x resolucion).
# Como terra no incluye flow accumulation D8, se usa la formula
# reducida ln(1 / tan(beta)), que omite el area acumulada.
# Para un calculo riguroso se recomienda el paquete {whitebox}.
cat("Calculando TWI aproximado (10 m)...\n")
dem_10m       <- aggregate(dem, fact = 5)
slope_rad_10m <- terrain(dem_10m, "slope", unit = "radians")
eps           <- 0.001
twi_10m       <- log(1 / (tan(slope_rad_10m) + eps))
twi_10m[is.infinite(twi_10m)] <- NA
names(twi_10m) <- "twi"

# ============================================================
# Muestreo de puntos de no-ocurrencia (negativos)
# Criterios: (1) pendiente > 5 deg, (2) fuera de buffer 1 km
# ============================================================
cat("Generando", n_positivos, "puntos de no-ocurrencia...\n")
mask_eligible <- slope > 5

cat("Calculando distancias a deslizamientos (10 m)...\n")
dist_ras_10m      <- distance(rasterize(landslides_dem_crs, dem_10m))
mask_eligible_10m <- aggregate(mask_eligible, fact = 5)
mask_eligible_10m[dist_ras_10m < 1000] <- NA

set.seed(42)
negativos    <- spatSample(
  mask_eligible_10m,
  size   = n_positivos,
  method = "random",
  na.rm  = TRUE,
  as.points = TRUE
)
negativos_sf <- st_as_sf(negativos)
cat("Puntos negativos generados:", nrow(negativos_sf), "\n")

# ============================================================
# Combinar y extraer covariables
# ============================================================
cat("Combinando puntos y extrayendo covariables...\n")
positives_df <- data.frame(st_coordinates(landslides_dem_crs), occ = 1L)
negatives_df <- data.frame(st_coordinates(negativos_sf),       occ = 0L)
all_points   <- rbind(positives_df, negatives_df)
all_spat     <- vect(all_points, geom = c("X", "Y"), crs = crs(dem))

# Nombrar capas
names(dem)    <- "elev"
names(slope)  <- "slope"
names(aspect) <- "aspect"

# Extraer covariables 2 m
cat("Extrayendo variables a 2 m...\n")
stack_2m <- c(dem, slope, aspect, curvature$plan, curvature$prof)
datos_2m <- extract(stack_2m, all_spat)

# Extraer TWI a 10 m
cat("Extrayendo TWI a 10 m...\n")
datos_twi <- extract(twi_10m, all_spat)

# ============================================================
# Construir dataframe final
# ============================================================
df_final <- data.frame(
  x         = all_points$X,
  y         = all_points$Y,
  occ       = all_points$occ,
  elev      = datos_2m$elev,
  slope     = datos_2m$slope,
  aspect    = datos_2m$aspect,
  curv_plan = datos_2m$curv_plan,
  curv_prof = datos_2m$curv_prof,
  twi       = datos_twi$twi
)

n_antes  <- nrow(df_final)
df_final <- df_final[complete.cases(df_final), ]
cat(
  "Registros finales (sin NA):", nrow(df_final),
  "(de", n_antes, ")\n"
)
cat("Positivos finales:", sum(df_final$occ == 1), "\n")
cat("Negativos finales:", sum(df_final$occ == 0), "\n")

cat("\nEstadisticos descriptivos:\n")
print(summary(
  df_final[, c("elev", "slope", "aspect", "curv_plan", "curv_prof", "twi")]
))

cat("\nGuardando datos de entrenamiento...\n")
saveRDS(df_final, output_data)
cat("Proceso completado ->", output_data, "\n")
