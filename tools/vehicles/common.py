"""Shared paths and JSON helpers for the vehicles workstream."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VEHICLES = ROOT / "vehicles"


def load_json(path):
    return json.loads(Path(path).read_text())


def save_json(path, data):
    Path(path).write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")


def references(slug):
    return load_json(VEHICLES / "references" / slug / "references.json")
