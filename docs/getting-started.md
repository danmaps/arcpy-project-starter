# Getting Started

This starter is meant to help an ArcGIS Pro user move from a single script to a small maintainable project without introducing unnecessary infrastructure.

If you already have a working ArcPy script, read [`customizing.md`](customizing.md) before reorganizing it. The three before/after examples in [`case-studies.md`](case-studies.md) show the intended style of refactoring and include prompts you can reuse with an AI coding assistant.

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

1. Record what your existing script currently reads, writes, changes, and returns.
2. Identify the geoprocessing operations in the script.
3. Move changing values such as paths and distances into YAML.
4. Move reusable workflow logic into `src/arcpy_project/workflows/`.
5. Keep the script under `scripts/` as a thin entry point.
6. Extract calculations, naming rules, validation, and other non-ArcPy logic into testable helper functions when that actually improves clarity or safety.
7. Verify the migrated workflow against a known baseline such as output names, feature counts, or expected field values.

For detailed paths for a single script, batch workflow, or ArcGIS Pro script tool/Python toolbox, see [`customizing.md`](customizing.md).

## 6. Give your coding agent the right context

`AGENTS.md` is the canonical project guidance. `CLAUDE.md` and `.github/copilot-instructions.md` point compatible tools back to the same rules.

For refactoring tasks, tell the agent which case study is closest to the problem:

- Case Study 1: hard-coded values and a growing one-off script
- Case Study 2: batch processing and hidden GIS-data assumptions
- Case Study 3: in-place edits, destructive operations, or partial-failure risk

This gives the agent a concrete target without asking it to redesign the project from first principles.

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
