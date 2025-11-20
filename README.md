# 🌟 Predicción del Potencial Competitivo de Equipos Pokémon con Machine Learning

Este proyecto utiliza datos reales obtenidos desde PokéAPI para construir un dataset de más de 100,000 equipos Pokémon, cada uno compuesto por 6 Pokémon.
Luego se entrenan varios modelos de Machine Learning (incluyendo una Red Neuronal MLP) para predecir si un equipo tiene alto o bajo potencial competitivo.

Este proyecto cumple con los requisitos de dataset grande, data real y comparación de múltiples modelos.

## 🧠 Objetivo

Desarrollar un modelo capaz de clasificar si un equipo de Pokémon tiene alto ("strong") o bajo ("weak") potencial competitivo, basándose únicamente en:

Sumas de estadísticas del equipo (HP, Attack, Defense, etc.)

Promedios de estadísticas del equipo

## 📚 Resumen del Proyecto

1. Obtención de datos reales desde PokéAPI:

 - Stats base: HP, Attack, Defense, Sp. Attack, Sp. Defense, Speed.

 - Tipo primario/secundario, altura, peso.


2. Generación de 100,000 equipos Pokémon:

   Cada equipo contiene 6 Pokémon escogidos al azar.

   - Para cada equipo se calculan:

   - sum_hp, sum_attack, ..., sum_speed

   - mean_hp, mean_attack, ..., mean_speed


3. Construcción de un índice sintético de poder (team_power_score):

   Inspirado en:

    - fórmulas de daño de Pokémon,

    - ratings compuestos tipo FIFA,

    - sistemas de valoración de eSports.

    - Incluye interacciones no lineales y ruido estocástico.


4. Clasificación:

  - Se define strong_team = 1 si team_power_score ≥ mediana.

  - Caso contrario: strong_team = 0.


5. Entrenamiento de modelos:

  - Regresión Logística (baseline)

  - Random Forest

  - SVM (RBF)

  - Red Neuronal (Keras MLP)


6. Evaluación final:

  - Accuracy

  - F1-score

  - Matriz de confusión

Comparación de modelos

