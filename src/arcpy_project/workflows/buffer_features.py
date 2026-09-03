from __future__ import annotations

from dataclasses import dataclass

from arcpy_project.config import BufferConfig


@dataclass(frozen=True)
class BufferResult:
    output_features: str
    input_count: int | None = None
    output_count: int | None = None


def format_distance(distance: float, units: str) -> str:
    value = int(distance) if float(distance).is_integer() else distance
    return f"{value} {units}"


def run_buffer(config: BufferConfig) -> BufferResult:
    try:
        import arcpy
    except ImportError as exc:
        raise RuntimeError(
            "ArcPy is not available. Run this workflow from the ArcGIS Pro Python environment."
        ) from exc

    if not arcpy.Exists(config.input_features):
        raise FileNotFoundError(f"Input features not found: {config.input_features}")

    arcpy.env.overwriteOutput = True

    input_count = int(arcpy.management.GetCount(config.input_features)[0])
    distance = format_distance(config.distance, config.units)

    arcpy.analysis.Buffer(
        in_features=config.input_features,
        out_feature_class=config.output_features,
        buffer_distance_or_field=distance,
        dissolve_option=config.dissolve_option,
    )

    output_count = int(arcpy.management.GetCount(config.output_features)[0])

    return BufferResult(
        output_features=config.output_features,
        input_count=input_count,
        output_count=output_count,
    )
