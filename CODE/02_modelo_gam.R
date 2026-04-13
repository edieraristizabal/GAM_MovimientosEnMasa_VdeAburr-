library(mgcv)
library(pROC)
library(ggplot2)
library(dplyr)

# ============================================================
# Cargar datos: occ debe ser numerico (0/1) para GAM binomial
# ============================================================
df <- readRDS("DATA/datos_entrenamiento.rds") |>
  mutate(occ = as.integer(as.character(occ))) |>
  filter(
    !is.na(elev), !is.na(slope), !is.na(aspect),
    !is.na(curv_plan), !is.na(curv_prof), !is.na(twi)
  )

cat("Total de registros:", nrow(df), "\n")
cat("Positivos:", sum(df$occ == 1), "| Negativos:", sum(df$occ == 0), "\n")

# ============================================================
# Division entrenamiento / prueba (70 / 30, estratificada)
# ============================================================
set.seed(42)
idx_pos   <- which(df$occ == 1)
idx_neg   <- which(df$occ == 0)
train_pos <- sample(idx_pos, size = round(0.7 * length(idx_pos)))
train_neg <- sample(idx_neg, size = round(0.7 * length(idx_neg)))
train_idx <- c(train_pos, train_neg)

df_train <- df[train_idx, ]
df_test  <- df[-train_idx, ]
cat("Entrenamiento:", nrow(df_train), "| Prueba:", nrow(df_test), "\n\n")

# ============================================================
# Modelo GAM con regresion logistica
#
# IMPORTANTE: El aspecto (0-360 deg) es una variable CIRCULAR.
# Se usa spline cubico ciclico (bs="cc") con extremos ligados
# en 0 y 360 grados para evitar discontinuidad artificial.
# ============================================================
cat("Ajustando modelo GAM (REML)...\n")
modelo_gam <- gam(
  occ ~ s(elev) + s(slope) +
    s(aspect, bs = "cc", k = 10) +
    s(curv_plan) + s(curv_prof) + s(twi),
  family = binomial(link = "logit"),
  data   = df_train,
  method = "REML",
  knots  = list(aspect = c(0, 360))
)

cat("\n=== Resumen del modelo ===\n")
print(summary(modelo_gam))

# ============================================================
# Diagnosticos del GAM
# ============================================================
cat("\n=== Concurvidad entre predictores ===\n")
print(concurvity(modelo_gam, full = FALSE))

cat("\nGenerando graficos de diagnostico (gam.check)...\n")
png("FIGURAS/gam_check.png", width = 900, height = 900, res = 120)
par(mfrow = c(2, 2))
gam.check(modelo_gam)
dev.off()

# ============================================================
# Evaluacion en conjunto de PRUEBA (no en entrenamiento)
# ============================================================
cat("\n=== Evaluacion en conjunto de prueba ===\n")
df_test$pred <- predict(modelo_gam, newdata = df_test, type = "response")
roc_obj  <- roc(df_test$occ, df_test$pred, quiet = TRUE)
auc_val  <- as.numeric(auc(roc_obj))
cat("AUC:", round(auc_val, 4), "\n")

# Umbral optimo: maximiza el Indice de Youden (equivalente al TSS)
coords_opt <- coords(
  roc_obj, x = "best", best.method = "youden",
  ret = c("threshold", "sensitivity", "specificity")
)
umbral_opt <- as.numeric(coords_opt["threshold"])
cat("Umbral optimo (Youden J):", round(umbral_opt, 3), "\n")

# Matriz de confusion con umbral optimo
pred_cat <- ifelse(df_test$pred > umbral_opt, 1L, 0L)
matriz   <- table(Real = df_test$occ, Predicho = pred_cat)
cat("\nMatriz de confusion (umbral optimo):\n")
print(matriz)

# ============================================================
# Metricas de desempeno
# ============================================================
tp <- matriz["1", "1"]
tn <- matriz["0", "0"]
fp <- matriz["0", "1"]
fn <- matriz["1", "0"]

sensibilidad  <- tp / (tp + fn)
especificidad <- tn / (tn + fp)
exactitud     <- (tp + tn) / nrow(df_test)
tss           <- sensibilidad + especificidad - 1
precision_val <- tp / (tp + fp)
f1            <- 2 * (precision_val * sensibilidad) /
  (precision_val + sensibilidad)

# Cohen's Kappa
po    <- exactitud
pe    <- ((tp + fp) * (tp + fn) + (tn + fn) * (tn + fp)) /
  nrow(df_test)^2
kappa <- (po - pe) / (1 - pe)

cat("\n--- Metricas de Desempeno (conjunto de prueba) ---\n")
cat("AUC                        :", round(auc_val, 4), "\n")
cat("Exactitud (Accuracy)       :", round(exactitud, 4), "\n")
cat("Sensibilidad (Recall)      :", round(sensibilidad, 4), "\n")
cat("Especificidad              :", round(especificidad, 4), "\n")
cat("Precision                  :", round(precision_val, 4), "\n")
cat("F1-Score                   :", round(f1, 4), "\n")
cat("TSS (True Skill Statistic) :", round(tss, 4), "\n")
cat("Kappa de Cohen             :", round(kappa, 4), "\n")

# ============================================================
# Figuras
# ============================================================
cat("\nGenerando figuras...\n")

# 1. Curva ROC
png("FIGURAS/curva_roc.png", width = 800, height = 800, res = 120)
plot(
  roc_obj,
  main = paste0(
    "Curva ROC — Conjunto de Prueba\n(AUC = ", round(auc_val, 3), ")"
  ),
  col = "steelblue", lwd = 2
)
abline(a = 0, b = 1, lty = 2, col = "gray50")
points(especificidad, sensibilidad, pch = 19, col = "red", cex = 1.4)
legend(
  "bottomright",
  legend = c(
    paste("AUC =", round(auc_val, 3)),
    paste("TSS =", round(tss, 3)),
    paste("Umbral =", round(umbral_opt, 3))
  ),
  bty = "n", cex = 0.9
)
grid()
dev.off()

# 2. Funciones de suavizado del GAM
png("FIGURAS/gam_smooths.png", width = 1400, height = 900, res = 120)
par(mfrow = c(2, 3))
plot(
  modelo_gam, select = 1, main = "Efecto Elevacion (m)",
  shade = TRUE, col = "darkred",    shade.col = "#FFCCCC",
  residuals = TRUE, pch = ".", cex = 2, ylab = "s(elev)"
)
plot(
  modelo_gam, select = 2, main = "Efecto Pendiente (deg)",
  shade = TRUE, col = "darkgreen",  shade.col = "#CCFFCC",
  residuals = TRUE, pch = ".", cex = 2, ylab = "s(slope)"
)
plot(
  modelo_gam, select = 3, main = "Efecto Aspecto (deg) — Ciclico",
  shade = TRUE, col = "darkblue",   shade.col = "#CCCCFF",
  residuals = TRUE, pch = ".", cex = 2, ylab = "s(aspect, cc)"
)
plot(
  modelo_gam, select = 4, main = "Curvatura Planiforme",
  shade = TRUE, col = "purple",     shade.col = "#EECCFF",
  residuals = TRUE, pch = ".", cex = 2, ylab = "s(curv_plan)"
)
plot(
  modelo_gam, select = 5, main = "Curvatura de Perfil",
  shade = TRUE, col = "brown",      shade.col = "#FFDDCC",
  residuals = TRUE, pch = ".", cex = 2, ylab = "s(curv_prof)"
)
plot(
  modelo_gam, select = 6, main = "Efecto TWI",
  shade = TRUE, col = "darkorange", shade.col = "#FFE0CC",
  residuals = TRUE, pch = ".", cex = 2, ylab = "s(twi)"
)
dev.off()

# 3. Importancia relativa: reduccion de devianza al omitir predictor
cat("\nCalculando importancia relativa (reduccion de devianza)...\n")
formulas_red <- list(
  sin_elev      = occ ~ s(slope) + s(aspect, bs = "cc", k = 10) +
    s(curv_plan) + s(curv_prof) + s(twi),
  sin_slope     = occ ~ s(elev) + s(aspect, bs = "cc", k = 10) +
    s(curv_plan) + s(curv_prof) + s(twi),
  sin_aspect    = occ ~ s(elev) + s(slope) +
    s(curv_plan) + s(curv_prof) + s(twi),
  sin_curv_plan = occ ~ s(elev) + s(slope) +
    s(aspect, bs = "cc", k = 10) + s(curv_prof) + s(twi),
  sin_curv_prof = occ ~ s(elev) + s(slope) +
    s(aspect, bs = "cc", k = 10) + s(curv_plan) + s(twi),
  sin_twi       = occ ~ s(elev) + s(slope) +
    s(aspect, bs = "cc", k = 10) + s(curv_plan) + s(curv_prof)
)
knots_red <- list(
  sin_elev      = list(aspect = c(0, 360)),
  sin_slope     = list(aspect = c(0, 360)),
  sin_aspect    = NULL,
  sin_curv_plan = list(aspect = c(0, 360)),
  sin_curv_prof = list(aspect = c(0, 360)),
  sin_twi       = list(aspect = c(0, 360))
)

red_dev <- mapply(function(f, k) {
  m <- gam(f, family = binomial, data = df_train, method = "REML", knots = k)
  modelo_gam$deviance - m$deviance
}, formulas_red, knots_red)

nombres_var <- c(
  "Elevacion", "Pendiente", "Aspecto",
  "Curv. Planiforme", "Curv. Perfil", "TWI"
)
names(red_dev) <- nombres_var
cat("Reduccion de devianza al omitir cada predictor:\n")
print(round(red_dev, 2))

df_imp <- data.frame(
  variable  = names(red_dev),
  delta_dev = as.numeric(red_dev)
)
g_imp <- ggplot(
  df_imp,
  aes(x = reorder(variable, delta_dev), y = delta_dev, fill = variable)
) +
  geom_col(show.legend = FALSE) +
  coord_flip() +
  labs(
    title = "Importancia relativa de predictores",
    x     = NULL,
    y     = "Reduccion de devianza (Delta D)"
  ) +
  theme_minimal(base_size = 13)
ggsave(
  "FIGURAS/importancia_predictores.png", g_imp,
  width = 6, height = 4, dpi = 120
)

# ============================================================
# Modelo final: reentrenado con el 100 % de los datos
# Las metricas de evaluacion (AUC, TSS, etc.) corresponden al
# conjunto de prueba independiente (30 %) calculado arriba.
# ============================================================
cat("\nReentrenando modelo final con el 100 % de los datos...\n")
modelo_final <- gam(
  occ ~ s(elev) + s(slope) +
    s(aspect, bs = "cc", k = 10) +
    s(curv_plan) + s(curv_prof) + s(twi),
  family = binomial(link = "logit"),
  data   = df,
  method = "REML",
  knots  = list(aspect = c(0, 360))
)
cat("Modelo final ajustado (n =", nrow(df), "registros)\n")
cat("Devianza explicada (100%):",
    round((1 - modelo_final$deviance / modelo_final$null.deviance) * 100, 1),
    "%\n")

saveRDS(modelo_final, "DATA/modelo_gam_final.rds")
cat("Modelo final guardado en DATA/modelo_gam_final.rds\n")
cat("Proceso de modelado completado.\n")
