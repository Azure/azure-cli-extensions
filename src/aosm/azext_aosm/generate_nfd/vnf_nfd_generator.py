# --------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT
# License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------
"""Contains a class for generating VNF NFDs and associated resources."""

import json
import os
import shutil
import tempfile
from functools import cached_property
from typing import Any, Dict, Optional

from knack.log import get_logger

from azext_aosm._configuration import VNFConfiguration
from azext_aosm.generate_nfd.nfd_generator_base import NFDGenerator
from azext_aosm.util.constants import (
    CONFIG_MAPPINGS,
    DEPLOYMENT_PARAMETERS,
    OPTIONAL_DEPLOYMENT_PARAMETERS_FILE,
    OPTIONAL_DEPLOYMENT_PARAMETERS_HEADING,
    SCHEMA_PREFIX,
    SCHEMAS,
    TEMPLATE_PARAMETERS,
    VHD_PARAMETERS,
    VNF_DEFINITION_BICEP_TEMPLATE,
    VNF_MANIFEST_BICEP_TEMPLATE,
)
from azext_aosm.util.utils import input_ack

logger = get_logger(__name__)

# Different types are used in ARM templates and NFDs. The list accepted by NFDs is
# documented in the AOSM meta-schema. This will be published in the future but for now
# can be found in
# https://microsoft.sharepoint.com/:w:/t/NSODevTeam/Ec7ovdKroSRIv5tumQnWIE0BE-B2LykRcll2Qb9JwfVFMQ
ARM_TO_JSON_PARAM_TYPES: Dict[str, str] = {
    "int": "integer",
    "secureString": "string",
}


class VnfNfdGenerator(NFDGenerator):
    # pylint: disable=too-many-instance-attributes
    """
    VNF NFD Generator.

    This takes a source ARM template and a config file, and outputs:
    - A bicep file for the NFDV
    - Parameters files that are used by the NFDV bicep file, these are the
      deployParameters and the mapping profiles of those deploy parameters
    - A bicep file for the Artifact manifests

    @param order_params: whether to order the deployment and template output parameters
                         with those without a default first, then those with a default.
                         Those without a default will definitely be required to be
                         exposed, those with a default may not be.
    @param interactive:  whether to prompt the user to confirm the parameters to be
                         exposed.
    """

    def __init__(self, config: VNFConfiguration, order_params: bool, interactive: bool):
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
        self.order_params = order_params
        self.interactive = interactive
        self.tmp_folder_name = ""
        self.image_name = f"{self.config.nf_name}Image"

    def generate_nfd(self) -> None:
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
        with open(self.arm_template_path, "r", encoding="utf-8") as _file:
            data = json.load(_file)
            if "parameters" in data:
                parameters: Dict[str, Any] = data["parameters"]
            else:
                print(
                    "No parameters found in the template provided. "
                    "Your NFD will have no deployParameters"
                )
                parameters = {}

        return parameters

    @property
    def vm_parameters_ordered(self) -> Dict[str, Any]:
        """The parameters from the VM ARM template, ordered as those without defaults then those with."""
        vm_parameters_no_default: Dict[str, Any] = {}
        vm_parameters_with_default: Dict[str, Any] = {}
        has_default_field: bool = False
        has_default: bool = False

        for key in self.vm_parameters:
            # Order parameters into those with and without defaults
            has_default_field = "defaultValue" in self.vm_parameters[key]
            has_default = (
                has_default_field and not self.vm_parameters[key]["defaultValue"] == ""
            )

            if has_default:
                vm_parameters_with_default[key] = self.vm_parameters[key]
            else:
                vm_parameters_no_default[key] = self.vm_parameters[key]

        return {**vm_parameters_no_default, **vm_parameters_with_default}

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
        nfd_parameters_with_default = {}
        vm_parameters_to_exclude = []

        vm_parameters = (
            self.vm_parameters_ordered if self.order_params else self.vm_parameters
        )

        for key in vm_parameters:
            if key == self.config.image_name_parameter:
                # There is only one correct answer for the image name, so don't ask the 
                # user, instead it is hardcoded in config mappings.
                continue
            
            # Order parameters into those without and then with defaults
            has_default_field = "defaultValue" in self.vm_parameters[key]
            has_default = (
                has_default_field and not self.vm_parameters[key]["defaultValue"] == ""
            )

            if self.interactive and has_default:
                # Interactive mode. Prompt user to include or exclude parameters
                # This requires the enter key after the y/n input which isn't ideal
                if not input_ack("y", f"Expose parameter {key}? y/n "):
                    logger.debug("Excluding parameter %s", key)
                    vm_parameters_to_exclude.append(key)
                    continue

            # Map ARM parameter types to JSON parameter types accepted by AOSM
            arm_type = self.vm_parameters[key]["type"]
            json_type = ARM_TO_JSON_PARAM_TYPES.get(arm_type, arm_type)

            if has_default:
                nfd_parameters_with_default[key] = {"type": json_type}

            nfd_parameters[key] = {"type": json_type}

        # Now we are out of the vm_parameters loop, we can remove the excluded
        # parameters so they don't get included in templateParameters.json
        # Remove from both ordered and unordered dicts
        for key in vm_parameters_to_exclude:
            self.vm_parameters.pop(key, None)

        deployment_parameters_path = os.path.join(folder_path, DEPLOYMENT_PARAMETERS)

        # Heading for the deployParameters schema
        deploy_parameters_full: Dict[str, Any] = SCHEMA_PREFIX
        deploy_parameters_full["properties"].update(nfd_parameters)

        with open(deployment_parameters_path, "w", encoding="utf-8") as _file:
            _file.write(json.dumps(deploy_parameters_full, indent=4))

        logger.debug("%s created", deployment_parameters_path)
        if self.order_params:
            print(
                "Deployment parameters for the generated NFDV are ordered by those "
                "without defaults first to make it easier to choose which to expose."
            )

        # Extra output file to help the user know which parameters are optional
        if not self.interactive:
            if nfd_parameters_with_default:
                optional_deployment_parameters_path = os.path.join(
                    folder_path, OPTIONAL_DEPLOYMENT_PARAMETERS_FILE
                )
                with open(
                    optional_deployment_parameters_path, "w", encoding="utf-8"
                ) as _file:
                    _file.write(OPTIONAL_DEPLOYMENT_PARAMETERS_HEADING)
                    _file.write(json.dumps(nfd_parameters_with_default, indent=4))
                print(
                    "Optional ARM parameters detected. Created "
                    f"{OPTIONAL_DEPLOYMENT_PARAMETERS_FILE} to help you choose which "
                    "to expose."
                )
                
    def write_template_parameters(self, folder_path: str) -> None:
        """
        Write out the NFD templateParameters.json file.

        :param folder_path: The folder to put this file in.
        """
        logger.debug("Create %s", TEMPLATE_PARAMETERS)
        vm_parameters = (
            self.vm_parameters_ordered if self.order_params else self.vm_parameters
        )

        template_parameters = {}

        for key in vm_parameters:
            if key == self.config.image_name_parameter:
                template_parameters[key] = self.image_name
                continue

            template_parameters[key] = f"{{deployParameters.{key}}}"

        template_parameters_path = os.path.join(folder_path, TEMPLATE_PARAMETERS)

        with open(template_parameters_path, "w", encoding="utf-8") as _file:
            _file.write(json.dumps(template_parameters, indent=4))

        logger.debug("%s created", template_parameters_path)

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
            "imageName": self.image_name,
            "azureDeployLocation": azureDeployLocation,
        }

        vhd_parameters_path = os.path.join(folder_path, VHD_PARAMETERS)
        with open(vhd_parameters_path, "w", encoding="utf-8") as _file:
            _file.write(json.dumps(vhd_parameters, indent=4))

        logger.debug("%s created", vhd_parameters_path)

    def copy_to_output_folder(self) -> None:
        """Copy the bicep templates, config mappings and schema into the build output folder."""
        code_dir = os.path.dirname(__file__)

        logger.info("Create NFD bicep %s", self.output_folder_name)
        os.mkdir(self.output_folder_name)

        bicep_path = os.path.join(code_dir, "templates", self.bicep_template_name)
        shutil.copy(bicep_path, self.output_folder_name)

        manifest_path = os.path.join(code_dir, "templates", self.manifest_template_name)
        shutil.copy(manifest_path, self.output_folder_name)
        # Copy everything in the temp folder to the output folder
        shutil.copytree(
            self.tmp_folder_name,
            self.output_folder_name,
            dirs_exist_ok=True,
        )

        logger.info("Copied files to %s", self.output_folder_name)
