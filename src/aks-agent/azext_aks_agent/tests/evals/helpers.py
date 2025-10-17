# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Utilities for AKS Agent eval tests."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

import yaml

MOCK_FILE = "mocks/response.txt"
AI_MARKER = "AI:"
REQUIRED_ENV_VARS: tuple[str, ...] = (
    "MODEL",
    "AKS_AGENT_RESOURCE_GROUP",
    "AKS_AGENT_CLUSTER",
    "KUBECONFIG",
    "AZURE_API_KEY",
    "AZURE_API_BASE",
    "AZURE_API_VERSION",
)
MANDATORY_TAGS: tuple[str, ...] = ("easy", "medium", "hard")


@dataclass(frozen=True)
class Scenario:
    """Represents a single eval scenario loaded from YAML."""

    name: str
    prompt: str
    expected_output: List[str]
    tags: List[str]
    path: Path
    before_commands: List[str]
    after_commands: List[str]
    resource_group: Optional[str]
    cluster_name: Optional[str]
    kubeconfig: Optional[str]
    env_overrides: Dict[str, str]
    evaluation_type: Optional[str]
    mock_path: Path


def load_scenarios(fixtures_root: Path) -> List[Scenario]:
    """Load all scenarios located beneath the fixtures root."""
    scenarios: List[Scenario] = []
    for yaml_path in sorted(fixtures_root.glob("**/test_case.yaml")):
        with yaml_path.open("r", encoding="utf-8") as handle:
            raw: Dict[str, Any] = yaml.safe_load(handle) or {}

        prompt = str(raw.get("user_prompt", "")).strip()
        if not prompt:
            raise ValueError(f"Scenario {yaml_path} missing 'user_prompt'")

        expected = _as_str_list(raw.get("expected_output"))
        if not expected:
            raise ValueError(f"Scenario {yaml_path} must define non-empty 'expected_output'")

        tags = _as_str_list(raw.get("tags"))
        if not any(tag in MANDATORY_TAGS for tag in tags):
            raise ValueError(
                f"Scenario {yaml_path} must include one of {MANDATORY_TAGS!r}"
            )

        before_commands = _as_command_list(raw.get("before_test"))
        after_commands = _as_command_list(raw.get("after_test"))
        env_overrides = _as_env_override(raw.get("test_env_vars"))
        evaluation_type = _parse_evaluation_type(raw.get("evaluation"))

        scenario = Scenario(
            name=yaml_path.parent.name,
            prompt=prompt,
            expected_output=expected,
            tags=tags,
            path=yaml_path,
            before_commands=before_commands,
            after_commands=after_commands,
            resource_group=_as_optional_str(raw.get("resource_group")),
            cluster_name=_as_optional_str(raw.get("cluster_name")),
            kubeconfig=_as_optional_str(raw.get("kubeconfig")),
            env_overrides=env_overrides,
            evaluation_type=evaluation_type,
            mock_path=yaml_path.parent,
        )
        scenarios.append(scenario)
    return scenarios


def extract_ai_answer(output: str) -> str:
    """Return the substring after the last AI marker."""
    index = output.rfind(AI_MARKER)
    if index == -1:
        raise ValueError("Could not locate 'AI:' marker in CLI output")
    return output[index + len(AI_MARKER) :].strip()


def find_missing_env_vars(env: Mapping[str, str]) -> List[str]:
    """Return a list of required environment variables that are missing or empty."""
    missing = [name for name in REQUIRED_ENV_VARS if not env.get(name)]
    return missing


def ensure_expected_output(expected: Iterable[str], answer: str) -> Optional[str]:
    """Verify each expected entry is present in the answer.

    Returns an error message when a check fails, otherwise ``None``.
    """
    for item in expected:
        if item not in answer:
            return f"Expected substring not found in AI response: {item!r}"
    return None


def _as_str_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        result: List[str] = []
        for item in value:
            if not isinstance(item, str):
                raise ValueError(f"List entries must be strings, got {type(item)!r}")
            result.append(item)
        return result
    raise ValueError(f"Expected string or list of strings, got {type(value)!r}")


def _as_command_list(value: Any) -> List[str]:
    commands = _as_str_list(value)
    return [cmd.strip() for cmd in commands if cmd.strip()]


def _as_env_override(value: Any) -> Dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError("test_env_vars must be a mapping of key/value strings")
    overrides: Dict[str, str] = {}
    for key, val in value.items():
        if not isinstance(key, str) or not isinstance(val, str):
            raise ValueError("test_env_vars entries must be strings")
        overrides[key] = val
    return overrides


def _as_optional_str(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    raise ValueError(f"Expected string for optional field, got {type(value)!r}")


def _parse_evaluation_type(value: Any) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ValueError("evaluation must be a mapping when provided")
    correctness = value.get("correctness")
    if correctness is None:
        return None
    if isinstance(correctness, dict):
        eval_type = correctness.get("type")
    else:
        eval_type = correctness
    if eval_type is None:
        return None
    if not isinstance(eval_type, str):
        raise ValueError("evaluation.correctness.type must be a string when provided")
    eval_type = eval_type.strip().lower()
    if eval_type and eval_type not in {"strict", "loose"}:
        raise ValueError(
            "evaluation.correctness.type must be one of {'strict', 'loose'}"
        )
    return eval_type or None


def load_mock_answer(scenario_dir: Path) -> str:
    """Load the mocked answer for a scenario."""
    mock_path = scenario_dir / MOCK_FILE
    if not mock_path.exists():
        raise FileNotFoundError(f"Mock response missing: {mock_path}")
    return mock_path.read_text(encoding="utf-8")


def save_mock_answer(scenario_dir: Path, answer: str) -> Path:
    """Persist the mocked answer for a scenario, returning the path."""
    mock_path = scenario_dir / MOCK_FILE
    mock_path.parent.mkdir(parents=True, exist_ok=True)
    mock_path.write_text(answer, encoding="utf-8")
    return mock_path
