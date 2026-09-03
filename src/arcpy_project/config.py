from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class BufferConfig:
    input_features: str
    output_features: str
    distance: float
    units: str
    dissolve_option: str = "NONE"
    log_level: str = "INFO"


def _require(mapping: dict[str, Any], key: str, section: str) -> Any:
    if key not in mapping or mapping[key] in (None, ""):
        raise ValueError(f"Missing required config value: {section}.{key}")
    return mapping[key]


def load_buffer_config(path: str | Path) -> BufferConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    paths = data.get("paths", {})
    buffer = data.get("buffer", {})
    logging = data.get("logging", {})

    distance = float(_require(buffer, "distance", "buffer"))
    if distance <= 0:
        raise ValueError("buffer.distance must be greater than zero")

    return BufferConfig(
        input_features=str(_require(paths, "input_features", "paths")),
        output_features=str(_require(paths, "output_features", "paths")),
        distance=distance,
        units=str(_require(buffer, "units", "buffer")),
        dissolve_option=str(buffer.get("dissolve_option", "NONE")),
        log_level=str(logging.get("level", "INFO")),
    )
