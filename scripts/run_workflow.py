from __future__ import annotations

import argparse

from arcpy_project.config import load_buffer_config
from arcpy_project.logging_config import configure_logging
from arcpy_project.workflows.buffer_features import run_buffer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the example ArcPy buffer workflow.")
    parser.add_argument("--config", required=True, help="Path to YAML configuration file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
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


if __name__ == "__main__":
    main()
