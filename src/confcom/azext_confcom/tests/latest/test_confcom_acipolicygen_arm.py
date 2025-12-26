# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import base64
import contextlib
import copy
import io
import json
import os
import tempfile
import pytest
from itertools import product

from azext_confcom.custom import acipolicygen_confcom
from azext_confcom.lib.serialization import policy_deserialize



TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), ".."))
CONFCOM_DIR = os.path.abspath(os.path.join(TEST_DIR, "..", "..", ".."))
SAMPLES_ROOT = os.path.abspath(os.path.join(TEST_DIR, "..", "..", "..", "samples", "aci"))
FRAGMENTS_DIR = os.path.abspath(os.path.join(TEST_DIR, "..", "..", "..", "samples", "fragments"))
POLICIES_DIR = os.path.abspath(os.path.join(TEST_DIR, "..", "..", "..", "samples", "policies"))


POLICYGEN_ARGS = {
    "policy.rego": {},
    "policy_debug.rego": {"debug_mode": True},
    "policy_exclude_default_fragment.rego": {"exclude_default_fragments": True},
    "policy_infrastructure_svn.rego": {"infrastructure_svn": "99"},
    "policy_disable_stdio.rego": {"disable_stdio": True},
    "policy_fragment.rego": {
        "include_fragments": True,
        "fragments_json": os.path.join(FRAGMENTS_DIR, "fragment.json"),
    },
    "policy_fragment_plus_infrastructure_svn.rego": {
        "infrastructure_svn": "99",
        "include_fragments": True,
        "fragments_json": os.path.join(FRAGMENTS_DIR, "fragment.json"),
    },
}


@pytest.mark.parametrize(
    "sample_directory,generated_policy_path",
    product(os.listdir(SAMPLES_ROOT), POLICYGEN_ARGS.keys())
)
def test_acipolicygen(sample_directory, generated_policy_path):

    # Ensure we're always in the same dir because fragments input json defines
    # the path relative to the signed fragment to the current dir and cannot use
    # absolute paths
    os.chdir(CONFCOM_DIR)

    for failing_sample_directory, failing_generated_policy_paths in [
        ("multi_container_groups", ("policy_fragment.rego", "policy_fragment_plus_infrastructure_svn.rego")), # TODO: https://github.com/Azure/azure-cli-extensions/issues/9229
    ]:
        if (
            (sample_directory == failing_sample_directory or failing_sample_directory is None)
            and (generated_policy_path in failing_generated_policy_paths or failing_generated_policy_paths is None)
        ):
            pytest.skip("Skipping test due to known issue")

    arm_template_path = os.path.join(SAMPLES_ROOT, sample_directory, "arm_template.json")
    parameters_path = os.path.join(SAMPLES_ROOT, sample_directory, "parameters.json")
    if not os.path.isfile(parameters_path):
        parameters_path = None
    flags = POLICYGEN_ARGS[generated_policy_path]

    with open(os.path.join(SAMPLES_ROOT, sample_directory, generated_policy_path), "r", encoding="utf-8") as f:
        expected_policy = f.read()

    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        acipolicygen_confcom(
            input_path=None,
            arm_template=arm_template_path,
            arm_template_parameters=parameters_path,
            image_name=None,
            virtual_node_yaml_path=None,
            infrastructure_svn=flags.pop("infrastructure_svn", None),
            tar_mapping_location=None,
            outraw=True,
            **flags,
        )
    actual_policy = buffer.getvalue()

    assert actual_policy == expected_policy, f"Policy generation mismatch, actual output for {os.path.join(sample_directory, generated_policy_path)}:\n{actual_policy}"


def change(arm, path, value):
    new_arm = copy.deepcopy(arm)
    walk_arm = new_arm
    *parents, last = path
    for key in parents:
        walk_arm = walk_arm[key]
    walk_arm[last] = value
    return new_arm

@pytest.mark.parametrize(
    "case",
    [
        (
            # Change the container name
            lambda arm: change(
                arm,
                ("resources", 0, "properties", "containers", 0, "name"),
                "changedContainer",
            ),
            {
                "changedContainer": {
                    "values_changed": {
                        "name": [
                            {
                                "policy_value": "container1",
                                "tested_value": "changedContainer"
                            }
                        ]
                    }
                }
            },
        ),
        (
            # Change the container image
            lambda arm: change(
                arm,
                ("resources", 0, "properties", "containers", 0, "properties", "image"),
                "mcr.microsoft.com/azurelinux/distroless/base@sha256:50c24841324cdb36a268bb1288dd6f8bd5bcf19055c24f6aaa750a740a8be62d",
            ),
            {
                "container1": {
                    "values_changed": {
                        "layers": [
                            {
                                "policy_value": "243e1b3ce08093f2f0d9cd6a9eafde8737f64fec105ed59c346d309fbe760b58",
                                "tested_value": "9d7a71ed5b89b9f894e224959fb09908e77d905e12c3e7c16c4b4f6c38ecc947"
                            }
                        ]
                    }
                }
            },
        ),
        (
            # Change the container resources (shouldn't affect policy)
            lambda arm: change(
                arm,
                ("resources", 0, "properties", "containers", 0, "properties", "resources", "requests", "cpu"),
                "2",
            ),
            {},
        ),
    ]
)
def test_acipolicygen_arm_diff(case):

    change_arm, expected_diff = case

    arm_template_path = os.path.join(SAMPLES_ROOT, "minimal", "arm_template.json")

    # Make a temporary copy of the ARM template
    with tempfile.NamedTemporaryFile(mode="w+", delete=True) as arm_template_file:
        with open(arm_template_path, "r", encoding="utf-8") as f:
            arm_template_file.write(f.read())
            arm_template_file.flush()

        # Populate the arm template with a CCEPolicy field
        acipolicygen_confcom(
            input_path=None,
            arm_template=arm_template_file.name,
            arm_template_parameters=None,
            image_name=None,
            virtual_node_yaml_path=None,
            infrastructure_svn=None,
            tar_mapping_location=None,
        )
        arm_template_file.seek(0)

        # Modify the ARM template
        arm_template = json.load(arm_template_file)
        arm_template_file.seek(0)
        arm_template_file.truncate()
        json.dump(
            change_arm(arm_template),
            arm_template_file,
            indent=2,
        )
        arm_template_file.flush()
        arm_template_file.seek(0)

        # Get the diff between the original and modified ARM template
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            try:
                acipolicygen_confcom(
                    input_path=None,
                    arm_template=arm_template_file.name,
                    arm_template_parameters=None,
                    image_name=None,
                    virtual_node_yaml_path=None,
                    infrastructure_svn=None,
                    tar_mapping_location=None,
                    diff=True,
                )
            except SystemExit as e:
                ...
        try:
            diff = json.loads(buffer.getvalue())
        except json.JSONDecodeError:
            diff = {}

        assert diff == expected_diff


def test_acipolicygen_arm_diff_with_allow_all():

    arm_template_path = os.path.join(SAMPLES_ROOT, "minimal", "arm_template.json")

    # Make a temporary copy of the ARM template (with the allow_all policy)
    with tempfile.NamedTemporaryFile(mode="w+", delete=True) as arm_template_file:
        with open(arm_template_path, "r", encoding="utf-8") as f:
            with open(os.path.join(POLICIES_DIR, "allow_all.rego"), "r", encoding="utf-8") as p:
                arm_template = json.load(f)
                arm_template["resources"][0]["properties"]["confidentialComputeProperties"]["ccePolicy"] = base64.b64encode(p.read().encode("utf-8")).decode("utf-8")
                json.dump(arm_template, arm_template_file, indent=2)
                arm_template_file.flush()

        # Get the diff between the original and modified ARM template
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            try:
                acipolicygen_confcom(
                    input_path=None,
                    arm_template=arm_template_file.name,
                    arm_template_parameters=None,
                    image_name=None,
                    virtual_node_yaml_path=None,
                    infrastructure_svn=None,
                    tar_mapping_location=None,
                    diff=True,
                )
            except SystemExit as e:
                ...
        try:
            diff = json.loads(buffer.getvalue())
        except json.JSONDecodeError:
            diff = {}

        # --diff only compares container policies, allow all doesn't specify any containers
        assert diff == {
            "container1": "mcr.microsoft.com/azurelinux/distroless/base@sha256:1e77d97e1e39f22ed9c52f49b3508b4c1044cec23743df9098ac44e025f654f2 not found in policy",
            "pause-container": "None not found in policy"
        }


@pytest.mark.parametrize(
    "container_definitions",
    [
        ["{}"], # Single empty container definition (use all default values)
        ["{}", "{}"], # Two empty container definitions
        ["[{}]", "{}"], # Two empty container definitions, one in subarray
        ["[{}, {}]", "{}"], # Three empty container definitions, two in subarray
        ['{"id": "test"}'], # Single container definition a field changed
    ]
)
def test_acipolicygen_with_containers_input_forms(container_definitions):

    acipolicygen_confcom(
        input_path=None,
        arm_template=None,
        arm_template_parameters=None,
        image_name=None,
        virtual_node_yaml_path=None,
        infrastructure_svn=None,
        tar_mapping_location=None,
        outraw=True,
        container_definitions=[json.loads(c) for c in container_definitions]
    )


def test_acipolicygen_with_containers_field_changed():

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
            outraw=True,
            container_definitions=[json.loads('{"id": "test"}')]
        )
    actual_policy = buffer.getvalue()
    assert '"id":"test"' in actual_policy


@pytest.mark.parametrize(
    "sample_directory",
    os.listdir(SAMPLES_ROOT),
)
def test_acipolicygen_with_containers(sample_directory):

    # Load expected policy
    with open(os.path.join(SAMPLES_ROOT, sample_directory, "policy.rego")) as expected_policy_file:
        expected_policy_str = expected_policy_file.read()

    # Load input container definition
    input_containers = []
    for file_path in os.listdir(os.path.join(SAMPLES_ROOT, sample_directory)):
        if file_path.startswith("container"):
            with open(os.path.join(SAMPLES_ROOT, sample_directory, file_path)) as input_containers_file:
                input_containers.append(json.loads(input_containers_file.read()))

    # Generate a policy
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
            outraw=True,
            container_definitions=input_containers,
        )
    actual_policy_str = buffer.getvalue()

    # Deserialize both policies for comparison (serialised policies might differ in formatting)
    with tempfile.NamedTemporaryFile(mode="w+", delete=True) as actual_policy_file, \
         tempfile.NamedTemporaryFile(mode="w+", delete=True) as expected_policy_file:

        actual_policy_file.write(actual_policy_str)
        actual_policy_file.flush()
        actual_policy = policy_deserialize(actual_policy_file.name)

        for expected in [e for e in expected_policy_str.split("package policy") if e.strip()]:
            expected_policy_file.seek(0)
            expected_policy_file.truncate()
            expected_policy_file.write(f"package policy{expected}")
            expected_policy_file.flush()
            expected_policy = policy_deserialize(expected_policy_file.name)

            assert actual_policy == expected_policy
