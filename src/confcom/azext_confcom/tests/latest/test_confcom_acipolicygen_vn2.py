# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import contextlib
import io
import json
import os
import pytest

from azext_confcom.custom import acipolicygen_confcom
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
def test_acipolicygen_virtual_node_yaml(sample_directory):

    os.chdir(CONFCOM_DIR)

    virtual_node_yaml_path = os.path.join(SAMPLES_ROOT, sample_directory, "virtual_node.yaml")
    expected_policy_path = os.path.join(SAMPLES_ROOT, sample_directory, "policy.rego")

    with open(expected_policy_path, "r", encoding="utf-8") as f:
        expected_policy = f.read()

    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        acipolicygen_confcom(
            input_path=None,
            arm_template=None,
            arm_template_parameters=None,
            image_name=None,
            virtual_node_yaml_path=virtual_node_yaml_path,
            infrastructure_svn=None,
            tar_mapping_location=None,
            outraw_pretty_print=True,
        )
    actual_policy = buffer.getvalue()

    assert actual_policy == expected_policy, (
        "Policy generation mismatch, actual output for "
        f"{os.path.join(sample_directory, 'policy.rego')}:\n{actual_policy}"
    )


@pytest.mark.parametrize(
    "sample_directory",
    sorted(
        d for d in os.listdir(SAMPLES_ROOT)
        if os.path.isdir(os.path.join(SAMPLES_ROOT, d))
    )
)
def test_acipolicygen_virtual_node_container_defs(sample_directory):

    os.chdir(CONFCOM_DIR)

    containers_defs_path = os.path.join(SAMPLES_ROOT, sample_directory, "containers.inc.rego")
    expected_policy_path = os.path.join(SAMPLES_ROOT, sample_directory, "policy.rego")

    with open(expected_policy_path, "r", encoding="utf-8") as f:
        expected_policy = f.read()

    with open(containers_defs_path, "r", encoding="utf-8") as f:
        container_defs = json.load(f)

    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        acipolicygen_confcom(
            input_path=None,
            arm_template=None,
            arm_template_parameters=None,
            image_name=None,
            virtual_node_yaml_path=None,
            infrastructure_svn=None,
            tar_mapping_location=None,
            outraw_pretty_print=True,
            container_definitions=container_defs
        )
    actual_policy = buffer.getvalue()

    actual_prefix, actual_containers, actual_suffix = _split_policy(actual_policy)
    expected_prefix, expected_containers, expected_suffix = _split_policy(expected_policy)

    assert actual_prefix + actual_suffix == expected_prefix + expected_suffix, (
        "Policy generation mismatch outside containers, actual output for "
        f"{os.path.join(sample_directory, 'policy.rego')}:\n{actual_policy}"
    )

    actual_container_defs = _normalize_containers(json.loads(actual_containers))
    expected_container_defs = _normalize_containers(json.loads(expected_containers))
    assert DeepDiff(
        actual_container_defs,
        expected_container_defs,
        ignore_order=True,
    ) == {}, (
        "Policy generation mismatch, actual output for "
        f"{os.path.join(sample_directory, 'policy.rego')}:\n{actual_policy}"
    )


def _split_policy(policy_text: str) -> tuple[str, str, str]:
    marker = "containers := "
    marker_index = policy_text.find(marker)
    if marker_index == -1:
        raise AssertionError("containers block not found in policy output")

    json_start = policy_text.find("[", marker_index)
    json_end = policy_text.find("]\n\n", json_start)
    if json_end == -1:
        raise AssertionError("containers JSON block not found in policy output")

    containers_json = policy_text[json_start:json_end + 1]
    return policy_text[:json_start], containers_json, policy_text[json_end + 1:]
