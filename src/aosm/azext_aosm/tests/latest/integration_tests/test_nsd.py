# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import shutil
import subprocess
import logging
import sys
from dataclasses import dataclass
from distutils.dir_util import copy_tree
from filecmp import dircmp
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, List
from unittest.mock import patch
from azext_aosm.vendored_sdks.models import (
    VirtualNetworkFunctionDefinitionVersion,
)
from unittest import TestCase

import jsonschema
from azure.core import exceptions as azure_exceptions
from azure.mgmt.resource.features.v2015_12_01.models import (
    FeatureProperties,
    FeatureResult,
)
from azext_aosm.common.constants import CNF_TYPE, VNF_TYPE
from azext_aosm.custom import (
    onboard_nsd_build,
    onboard_nsd_generate_config,
)

from azext_aosm.vendored_sdks import HybridNetworkManagementClient

mock_input_templates_folder = (
    (Path(__file__)).parent / "integration_test_mocks/mock_input_templates"
).resolve()
output_folder = ((Path(__file__).parent) / "nsd_output").resolve()

NSD_INPUT_FILE_NAME = "nsd_core_input.jsonc"

CGV_DATA = {
    "ubuntu-vm": {
        "nfdv": "1.0.0",
        "deployParameters": [
            {
                "location": "eastus",
                "subnetName": "subnet",
                "virtualNetworkId": "bar",
                "sshPublicKeyAdmin": "foo",
            }
        ],
        "managedIdentityId": "blah",
    },
}


MULTIPLE_INSTANCES_CGV_DATA = {
    "ubuntu-vm": {
        "nfdv": "1.0.0",
        "deployParameters": [
            {
                "location": "eastus",
                "subnetName": "subnet",
                "virtualNetworkId": "bar",
                "sshPublicKeyAdmin": "foo",
            },
            {
                "location": "eastus",
                "subnetName": "subnet2",
                "virtualNetworkId": "bar2",
                "sshPublicKeyAdmin": "foo2",
            },
        ],
        "managedIdentityId": "blah",
    },
}


MULTIPLE_NFs_CGV_DATA = {
    "multi-nf": {
        "nfdv": "1.0.0",
        "managedIdentityId": "exampleManagedIdentityId",
        "deployParameters": [{"service_port": 5222, "serviceAccount_create": False}],
    },
    "ubuntu-vm": {
        "nfdv": "1.0.0",
        "managedIdentity": "managed_identity",
        "deployParameters": {
            "location": "eastus",
            "subnetName": "ubuntu-vm-subnet",
            "ubuntuVmName": "ubuntu-vm",
            "virtualNetworkId": "ubuntu-vm-vnet",
            "sshPublicKeyAdmin": "public_key",
        },
    },
}


ubuntu_deploy_parameters = {
    "$schema": "https://json-schema.org/draft-07/schema#",
    "title": "DeployParametersSchema",
    "type": "object",
    "properties": {
        "location": {"type": "string"},
        "subnetName": {"type": "string"},
        "virtualNetworkId": {"type": "string"},
        "sshPublicKeyAdmin": {"type": "string"},
    },
}


nginx_deploy_parameters = {
    "$schema": "https://json-schema.org/draft-07/schema#",
    "title": "DeployParametersSchema",
    "type": "object",
    "properties": {
        "serviceAccount_create": {"type": "boolean"},
        "service_port": {"type": "integer"},
    },
    "required": ["serviceAccount_create", "service_port"],
}


# We don't want to get details from a real NFD (calling out to Azure) in a UT.
# Therefore we pass in a fake client to supply the deployment parameters from the "NFD".


@dataclass
class NetworkFunctionApplications:
    name: str
    depends_on_profile: list
    artifact_type: str


@dataclass
class NetworkFunctionTemplate:
    nfvi_type: str
    network_function_applications: List[NetworkFunctionApplications]


@dataclass
class NFDVProperties(VirtualNetworkFunctionDefinitionVersion):
    deploy_parameters: str
    network_function_template: NetworkFunctionTemplate  # type: ignore
    network_function_type: str


@dataclass
class NFDV:
    properties: NFDVProperties
    id: str


class NFDVs:
    def get(self, network_function_definition_group_name, **_):
        networkFunctionApplication = NetworkFunctionApplications(
            name="test", depends_on_profile=[], artifact_type=""
        )
        networkFunctionTemplate = NetworkFunctionTemplate(
            nfvi_type="AzureCore",
            network_function_applications=[networkFunctionApplication],
        )
        if "nginx" in network_function_definition_group_name:
            return NFDV(
                properties=NFDVProperties(
                    deploy_parameters=json.dumps(nginx_deploy_parameters),
                    network_function_template=networkFunctionTemplate,
                    network_function_type=CNF_TYPE,
                ),
                id="/subscriptions/00000/resourceGroups/rg/providers/Microsoft.HybridNetwork/publishers/pub/networkFunctionDefinitionGroups/nginx/networkFunctionDefinitionVersions/1.0.0",
            )
        else:
            return NFDV(
                properties=NFDVProperties(
                    deploy_parameters=json.dumps(ubuntu_deploy_parameters),
                    network_function_template=networkFunctionTemplate,
                    network_function_type=VNF_TYPE,
                ),
                id="/subscriptions/00000/resourceGroups/rg/providers/Microsoft.HybridNetwork/publishers/pub/networkFunctionDefinitionGroups/ubuntu/networkFunctionDefinitionVersions/1.0.0",
            )


class AOSMClient(HybridNetworkManagementClient):
    def __init__(self) -> None:
        self.network_function_definition_versions = NFDVs()  # type: ignore


mock_client = AOSMClient()


class MockFeatures:
    """Mock class for _check_features_enabled."""

    def __init__(self) -> None:
        """Mock init."""
        self.mock_state = "NotRegistered"

    def get(
        self, resource_provider_namespace: str, feature_name: str, **kwargs: Any
    ) -> FeatureResult:
        """Mock Features get function."""
        return FeatureResult(
            name=feature_name, properties=FeatureProperties(state=self.mock_state)
        )


class MockMissingFeatures:
    """Mock class for _check_features_enabled."""

    def __init__(self) -> None:
        """Fake init."""
        pass

    def get(
        self, resource_provider_namespace: str, feature_name: str, **kwargs: Any
    ) -> FeatureResult:
        """Mock features get function that raises an exception."""
        raise azure_exceptions.ResourceNotFoundError()


class FeaturesClient:
    """Mock class for _check_features_enabled."""

    def __init__(self) -> None:
        """Mock class for _check_features_enabled."""
        self.features = MockFeatures()


class MissingFeaturesClient:
    """Mock class for _check_features_enabled."""

    def __init__(self) -> None:
        """Mock class for _check_features_enabled."""
        self.features = MockMissingFeatures()


class FakeCmd:
    def __init__(self) -> None:
        self.cli_ctx = None


mock_cmd = FakeCmd()


def validate_schema_against_metaschema(schema_data):
    """Validate that the schema produced by the CLI matches the AOSM metaschema."""

    # There is a bug in the jsonschema module that means that it hits an error in with
    # the "$id" bit of the metaschema.  Here we use a modified version of the metaschema
    # with that small section removed.
    metaschema_file_path = (
        (Path(__file__).parent) / "metaschema_modified.json"
    ).resolve()
    with open(metaschema_file_path, "r", encoding="utf8") as f:
        metaschema = json.load(f)

    jsonschema.validate(instance=schema_data, schema=metaschema)


def validate_json_against_schema(json_data, schema_file):
    """Validate some test data against the schema produced by the CLI."""
    with open(schema_file, "r", encoding="utf8") as f:
        schema = json.load(f)

    validate_schema_against_metaschema(schema)

    jsonschema.validate(instance=json_data, schema=schema)


def build_bicep(bicep_template_path):
    bicep_output = subprocess.run(  # noqa
        [
            str(shutil.which("az")),
            "bicep",
            "build",
            "--file",
            bicep_template_path,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if bicep_output.returncode != 0:
        print(f"Invalid bicep: {bicep_template_path}")
        print(str(bicep_output.stderr).replace("\\n", "\n").replace("\\t", "\t"))
        raise RuntimeError("Invalid Bicep")


def compare_to_expected_output(expected_folder_name: str):
    """
    Compares nsd-cli-output to the supplied folder name.

    :param expected_folder_name: The name of the folder within nsd_output to compare
    with.
    """
    # Check files and folders within the top level directory are the same.
    expected_output_path = output_folder / expected_folder_name
    comparison = dircmp("nsd-cli-output", expected_output_path)

    try:
        assert len(comparison.diff_files) == 0
        assert len(comparison.left_only) == 0
        assert len(comparison.right_only) == 0

        # Check the files and folders within each of the subdirectories are the same.
        for subdir in comparison.subdirs.values():
            assert len(subdir.diff_files) == 0
            assert len(subdir.left_only) == 0
            assert len(subdir.right_only) == 0
    except:
        copy_tree("nsd-cli-output", str(expected_output_path))
        print(
            f"Output has changed in {expected_output_path}, use git diff to check if "
            f"you are happy with those changes."
        )
        raise


class TestNSDGenerator(TestCase):
    def setUp(self):
        # Prints out info logs in console if test fails
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    def test_generate_config(self):
        """Test generating a config file for a VNF."""
        starting_directory = os.getcwd()
        with TemporaryDirectory() as test_dir:
            os.chdir(test_dir)

            output_file_path = os.path.join(test_dir, "nsd-input.jsonc")

            try:
                onboard_nsd_generate_config(output_file_path)
                assert os.path.exists(output_file_path)
            finally:
                os.chdir(starting_directory)

    @patch(
        "azext_aosm.common.command_context.get_mgmt_service_client",
        return_value=mock_client,
    )
    def test_build(self, mock_get_mgmt_service_client):
        """Test building the NSD bicep templates."""
        starting_directory = os.getcwd()
        with TemporaryDirectory() as test_dir:
            os.chdir(test_dir)

            nsd_input_file_path = os.path.join(
                mock_input_templates_folder, NSD_INPUT_FILE_NAME
            )

            try:
                onboard_nsd_build(
                    cmd=mock_cmd,
                    config_file=nsd_input_file_path,
                )

                assert os.path.exists("nsd-cli-output")

                validate_json_against_schema(
                    CGV_DATA,
                    "nsd-cli-output/nsdDefinition/config-group-schema.json",
                )

                compare_to_expected_output("test_build")
            finally:
                os.chdir(starting_directory)

    @patch(
        "azext_aosm.common.command_context.get_mgmt_service_client",
        return_value=mock_client,
    )
    def test_build_multiple_instances(self, mock_get_mgmt_service_client):
        # Parameter is not used but we need to include it for the patch to work
        # TODO: this test passes but it doesn't actually test anything because
        # This functionality is currently broken
        """Test building the NSD bicep templates with multiple NFs allowed."""
        starting_directory = os.getcwd()
        with TemporaryDirectory() as test_dir:
            os.chdir(test_dir)

            try:
                onboard_nsd_build(
                    cmd=mock_cmd,
                    config_file=str(
                        mock_input_templates_folder / "input_multiple_instances.jsonc"
                    ),
                )

                assert os.path.exists("nsd-cli-output")
                validate_json_against_schema(
                    MULTIPLE_INSTANCES_CGV_DATA,
                    "nsd-cli-output/nsdDefinition/config-group-schema.json",
                )

                compare_to_expected_output("test_build_multiple_instances")
            finally:
                os.chdir(starting_directory)

    # TODO: creating NSDs with multiple NFs is broken at the moment.
    # Fix this test after the bug there is fixed.
    # @patch(
    #     "azext_aosm.common.command_context.get_mgmt_service_client",
    #     return_value=mock_client,
    # )
    # def test_build_multiple_nfs(self, mock_get_mgmt_service_client):
    #     """Test building the NSD bicep templates with multiple NFs allowed."""
    #     starting_directory = os.getcwd()
    #     with TemporaryDirectory() as test_dir:
    #         os.chdir(test_dir)

    #     try:
    #         onboard_nsd_build(
    #             cmd=mock_cmd,
    #             config_file=str(mock_input_templates_folder / "input_multi_nf_nsd.jsonc"),
    #         )

    #         assert os.path.exists("nsd-cli-output")

    #         # The bicep checks take a while, so we would only do them here and not
    #         # on the other tests. However, they are disabled until we can look at
    #         # them further, as the version of Bicep used ends up in the built file,
    #         # and we don't control what version of bicep is used in the pipeline or
    #         # on the user's machine.
    #         # build_bicep("nsd-bicep-templates/nginx-nfdg_nf.bicep")
    #         # build_bicep("nsd-bicep-templates/ubuntu-nfdg_nf.bicep")
    #         # build_bicep("nsd-bicep-templates/nsd_definition.bicep")
    #         # build_bicep("nsd-bicep-templates/artifact_manifest.bicep")

    #         compare_to_expected_output("test_build_multiple_nfs")
    #     finally:
    #         os.chdir(starting_directory)
