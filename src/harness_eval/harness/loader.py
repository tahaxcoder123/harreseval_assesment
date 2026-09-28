"""Loader for agent harnesses."""
import os
from pathlib import Path
from typing import Union
import yaml
from harness_eval.models import HarnessConfig


def load_harness(harness_path: Union[str, Path]) -> HarnessConfig:
    """Loads a harness definition from directory containing config.yaml."""
    path = Path(harness_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Harness directory does not exist: {path}")

    config_file = path / "config.yaml"
    if not config_file.exists():
        # Fallback to config.yml
        config_file = path / "config.yml"
        if not config_file.exists():
            raise FileNotFoundError(f"Missing config.yaml in harness directory: {path}")

    with open(config_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    # If name not provided, use directory name
    if "name" not in data:
        data["name"] = path.name

    # Check for AGENTS.md
    agents_path = path / data.get("agents_file", "AGENTS.md")
    if agents_path.exists():
        data["metadata"] = data.get("metadata", {})
        data["metadata"]["agents_file_present"] = True

    # Validate referenced prompt file if specified
    if "system_prompt" in data and data["system_prompt"]:
        prompt_path = path / data["system_prompt"]
        if prompt_path.exists():
            with open(prompt_path, "r", encoding="utf-8") as pf:
                data["metadata"]["prompt_preview"] = pf.read(150)

    return HarnessConfig(**data)
