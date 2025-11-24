# 🟢 Predicción de resultados en Pokémon Showdown (Gen 9 OU)

Proyecto final de Machine Learning basado 100 % en data real obtenida de replays públicos de Pokémon Showdown. Cada registro corresponde a un equipo completo enfrentándose a un rival concreto, lo que nos permite modelar match-ups reales sin recurrir a etiquetas sintéticas.

## ⚙️ Pipeline de datos

1. **Descarga de stats base (PokéAPI)**  
   `Proyecto3/descargar_pokeapi.py` guarda `data/pokemon_base_pokeapi.csv` con stats oficiales (HP, Attack, Defense, etc.)
2. **Scraping de replays (Showdown)**  
   `Proyecto3/scrape_showdown_replays.py` consume `https://replay.pokemonshowdown.com/search.json`, descarga cada replay `.json`, extrae los 6 Pokémon por jugador y guarda `data/pokemon_showdown_teams.csv` + `data/pokemon_showdown_teams_clean.csv`.
3. **EDA + Feature Engineering**  
   `Proyecto3/pokeproyecto.ipynb` (ejecutado) realiza el EDA, crea indicadores ofensivos/defensivos, codifica presencia de los 50 Pokémon más usados y construye un dataset **pairwise** `data/pokemon_showdown_pairwise.csv` con features `*_self`, `*_opp` y `*_diff`.
4. **Modelado y métricas**  
   En el notebook comparamos cuatro modelos exigidos por la rúbrica (Regresión Logística, Random Forest, SVM RBF y LightGBM) con validación cruzada estratificada y evaluación hold-out.

## 🧱 Estructura del repositorio

```text
Proyecto-Final-ML/
├── README.md
├── .gitignore
└── Proyecto3/
    ├── data/
    │   ├── pokemon_base_pokeapi.csv
    │   ├── pokemon_showdown_teams.csv
    │   ├── pokemon_showdown_teams_clean.csv
    │   └── pokemon_showdown_pairwise.csv
    ├── figures/
    │   ├── eda_turns_hist.png
    │   ├── eda_top_pokemon.png
    │   └── eda_rating_win.png
    ├── descargar_pokeapi.py
    ├── generar_dataset_poke_teams.py      # legado (dataset sintético)
    ├── scrape_showdown_replays.py
    └── pokeproyecto.ipynb                 # notebook completo (EDA + modelos)
```

## 🚀 Cómo reproducir

```bash
# 0. Ubicarse en Proyecto3
cd Proyecto3

# 1. Descargar stats base
python descargar_pokeapi.py

# 2. Scraping de replays (formato Gen9 OU por defecto)
python scrape_showdown_replays.py --max-replays 700 --pages 120

# 3. Abrir y ejecutar el notebook
jupyter lab pokeproyecto.ipynb
```

> En entornos sin Python global, usamos `nix-shell -p 'python3.withPackages (...)' --run "<comando>"`, pero cualquier venv con `pandas`, `requests`, `seaborn`, `matplotlib`, `scikit-learn` y `lightgbm` funciona.

## 📊 Resultados actuales

| Modelo                | F1 (CV 5-fold) | ROC-AUC (CV) | F1 Test | Precision Test | Recall Test |
|-----------------------|----------------|--------------|---------|----------------|-------------|
| Regresión Logística   | 0.62 ± 0.03    | 0.66 ± 0.04  | 0.61    | 0.62           | 0.61        |
| Random Forest         | 0.75 ± 0.02    | 0.80 ± 0.03  | 0.74    | 0.74           | 0.74        |
| SVM RBF               | 0.69 ± 0.03    | 0.74 ± 0.04  | 0.67    | 0.70           | 0.65        |
| **LightGBM (moderno)**| **0.82 ± 0.03**| **0.87 ± 0.02** | **0.80** | **0.80** | **0.80** |

Todas las métricas se calculan sobre el dataset pareado (828 registros). Se incluyen matriz de confusión y curva ROC en el notebook/figuras.

## 📝 Qué entregar al informe

- Capturas del EDA (`figures/*.png`).
- Tabla de métricas (arriba) + matriz de confusión/ROC del LightGBM optimizado.
- Descripción del pipeline de scraping + validación cruzada.
- Discusión sobre posibles mejoras: más features (roles/tipos), objetos/movimientos y modelos basados en sets (Set Transformers, Deep Sets).

## 👥 Autores

- Carranza Ramirez, César Gabriel  
- García Calle, Renato  
- Mercado Barbieri, Ariana Valeria  
- Paca Sotero, Jose Francisco  
