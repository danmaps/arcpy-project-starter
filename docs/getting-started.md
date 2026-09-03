# Getting Started

This starter is meant to help an ArcGIS Pro user move from a single script to a small maintainable project without introducing unnecessary infrastructure.

## 1. Start from the ArcGIS Pro Python environment

Use the ArcGIS Pro Python Command Prompt or another shell configured to use the Python environment that ships with ArcGIS Pro.

Verify ArcPy is available:

```powershell
python -c "import arcpy; print(arcpy.GetInstallInfo()['Version'])"
```

## 2. Install the project

From the project root:

```powershell
python -m pip install -e .
```

For development dependencies:

```powershell
python -m pip install -e ".[dev]"
```

## 3. Create local configuration

Copy the example configuration:

```powershell
Copy-Item config\example.yaml config\local.yaml
```

Edit `config\local.yaml` for your own inputs and outputs. The local file is excluded from Git so machine-specific paths do not leak into the shared project.

## 4. Run the example

```powershell
python scripts\run_workflow.py --config config\local.yaml
```

The example validates the input feature class, records feature counts, runs `arcpy.analysis.Buffer`, and logs the result.

## 5. Replace the example with your workflow

A useful migration pattern is:

1. Identify the geoprocessing operations in your existing script.
2. Move changing values such as paths and distances into YAML.
3. Move reusable workflow logic into `src/arcpy_project/workflows/`.
4. Keep the script under `scripts/` as a thin entry point.
5. Extract calculations, naming rules, validation, and other non-ArcPy logic into testable helper functions.

## Suggested next additions

Depending on the project, useful additions include:

- structured output folders
- a scratch geodatabase
- schema validation
- explicit spatial-reference checks
- a toolbox or script-tool wrapper
- enterprise geodatabase connection handling
- ArcGIS Online publishing in a separate integration module
- CI for pure-Python tests

Avoid adding infrastructure simply because it appears in generic Python project templates. ArcGIS automation often benefits more from a small explicit structure than from a large framework.
