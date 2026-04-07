library(sf)
library(terra)
library(ggplot2)
library(dplyr)
library(tidyr)
library(mgcv)

# ============================================================
# Configuracion
# ============================================================
input_points_rds <- "DATA/datos_entrenamiento.rds"
input_dem <- "DATA/DEM_VALLE_2m.tif"
modelo_rds <- "DATA/modelo_gam_final.rds"
inventory_gpkg <- "DATA/MenM_VdeA_cleaned_9377.gpkg"

# Paleta de colores susceptibilidad: verde=bajo, rojo=alto
susc_palette <- colorRampPalette(c("#1a7f1a", "#ffff00", "#cc0000"))(100)

cat("Cargando datos...\n")
df <- readRDS(input_points_rds)
modelo <- readRDS(modelo_rds)
dem <- rast(input_dem)
inventory <- st_read(inventory_gpkg, quiet = TRUE)

# ============================================================
# 0. Mapa de Localizacion del Valle de Aburrá
# ============================================================
cat("Generando Mapa de Localizacion...\n")

# Obtenemos el extent del DEM en WGS84 para el recuadro de localizacion
dem_ext_sf <- st_as_sf(as.polygons(ext(dem), crs = crs(dem))) |>
  st_transform(4326)

mapa_loc_ok <- tryCatch({
  if (!requireNamespace("rnaturalearth", quietly = TRUE)) stop("no pkg")
  colombia <- rnaturalearth::ne_countries(
    country = "Colombia", scale = "medium", returnclass = "sf"
  )
  antioquia <- tryCatch(
    rnaturalearth::ne_states(country = "Colombia", returnclass = "sf") |>
      filter(name == "Antioquia"),
    error = function(e) NULL
  )

  g_loc <- ggplot() +
    geom_sf(data = colombia, fill = "#d9d9d9", color = "white", linewidth = 0.5) +
    {
      if (!is.null(antioquia))
        geom_sf(data = antioquia, fill = "#aac8e0", color = "white", linewidth = 0.3)
    } +
    geom_sf(
      data = dem_ext_sf, fill = "#cc0000", color = "#880000",
      alpha = 0.8, linewidth = 0.8
    ) +
    coord_sf(xlim = c(-80, -66), ylim = c(-4, 13)) +
    annotate("text", x = -76.0, y = 5.8, label = "Valle\nde Aburrá",
             size = 2.5, color = "#880000", fontface = "bold") +
    labs(
      title = "Localización del Valle de Aburrá",
      x = "Longitud (°O)", y = "Latitud (°N)"
    ) +
    theme_minimal(base_size = 10) +
    theme(panel.grid.major = element_line(color = "#e0e0e0", linewidth = 0.3))

  ggsave(
    "FIGURAS/mapa_localizacion.png", g_loc,
    width = 5, height = 7, dpi = 150
  )
  TRUE
}, error = function(e) {
  cat(
    "  [AVISO] rnaturalearth no disponible.",
    "Generando mapa simplificado...\n"
  )
  # Alternativa: mapa del extent del DEM
  png("FIGURAS/mapa_localizacion.png", width = 600, height = 700, res = 120)
  plot(
    dem_ext_sf["geometry"],
    col = "#cc0000", border = "#880000", lwd = 2,
    main = "Localización del Valle de Aburrá\n(Antioquia, Colombia)",
    axes = TRUE
  )
  dev.off()
  FALSE
})
cat("  Mapa de localizacion generado.\n")

# ============================================================
# 1. Mapa de Inventario
# ============================================================
cat("Generando Mapa de Inventario...\n")
dem_50m <- aggregate(dem, fact = 25)
slope_50m <- terrain(dem_50m, "slope", unit = "radians")
aspect_50m <- terrain(dem_50m, "aspect", unit = "radians")
hill <- shade(slope_50m, aspect_50m)

png("FIGURAS/mapa_inventario.png", width = 1000, height = 1200, res = 120)
plot(
  hill,
  col = grey(0:100 / 100),
  legend = FALSE,
  main = "Distribucion Espacial de Movimientos en Masa (2001-2024)"
)
plot(
  st_geometry(st_transform(inventory, crs(dem))),
  add = TRUE, col = adjustcolor("red", alpha.f = 0.7), pch = 16, cex = 0.3
)
sbar(10000, type = "line", divs = 4, label = c(0, 5, 10), below = "km")
north(cbind(870000, 1205000))
dev.off()

# ============================================================
# 2. Estadisticos descriptivos de covariables (Tabla)
# ============================================================
cat("Calculando estadisticos descriptivos...\n")
vars_stat <- c("elev", "slope", "aspect", "curv_plan", "curv_prof", "twi")

stat_table <- do.call(rbind, lapply(vars_stat, function(v) {
  x <- df[, v]
  # Moda: peak de la densidad kernel
  dens <- density(x, na.rm = TRUE)
  moda <- dens$x[which.max(dens$y)]
  data.frame(
    Variable = v,
    Min = round(min(x, na.rm = TRUE), 2),
    Q1 = round(quantile(x, 0.25, na.rm = TRUE), 2),
    Media = round(mean(x, na.rm = TRUE), 2),
    Mediana = round(median(x, na.rm = TRUE), 2),
    Q3 = round(quantile(x, 0.75, na.rm = TRUE), 2),
    Max = round(max(x, na.rm = TRUE), 2),
    DE = round(sd(x, na.rm = TRUE), 2),
    Moda = round(moda, 2)
  )
}))

cat("\nEstadisticos descriptivos de covariables:\n")
print(stat_table)
write.csv(stat_table, "DATA/estadisticos_covariables.csv", row.names = FALSE)

# ============================================================
# 3. Histogramas comparativos y pruebas KS
# ============================================================
cat("Generando Histogramas Comparativos...\n")
vars_plot <- c("elev", "slope", "aspect", "curv_plan", "curv_prof", "twi")

df_long <- df |>
  select(all_of(c("occ", vars_plot))) |>
  mutate(occ = as.factor(occ)) |>
  pivot_longer(cols = -occ, names_to = "variable", values_to = "valor")

etiquetas_vars <- c(
  elev = "Elevacion (m)",
  slope = "Pendiente (deg)",
  aspect = "Aspecto (deg)",
  curv_plan = "Curv. Planiforme",
  curv_prof = "Curv. de Perfil",
  twi = "TWI"
)

cat("Resultados de Pruebas Kolmogorov-Smirnov:\n")
ks_results <- lapply(vars_plot, function(v) {
  p_vals <- df[df$occ == 1, v]
  n_vals <- df[df$occ == 0, v]
  test <- ks.test(p_vals, n_vals)
  cat(
    v, ": D =", round(test$statistic, 4),
    " p-value =", format(test$p.value, scientific = TRUE), "\n"
  )
  test
})

g_hist <- ggplot(df_long, aes(x = valor, fill = occ)) +
  geom_density(alpha = 0.5) +
  facet_wrap(
    ~variable,
    scales = "free",
    labeller = labeller(variable = etiquetas_vars)
  ) +
  scale_fill_manual(
    values = c("0" = "steelblue", "1" = "firebrick"),
    labels = c("No-ocurrencia", "Deslizamiento")
  ) +
  labs(
    title = "Distribucion de Variables por Clase",
    x = "Valor", y = "Densidad", fill = "Clase"
  ) +
  theme_minimal(base_size = 11)

ggsave(
  "FIGURAS/comparativa_histogramas.png", g_hist,
  width = 10, height = 7, dpi = 120
)

# ============================================================
# 4. Mapas de Variables Individuales (50 m)
# ============================================================
cat("Generando Mapas de Variables (50 m)...\n")
slope_50m_deg <- terrain(dem_50m, "slope", unit = "degrees")
aspect_50m_deg <- terrain(dem_50m, "aspect", unit = "degrees")

curvatures_50m <- tryCatch({
  list(
    curv_plan = terrain(dem_50m, "planc"),
    curv_prof = terrain(dem_50m, "profc")
  )
}, error = function(e) {
  w <- matrix(c(0, 1, 0, 1, -4, 1, 0, 1, 0), 3, 3)
  ct <- focal(dem_50m, w = w, fun = sum, na.rm = TRUE)
  list(curv_plan = ct, curv_prof = ct)
})

slope_rad_50m <- terrain(dem_50m, "slope", unit = "radians")
eps <- 0.001
twi_50m <- log(1 / (tan(slope_rad_50m) + eps))
twi_50m[is.infinite(twi_50m)] <- NA

layers <- list(
  elev = dem_50m,
  slope = slope_50m_deg,
  aspect = aspect_50m_deg,
  curv_plan = curvatures_50m$curv_plan,
  curv_prof = curvatures_50m$curv_prof,
  twi = twi_50m
)
titulos <- c(
  "Elevacion (m)", "Pendiente (deg)", "Aspecto (deg)",
  "Curvatura Planiforme", "Curvatura de Perfil", "TWI"
)

for (i in seq_along(layers)) {
  nm <- names(layers)[i]
  png(
    paste0("FIGURAS/mapa_", nm, ".png"),
    width = 1000, height = 1200, res = 120
  )
  plot(layers[[i]], main = titulos[i])
  sbar(10000, type = "line", divs = 4, label = c(0, 5, 10), below = "km")
  north(cbind(870000, 1205000))
  dev.off()
}

# ============================================================
# 5. Mapa de Susceptibilidad Regional (50 m) — colores verde-rojo
# ============================================================
cat("Generando Mapa de Susceptibilidad Regional (50 m)...\n")

names(layers$elev) <- "elev"
names(layers$slope) <- "slope"
names(layers$aspect) <- "aspect"
names(layers$curv_plan) <- "curv_plan"
names(layers$curv_prof) <- "curv_prof"
names(layers$twi) <- "twi"

stack_50m <- do.call(c, unname(lapply(layers, function(r) r)))
pred_50m <- predict(stack_50m, modelo, type = "response")

png(
  "FIGURAS/mapa_susceptibilidad_regional.png",
  width = 1000, height = 1200, res = 120
)
plot(
  pred_50m,
  main = "Susceptibilidad por Movimientos en Masa - Valle de Aburra (50 m)",
  col = susc_palette
)
sbar(10000, type = "line", divs = 4, label = c(0, 5, 10), below = "km")
north(cbind(870000, 1205000))
dev.off()

# ============================================================
# 6. Estadisticos de covariables para zonas de alta susceptibilidad
# ============================================================
cat("Calculando estadisticos para alta susceptibilidad...\n")
# Prediccion sobre todos los puntos del dataset
df$susc <- predict(modelo, newdata = df, type = "response")

# Definicion de alta susceptibilidad: percentil 75 o > 0.7
threshold_high <- max(0.7, quantile(df$susc, 0.75, na.rm = TRUE))
df_high <- df[df$susc >= threshold_high, ]
cat(
  "Puntos con susceptibilidad alta (>=", round(threshold_high, 2), "):",
  nrow(df_high), "\n"
)

stat_high <- do.call(rbind, lapply(vars_stat, function(v) {
  x <- df_high[, v]
  dens <- density(x, na.rm = TRUE)
  moda <- dens$x[which.max(dens$y)]
  data.frame(
    Variable = v,
    Min = round(min(x, na.rm = TRUE), 2),
    Media = round(mean(x, na.rm = TRUE), 2),
    Mediana = round(median(x, na.rm = TRUE), 2),
    Max = round(max(x, na.rm = TRUE), 2),
    DE = round(sd(x, na.rm = TRUE), 2),
    Moda = round(moda, 2)
  )
}))

cat("\nEstadisticos para zonas de alta susceptibilidad:\n")
print(stat_high)
write.csv(stat_high, "DATA/estadisticos_alta_susceptibilidad.csv",
          row.names = FALSE)

cat("\nAnalisis Exploratorio Finalizado.\n")
