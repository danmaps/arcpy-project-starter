from pathlib import Path

import pytest

from arcpy_project.config import load_buffer_config


def test_load_buffer_config(tmp_path: Path) -> None:
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        """
paths:
  input_features: C:/GIS/input.gdb/roads
  output_features: C:/GIS/output.gdb/roads_buffer
buffer:
  distance: 250
  units: Feet
logging:
  level: DEBUG
""".strip(),
        encoding="utf-8",
    )

    config = load_buffer_config(config_file)

    assert config.input_features.endswith("roads")
    assert config.output_features.endswith("roads_buffer")
    assert config.distance == 250
    assert config.units == "Feet"
    assert config.log_level == "DEBUG"


def test_rejects_nonpositive_distance(tmp_path: Path) -> None:
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        """
paths:
  input_features: a
  output_features: b
buffer:
  distance: 0
  units: Meters
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="greater than zero"):
        load_buffer_config(config_file)
