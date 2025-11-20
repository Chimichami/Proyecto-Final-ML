import pandas as pd
import numpy as np
import random

#trabajar todo en entorno .venv

# Semillas para reproducibilidad
random.seed(42)
np.random.seed(42)

# 1. Leer el dataset base de Pokémon (generado con PokéAPI)
df = pd.read_csv("pokemon_base_pokeapi.csv")

# Elegimos las columnas numéricas que usaremos como features
stat_cols = ["hp", "attack", "defense", "sp_attack", "sp_defense", "speed"]

# Aseguramos que sean numéricas
df[stat_cols] = df[stat_cols].apply(pd.to_numeric, errors="coerce")
df = df.dropna(subset=stat_cols).reset_index(drop=True)

n_pokemon = len(df)
print(f"Pokémon disponibles: {n_pokemon}")

if n_pokemon < 6:
    raise ValueError("Se necesitan al menos 6 Pokémon en el dataset base.")

# 2. Generar equipos sintéticos
N_EJEMPLOS = 100_000   # tamaño del dataset final

rows = []
for _ in range(N_EJEMPLOS):
    # Elegimos 6 Pokémon distintos al azar (equipo clásico 6v6)
    indices = random.sample(range(n_pokemon), 6)
    team = df.iloc[indices]

    # Nombres de los Pokémon
    names = list(team["name"].values)

    # Stats agregados del equipo (suma y promedio)
    sum_stats = team[stat_cols].sum()
    mean_stats = team[stat_cols].mean()

    sum_hp = sum_stats["hp"]
    sum_attack = sum_stats["attack"]
    sum_defense = sum_stats["defense"]
    sum_sp_attack = sum_stats["sp_attack"]
    sum_sp_defense = sum_stats["sp_defense"]
    sum_speed = sum_stats["speed"]

    # 3. Crear un "score" sintético de fuerza del equipo (no lineal)
    #
    # Justificación (para tu informe):
    # - Inspirado en ratings compuestos de juegos como FIFA y en fórmulas
    #   de daño de Pokémon: el ataque y la velocidad tienen impacto
    #   ligeramente superlineal; la defensa y el bulk tienen rendimientos
    #   decrecientes; la velocidad combinada con ataque especial modela
    #   "glass cannons" rápidos, etc.
    #
    # - attack_term: ataque total con ligera potencia > 1
    # - speed_term: interacción entre velocidad y ataque especial
    # - bulk_term: defensa + defensa especial + parte de HP, comprimido con log
    # - Se añade ruido gaussiano para simular variabilidad de combates.

    attack_term = sum_attack ** 1.1
    speed_term = np.sqrt(sum_speed * sum_sp_attack + 1.0)
    bulk_term = np.log1p(sum_defense + sum_sp_defense + 0.5 * sum_hp)

    team_power = (
        0.40 * attack_term +
        0.35 * speed_term +
        0.25 * bulk_term
    )

    # Añadimos ruido aleatorio para simular variabilidad (crits, matchups, etc.)
    team_power_noisy = team_power + np.random.normal(0, 20)

    rows.append({
        "p1_name": names[0],
        "p2_name": names[1],
        "p3_name": names[2],
        "p4_name": names[3],
        "p5_name": names[4],
        "p6_name": names[5],
        "sum_hp": sum_hp,
        "sum_attack": sum_attack,
        "sum_defense": sum_defense,
        "sum_sp_attack": sum_sp_attack,
        "sum_sp_defense": sum_sp_defense,
        "sum_speed": sum_speed,
        "mean_hp": mean_stats["hp"],
        "mean_attack": mean_stats["attack"],
        "mean_defense": mean_stats["defense"],
        "mean_sp_attack": mean_stats["sp_attack"],
        "mean_sp_defense": mean_stats["sp_defense"],
        "mean_speed": mean_stats["speed"],
        "team_power_score": team_power_noisy
    })

big_df = pd.DataFrame(rows)

# 4. Crear etiqueta binaria según la mediana del team_power_score
threshold = big_df["team_power_score"].median()
big_df["strong_team"] = (big_df["team_power_score"] >= threshold).astype(int)

print(big_df.head())
print(big_df.shape)

# 5. Guardar a CSV
big_df.to_csv("pokemon_teams_100k.csv", index=False)
print("Guardado pokemon_teams_100k.csv")
print(f"Umbral (mediana) de team_power_score: {threshold:.2f}")
