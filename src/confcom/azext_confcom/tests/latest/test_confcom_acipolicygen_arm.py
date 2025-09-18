# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import contextlib
import io
import os
import pytest
from itertools import product

from azext_confcom.custom import acipolicygen_confcom


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), ".."))
SAMPLES_ROOT = os.path.abspath(os.path.join(TEST_DIR, "..", "..", "..", "samples", "aci"))


POLICYGEN_ARGS = {
    "policy.rego": {},
    "policy_debug.rego": {"debug_mode": True},
    "policy_exclude_default_fragment.rego": {"exclude_default_fragments": True},
    "policy_infrastructure_svn.rego": {"infrastructure_svn": "99"},
    "policy_disable_stdio.rego": {"disable_stdio": True},
}


@pytest.mark.parametrize(
    "sample_directory,generated_policy_path",
    product(os.listdir(SAMPLES_ROOT), POLICYGEN_ARGS.keys())
)
def test_acipolicygen(sample_directory, generated_policy_path):

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
