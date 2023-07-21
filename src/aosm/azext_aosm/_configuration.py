# --------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT
# License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------
"""Configuration class for input config file parsing,"""
import abc
import logging
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from azure.cli.core.azclierror import InvalidArgumentValueError, ValidationError
from azext_aosm.util.constants import (
    CNF,
    NF_DEFINITION_OUTPUT_BICEP_PREFIX,
    NF_DEFINITION_JSON_FILENAME,
    NSD,
    NSD_OUTPUT_BICEP_PREFIX,
    VNF,
    SOURCE_ACR_REGEX,
)

logger = logging.getLogger(__name__)

DESCRIPTION_MAP: Dict[str, str] = {
    "publisher_resource_group_name": (
        "Resource group for the Publisher resource. "
        "Will be created if it does not exist."
    ),
    "publisher_name": (
        "Name of the Publisher resource you want your definition published to. "
        "Will be created if it does not exist."
    ),
    "publisher_name_nsd": (
        "Name of the Publisher resource you want your design published to. "
        "This should be the same as the publisher used for your NFDVs"
    ),
    "publisher_resource_group_name_nsd": "Resource group for the Publisher resource.",
    "nf_name": "Name of NF definition",
    "version": "Version of the NF definition",
    "acr_artifact_store_name": (
        "Name of the ACR Artifact Store resource. Will be created if it does not exist."
    ),
    "location": "Azure location to use when creating resources.",
    "blob_artifact_store_name": (
        "Name of the storage account Artifact Store resource. Will be created if it "
        "does not exist."
    ),
    "artifact_name": "Name of the artifact",
    "file_path": (
        "Optional. File path of the artifact you wish to upload from your local disk. "
        "Delete if not required."
    ),
    "blob_sas_url": (
        "Optional. SAS URL of the blob artifact you wish to copy to your Artifact"
        " Store. Delete if not required."
    ),
    "artifact_version": (
        "Version of the artifact. For VHDs this must be in format A-B-C. "
        "For ARM templates this must be in format A.B.C"
    ),
    "nsdv_description": "Description of the NSDV",
    "nsdg_name": (
        "Network Service Design Group Name. This is the collection of Network Service"
        " Design Versions. Will be created if it does not exist."
    ),
    "nsd_version": (
        "Version of the NSD to be created. This should be in the format A.B.C"
    ),
    "helm_package_name": "Name of the Helm package",
    "path_to_chart": (
        "File path of Helm Chart on local disk. Accepts .tgz, .tar or .tar.gz"
    ),
    "path_to_mappings": (
        "File path of value mappings on local disk where chosen values are replaced "
        "with deploymentParameter placeholders. Accepts .yaml or .yml. If left as a "
        "blank string, a value mappings file will be generated with every value "
        "mapped to a deployment parameter. Use a blank string and --interactive on "
        "the build command to interactively choose which values to map."
    ),
    "helm_depends_on": (
        "Names of the Helm packages this package depends on. "
        "Leave as an empty array if no dependencies"
    ),
    "image_name_parameter": (
        "The parameter name in the VM ARM template which specifies the name of the "
        "image to use for the VM."
    ),
    "source_registry_id": (
        "Resource ID of the source acr registry from which to pull the image"
    ),
    "source_registry_namespace": (
        "Optional. Namespace of the repository of the source acr registry from which "
        "to pull. For example if your repository is samples/prod/nginx then set this to"
        " samples/prod . Leave blank if the image is in the root namespace."
        "See https://learn.microsoft.com/en-us/azure/container-registry/"
        "container-registry-best-practices#repository-namespaces for further details."
    ),
}


@dataclass
class ArtifactConfig:
    artifact_name: str = DESCRIPTION_MAP["artifact_name"]
    # artifact.py checks for the presence of the default descriptions, change
    # there if you change the descriptions.
    file_path: Optional[str] = DESCRIPTION_MAP["file_path"]
    blob_sas_url: Optional[str] = DESCRIPTION_MAP["blob_sas_url"]
    version: Optional[str] = DESCRIPTION_MAP["artifact_version"]


@dataclass
class Configuration(abc.ABC):
    config_file: Optional[str] = None
    publisher_name: str = DESCRIPTION_MAP["publisher_name"]
    publisher_resource_group_name: str = DESCRIPTION_MAP[
        "publisher_resource_group_name"
    ]
    acr_artifact_store_name: str = DESCRIPTION_MAP["acr_artifact_store_name"]
    location: str = DESCRIPTION_MAP["location"]

    def path_from_cli_dir(self, path: str) -> str:
        """
        Convert path from config file to path from current directory.

        We assume that the path supplied in the config file is relative to the
        configuration file.  That isn't the same as the path relative to where ever the
        CLI is being run from.  This function fixes that up.

        :param path: The path relative to the config file.
        """
        assert self.config_file

        # If no path has been supplied we shouldn't try to update it.
        if path == "":
            return ""

        # If it is an absolute path then we don't need to monkey around with it.
        if os.path.isabs(path):
            return path

        config_file_dir = Path(self.config_file).parent

        updated_path = str(config_file_dir / path)

        logger.debug("Updated path: %s", updated_path)

        return updated_path

    @property
    def output_directory_for_build(self) -> Path:
        """Base class method to ensure subclasses implement this function."""
        raise NotImplementedError("Subclass must define property")

    @property
    def acr_manifest_names(self) -> List[str]:
        """
        The list of ACR manifest names..
        """
        raise NotImplementedError("Subclass must define property")


@dataclass
class NFConfiguration(Configuration):
    """Network Function configuration."""

    publisher_name: str = DESCRIPTION_MAP["publisher_name"]
    publisher_resource_group_name: str = DESCRIPTION_MAP[
        "publisher_resource_group_name"
    ]
    nf_name: str = DESCRIPTION_MAP["nf_name"]
    version: str = DESCRIPTION_MAP["version"]
    acr_artifact_store_name: str = DESCRIPTION_MAP["acr_artifact_store_name"]
    location: str = DESCRIPTION_MAP["location"]

    @property
    def nfdg_name(self) -> str:
        """Return the NFD Group name from the NFD name."""
        return f"{self.nf_name}-nfdg"

    @property
    def acr_manifest_names(self) -> List[str]:
        """
        Return the ACR manifest name from the NFD name.

        This is returned in a list for consistency with the NSConfiguration, where there
        can be multiple ACR manifests.
        """
        sanitized_nf_name = self.nf_name.lower().replace("_", "-")
        return [f"{sanitized_nf_name}-acr-manifest-{self.version.replace('.', '-')}"]


@dataclass
class VNFConfiguration(NFConfiguration):
    blob_artifact_store_name: str = DESCRIPTION_MAP["blob_artifact_store_name"]
    image_name_parameter: str = DESCRIPTION_MAP["image_name_parameter"]
    arm_template: Any = ArtifactConfig()
    vhd: Any = ArtifactConfig()

    def __post_init__(self):
        """
        Cope with deserializing subclasses from dicts to ArtifactConfig.

        Used when creating VNFConfiguration object from a loaded json config file.
        """
        if isinstance(self.arm_template, dict):
            self.arm_template["file_path"] = self.path_from_cli_dir(
                self.arm_template["file_path"]
            )
            self.arm_template = ArtifactConfig(**self.arm_template)

        if isinstance(self.vhd, dict):
            if self.vhd.get("file_path"):
                self.vhd["file_path"] = self.path_from_cli_dir(self.vhd["file_path"])
            self.vhd = ArtifactConfig(**self.vhd)
            self.validate()

    def validate(self) -> None:
        """
        Validate the configuration passed in.

        :raises ValidationError for any invalid config
        """

        if self.vhd.version == DESCRIPTION_MAP["version"]:
            # Config has not been filled in. Don't validate.
            return

        if "." in self.vhd.version or "-" not in self.vhd.version:
            raise ValidationError(
                "Config validation error. VHD artifact version should be in format"
                " A-B-C"
            )
        if "." not in self.arm_template.version or "-" in self.arm_template.version:
            raise ValidationError(
                "Config validation error. ARM template artifact version should be in"
                " format A.B.C"
            )
        filepath_set = (
            self.vhd.file_path and self.vhd.file_path != DESCRIPTION_MAP["file_path"]
        )
        sas_set = (
            self.vhd.blob_sas_url
            and self.vhd.blob_sas_url != DESCRIPTION_MAP["blob_sas_url"]
        )
        # If these are the same, either neither is set or both are, both of which are errors
        if filepath_set == sas_set:
            raise ValidationError(
                "Config validation error. VHD config must have either a local filepath"
                " or a blob SAS URL"
            )

        if filepath_set:
            # Explicitly set the blob SAS URL to None to avoid other code having to
            # check if the value is the default description
            self.vhd.blob_sas_url = None
        elif sas_set:
            self.vhd.file_path = None

    @property
    def sa_manifest_name(self) -> str:
        """Return the Storage account manifest name from the NFD name."""
        sanitized_nf_name = self.nf_name.lower().replace("_", "-")
        return f"{sanitized_nf_name}-sa-manifest-{self.version.replace('.', '-')}"

    @property
    def output_directory_for_build(self) -> Path:
        """Return the local folder for generating the bicep template to."""
        arm_template_name = Path(self.arm_template.file_path).stem
        return Path(f"{NF_DEFINITION_OUTPUT_BICEP_PREFIX}{arm_template_name}")


@dataclass
class HelmPackageConfig:
    name: str = DESCRIPTION_MAP["helm_package_name"]
    path_to_chart: str = DESCRIPTION_MAP["path_to_chart"]
    path_to_mappings: str = DESCRIPTION_MAP["path_to_mappings"]
    depends_on: List[str] = field(
        default_factory=lambda: [DESCRIPTION_MAP["helm_depends_on"]]
    )


@dataclass
class CNFConfiguration(NFConfiguration):
    source_registry_id: str = DESCRIPTION_MAP["source_registry_id"]
    source_registry_namespace: str = DESCRIPTION_MAP["source_registry_namespace"]
    helm_packages: List[Any] = field(default_factory=lambda: [HelmPackageConfig()])

    def __post_init__(self):
        """
        Cope with deserializing subclasses from dicts to HelmPackageConfig.

        Used when creating CNFConfiguration object from a loaded json config file.
        """
        for package_index, package in enumerate(self.helm_packages):
            if isinstance(package, dict):
                package["path_to_chart"] = self.path_from_cli_dir(
                    package["path_to_chart"]
                )
                package["path_to_mappings"] = self.path_from_cli_dir(
                    package["path_to_mappings"]
                )
                self.helm_packages[package_index] = HelmPackageConfig(**dict(package))

    @property
    def output_directory_for_build(self) -> Path:
        """Return the directory the build command will writes its output to."""
        return Path(f"{NF_DEFINITION_OUTPUT_BICEP_PREFIX}{self.nf_name}")

    def validate(self):
        """
        Validate the CNF config.

        :raises ValidationError: If source registry ID doesn't match the regex
        """
        if self.source_registry_id == DESCRIPTION_MAP["source_registry_id"]:
            # Config has not been filled in. Don't validate.
            return

        source_registry_match = re.search(SOURCE_ACR_REGEX, self.source_registry_id)
        if not source_registry_match or len(source_registry_match.groups()) < 2:
            raise ValidationError(
                "CNF config has an invalid source registry ID. Please run `az aosm "
                "nfd generate-config` to see the valid formats."
            )


NFD_NAME = (
    "The name of the existing Network Function Definition to deploy using this NSD"
)
NFD_VERSION = "The version of the existing Network Function Definition to base this NSD on.  This NSD will be able to deploy any NFDV with deployment parameters compatible with this version."
NFD_LOCATION = "The region that the NFDV is published to."
PUBLISHER_RESOURCE_GROUP = "The resource group that the publisher is hosted in."
PUBLISHER_NAME = "The name of the publisher that this NFDV is published under."
NFD_TYPE = "Type of Network Function. Valid values are 'cnf' or 'vnf'"
MULTIPLE_INSTANCES = (
    "Set to true or false.  Whether the NSD should allow arbitrary numbers of this "
    "type of NF.  If set to false only a single instance will be allowed.  Only "
    "supported on VNFs, must be set to false on CNFs."
)


@dataclass
class NFDRETConfiguration:
    publisher: str = PUBLISHER_NAME
    publisher_resource_group: str = PUBLISHER_RESOURCE_GROUP
    name: str = NFD_NAME
    version: str = NFD_VERSION
    publisher_offering_location: str = NFD_LOCATION
    type: str = NFD_TYPE
    multiple_instances: Union[str, bool] = MULTIPLE_INSTANCES

    def validate(self) -> None:
        """
        Validate the configuration passed in.

        :raises ValidationError for any invalid config
        """
        if self.name == NFD_NAME:
            raise ValidationError("Network function definition name must be set")

        if self.publisher == PUBLISHER_NAME:
            raise ValidationError(f"Publisher name must be set for {self.name}")

        if self.publisher_resource_group == PUBLISHER_RESOURCE_GROUP:
            raise ValidationError(
                f"Publisher resource group name must be set for {self.name}"
            )

        if self.version == NFD_VERSION:
            raise ValidationError(
                f"Network function definition version must be set for {self.name}"
            )

        if self.publisher_offering_location == NFD_LOCATION:
            raise ValidationError(
                f"Network function definition offering location must be set, for {self.name}"
            )

        if self.type not in [CNF, VNF]:
            raise ValueError(
                f"Network Function Type must be cnf or vnf for {self.name}"
            )

        if not isinstance(self.multiple_instances, bool):
            raise ValueError(
                f"multiple_instances must be a boolean for for {self.name}"
            )

        # There is currently a NFM bug that means that multiple copies of the same NF
        # cannot be deployed to the same custom location:
        # https://portal.microsofticm.com/imp/v3/incidents/details/405078667/home
        if self.type == CNF and self.multiple_instances:
            raise ValueError("Multiple instances is not supported on CNFs.")

    @property
    def build_output_folder_name(self) -> Path:
        """Return the local folder for generating the bicep template to."""
        current_working_directory = os.getcwd()
        return Path(current_working_directory, NSD_OUTPUT_BICEP_PREFIX)

    @property
    def arm_template(self) -> ArtifactConfig:
        """
        Return the parameters of the ARM template to be uploaded as part of
        the NSDV.
        """
        artifact = ArtifactConfig()
        artifact.artifact_name = f"{self.name.lower()}_nf_artifact"

        # We want the ARM template version to match the NSD version, but we don't have
        # that information here.
        artifact.version = None
        artifact.file_path = os.path.join(
            self.build_output_folder_name, NF_DEFINITION_JSON_FILENAME
        )
        return artifact

    @property
    def resource_element_name(self) -> str:
        """Return the name of the resource element."""
        artifact_name = self.arm_template.artifact_name
        return f"{artifact_name}_resource_element"

    def acr_manifest_name(self, nsd_version: str) -> str:
        """Return the ACR manifest name from the NFD name."""
        return (
            f"{self.name.lower().replace('_', '-')}"
            f"-nf-acr-manifest-{nsd_version.replace('.', '-')}"
        )


@dataclass
class NSConfiguration(Configuration):
    network_functions: List[NFDRETConfiguration] = field(
        default_factory=lambda: [
            NFDRETConfiguration(),
        ]
    )
    nsdg_name: str = DESCRIPTION_MAP["nsdg_name"]
    nsd_version: str = DESCRIPTION_MAP["nsd_version"]
    nsdv_description: str = DESCRIPTION_MAP["nsdv_description"]

    def __post_init__(self):
        """
        Covert things to the correct format.
        """
        if self.network_functions and isinstance(self.network_functions[0], dict):
            nf_ret_list = [
                NFDRETConfiguration(**config) for config in self.network_functions
            ]
            self.network_functions = nf_ret_list

    def validate(self):
        # validate that all of the configuration parameters are set

        if self.location == DESCRIPTION_MAP["location"] or "":
            raise ValueError("Location must be set")
        if self.publisher_name == DESCRIPTION_MAP["publisher_name_nsd"] or "":
            raise ValueError("Publisher name must be set")
        if (
            self.publisher_resource_group_name
            == DESCRIPTION_MAP["publisher_resource_group_name_nsd"]
            or ""
        ):
            raise ValueError("Publisher resource group name must be set")
        if (
            self.acr_artifact_store_name == DESCRIPTION_MAP["acr_artifact_store_name"]
            or ""
        ):
            raise ValueError("ACR Artifact Store name must be set")
        if self.network_functions == [] or None:
            raise ValueError(("At least one network function must be included."))
        else:
            for configuration in self.network_functions:
                configuration.validate()
        if self.nsdg_name == DESCRIPTION_MAP["nsdg_name"] or "":
            raise ValueError("NSD name must be set")
        if self.nsd_version == DESCRIPTION_MAP["nsd_version"] or "":
            raise ValueError("NSD Version must be set")

    @property
    def output_directory_for_build(self) -> Path:
        """Return the local folder for generating the bicep template to."""
        current_working_directory = os.getcwd()
        return Path(current_working_directory, NSD_OUTPUT_BICEP_PREFIX)

    @property
    def nfvi_site_name(self) -> str:
        """Return the name of the NFVI used for the NSDV."""
        return f"{self.nsdg_name}_NFVI"

    @property
    def cg_schema_name(self) -> str:
        """Return the name of the Configuration Schema used for the NSDV."""
        return f"{self.nsdg_name.replace('-', '_')}_ConfigGroupSchema"

    @property
    def acr_manifest_names(self) -> List[str]:
        """
        The list of ACR manifest names for all the NF ARM templates.
        """
        return [nf.acr_manifest_name(self.nsd_version) for nf in self.network_functions]


def get_configuration(
    configuration_type: str, config_file: Optional[str] = None
) -> Configuration:
    """
    Return the correct configuration object based on the type.

    :param configuration_type: The type of configuration to return
    :param config_file: The path to the config file
    :return: The configuration object
    """
    if config_file:
        with open(config_file, "r", encoding="utf-8") as f:
            config_as_dict = json.loads(f.read())
    else:
        config_as_dict = {}

    config: Configuration

    if configuration_type == VNF:
        config = VNFConfiguration(config_file=config_file, **config_as_dict)
    elif configuration_type == CNF:
        config = CNFConfiguration(config_file=config_file, **config_as_dict)
    elif configuration_type == NSD:
        config = NSConfiguration(config_file=config_file, **config_as_dict)
    else:
        raise InvalidArgumentValueError(
            "Definition type not recognized, options are: vnf, cnf or nsd"
        )

    return config
