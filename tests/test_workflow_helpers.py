from arcpy_project.workflows.buffer_features import format_distance


def test_format_distance_integer() -> None:
    assert format_distance(500.0, "Meters") == "500 Meters"


def test_format_distance_decimal() -> None:
    assert format_distance(12.5, "Feet") == "12.5 Feet"
