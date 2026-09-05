# Agent Instructions

This repository is an ArcPy project template intended for ArcGIS Pro users on Windows.

Treat this file as the canonical source of repository instructions. Compatibility files such as `CLAUDE.md` and `.github/copilot-instructions.md` should point here rather than duplicate a separate set of rules.

## Supporting guidance

Use these documents when they match the task:

- `docs/case-studies.md` shows three concrete before/after ArcPy refactors and the reasoning behind them.
- `docs/customizing.md` explains how to adapt this starter to a one-off script, a batch workflow, or an ArcGIS Pro script tool/Python toolbox.
- `docs/getting-started.md` covers installation and the example workflow.

When refactoring an existing script, prefer the closest case study over inventing a new architecture. Preserve working behavior unless the user explicitly asks to change it.

## Environment assumptions

- ArcGIS Pro 3.x on Windows 10/11
- Python provided by the ArcGIS Pro environment
- `arcpy` is available only inside an ArcGIS Pro-compatible Python environment
- Do not assume Linux, macOS, Conda-forge, or a generic CPython environment can import `arcpy`

## Project conventions

- Put reusable Python code under `src/arcpy_project/`
- Put executable entry points under `scripts/`
- Put user-specific settings in YAML under `config/`
- Never hard-code user names, drive letters, geodatabase paths, or enterprise connection files in reusable modules
- Keep pure Python logic separate from ArcPy calls whenever practical
- Prefer small workflow functions over one large procedural script
- Use the shared logger instead of ad hoc `print()` statements in reusable code
- Add structure only when it solves a concrete maintenance, safety, testing, or reuse problem

## ArcPy rules

- Import `arcpy` inside ArcPy-specific modules or functions when that improves testability
- Use `arcpy.Exists()` before operating on external GIS datasets when a missing path would otherwise fail later
- Use `arcpy.env.overwriteOutput` deliberately rather than relying on session defaults
- Treat geoprocessing messages as useful operational output
- Do not assume feature classes are shapefiles
- Do not assume ObjectID field names, spatial references, geometry types, or field schemas unless validated
- Prefer explicit output paths and names
- Avoid silently changing the active ArcGIS Pro project or map unless the task requires it
- For destructive or hard-to-reverse operations, prefer staged outputs and explicit promotion/replacement steps when practical

## Paths and configuration

- Use `pathlib.Path` for ordinary filesystem paths
- Keep geodatabase dataset paths as strings where ArcPy expects them
- Resolve configuration values in `config.py`
- Local config files may contain machine-specific paths and should not be committed

## Testing

- Pure Python helpers should be unit-testable without ArcGIS Pro
- ArcPy-dependent tests should be clearly separated or marked
- Do not mock ArcPy excessively just to increase test counts
- Prefer testing deterministic logic outside ArcPy and keeping ArcPy integration code thin
- Useful pure-Python test targets include naming rules, calculations, parameter validation, configuration parsing, and dataset-selection rules

## When generating code

Before editing:

1. Inspect the relevant config model and workflow module.
2. If the task is a refactor or migration, read the closest example in `docs/case-studies.md`.
3. Identify which logic truly requires ArcPy.
4. Identify hidden assumptions about fields, geometry, spatial reference, naming, paths, or session state.
5. Keep new dependencies minimal.
6. Preserve Windows and ArcGIS Pro compatibility.
7. Add or update tests for pure logic when possible.

When a task involves unknown GIS data, ask the code to validate inputs instead of inventing schema assumptions.

When adapting this template to an existing script, change structure incrementally and preserve a verifiable baseline such as output names, feature counts, or known field values.

## Definition of done

A change is complete when:

- Paths are configurable
- Errors are actionable
- Reusable code is not tied to one analyst's machine
- Important GIS assumptions are visible or validated
- Pure logic has tests where useful
- ArcPy behavior remains explicit
- Destructive actions are deliberate
- README, config examples, or supporting docs are updated if the user-facing workflow changed
