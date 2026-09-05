# ArcPy Refactoring Case Studies

These examples show how ordinary ArcPy scripts can grow into maintainable projects without turning GIS automation into a software architecture exercise.

They are intentionally written from the perspective of a GIS analyst who already has a script that works. The goal is not to rewrite working code for style points. The goal is to make the next change safer, make failures easier to understand, and give both humans and coding agents enough structure to work confidently.

If you are using an AI coding assistant, these case studies are also examples of the kind of refactoring this starter expects. Read `AGENTS.md` first, then use the closest case study as a pattern.

---

## Case study 1: The useful one-off buffer script that became a team workflow

### The situation

A GIS analyst writes a small script to buffer a feature class. It works, so they reuse it. Then a coworker needs it. Then the buffer distance changes. Then the output location changes. Soon the script has become shared operational code even though it still looks like a one-off.

### Before

```python
import arcpy

arcpy.env.overwriteOutput = True

input_fc = r"C:\Users\danny\Documents\GIS\Project\data.gdb\poles"
output_fc = r"C:\Users\danny\Documents\GIS\Project\data.gdb\poles_buffer"

print("Starting")
print(arcpy.management.GetCount(input_fc)[0])

arcpy.analysis.Buffer(
    input_fc,
    output_fc,
    "500 Meters",
    dissolve_option="NONE",
)

print(arcpy.management.GetCount(output_fc)[0])
print("Done")
```

Nothing is obviously wrong with this script. For one person, on one machine, for one dataset, it may be exactly enough.

The problems appear when the workflow changes:

- The analyst's Windows profile and directory structure are embedded in the code.
- A user must edit Python to change an input, output, or distance.
- There is no early validation that the input exists.
- `print()` messages provide little context when this runs unattended.
- The value `"500 Meters"` combines configuration and formatting logic.
- Any test of the workflow requires importing ArcPy.
- An AI agent asked to "change the buffer workflow" has no clear boundary between configuration, business logic, and execution.

### After

Use the starter's existing separation of configuration, workflow code, and executable scripts.

```text
config/
  local.yaml
scripts/
  run_workflow.py
src/arcpy_project/
  config.py
  logging_config.py
  workflows/
    buffer_features.py
tests/
  test_config.py
  test_workflow_helpers.py
```

Machine-specific values move to local YAML:

```yaml
paths:
  input_features: C:/GIS/Projects/PoleStudy/data.gdb/poles
  output_features: C:/GIS/Projects/PoleStudy/data.gdb/poles_buffer

buffer:
  distance: 500
  units: Meters
  dissolve_option: NONE
```

The executable script becomes a thin coordinator:

```python
config = load_buffer_config(args.config)
logger = configure_logging(config.log_level)

logger.info("Starting buffer workflow")
result = run_buffer(config)
logger.info(
    "Finished buffer workflow: %s -> %s features at %s",
    result.input_count,
    result.output_count,
    result.output_features,
)
```

The ArcPy-specific workflow validates its dependency and its input before doing work:

```python
if not arcpy.Exists(config.input_features):
    raise FileNotFoundError(
        f"Input features not found: {config.input_features}"
    )

input_count = int(arcpy.management.GetCount(config.input_features)[0])
distance = format_distance(config.distance, config.units)

arcpy.analysis.Buffer(
    in_features=config.input_features,
    out_feature_class=config.output_features,
    buffer_distance_or_field=distance,
    dissolve_option=config.dissolve_option,
)
```

And the pure formatting rule can be tested without ArcGIS Pro:

```python
def format_distance(distance: float, units: str) -> str:
    value = int(distance) if float(distance).is_integer() else distance
    return f"{value} {units}"
```

### What improved

The GIS operation did not become more complicated. The surrounding decisions became explicit.

The analyst can now change paths and parameters without editing Python. A teammate can create their own `local.yaml`. An agent can change validation without touching command-line parsing. Pure Python behavior can be tested in a normal environment. ArcPy remains concentrated in the part of the project that actually needs it.

### The structural lesson

When a one-off script starts accumulating users, parameters, or repeated edits, separate **values that change** from **logic that should stay stable**.

Do not split every ten lines into a new module. Start with three boundaries:

1. configuration,
2. reusable workflow logic,
3. a thin entry point.

### Prompt to give an agent

> Refactor this working ArcPy script into the structure used by this repository. Preserve behavior. Move machine-specific paths and user-adjustable values into YAML, keep ArcPy-dependent work in a workflow module, keep the executable script thin, and extract pure Python helpers only where they are useful to test. Follow `AGENTS.md` and use Case Study 1 in `docs/case-studies.md` as the pattern.

---

## Case study 2: The batch script with hidden schema assumptions

### The situation

A script processes several feature classes in a geodatabase. It grew by copying and modifying blocks of ArcPy code. It works on the original data, but nobody is quite sure what assumptions it makes about field names, geometry, spatial reference, or output naming.

This is common in GIS because the data model is often implicit in the analyst's head.

### Before

```python
import arcpy

workspace = r"D:\Projects\Inspection\inspection.gdb"
arcpy.env.workspace = workspace
arcpy.env.overwriteOutput = True

for fc in arcpy.ListFeatureClasses():
    print(f"Processing {fc}")

    # Assumes every feature class has these fields.
    arcpy.management.CalculateField(
        fc,
        "STATUS_TXT",
        "'Needs Review' if !STATUS! == 0 else 'Complete'",
        "PYTHON3",
    )

    # Assumes every input can be projected the same way.
    out_fc = f"{workspace}\\{fc}_wm"
    arcpy.management.Project(fc, out_fc, 3857)
```

The loop is short, but it contains several invisible contracts:

- every feature class is intended to be processed,
- every feature class has `STATUS` and `STATUS_TXT`,
- the fields are compatible with the expression,
- every input has a spatial reference that can be projected,
- WKID 3857 is appropriate for every output,
- every generated name is valid and unique,
- rerunning the script is safe,
- partial completion is acceptable if feature class number six fails.

An AI agent can easily make this script look cleaner without making those assumptions safer.

### After

First, make the data contract visible.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class DatasetRequirements:
    required_fields: tuple[str, ...]
    allowed_geometry_types: tuple[str, ...]


REQUIREMENTS = DatasetRequirements(
    required_fields=("STATUS", "STATUS_TXT"),
    allowed_geometry_types=("Point", "Polyline", "Polygon"),
)
```

Keep deterministic naming outside ArcPy:

```python
def projected_name(dataset_name: str, suffix: str = "_projected") -> str:
    name = dataset_name.strip()
    if not name:
        raise ValueError("dataset_name cannot be empty")
    return f"{name}{suffix}"
```

Then use ArcPy to validate the things only ArcPy can know:

```python
def validate_dataset(dataset: str, requirements: DatasetRequirements) -> None:
    import arcpy

    if not arcpy.Exists(dataset):
        raise FileNotFoundError(f"Dataset not found: {dataset}")

    description = arcpy.Describe(dataset)
    geometry_type = getattr(description, "shapeType", None)
    if geometry_type not in requirements.allowed_geometry_types:
        raise ValueError(
            f"Unsupported geometry type for {dataset}: {geometry_type}"
        )

    fields = {field.name for field in arcpy.ListFields(dataset)}
    missing = set(requirements.required_fields) - fields
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise ValueError(f"{dataset} is missing required fields: {missing_text}")
```

The workflow can now separate discovery, validation, and processing:

```python
def process_dataset(dataset: str, output_workspace: str, output_wkid: int) -> str:
    import arcpy

    validate_dataset(dataset, REQUIREMENTS)

    dataset_name = arcpy.Describe(dataset).baseName
    output_name = projected_name(dataset_name)
    output_fc = str(Path(output_workspace) / output_name)

    arcpy.management.CalculateField(
        dataset,
        "STATUS_TXT",
        "'Needs Review' if !STATUS! == 0 else 'Complete'",
        "PYTHON3",
    )

    arcpy.management.Project(dataset, output_fc, output_wkid)
    return output_fc
```

For a production project, you may decide the field calculation should also happen on a copy rather than the source. The important point is that the code now exposes that choice instead of hiding it inside a loop.

### What improved

The workflow now fails with a useful explanation before ArcPy reaches a more cryptic geoprocessing error. Naming rules can be tested without ArcPy. Schema assumptions are visible in one place. The output projection becomes configuration rather than a buried constant.

Most importantly, future changes become reviewable. If the requirement changes from "all feature classes need `STATUS`" to "only inspections need `STATUS`," there is an obvious place to encode that decision.

### The structural lesson

GIS scripts often have more **data assumptions** than code complexity. Make those assumptions first-class.

Before adding classes, frameworks, or abstractions, identify:

1. required fields,
2. allowed geometry types,
3. spatial-reference expectations,
4. naming rules,
5. which datasets are in scope.

Validate those explicitly at the boundary of the workflow.

### Prompt to give an agent

> Refactor this batch ArcPy workflow without changing its intended outputs. First identify and document its hidden assumptions about fields, geometry, spatial reference, dataset selection, and output naming. Move deterministic naming and selection rules into pure Python helpers where practical. Add ArcPy validation at the workflow boundary and make failures actionable. Do not invent schema requirements that are not present in the current script or data contract. Follow `AGENTS.md` and use Case Study 2 as the pattern.

---

## Case study 3: The script that edits important data in place

### The situation

A useful maintenance script updates an existing feature class directly. It started as an interactive tool run by the person who wrote it, but now it is being scheduled, handed to coworkers, or extended by an AI agent.

The biggest risk is no longer whether the Python works. The risk is whether a partial failure leaves the GIS data in an ambiguous state.

### Before

```python
import arcpy

assets = r"C:\GIS\Operations\operations.gdb\assets"

arcpy.management.CalculateField(
    assets,
    "RISK_CLASS",
    "classify(!SCORE!)",
    "PYTHON3",
    code_block="""
def classify(score):
    if score >= 80:
        return 'High'
    if score >= 50:
        return 'Medium'
    return 'Low'
""",
)

arcpy.management.DeleteField(assets, ["OLD_SCORE"])
print("Updated assets")
```

Again, this may be perfectly reasonable for a small, controlled job. But once the workflow matters operationally, several questions appear:

- What happens if `CalculateField` succeeds but `DeleteField` fails?
- What happens if `SCORE` contains nulls or unexpected values?
- Was the input feature count what the operator expected?
- Can the user inspect the result before the original is changed?
- Does the script leave enough information to understand what happened later?
- Can the classification rule be tested without running ArcPy?

### After

Start by moving the business rule out of the geoprocessing expression:

```python
def classify_risk(score: float | None) -> str:
    if score is None:
        raise ValueError("SCORE cannot be null")
    if score >= 80:
        return "High"
    if score >= 50:
        return "Medium"
    return "Low"
```

That rule can be unit tested independently:

```python
def test_classify_risk_boundaries():
    assert classify_risk(49.9) == "Low"
    assert classify_risk(50) == "Medium"
    assert classify_risk(80) == "High"
```

For the ArcPy workflow, stage the work in an explicit output instead of immediately mutating the source:

```python
def build_updated_assets(input_features: str, staged_output: str) -> str:
    import arcpy

    if not arcpy.Exists(input_features):
        raise FileNotFoundError(f"Input features not found: {input_features}")

    fields = {field.name for field in arcpy.ListFields(input_features)}
    required = {"SCORE", "RISK_CLASS"}
    missing = required - fields
    if missing:
        raise ValueError(
            "Input is missing required fields: " + ", ".join(sorted(missing))
        )

    arcpy.management.CopyFeatures(input_features, staged_output)

    before_count = int(arcpy.management.GetCount(input_features)[0])

    with arcpy.da.UpdateCursor(staged_output, ["SCORE", "RISK_CLASS"]) as cursor:
        for score, _ in cursor:
            cursor.updateRow((score, classify_risk(score)))

    after_count = int(arcpy.management.GetCount(staged_output)[0])
    if before_count != after_count:
        raise RuntimeError(
            f"Row count changed unexpectedly: {before_count} -> {after_count}"
        )

    return staged_output
```

The operator can now inspect or validate the staged result before a separate, explicit promotion step replaces or publishes anything important.

That promotion step should match the environment. It might mean replacing a file-geodatabase feature class, loading into an enterprise staging table, publishing a hosted feature layer, or simply handing the staged output to a reviewer. The starter does not assume one deployment model.

The key is that **building the candidate result** and **promoting the candidate result** are different actions.

### What improved

The classification rule is testable. Null handling is explicit. Required fields are validated. Row counts provide a basic integrity check. The source dataset is not modified until the workflow has produced a complete candidate output.

Logs can now describe the staged path, row counts, and validation result. If something fails, the operator has a much clearer answer to the question: "What did the script change?"

### The structural lesson

The more important the data, the less a workflow should rely on "it usually finishes."

When an ArcPy script performs destructive or hard-to-reverse operations:

1. validate before changing data,
2. isolate pure business rules where practical,
3. build a staged result,
4. check simple invariants such as row counts and required fields,
5. make the final replace/publish action explicit.

You do not need a complex transaction framework to get most of the safety benefit.

### Prompt to give an agent

> Refactor this ArcPy maintenance script to reduce the risk of partial or destructive updates. Preserve the intended business rule, but separate pure calculations from ArcPy where practical, validate required inputs and fields, write changes to a staged output, and add simple integrity checks before any replace or publish step. Do not invent an enterprise deployment process. Keep the promotion step explicit and adaptable to the user's environment. Follow `AGENTS.md` and use Case Study 3 as the pattern.

---

## Choosing the closest case study

Use Case Study 1 when the main problem is **hard-coded values and a growing one-off script**.

Use Case Study 2 when the main problem is **batch processing and hidden assumptions about GIS data**.

Use Case Study 3 when the main problem is **risk from in-place edits, destructive operations, or partial failure**.

Real projects often contain pieces of all three. Apply only the structure that solves a concrete problem. The point of this starter is to make ArcPy automation easier to change and easier to trust, not to maximize the number of files in the repository.
