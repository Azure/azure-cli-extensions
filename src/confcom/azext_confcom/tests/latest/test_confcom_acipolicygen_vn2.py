# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import contextlib
import io
import json
import os
import pytest

from azext_confcom import config
from azext_confcom.custom import (
    _validate_allow_kubeproxy,
    acipolicygen_confcom,
)
from deepdiff import DeepDiff
from knack.util import CLIError


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


def test_acipolicygen_virtual_node_yaml_allow_kubeproxy():
    os.chdir(CONFCOM_DIR)
    virtual_node_yaml_path = os.path.join(
        SAMPLES_ROOT,
        "basic_command_args",
        "virtual_node.yaml",
    )

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
            platform="linux/amd64",
            exclude_default_fragments=True,
            allow_kubeproxy=True,
        )

    actual_policy = buffer.getvalue()
    fragments_start = actual_policy.index("fragments := ") + len("fragments := ")
    fragments_end = actual_policy.index("\n\ncontainers :=", fragments_start)
    fragments = json.loads(actual_policy[fragments_start:fragments_end])
    assert fragments == [config.KUBE_PROXY_REGO_FRAGMENT]


def test_allow_kubeproxy_accepts_vn2_json(tmp_path):
    input_path = tmp_path / "input.json"
    input_path.write_text('{"scenario": "vn2"}', encoding="utf-8")

    _validate_allow_kubeproxy(
        allow_kubeproxy=True,
        input_path=str(input_path),
        virtual_node_yaml_path=None,
        platform="linux/amd64",
    )


def test_acipolicygen_vn2_json_allow_kubeproxy(tmp_path):
    input_path = tmp_path / "input.json"
    input_path.write_text(
        json.dumps(
            {
                "version": "1.0",
                "scenario": "vn2",
                "containers": [
                    {
                        "name": "container1",
                        "properties": {
                            "image": "mcr.microsoft.com/azurelinux/distroless/base:3.0",
                        },
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        acipolicygen_confcom(
            input_path=str(input_path),
            arm_template=None,
            arm_template_parameters=None,
            image_name=None,
            virtual_node_yaml_path=None,
            infrastructure_svn=None,
            tar_mapping_location=None,
            outraw_pretty_print=True,
            platform="linux/amd64",
            allow_kubeproxy=True,
        )

    actual_policy = buffer.getvalue()
    fragments_start = actual_policy.index("fragments := ") + len("fragments := ")
    fragments_end = actual_policy.index("\n\ncontainers :=", fragments_start)
    fragments = json.loads(actual_policy[fragments_start:fragments_end])
    assert config.KUBE_PROXY_REGO_FRAGMENT in fragments


@pytest.mark.parametrize(
    "input_contents,virtual_node_yaml_path,platform",
    [
        ('{"scenario": "aci"}', None, "linux/amd64"),
        (None, None, "linux/amd64"),
        (None, "pod.yaml", "windows/amd64"),
    ],
)
def test_allow_kubeproxy_rejects_non_vn2_sources(
    tmp_path,
    input_contents,
    virtual_node_yaml_path,
    platform,
):
    input_path = None
    if input_contents is not None:
        input_file = tmp_path / "input.json"
        input_file.write_text(input_contents, encoding="utf-8")
        input_path = str(input_file)

    with pytest.raises(CLIError):
        _validate_allow_kubeproxy(
            allow_kubeproxy=True,
            input_path=input_path,
            virtual_node_yaml_path=virtual_node_yaml_path,
            platform=platform,
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
