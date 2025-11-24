"""
Descarga replays recientes de Pokémon Showdown y genera un dataset tabular
con información de cada equipo (p1/p2) y etiquetado real de victoria.

Uso rápido:
    python scrape_showdown_replays.py --format gen9ou --pages 30 \
        --output showdown_teams.csv

Requiere que exista "pokemon_base_pokeapi.csv" (descargado vía PokéAPI).
Para especies que no estén en ese archivo, se consulta PokéAPI on-demand
para obtener sus estadísticas base.
"""

from __future__ import annotations

import argparse
import dataclasses
import logging
import re
import time
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import pandas as pd
import requests

SEARCH_URL = "https://replay.pokemonshowdown.com/search.json"
REPLAY_URL = "https://replay.pokemonshowdown.com/{replay_id}.json"
POKEAPI_URL = "https://pokeapi.co/api/v2/pokemon/{slug}"
SPECIES_URL = "https://pokeapi.co/api/v2/pokemon-species/{slug}"

STAT_COLS = ["hp", "attack", "defense", "sp_attack", "sp_defense", "speed"]

# Formas como Ogerpon-Wellspring o Samurott-Hisui aparecen tal cual en los
# replays; estas reglas ayudan a mapear a los slugs que usa PokéAPI.
SPECIAL_TOKEN_MAP = {
    "é": "e",
    "É": "e",
    "’": "",
    "'": "",
    ".": "",
}

FALLBACK_SLUGS = {
    "mimikyu": "mimikyu-disguised",
    "mimikyu-busted": "mimikyu-busted",
    "enamorus": "enamorus-incarnate",
    "landorus": "landorus-incarnate",
    "tornadus": "tornadus-incarnate",
    "thundurus": "thundurus-incarnate",
    "urshifu": "urshifu-single-strike",
    "maushold": "maushold-family-of-four",
    "maushold-family-of-three": "maushold-family-of-three",
    "greninja": "greninja",
    "ogerpon": "ogerpon",
    "ogerpon-wellspring": "ogerpon-wellspring-mask",
    "ogerpon-hearthflame": "ogerpon-hearthflame-mask",
    "ogerpon-cornerstone": "ogerpon-cornerstone-mask",
    "ogerpon-teal": "ogerpon-teal-mask",
    "zamazenta": "zamazenta",
    "zamazenta-crowned": "zamazenta-crowned",
}


def showdown_name_to_slug(name: str) -> str:
    slug = name.strip().lower().replace(" ", "-")
    for src, dst in SPECIAL_TOKEN_MAP.items():
        slug = slug.replace(src, dst)
    slug = slug.replace("%", "percent")
    slug = re.sub(r"[^a-z0-9\-]", "", slug)
    slug = re.sub(r"-\*$", "", slug)
    slug = slug.rstrip("-")
    return slug


@dataclasses.dataclass
class PokemonStats:
    name: str
    type1: Optional[str]
    type2: Optional[str]
    hp: float
    attack: float
    defense: float
    sp_attack: float
    sp_defense: float
    speed: float

    @classmethod
    def from_row(cls, row: pd.Series) -> "PokemonStats":
        return cls(
            name=row["name"],
            type1=row.get("type1"),
            type2=row.get("type2"),
            hp=float(row["hp"]),
            attack=float(row["attack"]),
            defense=float(row["defense"]),
            sp_attack=float(row["sp_attack"]),
            sp_defense=float(row["sp_defense"]),
            speed=float(row["speed"]),
        )


class PokemonStatsResolver:
    def __init__(self, base_csv: Path, sleep: float = 0.3) -> None:
        df = pd.read_csv(base_csv)
        df["name"] = df["name"].str.lower()
        self._stats: Dict[str, PokemonStats] = {
            row["name"]: PokemonStats.from_row(row) for _, row in df.iterrows()
        }
        self._sleep = sleep
        self._fetched: Dict[str, PokemonStats] = {}
        self._species_cache: Dict[str, Dict] = {}

    def _download_stats(self, slug: str) -> PokemonStats:
        logging.debug("Consultando PokéAPI para %s", slug)
        resp = requests.get(POKEAPI_URL.format(slug=slug), timeout=20)
        resp.raise_for_status()
        data = resp.json()
        stats_map = {s["stat"]["name"]: s["base_stat"] for s in data["stats"]}
        entry = PokemonStats(
            name=slug,
            type1=data["types"][0]["type"]["name"],
            type2=data["types"][1]["type"]["name"] if len(data["types"]) > 1 else None,
            hp=stats_map["hp"],
            attack=stats_map["attack"],
            defense=stats_map["defense"],
            sp_attack=stats_map["special-attack"],
            sp_defense=stats_map["special-defense"],
            speed=stats_map["speed"],
        )
        return entry

    def _load_species(self, slug: str) -> Optional[Dict]:
        if slug in self._species_cache:
            return self._species_cache[slug]
        try:
            resp = requests.get(SPECIES_URL.format(slug=slug), timeout=20)
            resp.raise_for_status()
        except requests.RequestException:
            return None
        data = resp.json()
        self._species_cache[slug] = data
        time.sleep(self._sleep)
        return data

    def _resolve_variant_slug(self, slug: str) -> Optional[str]:
        parts = slug.split("-")
        base_slug = parts[0]
        species_data = self._load_species(base_slug)
        if not species_data:
            return None
        candidate = None
        for variety in species_data.get("varieties", []):
            name = variety["pokemon"]["name"]
            if name == slug:
                return slug
            if len(parts) > 1 and parts[1] and parts[1] in name:
                candidate = name
        if candidate:
            return candidate
        for variety in species_data.get("varieties", []):
            if variety.get("is_default"):
                return variety["pokemon"]["name"]
        return None

    def get(self, showdown_name: str) -> Optional[PokemonStats]:
        slug = showdown_name_to_slug(showdown_name)
        slug = FALLBACK_SLUGS.get(slug, slug)
        if slug in self._stats:
            return self._stats[slug]
        if slug in self._fetched:
            return self._fetched[slug]
        entry: Optional[PokemonStats] = None
        try:
            entry = self._download_stats(slug)
        except requests.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 404:
                variant_slug = self._resolve_variant_slug(slug)
                if variant_slug and variant_slug != slug:
                    logging.debug("Reintentando con variante %s para %s", variant_slug, showdown_name)
                    try:
                        entry = self._download_stats(variant_slug)
                        slug = variant_slug
                    except requests.RequestException as inner_exc:
                        logging.warning("Variante %s también falló (%s)", variant_slug, inner_exc)
                        return None
                else:
                    logging.warning("No se encontró variante para %s", showdown_name)
                    return None
            else:
                logging.warning("Error HTTP para %s (%s)", showdown_name, exc)
                return None
        except requests.RequestException as exc:
            logging.warning("Error de red al consultar %s (%s)", showdown_name, exc)
            return None
        if entry is None:
            return None
        self._fetched[slug] = entry
        time.sleep(self._sleep)
        return entry

    def team_stats(self, names: Iterable[str]) -> Optional[Dict[str, float]]:
        stats = [self.get(name) for name in names]
        if any(s is None for s in stats):
            return None
        agg: Dict[str, float] = {}
        for col in STAT_COLS:
            values = [getattr(s, col) for s in stats if s is not None]
            agg[f"sum_{col}"] = float(sum(values))
            agg[f"mean_{col}"] = float(sum(values) / len(values))
        return agg


def fetch_replay_ids(format_id: str, max_replays: int, pages: int) -> List[str]:
    replay_ids: List[str] = []
    page = 1
    while len(replay_ids) < max_replays and page <= pages:
        params = {"format": format_id, "page": page}
        logging.debug("Descargando página %s ...", page)
        resp = requests.get(SEARCH_URL, params=params, timeout=15)
        resp.raise_for_status()
        payload = resp.json()
        if not payload:
            break
        for item in payload:
            if item.get("private"):
                continue
            replay_ids.append(item["id"])
            if len(replay_ids) >= max_replays:
                break
        page += 1
        time.sleep(0.5)
    return replay_ids


def parse_replay(replay_json: Dict) -> Optional[Dict]:
    log = replay_json.get("log", "")
    if not log:
        return None
    teams = {"p1": [], "p2": []}
    players: Dict[str, Dict[str, Optional[float]]] = {}
    winner_slot: Optional[str] = None
    winner_name: Optional[str] = None
    turns = 0
    for raw_line in log.splitlines():
        if raw_line.startswith("|player|"):
            _, _, slot, name, _, rating, *_ = (raw_line + "||||").split("|")
            rating_value: Optional[float] = None
            if rating:
                try:
                    rating_value = float(rating)
                except ValueError:
                    rating_value = None
            players[slot] = {"name": name, "rating": rating_value}
        elif raw_line.startswith("|poke|"):
            parts = raw_line.split("|")
            if len(parts) < 4:
                continue
            slot = parts[2]
            species_token = parts[3]
            species = species_token.split(",")[0].strip()
            if slot in teams and species:
                if species not in teams[slot]:
                    teams[slot].append(species)
        elif raw_line.startswith("|win|"):
            winner_name = raw_line.split("|")[2]
        elif raw_line.startswith("|turn|"):
            try:
                turns = int(raw_line.split("|")[2])
            except ValueError:
                continue
    if winner_name:
        for slot, info in players.items():
            if info["name"] == winner_name:
                winner_slot = slot
                break
    if not teams["p1"] or not teams["p2"] or winner_slot is None:
        return None
    return {
        "teams": teams,
        "players": players,
        "winner_slot": winner_slot,
        "turns": turns,
    }


def build_rows(
    replay_id: str,
    replay_json: Dict,
    parsed: Dict,
    resolver: PokemonStatsResolver,
) -> List[Dict]:
    rows: List[Dict] = []
    teams = parsed["teams"]
    players = parsed["players"]
    winner_slot = parsed["winner_slot"]
    turns = parsed["turns"]
    for slot in ("p1", "p2"):
        team_list = teams[slot]
        stats = resolver.team_stats(team_list)
        if stats is None:
            logging.debug("Saltando %s por stats faltantes", replay_id)
            return []
        player_info = players.get(slot, {})
        opp_slot = "p2" if slot == "p1" else "p1"
        opp_info = players.get(opp_slot, {})
        rating = player_info.get("rating")
        opp_rating = opp_info.get("rating")
        rating_diff = None
        if rating is not None and opp_rating is not None:
            rating_diff = rating - opp_rating
        row = {
            "replay_id": replay_id,
            "format_id": replay_json.get("formatid"),
            "player_slot": slot,
            "player_name": player_info.get("name"),
            "opponent_name": opp_info.get("name"),
            "player_rating": rating,
            "opponent_rating": opp_rating,
            "rating_diff": rating_diff,
            "turns": turns,
            "team_size": len(team_list),
            "team_pokemon": ",".join(team_list),
            "won_battle": 1 if slot == winner_slot else 0,
        }
        row.update(stats)
        rows.append(row)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Scraper de replays de Showdown")
    parser.add_argument("--format", default="gen9ou", help="Formato (ej. gen9ou)")
    parser.add_argument("--pages", type=int, default=25, help="Páginas del feed search a recorrer")
    parser.add_argument("--max-replays", type=int, default=400, help="Máximo de replays a descargar")
    parser.add_argument(
        "--base-stats",
        type=Path,
        default=Path("data/pokemon_base_pokeapi.csv"),
        help="CSV con stats base descargados de PokéAPI",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/pokemon_showdown_teams.csv"),
        help="Archivo de salida con features agregadas",
    )
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper()))
    resolver = PokemonStatsResolver(args.base_stats)
    replay_ids = fetch_replay_ids(args.format, args.max_replays, args.pages)
    logging.info("Se intentará procesar %d replays del formato %s", len(replay_ids), args.format)

    all_rows: List[Dict] = []
    for idx, replay_id in enumerate(replay_ids, start=1):
        try:
            resp = requests.get(REPLAY_URL.format(replay_id=replay_id), timeout=15)
            resp.raise_for_status()
        except Exception as exc:  # noqa: BLE001
            logging.warning("No se pudo descargar replay %s: %s", replay_id, exc)
            continue
        replay_json = resp.json()
        parsed = parse_replay(replay_json)
        if not parsed:
            continue
        rows = build_rows(replay_id, replay_json, parsed, resolver)
        all_rows.extend(rows)
        if idx % 25 == 0:
            logging.info("Procesados %d/%d replays", idx, len(replay_ids))
        time.sleep(0.2)

    if not all_rows:
        logging.error("No se generaron filas; revisar filtros o formato.")
        return
    df = pd.DataFrame(all_rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)
    logging.info("Dataset guardado en %s (%d filas)", args.output, len(df))


if __name__ == "__main__":
    main()
