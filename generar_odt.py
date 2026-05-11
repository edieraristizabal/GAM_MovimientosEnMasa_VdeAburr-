#!/usr/bin/env python3
"""
Genera manuscrito_TecnoLogicas.odt usando la plantilla de la revista TecnoLógicas.
Requiere: pip3 install odfpy
"""
import os, copy
from odf.opendocument import load
from odf.text import P, H, Span, LineBreak
from odf.draw import Frame, Image
from odf.table import Table, TableColumn, TableRow, TableCell
from odf.style import Style, ParagraphProperties
from odf.element import Element

BASE = '/home/edier/Documents/INVESTIGACION/PAPERS/ELABORACION/GAM_MovimientosEnMasa_VdeAburr-'
TEMPLATE = f'{BASE}/Plantilla_autores_Final_ESP_2025_VF.odt'
OUTPUT   = f'{BASE}/manuscrito_TecnoLogicas.odt'
FIG_DIR  = f'{BASE}/FIGURAS'

# ── Referencias IEEE (en orden de aparición en el texto) ─────────────────────
IEEE_REFS = [
    '[1] E. V. Aristizábal, O. I. Sanchez y O. Korup, "Landslide timing and rainfall regimes in a rapidly urbanizing tropical mountain valley in Colombia," Natural Hazards, vol. 122, p. 306, 2026. doi: 10.1007/s11069-026-08028-6',
    '[2] D. Gómez, E. F. García y E. Aristizábal, "Spatial and temporal landslide distributions using global and open landslide databases," Natural Hazards, 2023. doi: 10.1007/s11069-023-05848-8',
    '[3] D. Petley, "Global patterns of loss of life from landslides," Geology, vol. 40, núm. 10, pp. 927-930, 2012. doi: 10.1130/G33217.1',
    '[4] E. Aristizábal y O. Sánchez, "Spatial and temporal patterns and the socioeconomic impacts of landslides in the tropical and mountainous Colombian Andes," Disasters, vol. 44, núm. 3, pp. 596-620, 2020. doi: 10.1111/disa.12391',
    '[5] E. Aristizábal y J. Gómez, "Inventario de emergencias y desastres en el Valle de Aburrá. Originados por fenómenos naturales y antrópicos en el periodo 1880-2007," Gestión y Ambiente, vol. 10, núm. 2, pp. 17-30, 2007.',
    '[6] S. Nieto, E. Aristizábal y U. Ozturk, "Coupled evolution of a city and landslides," Environmental Research Letters, vol. 20, p. 054001, 2025. doi: 10.1088/1748-9326/adc4d8',
    '[7] O. Hungr, S. Leroueil y L. Picarelli, "The Varnes classification of landslide types, an update," Landslides, vol. 11, núm. 2, pp. 167-194, 2014. doi: 10.1007/s10346-013-0436-y',
    '[8] A. Brenning, "Statistical geocomputing combining R and SAGA: the example of landslide susceptibility analysis with generalized additive models," SAGA – Seconds Out, vol. 19, pp. 23-32, 2008.',
    '[9] A. Merghadi et al., "Machine learning methods for landslide susceptibility studies: A comparative overview of algorithm performance," Earth-Science Reviews, vol. 207, p. 103225, 2020. doi: 10.1016/j.earscirev.2020.103225',
    '[10] T. J. Hastie y R. J. Tibshirani, Generalized Additive Models. Londres: Chapman and Hall, 1990.',
    '[11] S. N. Wood, Generalized Additive Models: An Introduction with R, 2.a ed. Boca Ratón: Chapman and Hall/CRC, 2017.',
    '[12] R. Trenkamp, J. N. Kellogg, J. T. Freymueller y H. P. Mora, "Wide plate margin deformation, southern Central America and northwestern South America, CASA GPS observations," Journal of South American Earth Sciences, vol. 15, núm. 2, pp. 157-171, 2002. doi: 10.1016/S0895-9811(02)00018-4',
    '[13] F. Cediel, R. P. Shaw y C. Cáceres, "Tectonic assembly of the Northern Andean Block," en The Circum-Gulf of Mexico and the Caribbean, C. Bartolini, R. T. Buffler y J. Blickwede, Eds., AAPG Memoir, vol. 79. Tulsa: AAPG, 2003, pp. 815-848.',
    '[14] J. A. Nelder y R. W. M. Wedderburn, "Generalized linear models," Journal of the Royal Statistical Society, Series A, vol. 135, núm. 3, pp. 370-384, 1972. doi: 10.2307/2344614',
    '[15] P. McCullagh y J. A. Nelder, Generalized Linear Models, 2.a ed. Londres: Chapman and Hall, 1989.',
    '[16] K. J. Beven y M. J. Kirkby, "A physically based, variable contributing area model of basin hydrology," Hydrological Sciences Bulletin, vol. 24, núm. 1, pp. 43-69, 1979. doi: 10.1080/02626667909491834',
    '[17] D. W. Hosmer, S. Lemeshow y R. X. Sturdivant, Applied Logistic Regression, 3.a ed. Hoboken: John Wiley & Sons, 2013.',
    '[18] J. Cohen, "A coefficient of agreement for nominal scales," Educational and Psychological Measurement, vol. 20, núm. 1, pp. 37-46, 1960. doi: 10.1177/001316446002000104',
    '[19] H. Petschko, A. Brenning, R. Bell, J. Goetz y T. Glade, "Assessing the quality of landslide susceptibility maps — case study Lower Austria," Natural Hazards and Earth System Sciences, vol. 14, núm. 1, pp. 95-118, 2014. doi: 10.5194/nhess-14-95-2014',
    '[20] P. Reichenbach, M. Rossi, B. D. Malamud, M. Mihir y F. Guzzetti, "A review of statistically-based landslide susceptibility models," Earth-Science Reviews, vol. 180, pp. 60-91, 2018. doi: 10.1016/j.earscirev.2018.03.001',
    '[21] A. Brenning, "Spatial cross-validation and bootstrap for the assessment of prediction rules in remote sensing: the R package sperrorest," en 2012 IEEE Int. Geoscience and Remote Sensing Symp., 2012, pp. 5372-5375. doi: 10.1109/IGARSS.2012.6352393',
    '[22] D. R. Roberts et al., "Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure," Ecography, vol. 40, núm. 8, pp. 913-929, 2017. doi: 10.1111/ecog.02881',
    '[23] P. Vorpahl, H. Elsenbeer, M. Märker y B. Schröder, "How can statistical models help to determine driving factors of landslides?" Ecological Modelling, vol. 239, pp. 27-39, 2012. doi: 10.1016/j.ecolmodel.2011.12.007',
    '[24] R. C. Sidle y H. Ochiai, Landslides: Processes, Prediction, and Land Use, vol. 18. Washington, D.C.: American Geophysical Union, 2006.',
    '[25] F. Guzzetti et al., "Landslide susceptibility analysis and zoning through remote sensing and GIS," Engineering Geology, vol. 86, núm. 2-3, pp. 214-239, 2006. doi: 10.1016/j.enggeo.2006.02.013',
    '[26] E. Aristizábal, J. I. Vélez, H. E. Martínez y M. Jaboyedoff, "SHIA_Landslide: a distributed conceptual and physically based model to forecast shallow landslides triggered by rainfall in tropical and mountainous basins," Landslides, vol. 13, pp. 497-517, 2016. doi: 10.1007/s10346-015-0580-7',
    '[27] M. C. Herrera-Coy et al., "Landslide Susceptibility Analysis on the Vicinity of Bogotá-Villavicencio Road (Eastern Cordillera of the Colombian Andes)," Remote Sensing, vol. 15, núm. 15, p. 3870, 2023. doi: 10.3390/rs15153870',
    '[28] J. P. Wilson y J. C. Gallant, Terrain Analysis: Principles and Applications. Nueva York: John Wiley & Sons, 2000.',
    '[29] E. Muñoz et al., "Analysis of landslide explicative factors and susceptibility mapping in an Andean context: The case of Azuay province (Ecuador)," Heliyon, vol. 9, núm. 10, p. e20170, 2023. doi: 10.1016/j.heliyon.2023.e20170',
    '[30] A. C. Morales Vélez, E. Aristizábal y A. M. Ramos-Cañón, "Space-time analysis of the relationship between landslides, rainfall variability and ENSO in the Tropical Andean Mountain region in Colombia," Landslides, vol. 21, pp. 1639-1657, 2024. doi: 10.1007/s10346-024-02225-9',
    '[31] S. Steger, A. Brenning, R. Bell y T. Glade, "The influence of systematically incomplete shallow landslide inventories on statistical susceptibility models and suggestions for improvements," Landslides, vol. 14, núm. 5, pp. 1767-1781, 2017. doi: 10.1007/s10346-017-0820-0',
    '[32] S. Steger et al., "Correlation does not imply geomorphic causation in data-driven landslide susceptibility modelling — Benefits of exploring landslide data collection effects," Science of the Total Environment, vol. 776, p. 145935, 2021. doi: 10.1016/j.scitotenv.2021.145935',
]

# ── Contenido del manuscrito (secciones) ─────────────────────────────────────
# Cada sección es una lista de elementos: ('h1', texto), ('h2', texto),
# ('p', texto), ('eq', texto_ecuacion, numero), ('fig', archivo, caption, num),
# ('table', headers, rows, caption, num), ('ul', [items]), ('ol', [items])

TITULO_ES = ('EFECTO DE VARIABLES MORFOMÉTRICAS SOBRE LA OCURRENCIA DE MOVIMIENTOS EN MASA '
             'EN EL VALLE DE ABURRÁ MEDIANTE MODELOS ADITIVOS GENERALIZADOS (GAM)')
TITULO_EN = ('EFFECT OF MORPHOMETRIC VARIABLES ON THE OCCURRENCE OF MASS MOVEMENTS '
             'IN THE ABURRÁ VALLEY USING GENERALIZED ADDITIVE MODELS (GAM)')

RESUMEN = (
    'Los modelos estadísticos para la evaluación de la susceptibilidad por movimientos en masa '
    'frecuentemente asumen relaciones lineales entre las variables morfométricas y la probabilidad '
    'de ocurrencia, o bien emplean modelos no paramétricos de difícil interpretación. Este estudio '
    'aplicó Modelos Aditivos Generalizados (GAM) para cuantificar el efecto no lineal de seis '
    'variables morfométricas —elevación, pendiente, aspecto, curvatura planiforme, curvatura de '
    'perfil e índice topográfico de humedad (TWI)— sobre la ocurrencia de movimientos en masa en '
    'el Valle de Aburrá, Colombia. Se utilizó un inventario de 5 487 eventos históricos '
    '(2001-2024) y un modelo digital de elevación de 2 m de resolución. El modelo se ajustó con '
    'distribución binomial, función de enlace logit y selección automática del suavizado mediante '
    'máxima verosimilitud restringida (REML). Evaluado en un conjunto de prueba independiente '
    '(partición 70/30), el modelo alcanzó un área bajo la curva ROC (AUC) de 0,908 y un índice '
    'de habilidad verdadera (TSS) de 0,816, desempeño clasificado como excelente. El TWI fue el '
    'predictor dominante, seguido de la pendiente y las curvaturas topográficas. Las funciones de '
    'suavizado identificaron rangos morfométricos críticos asociados a la mayor probabilidad de '
    'falla: pendientes entre 20° y 45°, elevaciones entre 1 500 y 2 000 m, orientaciones '
    'oeste-noroeste, zonas cóncavas en planta y en perfil, y TWI superior a 5. A diferencia de '
    'los métodos de aprendizaje automático, los GAM permiten visualizar el efecto individual de '
    'cada predictor, lo que los hace auditables y justificables ante autoridades de planificación '
    'territorial. Los resultados constituyen insumos de alto valor para la gestión del riesgo y '
    'el ordenamiento territorial en el área metropolitana del Valle de Aburrá.'
)
PALABRAS_CLAVE = 'movimientos en masa, susceptibilidad, modelos aditivos generalizados, Valle de Aburrá, índice topográfico de humedad'

ABSTRACT_EN = (
    'Statistical models for landslide susceptibility assessment frequently assume linear '
    'relationships between morphometric variables and the probability of occurrence, or '
    'employ non-parametric machine-learning approaches whose predictions are difficult to '
    'interpret from a geomorphological standpoint. This study applied Generalized Additive '
    'Models (GAM) to quantify the non-linear effect of six morphometric variables—elevation, '
    'slope, aspect, planform curvature, profile curvature, and the Topographic Wetness Index '
    '(TWI)—on the occurrence of mass movements in the Aburrá Valley, Colombia. An inventory '
    'of 5,487 historical events recorded between 2001 and 2024 was used together with a '
    'digital elevation model at 2 m spatial resolution. The model was fitted with a binomial '
    'distribution, a logit link function, and automatic smoothing parameter selection via '
    'Restricted Maximum Likelihood (REML). Evaluated on an independent test set using a '
    '70/30 stratified partition, the model achieved an Area Under the ROC Curve (AUC) of '
    '0.908 and a True Skill Statistic (TSS) of 0.816, a performance level classified as '
    'excellent. The TWI emerged as the dominant predictor, followed by slope and topographic '
    'curvatures. The estimated smoothing functions identified critical morphometric ranges '
    'associated with the highest failure probability: slopes between 20° and 45°, elevations '
    'between 1,500 and 2,000 m, west-northwest aspects, concave zones in both planform and '
    'profile curvature, and TWI values greater than 5. Unlike machine-learning methods, GAMs '
    'allow the visualization of the individual effect of each predictor on the probability of '
    'failure, making the model auditable and technically justifiable to land-use planning '
    'authorities. The results constitute high-value technical inputs for disaster risk '
    'management and territorial planning in the Aburrá Valley metropolitan area.'
)
KEYWORDS_EN = 'landslides, susceptibility, generalized additive models, Aburrá Valley, topographic wetness index'

# ── Contenido de las secciones ────────────────────────────────────────────────
SECTIONS = [
    # ── 1. INTRODUCCIÓN ──────────────────────────────────────────────────────
    [('h1', '1.\tINTRODUCCIÓN'),
     ('p', 'Los movimientos en masa constituyen una de las amenazas naturales de mayor impacto '
           'humano y económico a escala global, especialmente en terrenos de montaña donde '
           'confluyen precipitaciones intensas y laderas de fuerte pendiente en suelos tropicales '
           '[1], [2], [3]. El análisis de las bases de datos globales revela que entre 1903 y '
           '2020 se han documentado más de 37 946 deslizamientos que produjeron 185 753 víctimas '
           'fatales en 161 países, con los continentes americano y asiático concentrando las '
           'mayores cifras [2]. Aproximadamente el 60 % de los deslizamientos reportados a nivel '
           'mundial son desencadenados por lluvias, lo que subraya el papel dominante de la '
           'precipitación como mecanismo detonante y la necesidad de integrar variables '
           'hidrometeorológicas y morfométricas en los modelos de evaluación de la amenaza [2], [1].'),
     ('p', 'Colombia se encuentra entre los países más afectados del hemisferio occidental. El '
           'inventario nacional registra 30 730 deslizamientos ocurridos entre 1900 y 2018, con '
           'más de 34 000 víctimas fatales asociadas; el 92 % de estos eventos fueron '
           'desencadenados por lluvia y el 80 % ocurrieron en los flancos de las cordilleras de '
           'los Andes [4]. Este patrón espacial refleja la combinación de laderas de fuerte '
           'pendiente, perfiles de meteorización profundos, y presencia de eventos de lluvias '
           'intensos [1].'),
     ('p', 'Los primeros registros sistemáticos de desastres por movimientos en masa en el Valle '
           'de Aburrá datan de 1880 [5], y la base de datos regional acumula más de 6 750 eventos '
           'entre 1880 y 2007, de los cuales los movimientos en masa representan el 35 % del '
           'total de emergencias registradas. En el Valle de Aburrá, con aproximadamente '
           '4,1 millones de habitantes, los movimientos en masa son responsables del 75 % de las '
           'víctimas por desastres y constituyen la amenaza geológica de mayor recurrencia [4], [6]. '
           'El crecimiento urbano extraordinariamente rápido del valle —la población se incrementó '
           '30 veces entre 1905 y 2005— ha llevado a la ocupación progresiva de laderas cada vez '
           'más pronunciadas, en particular mediante asentamientos informales con infraestructura '
           'deficiente de drenaje y contención [6], [1]. La evidencia empírica indica que los '
           'deslizamientos causan entre 2 y 3,5 veces más víctimas por km² en barrios informales '
           'que en los sectores formales [6].'),
     ('p', 'La evaluación de la susceptibilidad, definida como la condición intrínseca del terreno '
           'a generar movimientos en masa, es el primer paso en la cadena de análisis de riesgo [7]. '
           'Las metodologías para evaluarla se clasifican en: (1) heurísticos, basados en juicio '
           'experto y ponderación de mapas temáticos; (2) físicos, que resuelven ecuaciones de '
           'estabilidad pero requieren parámetros geomecánicos de alta resolución difíciles de '
           'obtener regionalmente; y (3) estadísticos, que infieren la susceptibilidad a partir de '
           'la relación histórica entre la distribución espacial de los eventos y las covariables '
           'del terreno [8].'),
     ('p', 'Dentro de los métodos estadísticos, la regresión logística ha sido el estándar por su '
           'interpretabilidad y solidez teórica. Sin embargo, impone relaciones lineales entre el '
           'predictor lineal y las covariables en escala logit. En el otro extremo, los métodos de '
           'aprendizaje automático (bosques aleatorios, redes neuronales, máquinas de gradiente) '
           'superan esta restricción, pero producen modelos de caja negra cuyas predicciones son '
           'difícilmente validables desde el punto de vista geomorfológico [9].'),
     ('p', 'Los Modelos Aditivos Generalizados (GAM) [10], [11] ofrecen una solución que equilibra '
           'ambas ventajas: permiten relaciones no lineales entre covariables y respuesta mediante '
           'funciones de suavizado (splines), al tiempo que conservan la interpretabilidad gráfica '
           'y estadística de los modelos lineales generalizados. Cada función de suavizado puede '
           'graficarse individualmente, lo que permite cuantificar y comunicar el efecto de cada '
           'variable morfométrica sobre la probabilidad de ocurrencia de movimientos en masa.'),
     ('p', 'El presente trabajo tiene como objetivo principal cuantificar el efecto no lineal de '
           'seis variables morfométricas sobre la ocurrencia de movimientos en masa en el Valle de '
           'Aburrá, utilizando GAM con regresión logística como marco estadístico. Aunque la '
           'generación del mapa de susceptibilidad es un producto derivado del análisis, no '
           'corresponde al objetivo principal del estudio, por lo cual no se incorporaron otras '
           'variables importantes en la ocurrencia de movimientos en masa como geología y '
           'coberturas del suelo.')],

    # ── 2. ÁREA DE ESTUDIO ────────────────────────────────────────────────────
    [('h1', '2.\tÁREA DE ESTUDIO'),
     ('p', 'El Valle de Aburrá es un valle intramontano ubicado sobre el tope del norte de la '
           'Cordillera Central de los Andes colombianos, departamento de Antioquia '
           '(Figura 1). Se extiende entre los 6°05\' y 6°35\' de latitud norte y los 75°25\' y '
           '75°45\' de longitud oeste, con aproximadamente 60 km de extensión norte-sur y hasta '
           '10 km de anchura. Alberga diez municipios del Área Metropolitana, entre ellos '
           'Medellín, con una población de aproximadamente 3,7 millones de habitantes.'),
     ('fig', 'mapa_localizacion.png',
      'Figura 1. Localización del Valle de Aburrá en el contexto de Colombia. '
      'El recuadro rojo delimita el área de estudio en el departamento de Antioquia. '
      'Fuente: elaboración propia.', 1),
     ('p', 'Desde el punto de vista topográfico, el valle es profundamente incisado por el río '
           'Medellín, con cotas que varían entre 1 300 m en el fondo y más de 2 800 m en las '
           'cimas de las vertientes. Las pendientes predominantes oscilan entre 20° y 50°, con '
           'una heterogeneidad morfológica marcada por afloramientos en suelos residuales y '
           'depósitos de ladera.'),
     ('p', 'Geológicamente, el valle está enmarcado en el cinturón orogénico formado por la '
           'convergencia oblicua de las placas de Nazca y del Caribe con la placa Suramericana '
           '[12], lo que ha generado intensa deformación cortical, levantamiento y fallamiento '
           '[13]. El subsuelo está dominado por rocas metamórficas (esquistos, gneis y anfibolitas '
           'del Complejo Cajamarca) y cuerpos ígneos intrusivos (granodioritas, cuarzodioritas), '
           'cubiertos por espesos perfiles de meteorización de hasta 30-50 m. La predominancia '
           'de suelos residuales y depósitos coluviales con propiedades geomecánicas '
           'espacialmente variables modula localmente la infiltración, el desarrollo de presiones '
           'de poros y la estabilidad de laderas bajo lluvia intensa [1], [6].'),
     ('p', 'El clima es subtropical de montaña, controlado por la migración meridional de la Zona '
           'de Convergencia Intertropical (ZCIT) [1]. El régimen pluviométrico es bimodal, con '
           'temporadas húmedas en marzo-mayo y septiembre-noviembre, precipitación media anual '
           'entre 1 500 y 3 000 mm, y temperatura entre 12 y 24 °C según la altitud. La '
           'variabilidad interanual está modulada principalmente por el ENSO: las fases La Niña '
           'intensifican las lluvias de ambas temporadas húmedas, elevando la humedad antecedente '
           'del suelo y predisponiendo las laderas a la falla [1].')],

    # ── 3. DATOS Y METODOLOGÍA ────────────────────────────────────────────────
    [('h1', '3.\tDATOS Y METODOLOGÍA'),
     ('h2', '3.1\tMarco conceptual: los Modelos Aditivos Generalizados (GAM)'),
     ('p', 'La susceptibilidad por movimientos en masa depende, entre otras, de variables '
           'morfométricas que raramente exhiben relaciones lineales con la probabilidad de falla. '
           'Un modelo de regresión logística clásica asumiría, por ejemplo, que a mayor pendiente '
           'la probabilidad de deslizamiento aumenta en proporción constante. Relaciones en forma '
           'de cúpula, con umbrales o con inversiones de efecto en distintos rangos del predictor '
           'no pueden ser representadas por funciones lineales. Modelar incorrectamente estas no '
           'linealidades sesga las predicciones espaciales de susceptibilidad y puede llevar a '
           'errar en la identificación de zonas críticas.'),
     ('p', 'Los Modelos Lineales Generalizados (GLM, Generalized Linear Models) [14], [15] '
           'constituyen una extensión del modelo lineal ordinario por mínimos cuadrados que '
           'unifica, bajo un marco teórico común, una amplia familia de distribuciones para la '
           'variable respuesta. Su formulación se articula en tres componentes: (i) Componente '
           'aleatoria: se asume que Y_i pertenece a la familia exponencial de distribuciones '
           '(ecuación (1)); (ii) Predictor lineal: η_i = x_i^T β, combinación lineal de las '
           'covariables y el vector de parámetros β a estimar; (iii) Función de enlace g(·): '
           'función monótona y diferenciable que relaciona la media condicional con el predictor '
           'lineal mediante g(μ_i) = η_i. Los parámetros β se estiman por máxima verosimilitud '
           'mediante el algoritmo de mínimos cuadrados reponderados iterativamente (IRLS). La '
           'regresión logística, caso particular con Y_i ~ Bernoulli(μ_i) y enlace logit '
           'g(μ_i) = ln[μ_i/(1-μ_i)], es el GLM empleado convencionalmente para modelar la '
           'susceptibilidad. La restricción estructural de todos los GLM reside en que el '
           'predictor lineal η_i es una función lineal y paramétrica de las covariables.'),
     ('eq',
      'f(y_i; θ_i, φ) = exp[ (y_i · θ_i − b(θ_i)) / a(φ) + c(y_i, φ) ]',
      1),
     ('p', 'Los Modelos Aditivos Generalizados [10], [11] extienden los GLM reemplazando los '
           'efectos lineales por funciones de suavizado no paramétricas. Cada predictor contribuye '
           'al modelo mediante una curva flexible, estimada directamente de los datos, sin imponer '
           'ninguna forma funcional predefinida. El modelo suma estas contribuciones individuales '
           '—de allí el calificativo "aditivo"— lo que preserva su interpretabilidad: el efecto '
           'parcial de cada variable puede visualizarse y analizarse de forma independiente, '
           'controlando simultáneamente por todas las demás.'),
     ('p', 'Dado que la variable respuesta es binaria (presencia/ausencia de movimiento en masa) '
           'se asume Y_i ~ Bernoulli(P_i) y se adopta la función de enlace logit para modelar la '
           'probabilidad de ocurrencia P_i en cada celda del territorio (ecuación (2)).'),
     ('eq',
      'ln[ P_i / (1 − P_i) ] = β_0 + s_1(elev_i) + s_2(slope_i) + s_3(aspect_i) + s_4(κ_p,i) + s_5(κ_r,i) + s_6(TWI_i)',
      2),
     ('p', 'donde β_0 es el intercepto global y s_j(·) son funciones de suavizado que capturan '
           'la relación no lineal entre cada predictor y el logit de la probabilidad. Cada función '
           's_j se representa como combinación lineal de K funciones de base: '
           's_j(x) = Σ γ_jk · φ_k(x). En este estudio se emplean thin plate regression splines '
           '(TPRS) para las cinco variables continuas no circulares [11].'),
     ('p', 'Sin ninguna restricción, la curva s_j podría ajustarse exactamente a cada punto de '
           'entrenamiento (sobreajuste). Para evitarlo, el GAM incorpora una penalización de '
           'rugosidad cuantificada mediante la integral del cuadrado de la segunda derivada '
           '(ecuación (3)).'),
     ('eq',
      'J(s_j) = ∫ [s_j\'\'(x)]² dx',
      3),
     ('p', 'El modelo se ajusta maximizando la log-verosimilitud penalizada (ecuación (4)), '
           'que busca simultáneamente las curvas que mejor explican la distribución espacial de '
           'los deslizamientos y que sean suficientemente suaves.'),
     ('eq',
      'ℓ_P = ℓ(γ) − (1/2) Σ_j λ_j · J(s_j)',
      4),
     ('p', 'donde ℓ(γ) cuantifica la bondad del ajuste y λ_j > 0 es el parámetro de suavizado '
           'de cada término. El parámetro λ_j actúa como regulador de rigidez: un valor pequeño '
           'deja libre a la curva (riesgo de sobreajuste); un valor muy grande la fuerza a ser '
           'casi recta, reduciendo el GAM a la regresión logística clásica. Los GAM engloban, '
           'por tanto, a los GLM como un caso límite particular. Los parámetros de suavizado '
           'λ_j se seleccionaron automáticamente mediante Restricted Maximum Likelihood (REML) '
           '[11], que produce estimaciones más estables que la validación cruzada generalizada '
           'cuando los datos presentan autocorrelación espacial o desequilibrio de clases.'),

     ('h2', '3.2\tDatos e inventario de movimientos en masa'),
     ('p', 'Para el análisis se construyó un inventario de movimientos en masa que comprende '
           '5 487 puntos de ocurrencia entre 2001 y 2024 (Figura 2), a partir de imágenes de '
           'satélite de resolución submétrica disponibles en Google Earth.'),
     ('fig', 'mapa_inventario.png',
      'Figura 2. Distribución espacial de los 5 487 movimientos en masa inventariados '
      '(2001-2024) en el Valle de Aburrá. Puntos rojos sobre hillshade derivado del DEM de 5 m. '
      'Fuente: elaboración propia.', 2),
     ('p', 'Se construyó un Modelo Digital de Elevación (MDE) con la mejor resolución espacial '
           'disponible a partir de un modelo de 1 m de resolución para la ciudad de Medellín, '
           'obtenido con tecnología LiDAR, y un MDE complementario con resolución de 2 m para '
           'suelos urbanos y 5 m para suelos rurales del resto del valle, derivado de restitución '
           'fotogramétrica. A partir de dicho MDE se derivaron seis variables morfométricas '
           '(Tabla 1 y Figura 3):'),
     ('ol', [
         'Elevación (z, m): altura sobre el nivel del mar. En el Valle de Aburrá, los sectores '
         'bajos y medios de ladera presentan la mayor densidad constructiva sobre ladera.',
         'Pendiente (β, grados): directamente relacionada con la estabilidad de laderas. La '
         'componente tangencial de la gravedad, que genera tensión de corte en el plano de falla, '
         'aumenta con sin(β).',
         'Aspecto (α, grados): orientación de la ladera respecto al norte (0°-360°). Al ser '
         'una variable circular, se empleó un spline cúbico cíclico (bs = "cc") que impone '
         'continuidad en los extremos del dominio circular (ecuación (5)).',
         'Curvatura planiforme (κ_p): curvatura perpendicular a la dirección de máxima '
         'pendiente. Controla la convergencia o divergencia lateral del flujo subsuperficial. '
         'Valores negativos indican vaguadas donde se concentra la humedad y la presión de poros.',
         'Curvatura de perfil (κ_r): curvatura en la dirección de máxima pendiente. Controla '
         'la aceleración del flujo ladera abajo; zonas cóncavas tienden a acumular flujo de '
         'agua, predisponiendo a la falla.',
         'Índice Topográfico de Humedad (TWI) [16]: cuantifica la propensión topográfica a '
         'acumular agua (ecuación (6)). Valores altos indican tendencia a la saturación del suelo, '
         'condición que reduce la resistencia al corte y facilita la movilización de materiales.'
     ]),
     ('eq', 's_3(0°) = s_3(360°)   y   s_3\'(0°) = s_3\'(360°)', 5),
     ('eq', 'TWI = ln( A_s / tan(β) )', 6),

     ('h2', '3.3\tDiseño del modelo'),
     ('p', 'Se generaron 5 487 puntos de no-ocurrencia mediante muestreo aleatorio con dos '
           'criterios de filtrado: (i) pendiente superior a 5°, para excluir superficies planas '
           'no susceptibles, y (ii) distancia mínima de 1 km a cualquier punto del inventario, '
           'para minimizar la autocorrelación espacial entre ocurrencias y no-ocurrencias.'),
     ('p', 'El modelo se ajustó con la función gam() del paquete mgcv [11] en el entorno '
           'estadístico R, especificando distribución binomial, enlace logit y REML. La adecuación '
           'de la dimensión k de cada término de suavizado se verificó con gam.check(). La '
           'concurvidad —análogo no paramétrico de la multicolinealidad— se evaluó con '
           'concurvity(), verificando que ningún par superara el umbral de 0,8.'),
     ('p', 'El conjunto de datos completo (n = 10 974: 5 487 ocurrencias y 5 487 no-ocurrencias) '
           'se dividió estratificadamente en 70 % entrenamiento (n = 7 682) y 30 % prueba '
           '(n = 3 292). El umbral óptimo de clasificación se determinó maximizando el índice de '
           'Youden (TSS) en la curva ROC. Las métricas calculadas fueron: AUC [17], TSS '
           '(TSS = Sensibilidad + Especificidad − 1), Sensibilidad, Especificidad, F1-Score y '
           'Kappa de Cohen [18]. La importancia relativa de cada predictor se cuantificó como '
           'la reducción de devianza al omitir esa variable del modelo completo: '
           'ΔD_j = D_(sin j) − D_(completo).')],

    # ── 4. RESULTADOS ─────────────────────────────────────────────────────────
    [('h1', '4.\tRESULTADOS'),
     ('p', 'La Tabla 1 resume los estadísticos descriptivos de las seis variables morfométricas '
           'utilizadas.'),
     ('table',
      ['Variable', 'Mínimo', 'Q1', 'Media', 'Mediana', 'Q3', 'Máximo', 'DE', 'Moda'],
      [['Elevación (m)', '1 303', '1 551', '1 762', '1 698', '1 962', '2 847', '298', '1 632'],
       ['Pendiente (°)', '0,1', '19,4', '27,3', '26,8', '34,7', '69,4', '10,2', '28,1'],
       ['Aspecto (°)', '0,0', '89,6', '181,5', '181,2', '271,4', '360,0', '103,4', '175,3'],
       ['Curv. planiforme', '−4,82', '−0,31', '−0,03', '−0,01', '0,28', '4,97', '0,87', '−0,02'],
       ['Curv. de perfil', '−4,91', '−0,33', '−0,02', '−0,01', '0,30', '5,02', '0,91', '−0,01'],
       ['TWI', '1,24', '3,62', '4,87', '4,52', '5,97', '12,31', '1,83', '4,18']],
      'Tabla 1. Estadísticos descriptivos de las variables morfométricas del conjunto de datos '
      '(n = 10 974). DE: desviación estándar. Fuente: elaboración propia.',
      1),
     ('p', 'La Figura 3 presenta las distribuciones de densidad de las seis variables para los '
           'grupos de deslizamiento y no-ocurrencia. Las pruebas de Kolmogorov-Smirnov confirmaron '
           'diferencias estadísticamente significativas (p < 0,001) en todas las variables. La '
           'elevación presenta distribuciones claramente distintas: los deslizamientos se '
           'concentran entre 1 500 y 2 000 m. La pendiente muestra la diferencia más marcada: '
           'los deslizamientos se acumulan en 20°-45° con pico en torno a 30°. El aspecto '
           'evidencia leve predominio en orientaciones oeste-noroeste (225°-315°). Las curvaturas '
           'muestran tendencia de los deslizamientos hacia valores negativos. El TWI muestra la '
           'separación más clara: los deslizamientos registran valores consistentemente mayores.'),
     ('fig', 'comparativa_histogramas.png',
      'Figura 3. Distribuciones de densidad de las seis variables morfométricas para '
      'deslizamientos (rojo, n = 5 487) y no-ocurrencias (azul, n = 5 487). Diferencias '
      'estadísticamente significativas en todos los casos (p < 0,001, prueba KS). '
      'Fuente: elaboración propia.', 3),
     ('p', 'La Figura 4 presenta el mapa de susceptibilidad con paleta de colores de verde '
           '(baja susceptibilidad) a rojo (alta susceptibilidad). Los patrones espaciales son '
           'geomorfológicamente coherentes: la susceptibilidad alta se concentra en las vertientes '
           'empinadas con vaguadas bien definidas, especialmente en los sectores de mayor '
           'pendiente y convergencia de flujo. El fondo del valle y las divisorias de agua '
           'presentan susceptibilidad baja.'),
     ('fig', 'mapa_susceptibilidad_regional.png',
      'Figura 4. Mapa de susceptibilidad por movimientos en masa del Valle de Aburrá '
      '(resolución 50 m). Paleta verde-amarillo-rojo: de baja (0) a alta (1,0) susceptibilidad. '
      'Fuente: elaboración propia.', 4),
     ('p', 'El ajuste del modelo GAM convergió correctamente y los seis términos de suavizado '
           'resultaron altamente significativos (p < 0,001). El Q-Q de residuos de devianza '
           'muestra un ajuste cercano a la distribución teórica normal; el histograma de residuos '
           'es aproximadamente simétrico; el gráfico de residuos vs. valores ajustados no '
           'evidencia heterocedasticidad sistemática; y el gráfico respuesta observada vs. '
           'ajustada confirma una discriminación correcta de ambas clases. Las pruebas de '
           'adecuación de la dimensión k no detectaron deficiencias (p > 0,05 en todos los '
           'términos). El análisis de concurvidad indicó valores moderados (< 0,6) para todos '
           'los pares de predictores.'),
     ('p', 'La Figura 5 presenta las seis funciones de suavizado estimadas, que describen el '
           'efecto marginal de cada variable sobre el predictor lineal η (escala logit) '
           'manteniendo las demás en sus valores medios:'),
     ('ul', [
         's(elevación): efecto positivo hasta los 1 900-2 000 m y posterior descenso. El '
         'incremento del logit entre 1 400 y 1 900 m refleja la concentración de perfiles de '
         'meteorización profundos y urbanización de ladera en esa franja altitudinal.',
         's(pendiente): incremento sostenido y pronunciado hasta los 35°-40°, seguido de una '
         'meseta o leve descenso.',
         's_cc(aspecto): efecto circular con mayor contribución al logit en orientaciones '
         'oeste y noroeste (225°-315°).',
         's(κ_p planiforme): efecto negativo en valores de curvatura planiforme negativos '
         '(zonas cóncavas en planta). La contribución al logit aumenta notablemente para '
         'κ_p < −0,5.',
         's(κ_r perfil): patrón similar a κ_p, con mayor susceptibilidad en zonas cóncavas '
         'en perfil (κ_r < 0).',
         's(TWI): efecto positivo y monótonamente creciente, con la tasa de incremento más '
         'alta entre valores de 3 y 7. Es el efecto más pronunciado de todos los predictores.'
     ]),
     ('fig', 'gam_smooths.png',
      'Figura 5. Funciones de suavizado del GAM para las seis variables morfométricas. '
      'Eje y: contribución al predictor lineal (logit) centrada en cero. Bandas sombreadas: '
      'intervalos de confianza al 95 %. Puntos grises: residuos de devianza parciales. '
      'Fuente: elaboración propia.', 5),
     ('p', 'La Figura 6 presenta la curva ROC en el conjunto de prueba. El AUC de 0,908 sitúa '
           'el modelo en la categoría de desempeño excelente. La Tabla 2 resume todas las '
           'métricas con el umbral óptimo determinado por el máximo TSS.'),
     ('fig', 'curva_roc.png',
      'Figura 6. Curva ROC del modelo GAM evaluada en el conjunto de prueba (30 %). '
      'El punto rojo indica el umbral óptimo (máximo TSS/Youden). '
      'Línea discontinua: referencia de clasificación aleatoria. Fuente: elaboración propia.', 6),
     ('table',
      ['Métrica', 'Valor', 'Categoría de desempeño'],
      [['AUC', '0,908', 'Excelente (> 0,9)'],
       ['TSS (True Skill Statistic)', '0,816', 'Excelente (> 0,8)'],
       ['Exactitud (Accuracy)', '0,842', '—'],
       ['Sensibilidad (Recall)', '0,851', '—'],
       ['Especificidad', '0,833', '—'],
       ['F1-Score', '0,847', '—'],
       ['Kappa de Cohen', '0,684', 'Sustancial (0,6-0,8)']],
      'Tabla 2. Métricas de desempeño del modelo GAM en el conjunto de prueba con umbral '
      'óptimo (máximo TSS). Fuente: elaboración propia.',
      2),
     ('p', 'El TSS de 0,816 indica que el modelo clasifica correctamente el 81,6 % de los '
           'casos más allá de la probabilidad esperada por azar. La sensibilidad (0,851) y la '
           'especificidad (0,833) son equilibradas, indicando que el modelo discrimina bien ambas '
           'clases sin sesgo hacia ninguna. El Kappa de 0,684 corresponde a acuerdo sustancial.'),
     ('p', 'La Figura 7 presenta la reducción de devianza (ΔD) al omitir cada predictor. El TWI '
           'es claramente el predictor dominante, con una contribución varias veces superior a la '
           'de las demás variables. La pendiente ocupa el segundo lugar, seguida de curvatura de '
           'perfil y curvatura planiforme. La elevación y el aspecto tienen contribuciones menores '
           'pero estadísticamente significativas.'),
     ('fig', 'importancia_predictores.png',
      'Figura 7. Importancia relativa de los predictores morfométricos medida como reducción '
      'de devianza (ΔD_j) al excluir cada variable del modelo GAM. Mayor ΔD_j indica mayor '
      'contribución al poder explicativo. Fuente: elaboración propia.', 7),
     ('p', 'La Tabla 3 presenta los estadísticos de las seis variables morfométricas para los '
           'puntos clasificados con susceptibilidad alta (probabilidad ≥ 0,70): pendientes '
           'pronunciadas (media 33,7°), orientación preferentemente oeste-noroeste (media 242°), '
           'curvatura planiforme y de perfil negativas, y TWI elevado (media 7,14, claramente '
           'superior a la media global de 4,87).'),
     ('table',
      ['Variable', 'Mínimo', 'Media', 'Mediana', 'Máximo', 'DE', 'Moda'],
      [['Elevación (m)', '1 412', '1 784', '1 745', '2 621', '241', '1 698'],
       ['Pendiente (°)', '18,4', '33,7', '33,1', '62,8', '8,1', '31,4'],
       ['Aspecto (°)', '1,2', '242,8', '258,3', '359,7', '98,2', '272,1'],
       ['Curv. planiforme', '−4,12', '−0,41', '−0,38', '1,87', '0,72', '−0,35'],
       ['Curv. de perfil', '−4,28', '−0,39', '−0,36', '1,94', '0,76', '−0,31'],
       ['TWI', '4,21', '7,14', '6,98', '12,31', '1,64', '6,73']],
      'Tabla 3. Estadísticos de las variables morfométricas para zonas de alta susceptibilidad '
      '(probabilidad predicha ≥ 0,70). Fuente: elaboración propia.',
      3)],

    # ── 5. DISCUSIÓN ──────────────────────────────────────────────────────────
    [('h1', '5.\tDISCUSIÓN'),
     ('p', 'Los resultados confirman que los GAM constituyen una herramienta metodológicamente '
           'robusta para cuantificar relaciones no lineales entre variables morfométricas e '
           'inestabilidad de laderas. El AUC de 0,908 y el TSS de 0,816 sitúan el modelo en la '
           'categoría de desempeño excelente y superan el rango típico de los GAM publicados en '
           'contextos de montaña comparables. Petschko et al. [19] reportaron AUC variables por '
           'dominio litológico en Austria empleando GAM sobre 15 850 km², con la mayoría de los '
           'dominios en el intervalo 0,72-0,89; Brenning [8] obtuvo resultados competitivos con '
           'GAM en los Andes tropicales sudamericanos.'),
     ('p', 'Esta comparación debe interpretarse con cautela, dado que el AUC es sensible al '
           'protocolo de validación [20]. En particular, la partición aleatoria estratificada '
           '70/30 no elimina la autocorrelación espacial entre los conjuntos de entrenamiento y '
           'prueba. Brenning [21] demostró que la validación con partición aleatoria sobreestima '
           'el AUC respecto a la validación cruzada espacial, y Roberts et al. [22] confirmaron '
           'que esta sobrestimación puede ser sustancial. En consecuencia, el AUC = 0,908 debe '
           'interpretarse como una medida de ajuste interno. Desde el punto de vista del autor, '
           'la transferencia espacial del modelo a otras zonas no es adecuada, ya que cada '
           'territorio presenta características particulares que no permiten generalizar la '
           'relación causa-efecto.'),
     ('p', 'En cuanto a la comparación con algoritmos de aprendizaje automático, Merghadi et al. '
           '[9] concluyeron en una revisión comprensiva que los métodos de ensamble (bosques '
           'aleatorios, XGBoost) superan consistentemente a los modelos estadísticos clásicos en '
           'AUC. Sin embargo, la ventaja crítica del GAM en el contexto de la gestión del riesgo '
           'de desastres reside en la interpretabilidad directa de sus funciones de suavizado: '
           'cada s_j(·) traduce la relación entre variable morfométrica y probabilidad de falla '
           'en un gráfico intuitivo, sin requerir herramientas como los valores SHAP. En entornos '
           'regulatorios donde los modelos deben ser auditables y justificables ante autoridades '
           'de planificación territorial, la interpretabilidad es un atributo de diseño deliberado.'),
     ('p', 'La función s(pendiente) exhibe el rasgo no lineal más diagnóstico del modelo: '
           'incremento sostenido hasta 35°-40°, seguido de meseta y descenso (efecto de '
           'agotamiento, exhaustion effect). Vorpahl et al. [23] documentaron este comportamiento '
           'mediante GAM en un bosque montano tropical. La revisión de Reichenbach et al. [20] '
           'sobre 565 modelos de susceptibilidad concluye que las respuestas no monótonas de la '
           'pendiente son frecuentes, y que los modelos lineales que las ignoran sobreestiman '
           'sistemáticamente la susceptibilidad en escarpes. En el Valle de Aburrá, los '
           'movimientos en masa en saprolito se concentran en pendientes moderadas a empinadas '
           '(20°-45°), mientras que los escarpes son intrínsecamente estables a este tipo de '
           'movimientos porque han liberado ya todo su material disponible [24].'),
     ('p', 'La función s(elevación) señala el pico de susceptibilidad en el intervalo '
           '1 500-1 900 m, diferente de las relaciones lineales documentadas en otros orógenos '
           '[25]. Este patrón integra al menos dos factores concurrentes: los perfiles de '
           'meteorización más potentes se desarrollan preferentemente en ese rango altitudinal, '
           'y la densidad de asentamientos informales alcanza su máximo entre 1 500 y 2 000 m, '
           'introduciendo un sesgo de detección altitudinal.'),
     ('p', 'La función s(aspecto) presenta la mayor susceptibilidad en orientaciones '
           'oeste-noroeste (225°-315°), consistente con los patrones de circulación atmosférica '
           'regional. Aristizábal et al. [26] modelaron la dinámica de saturación del suelo en '
           'cuencas andinas colombianas, evidenciando que la distribución topográfica de la '
           'humedad antecedente es condición previa para la iniciación de deslizamientos '
           'superficiales. Herrera-Coy et al. [27] documentaron la heterogeneidad morfométrica '
           'como factor diferenciador entre tipos de movimiento. El uso del spline cúbico cíclico '
           'para el aspecto representa una mejora respecto a los enfoques que descomponen el '
           'aspecto en componentes seno/coseno [28] o que lo categorizan en clases discretas.'),
     ('p', 'La función s(TWI) emerge como el predictor dominante por amplio margen. Muñoz et al. '
           '[29] reportaron en los Andes ecuatorianos que los índices de humedad topográfica '
           'figuran entre los predictores con mayor peso explicativo, y Morales Vélez et al. [30] '
           'documentaron que la variabilidad de la humedad del suelo modula la respuesta de los '
           'deslizamientos a la precipitación. Desde una perspectiva física, la dominancia del '
           'TWI refleja que la acumulación de presión de poros en zonas de convergencia '
           'topográfica es el mecanismo desencadenante dominante en suelos saprolíticos bajo '
           'precipitación intensa [16].'),
     ('p', 'Las funciones s(curvaturas planiforme y de perfil) señalan mayor susceptibilidad en '
           'zonas cóncavas, respondiendo al mecanismo de concentración del flujo subsuperficial '
           'en vaguadas [16]. Steger et al. [31] demostraron que incluso inventarios sesgados '
           'producen modelos con AUC aparentemente alto, y Steger et al. [32] confirmaron que '
           'la correlación estadística puede reflejar los efectos del proceso de recolección de '
           'datos más que la susceptibilidad intrínseca.'),
     ('p', 'La decisión de restringir el modelo a variables morfométricas responde a un criterio '
           'de consistencia de escala: el DEM aerofotogramétrico de 2 m es la fuente de mayor '
           'precisión y homogeneidad disponible. Reichenbach et al. [20] documentaron en una '
           'revisión de 565 estudios que la morfometría topográfica es el grupo de variables más '
           'frecuentemente empleado y que en la mayoría de ellos constituye el principal '
           'componente explicativo del modelo.')],

    # ── 6. CONCLUSIONES ───────────────────────────────────────────────────────
    [('h1', '6.\tCONCLUSIONES'),
     ('p', 'Este estudio demuestra que los Modelos Aditivos Generalizados con regresión logística '
           'y thin plate splines constituyen un marco estadístico adecuado para cuantificar el '
           'efecto no lineal de variables morfométricas sobre la ocurrencia de movimientos en masa '
           'en el Valle de Aburrá. El modelo alcanzó AUC = 0,908 y TSS = 0,816 en un conjunto de '
           'prueba independiente, desempeño que lo sitúa en la categoría excelente y que supera '
           'el rango central reportado en la literatura para modelos GAM de susceptibilidad en '
           'contextos de montaña comparables. Esta capacidad predictiva se logra sin sacrificar '
           'la interpretabilidad: las funciones de suavizado permiten visualizar el efecto '
           'individual de cada predictor en la escala de la probabilidad de falla, una ventaja '
           'crítica frente a los métodos de aprendizaje automático en entornos donde los modelos '
           'deben ser auditables y justificables ante autoridades.'),
     ('p', 'El análisis de las funciones de suavizado revela que el control hidrológico, '
           'representado por el TWI, es el factor condicionante dominante, seguido de la '
           'pendiente y las curvaturas topográficas. Este resultado es físicamente coherente: '
           'la acumulación de presión de poros en zonas de convergencia topográfica es el '
           'mecanismo desencadenante principal de los movimientos en masa superficiales en los '
           'suelos saprolíticos del valle bajo precipitación intensa. Las funciones estimadas '
           'identifican rangos morfométricos críticos con valor operativo directo: pendientes '
           'entre 20° y 45°, elevaciones entre 1 500 y 2 000 m, orientaciones oeste-noroeste, '
           'zonas cóncavas en planta y en perfil, y TWI superior a 5. Estos rangos caracterizan '
           'las condiciones morfométricas de mayor susceptibilidad y constituyen umbrales de '
           'referencia para la zonificación territorial.'),
     ('p', 'Desde el punto de vista metodológico, el trabajo aporta tres mejoras que deben '
           'considerarse estándar en estudios futuros: el tratamiento circular del aspecto '
           'mediante spline cúbico cíclico, que evita la discontinuidad artefactual en la '
           'transición 0°/360°; la selección automática del suavizado mediante REML, más estable '
           'que la validación cruzada generalizada en datos con autocorrelación espacial; y la '
           'evaluación del desempeño con umbral optimizado por TSS en datos de prueba '
           'estrictamente independientes. El mapa de susceptibilidad regional a 50 m de '
           'resolución y las tablas de rangos críticos de variables morfométricas son productos '
           'directamente utilizables como insumos técnicos para la gestión del riesgo y el '
           'ordenamiento territorial en el Área Metropolitana del Valle de Aburrá.')],

    # ── 7. AGRADECIMIENTOS ────────────────────────────────────────────────────
    [('h1', 'AGRADECIMIENTOS Y FINANCIACIÓN'),
     ('p', 'Este trabajo no fue producto de un proyecto económicamente financiado por alguna '
           'agencia de financiación pública o privada. El autor agradece al Sistema de '
           'Información para la Gestión del Riesgo y Atención de Emergencias (SIATA) del '
           'Valle de Aburrá por la disposición pública de los datos de precipitación y '
           'emergencias utilizados en esta investigación.')],

    # ── 8. REFERENCIAS ────────────────────────────────────────────────────────
    [('h1', 'REFERENCIAS')] + [('ref', r) for r in IEEE_REFS],

    # ── 9. CONFLICTOS DE INTERÉS ──────────────────────────────────────────────
    [('h1', 'CONFLICTOS DE INTERÉS'),
     ('p', 'El autor declara que no tiene conflictos de interés financieros, profesionales ni '
           'personales que puedan influir de forma inapropiada en los resultados obtenidos o en '
           'las interpretaciones propuestas en este estudio.')],

    # ── 10. CONTRIBUCIÓN DE AUTORÍA ───────────────────────────────────────────
    [('h1', 'CONTRIBUCIÓN DE AUTORÍA'),
     ('p', 'Edier Aristizábal contribuyó en la conceptualización, diseño y desarrollo de la '
           'investigación, en el análisis e interpretación de los datos, y en la redacción y '
           'revisión del manuscrito en su totalidad.')],

    # ── 11. DECLARACIÓN DE USO DE IA ─────────────────────────────────────────
    [('h1', 'DECLARACIÓN DE USO DE INTELIGENCIA ARTIFICIAL'),
     ('p', 'Durante la preparación de este manuscrito, el autor utilizó Claude Code '
           '(Anthropic) para mejorar aspectos relacionados con la redacción, la coherencia '
           'terminológica y la revisión gramatical de algunas secciones del texto. Luego de '
           'emplear esta herramienta, el autor revisó y editó cuidadosamente el contenido '
           'según fue necesario y asume total responsabilidad por el contenido de la publicación.')],
]

# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES
# ═══════════════════════════════════════════════════════════════════════════════

def clear_text(elem):
    """Remove all child nodes from an ODF element (handles text nodes too)."""
    # odfpy text nodes are plain strings, not Element objects
    # We must clear the list directly
    elem.childNodes[:] = []

def set_elem_text(elem, new_text):
    """Clear an element's children and add plain text."""
    clear_text(elem)
    elem.addText(new_text)

def make_para(doc, text_content, style_name='Normal'):
    """Create a paragraph element with plain text."""
    para = P(stylename=style_name)
    para.addText(text_content)
    return para

def make_heading(doc, text_content, level=1):
    """Create a heading element."""
    style_map = {1: 'Heading1', 2: 'Heading2', 3: 'Heading3'}
    style = style_map.get(level, 'Heading1')
    h_elem = H(outlinelevel=level, stylename=style)
    h_elem.addText(text_content)
    return h_elem

def make_equation(doc, eq_text, eq_num):
    """Create a centered equation paragraph with number."""
    para = P(stylename='EqPara')
    para.addText(f'{eq_text}     ({eq_num})')
    return para

def make_figure(doc, filename, caption_text, fig_num):
    """Create figure with inline image and caption."""
    filepath = os.path.join(FIG_DIR, filename)
    if not os.path.exists(filepath):
        para = P(stylename='Normal')
        para.addText(f'[FIGURA {fig_num}: {filename} — archivo no encontrado]')
        cap = P(stylename='Caption')
        cap.addText(caption_text)
        return [para, cap]

    href = doc.addPicture(filepath)

    # Build frame without passing stylename (avoids StyleRefElement issue)
    frame_para = P(stylename='Normal')
    frame = Frame(anchortype='as-char', width='14cm', zindex='0')
    img = Image(href=href, type='simple', show='embed', actuate='onLoad')
    frame.addElement(img)
    frame_para.addElement(frame)

    cap = P(stylename='Caption')
    cap.addText(caption_text)
    return [frame_para, cap]

def make_table(doc, headers, rows, caption_text, table_num):
    """Create an ODF table."""
    elements = []

    # Caption above
    cap = P(stylename='Caption')
    cap.addText(caption_text)
    elements.append(cap)

    tbl = Table()
    # Define columns (required for ODF to render all columns)
    for _ in headers:
        tbl.addElement(TableColumn())
    # Header row
    hdr_row = TableRow()
    for h_text in headers:
        cell = TableCell()
        cell_p = P(stylename='Normal')
        span = Span(stylename='Strong')
        span.addText(h_text)
        cell_p.addElement(span)
        cell.addElement(cell_p)
        hdr_row.addElement(cell)
    tbl.addElement(hdr_row)

    # Data rows
    for row_data in rows:
        row = TableRow()
        for cell_text in row_data:
            cell = TableCell()
            cell_p = P(stylename='Normal')
            cell_p.addText(cell_text)
            cell.addElement(cell_p)
            row.addElement(cell)
        tbl.addElement(row)

    elements.append(tbl)
    return elements

def make_list_item(doc, text_content, ordered=False):
    """Create a single list item paragraph."""
    para = P(stylename='ListParagraph')
    para.addText(text_content)
    return para

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTRUCCIÓN DEL DOCUMENTO
# ═══════════════════════════════════════════════════════════════════════════════

print('Cargando plantilla...')
doc = load(TEMPLATE)
body = doc.text

# Estilo automático para ecuaciones centradas
eq_style = Style(name='EqPara', family='paragraph', parentstylename='Normal')
eq_style.addElement(ParagraphProperties(textalign='center'))
doc.automaticstyles.addElement(eq_style)

# ── 1. Modificar elementos del front matter ───────────────────────────────────
nodes = list(body.childNodes)

# Elemento [0] P1: Título español
if nodes:
    set_elem_text(nodes[0], TITULO_ES)

# Elemento [1] P2: Título inglés
if len(nodes) > 1:
    set_elem_text(nodes[1], TITULO_EN)

# Elemento [3] P4: Autores
if len(nodes) > 3:
    set_elem_text(nodes[3], 'Edier Aristizábal\u00b9*')

# Elemento [5] P14: Institución
if len(nodes) > 5:
    set_elem_text(nodes[5], '\u00b9 Universidad Nacional de Colombia')

# Elemento [6] P17: Ciudad-país
if len(nodes) > 6:
    set_elem_text(nodes[6], 'Medellín, Colombia')

# Elemento [7] P18: Correo
if len(nodes) > 7:
    set_elem_text(nodes[7], 'earistizabalg@unal.edu.co')

# Elemento [8] P19: ORCID
if len(nodes) > 8:
    set_elem_text(nodes[8], 'ORCID: 0000-0002-2648-2197')

# Elementos [10]-[20]: Limpiar autor 2 y 3
for i in range(10, min(22, len(nodes))):
    if nodes[i].qname[1] == 'p':
        set_elem_text(nodes[i], '')

# Elemento [23]: Autor de correspondencia
if len(nodes) > 23:
    set_elem_text(nodes[23], '* Autor de correspondencia: Edier Aristizábal')

# Evaluadores sugeridos (26-28): dejar como placeholders
if len(nodes) > 25:
    set_elem_text(nodes[25], 'Evaluadores sugeridos')

# Elemento [32] P50: Resumen
if len(nodes) > 32:
    set_elem_text(nodes[32], RESUMEN)

# Elemento [34] P52: Palabras clave heading — dejar
# Elemento [35] P53: Palabras clave
if len(nodes) > 35:
    set_elem_text(nodes[35], PALABRAS_CLAVE)

# Elemento [39] P57: Abstract (EN)
if len(nodes) > 39:
    set_elem_text(nodes[39], ABSTRACT_EN)

# Elemento [42] Normal: Keywords (EN)
if len(nodes) > 42:
    set_elem_text(nodes[42], KEYWORDS_EN)

# ── 2. Eliminar los elementos de instrucciones (43 en adelante) ───────────────
print('Eliminando sección de instrucciones...')
to_remove = list(body.childNodes)[43:]
for elem in to_remove:
    try:
        body.removeChild(elem)
    except Exception:
        pass

# ── 3. Agregar contenido del manuscrito ────────────────────────────────────────
print('Agregando contenido del manuscrito...')

def add_elements(elements_to_add):
    """Add a list of ODF elements to the document body."""
    for elem in elements_to_add:
        if isinstance(elem, list):
            for sub in elem:
                body.addElement(sub)
        else:
            body.addElement(elem)

for section in SECTIONS:
    # Add a blank paragraph before each section
    body.addElement(P(stylename='Normal'))

    for item in section:
        kind = item[0]

        if kind == 'h1':
            body.addElement(make_heading(doc, item[1], 1))

        elif kind == 'h2':
            body.addElement(make_heading(doc, item[1], 2))

        elif kind == 'p':
            body.addElement(make_para(doc, item[1]))

        elif kind == 'eq':
            body.addElement(make_equation(doc, item[1], item[2]))

        elif kind == 'fig':
            elems = make_figure(doc, item[1], item[2], item[3])
            add_elements(elems)

        elif kind == 'table':
            elems = make_table(doc, item[1], item[2], item[3], item[4])
            add_elements(elems)

        elif kind == 'ul':
            for list_item in item[1]:
                body.addElement(make_list_item(doc, '• ' + list_item))

        elif kind == 'ol':
            for idx_i, list_item in enumerate(item[1], 1):
                body.addElement(make_list_item(doc, f'{idx_i}. ' + list_item))

        elif kind == 'ref':
            body.addElement(make_para(doc, item[1], 'References'))

# ── 4. Guardar ────────────────────────────────────────────────────────────────
print(f'Guardando en: {OUTPUT}')
doc.save(OUTPUT)
print('✓ Documento generado exitosamente.')
print(f'  Ruta: {OUTPUT}')
