import requests
import pandas as pd
from time import sleep
from pathlib import Path

#trabajar todo en entorno .venv

BASE_URL = "https://pokeapi.co/api/v2"
OUTPUT_PATH = Path("data/pokemon_base_pokeapi.csv")

def get_all_pokemon(limit=1000): 
    url = f"{BASE_URL}/pokemon?limit={limit}&offset=0"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    return [p["url"] for p in data["results"]]

def descargar_pokemon_detalle(limit=1000):
    urls = get_all_pokemon(limit=limit)
    registros = []

    for i, url in enumerate(urls, start=1):
        resp = requests.get(url)
        resp.raise_for_status()
        poke = resp.json()

        # nombre
        name = poke["name"]

        # tipos (puede tener 1 o 2)
        types = [t["type"]["name"] for t in poke["types"]]
        type1 = types[0]
        type2 = types[1] if len(types) > 1 else None

        # stats base (hp, attack, defense, sp_atk, sp_def, speed)
        stats_map = {s["stat"]["name"]: s["base_stat"] for s in poke["stats"]}
        hp = stats_map.get("hp")
        attack = stats_map.get("attack")
        defense = stats_map.get("defense")
        sp_atk = stats_map.get("special-attack")
        sp_def = stats_map.get("special-defense")
        speed = stats_map.get("speed")

        # altura y peso
        height = poke["height"]
        weight = poke["weight"]

        registros.append({
            "name": name,
            "type1": type1,
            "type2": type2,
            "hp": hp,
            "attack": attack,
            "defense": defense,
            "sp_attack": sp_atk,
            "sp_defense": sp_def,
            "speed": speed,
            "height": height,
            "weight": weight,
        })

        if i % 50 == 0:
            print(f"Llevamos {i} Pokémon descargados...")
            # PokéAPI pide ser amable con el servidor
            sleep(0.2)

    df = pd.DataFrame(registros)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Guardado {OUTPUT_PATH} con {len(df)} filas y {len(df.columns)} columnas")

if __name__ == "__main__":
    descargar_pokemon_detalle(limit=1000)  
