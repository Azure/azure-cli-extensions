# --------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT
# License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------
"""Contains a class for generating VNF NFDs and associated resources."""

import logging
import json
import os
import shutil
import tempfile

from functools import cached_property
from pathlib import Path
from typing import Any, Dict, Optional
from knack.log import get_logger

from azext_aosm.generate_nfd.nfd_generator_base import NFDGenerator

from azext_aosm._configuration import VNFConfiguration
from azext_aosm.util.constants import (
    VNF_DEFINITION_BICEP_TEMPLATE,
    VNF_MANIFEST_BICEP_TEMPLATE,
    CONFIG_MAPPINGS,
    SCHEMAS,
    SCHEMA_PREFIX,
    DEPLOYMENT_PARAMETERS,
)


logger = get_logger(__name__)


class VnfNfdGenerator(NFDGenerator):
    """
    VNF NFD Generator.

    This takes a source ARM template and a config file, and outputs:
    - A bicep file for the NFDV
    - Parameters files that are used by the NFDV bicep file, these are the
      deployParameters and the mapping profiles of those deploy parameters
    - A bicep file for the Artifact manifests
    """

    def __init__(self, config: VNFConfiguration):
        super(NFDGenerator, self).__init__()
        self.config = config
        self.bicep_template_name = VNF_DEFINITION_BICEP_TEMPLATE
        self.manifest_template_name = VNF_MANIFEST_BICEP_TEMPLATE

        self.arm_template_path = self.config.arm_template.file_path
        self.output_folder_name = self.config.build_output_folder_name

        self._bicep_path = os.path.join(
            self.output_folder_name, self.bicep_template_name
        )
        self._manifest_path = os.path.join(
            self.output_folder_name, self.manifest_template_name
        )

    def generate_nfd(self) -> None:
        """Create a bicep template for an NFD from the ARM template for the VNF."""
        """
        Generate a VNF NFD which comprises an group, an Artifact Manifest and a NFDV.

        Create a bicep template for an NFD from the ARM template for the VNF.
        """

        # Create temporary folder.
        with tempfile.TemporaryDirectory() as tmpdirname:
            self.tmp_folder_name = tmpdirname

            self.create_parameter_files()
            self.copy_to_output_folder()
            print(f"Generated NFD bicep templates created in {self.output_folder_name}")
            print(
                "Please review these templates. When you are happy with them run "
                "`az aosm nfd publish` with the same arguments."
            )

    @property
    def bicep_path(self) -> Optional[str]:
        """Returns the path to the bicep file for the NFD if it has been created."""
        if os.path.exists(self._bicep_path):
            return self._bicep_path

        return None

    @property
    def manifest_path(self) -> Optional[str]:
        """Returns the path to the bicep file for the NFD if it has been created."""
        if os.path.exists(self._manifest_path):
            return self._manifest_path

        return None

    @cached_property
    def vm_parameters(self) -> Dict[str, Any]:
        """The parameters from the VM ARM template."""
        with open(self.arm_template_path, "r") as _file:
            data = json.load(_file)
            if "parameters" in data:
                parameters: Dict[str, Any] = data["parameters"]
            else:
                print(
                    "No parameters found in the template provided. Your schema will have no properties"
                )
                parameters = {}

        return parameters

    def create_parameter_files(self) -> None:
        """Create the Deployment and Template json parameter files."""
        schemas_folder_path = os.path.join(self.tmp_folder_name, SCHEMAS)
        os.mkdir(schemas_folder_path)
        self.write_deployment_parameters(schemas_folder_path)

        mappings_folder_path = os.path.join(self.tmp_folder_name, CONFIG_MAPPINGS)
        os.mkdir(mappings_folder_path)
        self.write_template_parameters(mappings_folder_path)
        self.write_vhd_parameters(mappings_folder_path)

    def write_deployment_parameters(self, folder_path: str) -> None:
        """
        Write out the NFD deploymentParameters.json file.

        :param folder_path: The folder to put this file in.
        """
        logger.debug("Create deploymentParameters.json")

        nfd_parameters = {}

        for key in self.vm_parameters:
            # ARM templates allow int and secureString but we do not currently accept them in AOSM
            # This may change, but for now we should change them to accepted types integer and string
            if self.vm_parameters[key]["type"] == "int":
                nfd_parameters[key] = {"type": "integer"}
            elif self.vm_parameters[key]["type"] == "secureString":
                nfd_parameters[key] = {"type": "string"}
            else:
                nfd_parameters[key] = {"type": self.vm_parameters[key]["type"]}

        deployment_parameters_path = os.path.join(folder_path, DEPLOYMENT_PARAMETERS)

        # Heading for the deployParameters schema
        deploy_parameters_full: Dict[str, Any] = SCHEMA_PREFIX
        deploy_parameters_full["properties"].update(nfd_parameters)

        with open(deployment_parameters_path, "w") as _file:
            _file.write(json.dumps(deploy_parameters_full, indent=4))

        logger.debug(f"{deployment_parameters_path} created")

    def write_template_parameters(self, folder_path: str) -> None:
        """
        Write out the NFD templateParameters.json file.

        :param folder_path: The folder to put this file in.
        """
        logger.debug("Create templateParameters.json")
        template_parameters = {
            key: f"{{deployParameters.{key}}}" for key in self.vm_parameters
        }

        template_parameters_path = os.path.join(folder_path, "templateParameters.json")

        with open(template_parameters_path, "w") as _file:
            _file.write(json.dumps(template_parameters, indent=4))

        logger.debug(f"{template_parameters_path} created")

    def write_vhd_parameters(self, folder_path: str) -> None:
        """
        Write out the NFD vhdParameters.json file.

        :param folder_path: The folder to put this file in.
        """
        azureDeployLocation: str
        if self.vm_parameters.get("location"):
            # Location can be passed in as deploy parameter
            azureDeployLocation = "{deployParameters.location}"
        else:
            # Couldn't find a location parameter in the source template, so hard code to
            # the location we are deploying the publisher to.
            azureDeployLocation = self.config.location

        vhd_parameters = {
            "imageName": f"{self.config.nf_name}Image",
            "azureDeployLocation": azureDeployLocation,
        }

        vhd_parameters_path = os.path.join(folder_path, "vhdParameters.json")
        with open(vhd_parameters_path, "w", encoding="utf-8") as _file:
            _file.write(json.dumps(vhd_parameters, indent=4))

        logger.debug(f"{vhd_parameters_path} created")

    def copy_to_output_folder(self) -> None:
        """Copy the bicep templates, config mappings and schema into the build output folder."""
        code_dir = os.path.dirname(__file__)

        logger.info("Create NFD bicep %s", self.output_folder_name)
        os.mkdir(self.output_folder_name)

        bicep_path = os.path.join(code_dir, "templates", self.bicep_template_name)
        shutil.copy(bicep_path, self.output_folder_name)

        manifest_path = os.path.join(code_dir, "templates", self.manifest_template_name)
        shutil.copy(manifest_path, self.output_folder_name)

        os.mkdir(os.path.join(self.output_folder_name, SCHEMAS))
        tmp_schema_path = os.path.join(
            self.tmp_folder_name, SCHEMAS, DEPLOYMENT_PARAMETERS
        )
        output_schema_path = os.path.join(
            self.output_folder_name, SCHEMAS, DEPLOYMENT_PARAMETERS
        )
        shutil.copy(
            tmp_schema_path,
            output_schema_path,
        )

        tmp_config_mappings_path = os.path.join(self.tmp_folder_name, CONFIG_MAPPINGS)
        output_config_mappings_path = os.path.join(
            self.output_folder_name, CONFIG_MAPPINGS
        )
        shutil.copytree(
            tmp_config_mappings_path,
            output_config_mappings_path,
            dirs_exist_ok=True,
        )

        logger.info("Copied files to %s", self.output_folder_name)
