# 🌟 Predicción del Potencial Competitivo de Equipos Pokémon con Machine Learning

Este proyecto utiliza datos reales obtenidos desde PokéAPI para construir un dataset de más de 100,000 equipos Pokémon, cada uno compuesto por 6 Pokémon.
Luego se entrenan varios modelos de Machine Learning (incluyendo una Red Neuronal MLP) para predecir si un equipo tiene alto o bajo potencial competitivo.

Este proyecto cumple con los requisitos de dataset grande, data real y comparación de múltiples modelos.

## 🧠 Objetivo

Desarrollar un modelo capaz de clasificar si un equipo de Pokémon tiene alto ("strong") o bajo ("weak") potencial competitivo, basándose únicamente en:

Sumas de estadísticas del equipo (HP, Attack, Defense, etc.)

Promedios de estadísticas del equipo

## 📚 Resumen del Proyecto

### 1. Obtención de datos reales desde PokéAPI:

 - Stats base: HP, Attack, Defense, Sp. Attack, Sp. Defense, Speed.

 - Tipo primario/secundario, altura, peso.


### 2. Generación de 100,000 equipos Pokémon:

   Cada equipo contiene 6 Pokémon escogidos al azar.

   - Para cada equipo se calculan:

   - sum_hp, sum_attack, ..., sum_speed

   - mean_hp, mean_attack, ..., mean_speed


### 3. Construcción de un índice sintético de poder (team_power_score):

   Inspirado en:

   - fórmulas de daño de Pokémon,

   - ratings compuestos tipo FIFA,

   - sistemas de valoración de eSports.

   - Incluye interacciones no lineales y ruido estocástico.


### 4. Clasificación:

  - Se define strong_team = 1 si team_power_score ≥ mediana.

  - Caso contrario: strong_team = 0.


### 5. Entrenamiento de modelos:

  - Regresión Logística (baseline)

  - Random Forest

  - SVM (RBF)

  - Red Neuronal (Keras MLP)


### 6. Evaluación final:

  - Accuracy

  - F1-score

  - Matriz de confusión

  - Comparación de modelos

## 🏗️ Arquitectura del Proyecto

```txt
Proyecto/
│
├── descargar_pokeapi.py            # Descarga stats reales desde PokéAPI
├── generar_dataset_poke_teams.py   # Genera 100k equipos Pokémon
├── pokeproyecto.ipynb              # Notebook con EDA, modelos y resultados
├── pokemon_base_pokeapi.csv        # Datos reales de Pokémon
├── pokemon_teams_100k.csv          # Dataset final para ML
└── README.md
```
# 📦 Instalación
### 1. Clona el repositorio:
   ```powershell
   git clone https://github.com/Chimichami/Proyecto-Final-ML.git
   cd repositorio
   ```
### 2. Crea y activa tu entorno virtual:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```
### 3. Instala dependencias:
   ```powershell
   pip install pandas scikit-learn tensorflow matplotlib seaborn ipykernel
   ```

## 🚀 Uso

### 1. Descargar datos base desde PokéAPI

```powershell
python descargar_pokeapi.py
```

Esto generará:

```
pokemon_base_pokeapi.csv
```

---

### 2. Generar dataset de equipos (100k filas)

```powershell
python generar_dataset_poke_teams.py
```

Esto generará:

```
pokemon_teams_100k.csv
```

---

### 3. Entrenar modelos

Abre y ejecuta todas las celdas en:

```
pokeproyecto.ipynb
```
# 📌 Justificación del Índice team_power_score

El proyecto utiliza un índice sintético que combina estadísticas ofensivas, defensivas y de velocidad, inspirado en:

- Damage Formula oficial de Pokémon

- Overall Rating (OVR) de FIFA

- Champion Strength Score de League of Legends

- Sistemas de poder en eSports

Esto sigue un estándar real de la industria para modelar rendimiento basado en stats numéricos.

# 👩‍💻 Autores
Proyecto realizado por:
- Carranza Ramirez, Cesar Gabriel
- Garcia Calle, Renato
- Mercado Barbieri, Ariana Valeria
- Paca Sotero, Jose Francisco


   



