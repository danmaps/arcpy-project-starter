# ArcPy Project Starter

A practical project template for GIS analysts and developers who want to turn one-off ArcPy scripts into maintainable Python projects.

This starter is designed for real ArcGIS Pro work on Windows. It gives you an opinionated structure for configuration, logging, testing, reusable workflows, and AI-assisted development without pretending ArcPy behaves like a normal cross-platform Python library.

## What this gives you

- A clean `src/` package layout
- YAML configuration instead of hard-coded paths
- Centralized logging
- A small reusable ArcPy workflow
- A command-line runner pattern
- Tests that separate pure Python logic from ArcPy-dependent code
- Canonical `AGENTS.md` guidance for AI coding agents
- `CLAUDE.md` and GitHub Copilot compatibility instructions that point agents to the same rules
- Three ArcPy-specific before/after case studies that show how a working script can evolve safely
- A customization playbook for single scripts, batch workflows, and ArcGIS Pro script tools/Python toolboxes
- ArcGIS Pro-aware `.gitignore`
- A structure you can copy for actual production GIS automation

## Project layout

```text
arcpy-project-starter/
├── .github/
│   └── copilot-instructions.md
├── AGENTS.md
├── CLAUDE.md
├── LICENSE.txt
├── NOTICE.txt
├── README.md
├── pyproject.toml
├── .gitignore
├── config/
│   └── example.yaml
├── docs/
│   ├── case-studies.md
│   ├── customizing.md
│   └── getting-started.md
├── scripts/
│   └── run_workflow.py
├── src/
│   └── arcpy_project/
│       ├── __init__.py
│       ├── config.py
│       ├── logging_config.py
│       └── workflows/
│           ├── __init__.py
│           └── buffer_features.py
└── tests/
    ├── test_config.py
    └── test_workflow_helpers.py
```

## Quick start

1. Clone or unzip the project.
2. Open the ArcGIS Pro Python Command Prompt.
3. Install the project in editable mode:

```powershell
python -m pip install -e .
```

4. Copy the example config:

```powershell
Copy-Item config\example.yaml config\local.yaml
```

5. Edit `config\local.yaml` with your own paths.
6. Run the example workflow:

```powershell
python scripts\run_workflow.py --config config\local.yaml
```

## If you already have an ArcPy script

You do not need to start over.

Read [`docs/customizing.md`](docs/customizing.md) for a step-by-step migration path, then use the closest example in [`docs/case-studies.md`](docs/case-studies.md):

1. a one-off script that grew into a shared workflow,
2. a batch script with hidden schema assumptions,
3. a maintenance script that edits important data in place.

Each case study includes a before/after example, the structural lesson, and a prompt you can give an AI coding assistant.

## Why this structure

Most GIS automation starts as a useful script and then accumulates hard-coded paths, duplicated environment settings, print statements, and hidden assumptions. This template separates the parts that change from the parts that should stay stable.

The goal is not abstraction for its own sake. The goal is to make the next change safer and easier.

## Testing

Run pure-Python tests from any normal Python environment:

```powershell
python -m pytest
```

Tests that require `arcpy` should be run from the ArcGIS Pro Python environment. Keep as much logic as possible outside ArcPy-specific code so ordinary tests stay fast and portable.

## AI-assisted development

`AGENTS.md` is the canonical repository guidance. It explains ArcGIS Pro constraints, project conventions, path handling, testing boundaries, and how generated code should interact with ArcPy.

`CLAUDE.md` and `.github/copilot-instructions.md` are intentionally thin compatibility files that direct supported coding agents back to the same source of truth.

For refactoring work, `docs/case-studies.md` gives the agent concrete examples of the kind of project evolution this starter is designed to encourage.

## Using this as your own project

Rename the `arcpy_project` package, replace the example workflow, and update the config keys. Keep the surrounding structure only where it helps your workflow.

For three common adaptation paths and ready-to-use agent prompts, see [`docs/customizing.md`](docs/customizing.md).

## License

ArcPy Project Starter is **proprietary software, not open-source software**.

An individual purchase licenses one person to use and modify the Starter Kit for unlimited personal, professional, employer, and client projects. Software and project-specific deliverables you build with the Starter Kit may be used and distributed normally.

The reusable Starter Kit itself may not be resold, published, shared as a template, placed in a public repository, or distributed to other people for their independent reuse. Multiple developers who need direct access to the reusable Starter Kit require separate individual licenses or a team/organization license.

See [`LICENSE.txt`](LICENSE.txt) for the complete terms and [`NOTICE.txt`](NOTICE.txt) for third-party and trademark notices.

Copyright (c) 2026 Danny McVey. All rights reserved.
