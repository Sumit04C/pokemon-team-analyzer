"""
One-time (re-runnable) loader for reference data from PokéAPI.

Run from the project root with:
    docker compose run --rm app python scripts/load_pokeapi.py

Loads, in dependency order:
    generations -> types -> pokemon -> pokemon_types
Responses are cached as JSON files in scripts/.cache so re-runs are fast
and we don't hammer the API.
"""
import json
import os
import time
from pathlib import Path

import requests
from sqlalchemy import create_engine, text

BASE_URL = "https://pokeapi.co/api/v2"
CACHE_DIR = Path(__file__).parent / ".cache"
CACHE_DIR.mkdir(exist_ok=True)

session = requests.Session()


def get_json(url: str) -> dict:
    """Fetch a URL, using an on-disk cache keyed by the URL path."""
    key = url.replace(BASE_URL, "").strip("/").replace("/", "_").replace("?", "_")
    cache_file = CACHE_DIR / f"{key or 'root'}.json"

    if cache_file.exists():
        return json.loads(cache_file.read_text())

    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    cache_file.write_text(json.dumps(data))
    time.sleep(0.05)  # be polite; only sleeps on real network calls
    return data


def id_from_url(url: str) -> int:
    """'https://pokeapi.co/api/v2/type/10/' -> 10"""
    return int(url.rstrip("/").split("/")[-1])


def list_resources(endpoint: str) -> list[dict]:
    """Return the {name, url} entries for an endpoint (all of them)."""
    return get_json(f"{BASE_URL}/{endpoint}?limit=2000")["results"]


def load_generations(conn) -> None:
    rows = []
    for entry in list_resources("generation"):
        data = get_json(entry["url"])
        rows.append({"id": data["id"], "name": data["name"]})

    conn.execute(
        text("INSERT INTO generations (id, name) VALUES (:id, :name) "
             "ON CONFLICT (id) DO NOTHING"),
        rows,
    )
    print(f"generations: {len(rows)} processed")


def load_types(conn) -> None:
    rows = []
    for entry in list_resources("type"):
        type_id = id_from_url(entry["url"])
        # IDs above 10000 are special types ('unknown', 'shadow'), skip them
        if type_id >= 10000:
            continue
        rows.append({"id": type_id, "name": entry["name"]})

    conn.execute(
        text("INSERT INTO types (id, name) VALUES (:id, :name) "
             "ON CONFLICT (id) DO NOTHING"),
        rows,
    )
    print(f"types: {len(rows)} processed")


def load_pokemon(conn) -> None:
    entries = list_resources("pokemon")
    total = len(entries)
    print(f"pokemon: fetching {total} entries (cached after the first run)...")

    pokemon_rows = []
    type_rows = []
    for i, entry in enumerate(entries, start=1):
        data = get_json(entry["url"])
        pokemon_rows.append({"id": data["id"], "name": data["name"]})

        for t in data["types"]:
            type_rows.append({
                "pokemon_id": data["id"],
                "type_id": id_from_url(t["type"]["url"]),
                "slot": t["slot"],
            })

        if i % 100 == 0:
            print(f"  {i}/{total}")

    # Pokémon first, because pokemon_types has a foreign key to it
    conn.execute(
        text("INSERT INTO pokemon (id, name) VALUES (:id, :name) "
             "ON CONFLICT (id) DO NOTHING"),
        pokemon_rows,
    )
    conn.execute(
        text("INSERT INTO pokemon_types (pokemon_id, type_id, slot) "
             "VALUES (:pokemon_id, :type_id, :slot) "
             "ON CONFLICT (pokemon_id, type_id) DO NOTHING"),
        type_rows,
    )
    print(f"pokemon: {len(pokemon_rows)} processed, "
          f"pokemon_types: {len(type_rows)} processed")


def main() -> None:
    engine = create_engine(os.environ["DATABASE_URL"])

    # One transaction: if anything fails, nothing is half-loaded
    with engine.begin() as conn:
        load_generations(conn)
        load_types(conn)
        load_pokemon(conn)

    print("Done.")


if __name__ == "__main__":
    main()