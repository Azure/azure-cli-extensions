# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import pytest

from azext_confcom.command.containers_from_vn2 import containers_from_vn2
from deepdiff import DeepDiff


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), ".."))
CONFCOM_DIR = os.path.abspath(os.path.join(TEST_DIR, "..", "..", ".."))
SAMPLES_ROOT = os.path.abspath(os.path.join(TEST_DIR, "..", "..", "..", "samples", "vn2"))


def _normalize_env_rules(container: dict) -> dict:
    normalized = json.loads(json.dumps(container))
    env_rules = normalized.get("env_rules") or []
    normalized_rules = []
    for rule in env_rules:
        pattern = rule.get("pattern")
        if pattern is None:
            name = rule.get("name") or ""
            value = rule.get("value") or ""
            pattern = f"{name}={value}"
        normalized_rules.append({
            "pattern": pattern,
            "strategy": rule.get("strategy"),
            "required": rule.get("required", False),
        })
    normalized["env_rules"] = normalized_rules
    return normalized


def _normalize_containers(containers: list[dict]) -> list[dict]:
    return [_normalize_env_rules(container) for container in containers]


@pytest.mark.parametrize(
    "sample_directory",
    sorted(
        d for d in os.listdir(SAMPLES_ROOT)
        if os.path.isdir(os.path.join(SAMPLES_ROOT, d))
    )
)
def test_containers_from_vn2(sample_directory):

    os.chdir(CONFCOM_DIR)

    virtual_node_yaml_path = os.path.join(SAMPLES_ROOT, sample_directory, "virtual_node.yaml")
    expected_containers_path = os.path.join(SAMPLES_ROOT, sample_directory, "containers.inc.rego")

    with open(expected_containers_path, "r", encoding="utf-8") as f:
        expected_containers = json.load(f)

    actual_containers = json.loads(
        containers_from_vn2(
            template=virtual_node_yaml_path,
            container_name=None,
        )
    )
    actual_containers = _normalize_containers(actual_containers)
    expected_normalized = _normalize_containers(expected_containers)
    assert DeepDiff(actual_containers, expected_normalized, ignore_order=True) == {}, (
        "Container list mismatch, actual output for "
        f"{os.path.join(sample_directory, 'containers.inc.rego')}\n"
        f"{actual_containers}"
    )

    for expected_container in expected_containers:
        container_name = expected_container.get("name")
        actual_container_list = json.loads(
            containers_from_vn2(
                template=virtual_node_yaml_path,
                container_name=container_name,
            )
        )
        assert len(actual_container_list) == 1, (
            "Expected single container definition for "
            f"{os.path.join(sample_directory, 'containers.inc.rego')}:{container_name}"
        )
        actual_container = _normalize_env_rules(actual_container_list[0])
        expected_container = _normalize_env_rules(expected_container)
        assert DeepDiff(actual_container, expected_container, ignore_order=True) == {}, (
            "Container mismatch, actual output for "
            f"{os.path.join(sample_directory, 'containers.inc.rego')}:{container_name}\n"
            f"{actual_container}"
        )
