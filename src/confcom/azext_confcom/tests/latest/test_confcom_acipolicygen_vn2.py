# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import contextlib
import io
import os
import pytest

from azext_confcom.custom import acipolicygen_confcom


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), ".."))
CONFCOM_DIR = os.path.abspath(os.path.join(TEST_DIR, "..", "..", ".."))
SAMPLES_ROOT = os.path.abspath(os.path.join(TEST_DIR, "..", "..", "..", "samples", "vn2"))


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
