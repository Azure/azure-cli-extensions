# --------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT
# License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------
"""Contains a class for generating VNF NFDs and associated resources."""
from knack.log import get_logger
import json
import logging
import os
import shutil
from functools import cached_property
from pathlib import Path
from typing import Any, Dict, Optional

from azext_aosm.generate_nfd.nfd_generator_base import NFDGenerator

from azext_aosm._configuration import VNFConfiguration
from azext_aosm.publisher_resources.publisher_resources import (
    PublisherResourceGenerator,
)
from azext_aosm._constants import (
    VNF_DEFINITION_BICEP_SOURCE_TEMPLATE,
    VNF_DEFINITION_OUTPUT_BICEP_PREFIX,
)


logger = get_logger(__name__)


class VnfBicepNfdGenerator(NFDGenerator):
    """_summary_

    :param NFDGenerator: _description_
    :type NFDGenerator: _type_
    """

    def __init__(self, config: VNFConfiguration):
        super(NFDGenerator, self).__init__(
            # config=config,
        )
        self.config = config
        self.bicep_template_name = VNF_DEFINITION_BICEP_SOURCE_TEMPLATE

        self.arm_template_path = self.config.arm_template["file_path"]
        self.folder_name = f"{VNF_DEFINITION_OUTPUT_BICEP_PREFIX}{Path(str(self.arm_template_path)).stem}"

        self._bicep_path = os.path.join(self.folder_name, self.bicep_template_name)

    def generate_nfd(self) -> None:
        """Generate a VNF NFD which comprises an group, an Artifact Manifest and a NFDV."""
        # assert isinstance(self.config, VNFConfiguration)
        if self.bicep_path:
            logger.info("Using the existing NFD bicep template %s.", self.bicep_path)
            logger.info(
                'To generate a new NFD, delete the folder "%s" and re-run this command.',
                os.path.dirname(self.bicep_path),
            )
        else:
            self.write()

    def write(self) -> None:
        """
        Create a bicep template for an NFD from the ARM template for the VNF.

        :param arm_template_path: The path to the ARM template for deploying the VNF.
        :param nf_name: The name of the NF.

        :return: Path to the bicep file.
        """
        logger.info("Generate NFD bicep template for %s", self.arm_template_path)
        print(f"Generate NFD bicep template for {self.arm_template_path}")

        self._create_nfd_folder()
        self.create_parameter_files()
        self.copy_bicep()
        print(f"Generated NFD bicep template created in {self.folder_name}")

    @property
    def bicep_path(self) -> Optional[str]:
        """Returns the path to the bicep file for the NFD if it has been created."""
        if os.path.exists(self._bicep_path):
            return self._bicep_path

        return None

    def _create_nfd_folder(self) -> None:
        """
        Create the folder for the NFD bicep files.

        :raises RuntimeError: If the user aborts.
        """
        if os.path.exists(self.folder_name):
            carry_on = input(
                f"The folder {self.folder_name} already exists - delete it and continue? (y/n)"
            )
            if carry_on != "y":
                raise RuntimeError("User aborted!")

            shutil.rmtree(self.folder_name)

        logger.info("Create NFD bicep %s", self.folder_name)
        os.mkdir(self.folder_name)

    @cached_property
    def vm_parameters(self) -> Dict[str, Any]:
        """The parameters from the VM ARM template."""
        with open(self.arm_template_path, "r") as _file:
            parameters: Dict[str, Any] = json.load(_file)["parameters"]

        return parameters

    def create_parameter_files(self) -> None:
        """Create the Deployment and Template json parameter files."""
        schemas_folder_path = os.path.join(self.folder_name, "schemas")
        os.mkdir(schemas_folder_path)
        self.write_deployment_parameters(schemas_folder_path)

        mappings_folder_path = os.path.join(self.folder_name, "configMappings")
        os.mkdir(mappings_folder_path)
        self.write_template_parameters(mappings_folder_path)
        self.write_vhd_parameters(mappings_folder_path)

    def write_deployment_parameters(self, folder_path: str) -> None:
        """
        Write out the NFD deploymentParameters.json file.

        :param folder_path: The folder to put this file in.
        """
        logger.debug("Create deploymentParameters.json")

        nfd_parameters: Dict[str, Any] = {
            key: {"type": self.vm_parameters[key]["type"]} for key in self.vm_parameters
        }

        deployment_parameters_path = os.path.join(
            folder_path, "deploymentParameters.json"
        )

        with open(deployment_parameters_path, "w") as _file:
            _file.write(json.dumps(nfd_parameters, indent=4))

        logger.debug("%s created", deployment_parameters_path)

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

        logger.debug("%s created", template_parameters_path)

    def write_vhd_parameters(self, folder_path: str) -> None:
        """
        Write out the NFD vhdParameters.json file.

        :param folder_path: The folder to put this file in.
        """
        vhd_parameters = {
            "imageName": f"{self.config.nf_name}Image",
            "azureDeployLocation": "{deployParameters.location}",
        }

        vhd_parameters_path = os.path.join(folder_path, "vhdParameters.json")

        with open(vhd_parameters_path, "w", encoding="utf-8") as _file:
            _file.write(json.dumps(vhd_parameters, indent=4))

        logger.debug("%s created", vhd_parameters_path)

    def copy_bicep(self) -> None:
        """
        Copy the bicep template into place.

        :param folder_name: The name of the folder to copy the bicep template to.

        :returns: Path to the bicep file
        """
        code_dir = os.path.dirname(__file__)

        bicep_path = os.path.join(code_dir, "templates", self.bicep_template_name)

        shutil.copy(bicep_path, self.folder_name)
