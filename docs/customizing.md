# Customizing the Starter for Your ArcPy Workflow

This repository is a starting structure, not a framework you have to preserve exactly.

The safest way to use it is to begin with a real GIS task, keep the parts that solve an actual maintenance problem, and delete the example pieces you do not need.

If you already have a working script, do not rewrite it from scratch just to fit this template. Migrate it in small steps and verify that its behavior stays the same.

## Before you change the structure

Capture what the current workflow does while it still works.

Write down:

- the inputs it reads,
- the outputs it creates or changes,
- the parameters a user is expected to change,
- any assumptions about fields, geometry, spatial reference, or layer names,
- any destructive operations,
- whether it expects to run inside ArcGIS Pro or from an ArcGIS Pro Python environment,
- one small dataset you can use to verify the migrated version.

For important workflows, also record basic baseline results such as feature counts, output names, or known field values. The goal is to distinguish a structural refactor from a behavior change.

---

## Path 1: Turn one working script into a small project

Choose this path when you have a single `.py` file that is useful but is accumulating hard-coded paths, parameters, helper functions, or repeated edits.

### Keep

```text
AGENTS.md
config/
scripts/
src/arcpy_project/
tests/
```

### Change

1. Rename `arcpy_project` to a package name that describes your workflow or project.
2. Copy `config/example.yaml` to a project-specific example and replace the buffer settings with your own user-adjustable values.
3. Replace `buffer_features.py` with a workflow module for your operation.
4. Keep `scripts/run_workflow.py` as a thin entry point that loads configuration, configures logging, calls the workflow, and reports the result.
5. Move only reusable or testable logic out of the workflow. Do not split functions into separate modules just because you can.
6. Add tests for deterministic logic such as naming rules, calculations, parameter validation, and configuration parsing.

### A good first migration

If your current script looks roughly like this:

```python
import arcpy

input_fc = r"C:\GIS\data.gdb\roads"
out_fc = r"C:\GIS\data.gdb\roads_buffer"
distance = "100 Feet"

arcpy.analysis.Buffer(input_fc, out_fc, distance)
```

Your first refactor does not need dependency injection, service classes, factories, or a plugin system.

A useful target is simply:

```text
config/local.yaml        # paths and distance
scripts/run_workflow.py  # command-line entry point
src/.../workflow.py      # ArcPy operation and validation
tests/                   # config or pure helper tests
```

See Case Study 1 in [`case-studies.md`](case-studies.md).

### Agent prompt

> I have an existing ArcPy script that works. Migrate it into this starter incrementally without changing behavior. First identify configuration values, ArcPy-dependent logic, pure Python logic, and side effects. Keep the project small. Follow `AGENTS.md`, `docs/customizing.md`, and Case Study 1 in `docs/case-studies.md`.

---

## Path 2: Organize a repeatable batch workflow

Choose this path when one script loops over many datasets, performs several geoprocessing steps, or contains repeated blocks for similar inputs.

The main problem in batch GIS code is often not file length. It is hidden assumptions about the data.

### Recommended structure

```text
config/
  example.yaml
scripts/
  run_batch.py
src/<your_package>/
  config.py
  logging_config.py
  workflows/
    batch_process.py
  validation.py          # only if validation is shared enough to justify it
tests/
  test_config.py
  test_naming.py
  test_selection_rules.py
```

### Make these decisions explicit

Before reorganizing the loop, identify:

- Which datasets should be processed?
- Which fields must exist?
- Which geometry types are valid?
- What spatial references are expected or allowed?
- How are output names generated?
- What happens when one dataset fails?
- Is rerunning the workflow safe?

Put changing operational values in configuration. Keep deterministic selection and naming rules in pure Python where practical. Use ArcPy at the boundary to inspect real GIS data and run geoprocessing tools.

### Avoid the "generic pipeline" trap

A batch workflow does not automatically need a workflow engine or a generic `Task` abstraction.

If the workflow is:

1. discover feature classes,
2. validate them,
3. project them,
4. calculate fields,
5. write outputs,

then five clear functions may be better than a configurable execution framework.

See Case Study 2 in [`case-studies.md`](case-studies.md).

### Agent prompt

> Refactor this batch ArcPy script using the starter's conventions. Preserve output behavior. Identify hidden assumptions about dataset selection, schema, geometry, spatial reference, naming, and reruns before changing structure. Keep ArcPy integration explicit and extract only deterministic logic that benefits from testing. Follow `AGENTS.md` and Case Study 2 in `docs/case-studies.md`.

---

## Path 3: Use the project behind an ArcGIS Pro script tool or Python toolbox

Choose this path when the user experience should remain inside ArcGIS Pro.

The ArcGIS Pro tool should be an adapter around the project, not the place where all workflow logic lives.

### Recommended split

```text
src/<your_package>/
  config.py
  workflows/
    update_assets.py
scripts/
  run_workflow.py
  script_tool.py
```

Or, if you use a Python toolbox:

```text
src/<your_package>/
  workflows/
    update_assets.py
toolbox/
  project_tools.pyt
```

The script-tool or toolbox layer can handle ArcGIS Pro-specific UI concerns such as:

- `arcpy.GetParameterAsText`,
- derived output parameters,
- `arcpy.AddMessage`, `AddWarning`, and `AddError`,
- tool parameter validation,
- interaction with the current ArcGIS Pro session when the workflow truly requires it.

The reusable workflow module should still own the actual operation.

### Example wrapper

```python
import arcpy

from your_package.workflows.update_assets import run_update


def main() -> None:
    input_features = arcpy.GetParameterAsText(0)
    output_features = arcpy.GetParameterAsText(1)

    result = run_update(input_features, output_features)
    arcpy.SetParameterAsText(1, result.output_features)
    arcpy.AddMessage(
        f"Created {result.output_count} features: {result.output_features}"
    )


if __name__ == "__main__":
    main()
```

This lets the same workflow remain understandable outside the tool UI and makes it easier to add a command-line runner, scheduled execution, or automated tests later.

### When `CURRENT` is appropriate

`arcpy.mp.ArcGISProject("CURRENT")` is useful when the workflow intentionally operates on the open ArcGIS Pro project. Do not introduce `CURRENT` merely because a script tool runs inside Pro. Prefer explicit datasets and project paths when the workflow can operate without session state.

### Agent prompt

> Adapt this project for an ArcGIS Pro script tool. Keep the script-tool file thin: parameter input, messages, calling the reusable workflow, and derived outputs. Do not move the main geoprocessing logic into the tool wrapper. Use `CURRENT` only if the task truly depends on the active ArcGIS Pro project. Follow `AGENTS.md` and `docs/customizing.md`.

---

## If the workflow modifies important data

If your script edits source data in place, deletes fields, overwrites production outputs, republishes services, or performs another hard-to-reverse action, read Case Study 3 in [`case-studies.md`](case-studies.md).

A useful default is to separate:

1. **build the candidate result**, and
2. **promote or replace the real result**.

The exact promotion step depends on your environment. It might be a file geodatabase replacement, enterprise geodatabase load, hosted layer publish, or manual review. This starter intentionally does not invent that deployment decision for you.

---

## What to rename

At minimum, most projects should rename:

- `arcpy_project` to the actual package name,
- the example workflow module,
- the example config keys,
- the executable script description,
- project metadata in `pyproject.toml`.

Search the repository for `arcpy_project`, `buffer`, and `example_buffer_project` after renaming so you do not leave stale example references behind.

## What you can delete

Delete example code once it has taught you the pattern.

You do not need to keep:

- the buffer workflow,
- buffer-specific tests,
- config fields your project does not use,
- documentation sections that no longer describe the project.

Do keep the general guidance in `AGENTS.md` unless your environment has a reason to change it.

## What not to copy blindly from generic Python templates

ArcPy has constraints that ordinary Python packages do not.

Be cautious about introducing:

- a new Python version that does not match ArcGIS Pro,
- Conda-forge packages simply because a generic setup guide uses them,
- Docker as the default ArcPy runtime,
- Unix-only paths or shell commands,
- aggressive ArcPy mocking,
- abstractions designed mainly to hide ArcPy rather than make the workflow clearer.

The ArcGIS Pro Python environment is part of the application. Treat compatibility with that environment as a project requirement.

## A practical definition of done

A migrated project is in good shape when:

- another user can provide their own paths without editing reusable Python code,
- important GIS assumptions are visible or validated,
- the executable entry point is easy to understand,
- ArcPy-dependent code is easy to identify,
- deterministic rules can be tested without ArcPy where useful,
- destructive actions are deliberate,
- failures tell the operator what input or assumption caused the problem,
- an AI coding agent can identify where to make a change without rewriting unrelated parts of the workflow.

That is enough structure for many real ArcPy projects.
