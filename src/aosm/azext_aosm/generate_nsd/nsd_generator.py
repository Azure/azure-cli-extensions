# --------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT
# License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------
"""Contains a class for generating NSDs and associated resources."""
import json
import os
import shutil
import tempfile
from typing import Dict

from jinja2 import Template
from knack.log import get_logger
from azext_aosm.vendored_sdks.models import NFVIType

from azext_aosm._configuration import NSConfiguration
from azext_aosm.util.constants import (
    CONFIG_MAPPINGS,
    NF_DEFINITION_BICEP_FILE,
    NF_TEMPLATE_BICEP_FILE,
    NSD_ARTIFACT_MANIFEST_BICEP_FILE,
    NSD_ARTIFACT_MANIFEST_SOURCE_TEMPLATE,
    NSD_CONFIG_MAPPING_FILE,
    NSD_DEFINITION_BICEP_FILE,
    NSD_DEFINITION_BICEP_SOURCE_TEMPLATE,
    SCHEMAS,
    TEMPLATES,
    VNF,
)
from azext_aosm.util.management_clients import ApiClients
from azext_aosm.vendored_sdks.models import NetworkFunctionDefinitionVersion

logger = get_logger(__name__)

# Different types are used in Bicep templates and NFDs. The list accepted by NFDs is
# documented in the AOSM meta-schema. This will be published in the future but for now
# can be found in
# https://microsoft.sharepoint.com/:w:/t/NSODevTeam/Ec7ovdKroSRIv5tumQnWIE0BE-B2LykRcll2Qb9JwfVFMQ
NFV_TO_BICEP_PARAM_TYPES: Dict[str, str] = {
    "integer": "int",
    "boolean": "bool",
}


class NSDGenerator:
    """
    NSD Generator.

    This takes a config file and a set of NFDV deploy_parameters and outputs:
    - A bicep file for the NSDV
    - Parameters files that are used by the NSDV bicep file, these are the
      schemas and the mapping profiles of those schemas parameters
    - A bicep file for the Artifact manifest
    - A bicep and JSON file defining the Network Function that will
      be deployed by the NSDV
    """

    def __init__(self, api_clients: ApiClients, config: NSConfiguration):
        self.config = config
        self.nsd_bicep_template_name = NSD_DEFINITION_BICEP_SOURCE_TEMPLATE
        self.nf_bicep_template_name = NF_TEMPLATE_BICEP_FILE
        self.nsd_bicep_output_name = NSD_DEFINITION_BICEP_FILE

        self.build_folder_name = self.config.build_output_folder_name
        nfdv = self._get_nfdv(config, api_clients)
        print("Finding the deploy parameters of the NFDV resource")
        if not nfdv.deploy_parameters:
            raise NotImplementedError(
                "NFDV has no deploy parameters, cannot generate NSD."
            )
        self.deploy_parameters: str = nfdv.deploy_parameters

    def _get_nfdv(
        self, config: NSConfiguration, api_clients
    ) -> NetworkFunctionDefinitionVersion:
        """Get the existing NFDV resource object."""
        print(
            "Reading existing NFDV resource object "
            f"{config.network_function_definition_version_name} from group "
            f"{config.network_function_definition_group_name}"
        )
        nfdv_object = api_clients.aosm_client.network_function_definition_versions.get(
            resource_group_name=config.publisher_resource_group_name,
            publisher_name=config.publisher_name,
            network_function_definition_group_name=config.network_function_definition_group_name,
            network_function_definition_version_name=config.network_function_definition_version_name,
        )
        return nfdv_object

    def generate_nsd(self) -> None:
        """Generate a NSD templates which includes an Artifact Manifest, NFDV and NF templates."""
        logger.info(f"Generate NSD bicep templates")

        # Create temporary folder.
        with tempfile.TemporaryDirectory() as tmpdirname:
            self.tmp_folder_name = tmpdirname

            self.create_parameter_files()
            self.write_nsd_manifest()
            self.write_nf_bicep()
            self.write_nsd_bicep()

            self.copy_to_output_folder()
            print(f"Generated NSD bicep templates created in {self.build_folder_name}")
            print(
                "Please review these templates. When you are happy with them run "
                "`az aosm nsd publish` with the same arguments."
            )

    def create_parameter_files(self) -> None:
        """Create the Schema and configMappings json files."""
        temp_schemas_folder_path = os.path.join(self.tmp_folder_name, SCHEMAS)
        os.mkdir(temp_schemas_folder_path)
        self.write_schema(temp_schemas_folder_path)

        temp_mappings_folder_path = os.path.join(self.tmp_folder_name, CONFIG_MAPPINGS)
        os.mkdir(temp_mappings_folder_path)
        self.write_config_mappings(temp_mappings_folder_path)

    def write_schema(self, folder_path: str) -> None:
        """
        Write out the NSD Config Group Schema JSON file.

        :param folder_path: The folder to put this file in.
        """
        logger.debug(f"Create {self.config.cg_schema_name}.json")

        schema_path = os.path.join(folder_path, f"{self.config.cg_schema_name}.json")

        with open(schema_path, "w") as _file:
            _file.write(json.dumps(json.loads(self.deploy_parameters), indent=4))

        logger.debug(f"{schema_path} created")

    def write_config_mappings(self, folder_path: str) -> None:
        """
        Write out the NSD configMappings.json file.

        :param folder_path: The folder to put this file in.
        """

        deploy_parameters_dict = json.loads(self.deploy_parameters)
        deploy_properties = deploy_parameters_dict["properties"]

        logger.debug("Create configMappings.json")
        config_mappings = {
            key: f"{{configurationparameters('{self.config.cg_schema_name}').{key}}}"
            for key in deploy_properties
        }

        config_mappings_path = os.path.join(folder_path, NSD_CONFIG_MAPPING_FILE)

        with open(config_mappings_path, "w") as _file:
            _file.write(json.dumps(config_mappings, indent=4))

        logger.debug(f"{config_mappings_path} created")

    def write_nf_bicep(self) -> None:
        """Write out the Network Function bicep file."""
        bicep_params = ""

        bicep_deploymentValues = ""

        deploy_parameters_dict = json.loads(self.deploy_parameters)
        if "properties" not in deploy_parameters_dict:
            raise ValueError(
                f"NFDV in {self.config.network_function_definition_group_name} has "
                "no properties within deployParameters"
            )

        deploy_properties = deploy_parameters_dict["properties"]

        for key, value in deploy_properties.items():
            # location is sometimes part of deploy_properties.
            # We want to avoid having duplicate params in the bicep template
            if key != "location":
                bicep_type = (
                    NFV_TO_BICEP_PARAM_TYPES.get(value["type"]) or value["type"]
                )
                bicep_params += f"param {key} {bicep_type}\n"
            bicep_deploymentValues += f"{key}: {key}\n  "

        self.generate_bicep(
            self.nf_bicep_template_name,
            NF_DEFINITION_BICEP_FILE,
            {
                "bicep_params": bicep_params,
                "deploymentValues": bicep_deploymentValues,
                "network_function_name": self.config.network_function_name,
                "publisher_name": self.config.publisher_name,
                "network_function_definition_group_name": self.config.network_function_definition_group_name,
                "network_function_definition_version_name": self.config.network_function_definition_version_name,
                "network_function_definition_offering_location": self.config.network_function_definition_offering_location,
                "location": self.config.location,
                # Ideally we would use the network_function_type from reading the actual
                # NF, as we do for deployParameters, but the SDK currently doesn't
                # support this and needs to be rebuilt to do so.
                "nfvi_type": NFVIType.AZURE_CORE
                if self.config.network_function_type == VNF
                else NFVIType.AZURE_ARC_KUBERNETES.value,
            },
        )

    def write_nsd_bicep(self) -> None:
        """Write out the NSD bicep file."""
        params = {
            "nfvi_site_name": self.config.nfvi_site_name,
            "armTemplateName": self.config.arm_template_artifact_name,
            "armTemplateVersion": self.config.arm_template.version,
            "cg_schema_name": self.config.cg_schema_name,
            "nsdv_description": self.config.nsdv_description,
            "ResourceElementName": self.config.resource_element_name,
        }

        self.generate_bicep(
            self.nsd_bicep_template_name, self.nsd_bicep_output_name, params
        )

    def write_nsd_manifest(self) -> None:
        """Write out the NSD manifest bicep file."""
        logger.debug("Create NSD manifest")

        self.generate_bicep(
            NSD_ARTIFACT_MANIFEST_SOURCE_TEMPLATE, NSD_ARTIFACT_MANIFEST_BICEP_FILE, {}
        )

    def generate_bicep(self, template_name, output_file_name, params) -> None:
        """
        Render the bicep templates with the correct parameters and copy them into the build output folder.

        :param template_name: The name of the template to render
        :param output_file_name: The name of the output file
        :param params: The parameters to render the template with
        """

        code_dir = os.path.dirname(__file__)

        bicep_template_path = os.path.join(code_dir, TEMPLATES, template_name)

        with open(bicep_template_path, "r") as file:
            bicep_contents = file.read()

        bicep_template = Template(bicep_contents)

        # Render all the relevant parameters in the bicep template
        rendered_template = bicep_template.render(**params)

        bicep_file_build_path = os.path.join(self.tmp_folder_name, output_file_name)

        with open(bicep_file_build_path, "w") as file:
            file.write(rendered_template)

    def copy_to_output_folder(self) -> None:
        """Copy the bicep templates, config mappings and schema into the build output folder."""
        code_dir = os.path.dirname(__file__)

        logger.info("Create NSD bicep %s", self.build_folder_name)
        os.mkdir(self.build_folder_name)

        shutil.copytree(
            self.tmp_folder_name,
            self.build_folder_name,
            dirs_exist_ok=True,
        )

        logger.info("Copied files to %s", self.build_folder_name)
