import json
from pathlib import Path


def export_json(path: Path, data: dict):
    """Export a dictionary to a JSON file"""
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
