# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Contains a class for generating VNF NFDs and associated resources."""

import json
import shutil
import tempfile
from functools import cached_property
from pathlib import Path
from typing import Any, Dict, Optional

from knack.log import get_logger

from azext_aosm._configuration import ArtifactConfig, VNFConfiguration
from azext_aosm.generate_nfd.nfd_generator_base import NFDGenerator
from azext_aosm.util.constants import (
    CONFIG_MAPPINGS_DIR_NAME,
    DEPLOYMENT_PARAMETERS_FILENAME,
    EXTRA_VHD_PARAMETERS,
    OPTIONAL_DEPLOYMENT_PARAMETERS_FILENAME,
    OPTIONAL_DEPLOYMENT_PARAMETERS_HEADING,
    SCHEMA_PREFIX,
    SCHEMAS_DIR_NAME,
    TEMPLATE_PARAMETERS_FILENAME,
    VHD_PARAMETERS_FILENAME,
    VNF_DEFINITION_BICEP_TEMPLATE_FILENAME,
    VNF_MANIFEST_BICEP_TEMPLATE_FILENAME,
)
from azext_aosm.util.utils import input_ack, snake_case_to_camel_case

logger = get_logger(__name__)

# Different types are used in ARM templates and NFDs. The list accepted by NFDs is
# documented in the AOSM meta-schema. This will be published in the future but for now
# can be found in
# https://microsoft.sharepoint.com/:w:/t/NSODevTeam/Ec7ovdKroSRIv5tumQnWIE0BE-B2LykRcll2Qb9JwfVFMQ
ARM_TO_JSON_PARAM_TYPES: Dict[str, str] = {
    "int": "integer",
    "securestring": "string",
    "bool": "boolean",
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

    def __init__(
        self, config: VNFConfiguration, order_params: bool, interactive: bool
    ):
        self.config = config

        assert isinstance(self.config.arm_template, ArtifactConfig)
        assert self.config.arm_template.file_path

        self.arm_template_path = Path(self.config.arm_template.file_path)
        self.output_directory: Path = self.config.output_directory_for_build

        self._vnfd_bicep_path = Path(
            self.output_directory, VNF_DEFINITION_BICEP_TEMPLATE_FILENAME
        )
        self._manifest_bicep_path = Path(
            self.output_directory, VNF_MANIFEST_BICEP_TEMPLATE_FILENAME
        )
        self.order_params = order_params
        self.interactive = interactive
        self._tmp_dir: Optional[Path] = None
        self.image_name = f"{self.config.nf_name}Image"

    def generate_nfd(self) -> None:
        """
        Generate a VNF NFD which comprises an group, an Artifact Manifest and a NFDV.

        Create a bicep template for an NFD from the ARM template for the VNF.
        """
        # Create temporary directory.
        with tempfile.TemporaryDirectory() as tmpdirname:
            self._tmp_dir = Path(tmpdirname)

            self._create_parameter_files()
            self._copy_to_output_directory()
            print(
                f"Generated NFD bicep templates created in {self.output_directory}"
            )
            print(
                "Please review these templates. When you are happy with them run "
                "`az aosm nfd publish` with the same arguments."
            )

    @property
    def nfd_bicep_path(self) -> Optional[Path]:
        """Returns the path to the bicep file for the NFD if it has been created."""
        if self._vnfd_bicep_path.exists():
            return self._vnfd_bicep_path
        return None

    @property
    def manifest_bicep_path(self) -> Optional[Path]:
        """Returns the path to the bicep file for the NFD if it has been created."""
        if self._manifest_bicep_path.exists():
            return self._manifest_bicep_path
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
                has_default_field
                and not self.vm_parameters[key]["defaultValue"] == ""
            )

            if has_default:
                vm_parameters_with_default[key] = self.vm_parameters[key]
            else:
                vm_parameters_no_default[key] = self.vm_parameters[key]

        return {**vm_parameters_no_default, **vm_parameters_with_default}

    def _create_parameter_files(self) -> None:
        """Create the deployment, template and VHD parameter files."""
        assert self._tmp_dir
        tmp_schemas_directory: Path = self._tmp_dir / SCHEMAS_DIR_NAME
        tmp_schemas_directory.mkdir()
        self.write_deployment_parameters(tmp_schemas_directory)

        tmp_mappings_directory: Path = self._tmp_dir / CONFIG_MAPPINGS_DIR_NAME
        tmp_mappings_directory.mkdir()
        self.write_template_parameters(tmp_mappings_directory)
        self.write_vhd_parameters(tmp_mappings_directory)

    def write_deployment_parameters(self, directory: Path) -> None:
        """
        Write out the NFD deploymentParameters.json file to `directory`

        :param directory: The directory to put this file in.
        """
        logger.debug("Create deploymentParameters.json")

        nfd_parameters = {}
        nfd_parameters_with_default = {}
        vm_parameters_to_exclude = []

        vm_parameters = (
            self.vm_parameters_ordered
            if self.order_params
            else self.vm_parameters
        )

        for key in vm_parameters:
            if key == self.config.image_name_parameter:
                # There is only one correct answer for the image name, so don't ask the
                # user, instead it is hardcoded in config mappings.
                continue

            # Order parameters into those without and then with defaults
            has_default_field = "defaultValue" in self.vm_parameters[key]
            has_default = (
                has_default_field
                and not self.vm_parameters[key]["defaultValue"] == ""
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
            json_type = ARM_TO_JSON_PARAM_TYPES.get(arm_type.lower(), arm_type)

            if has_default:
                nfd_parameters_with_default[key] = {"type": json_type}

            nfd_parameters[key] = {"type": json_type}

        # Now we are out of the vm_parameters loop, we can remove the excluded
        # parameters so they don't get included in templateParameters.json
        # Remove from both ordered and unordered dicts
        for key in vm_parameters_to_exclude:
            self.vm_parameters.pop(key, None)

        deployment_parameters_path = directory / DEPLOYMENT_PARAMETERS_FILENAME

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
                optional_deployment_parameters_path = (
                    directory / OPTIONAL_DEPLOYMENT_PARAMETERS_FILENAME
                )
                with open(
                    optional_deployment_parameters_path, "w", encoding="utf-8"
                ) as _file:
                    _file.write(OPTIONAL_DEPLOYMENT_PARAMETERS_HEADING)
                    _file.write(
                        json.dumps(nfd_parameters_with_default, indent=4)
                    )
                print(
                    "Optional ARM parameters detected. Created "
                    f"{OPTIONAL_DEPLOYMENT_PARAMETERS_FILENAME} to help you choose which "
                    "to expose."
                )

    def write_template_parameters(self, directory: Path) -> None:
        """
        Write out the NFD templateParameters.json file to `directory`.

        :param directory: The directory to put this file in.
        """
        logger.debug("Create %s", TEMPLATE_PARAMETERS_FILENAME)
        vm_parameters = (
            self.vm_parameters_ordered
            if self.order_params
            else self.vm_parameters
        )

        template_parameters = {}

        for key in vm_parameters:
            if key == self.config.image_name_parameter:
                template_parameters[key] = self.image_name
                continue

            template_parameters[key] = f"{{deployParameters.{key}}}"

        template_parameters_path = directory / TEMPLATE_PARAMETERS_FILENAME

        with open(template_parameters_path, "w", encoding="utf-8") as _file:
            _file.write(json.dumps(template_parameters, indent=4))

        logger.debug("%s created", template_parameters_path)

    def write_vhd_parameters(self, directory: Path) -> None:
        """
        Write out the NFD vhdParameters.json file to `directory`.

        :param directory: The directory to put this file in.
        """
        vhd_config = self.config.vhd
        # vhdImageMappingRuleProfile userConfiguration within the NFDV API accepts azureDeployLocation
        # as the location where the image resource should be created from the VHD. The CLI does not
        # expose this as it defaults to the NF deploy location, and we can't think of situations where
        # it should be different.
        vhd_parameters = {
            "imageName": self.image_name,
            **{
                snake_case_to_camel_case(key): value
                for key, value in vhd_config.__dict__.items()
                if key in EXTRA_VHD_PARAMETERS and value is not None
            },
        }

        vhd_parameters_path = directory / VHD_PARAMETERS_FILENAME
        with open(vhd_parameters_path, "w", encoding="utf-8") as _file:
            _file.write(json.dumps(vhd_parameters, indent=4))

        logger.debug("%s created", vhd_parameters_path)

    def _copy_to_output_directory(self) -> None:
        """Copy the static bicep templates and generated config mappings and schema into the build output directory."""
        logger.info("Create NFD bicep %s", self.output_directory)
        assert self._tmp_dir
        Path(self.output_directory).mkdir(exist_ok=True)

        static_bicep_templates_dir = Path(__file__).parent / "templates"

        static_vnfd_bicep_path = (
            static_bicep_templates_dir / VNF_DEFINITION_BICEP_TEMPLATE_FILENAME
        )
        shutil.copy(static_vnfd_bicep_path, self.output_directory)

        static_manifest_bicep_path = (
            static_bicep_templates_dir / VNF_MANIFEST_BICEP_TEMPLATE_FILENAME
        )
        shutil.copy(static_manifest_bicep_path, self.output_directory)
        # Copy everything in the temp directory to the output directory
        shutil.copytree(
            self._tmp_dir,
            self.output_directory,
            dirs_exist_ok=True,
        )

        logger.info("Copied files to %s", self.output_directory)
