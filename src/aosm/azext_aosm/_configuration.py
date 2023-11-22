# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Configuration class for input config file parsing,"""
import abc
import logging
import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from azure.cli.core.azclierror import (
    InvalidArgumentValueError,
    ValidationError,
)
from azext_aosm.util.constants import (
    CNF,
    NF_DEFINITION_OUTPUT_BICEP_PREFIX,
    NF_DEFINITION_JSON_FILENAME,
    NSD,
    NSD_OUTPUT_BICEP_PREFIX,
    VNF,
)

logger = logging.getLogger(__name__)


@dataclass
class ArtifactConfig:
    # artifact.py checks for the presence of the default descriptions, change
    # there if you change the descriptions.
    artifact_name: str = ""
    version: Optional[str] = ""
    file_path: Optional[str] = None

    @classmethod
    def helptext(cls) -> "ArtifactConfig":
        """
        Build an object where each value is helptext for that field.
        """
        return ArtifactConfig(
            artifact_name="Optional. Name of the artifact.",
            version="Version of the artifact in A.B.C format.",
            file_path=(
                "File path of the artifact you wish to upload from your local disk. "
                "Relative paths are relative to the configuration file. "
                "On Windows escape any backslash with another backslash."
            ),

        )

    def validate(self):
        """
        Validate the configuration.
        """
        if not self.version:
            raise ValidationError("version must be set.")
        if not self.file_path:
            raise ValidationError("file_path must be set.")


@dataclass
class VhdArtifactConfig(ArtifactConfig):
    # If you add a new property to this class, consider updating EXTRA_VHD_PARAMETERS in
    # constants.py - see comment there for details.
    blob_sas_url: Optional[str] = None
    image_disk_size_GB: Optional[Union[str, int]] = None
    image_hyper_v_generation: Optional[str] = None
    image_api_version: Optional[str] = None

    def __post_init__(self):
        """
        Convert parameters to the correct types.
        """
        if (
            isinstance(self.image_disk_size_GB, str)
            and self.image_disk_size_GB.isdigit()
        ):
            self.image_disk_size_GB = int(self.image_disk_size_GB)

    @classmethod
    def helptext(cls) -> "VhdArtifactConfig":
        """
        Build an object where each value is helptext for that field.
        """

        artifact_config = ArtifactConfig.helptext()
        artifact_config.file_path = (
            "Optional. File path of the artifact you wish to upload from your local disk. "
            "Delete if not required. Relative paths are relative to the configuration file."
            "On Windows escape any backslash with another backslash."
        )
        artifact_config.version = (
            "Version of the artifact in A-B-C format."
        )
        return VhdArtifactConfig(
            blob_sas_url=(
                "Optional. SAS URL of the blob artifact you wish to copy to your Artifact"
                " Store. Delete if not required."
            ),
            image_disk_size_GB=(
                "Optional. Specifies the size of empty data disks in gigabytes. "
                "This value cannot be larger than 1023 GB. Delete if not required."
            ),
            image_hyper_v_generation=(
                "Optional. Specifies the HyperVGenerationType of the VirtualMachine "
                "created from the image. Valid values are V1 and V2. V1 is the default if "
                "not specified. Delete if not required."
            ),
            image_api_version=(
                "Optional. The ARM API version used to create the "
                "Microsoft.Compute/images resource. Delete if not required."
            ),
            **asdict(artifact_config),
        )

    def validate(self):
        """
        Validate the configuration.
        """
        if not self.version:
            raise ValidationError("version must be set for vhd.")
        if self.blob_sas_url and self.file_path:
            raise ValidationError("Only one of file_path or blob_sas_url may be set for vhd.")
        if not (self.blob_sas_url or self.file_path):
            raise ValidationError("One of file_path or sas_blob_url must be set for vhd.")


@dataclass
class Configuration(abc.ABC):
    config_file: Optional[str] = None
    publisher_name: str = ""
    publisher_resource_group_name: str = ""
    acr_artifact_store_name: str = ""
    location: str = ""

    def __post_init__(self):
        """
        Set defaults for resource group and ACR as the publisher name tagged with -rg or -acr
        """
        if self.publisher_name:
            if not self.publisher_resource_group_name:
                self.publisher_resource_group_name = f"{self.publisher_name}-rg"
            if not self.acr_artifact_store_name:
                self.acr_artifact_store_name = f"{self.publisher_name}-acr"

    @classmethod
    def helptext(cls):
        """
        Build an object where each value is helptext for that field.
        """
        return Configuration(
            publisher_name=(
                "Name of the Publisher resource you want your definition published to. "
                "Will be created if it does not exist."
            ),
            publisher_resource_group_name=(
                "Optional. Resource group for the Publisher resource. "
                "Will be created if it does not exist (with a default name if none is supplied)."
            ),
            acr_artifact_store_name=(
                "Optional. Name of the ACR Artifact Store resource. "
                "Will be created if it does not exist (with a default name if none is supplied)."
            ),
            location="Azure location to use when creating resources.",
        )

    def validate(self):
        """
        Validate the configuration.
        """
        if not self.location:
            raise ValidationError("Location must be set")
        if not self.publisher_name:
            raise ValidationError("Publisher name must be set")
        if not self.publisher_resource_group_name:
            raise ValidationError("Publisher resource group name must be set")
        if not self.acr_artifact_store_name:
            raise ValidationError("ACR Artifact Store name must be set")

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
        """The list of ACR manifest names."""
        raise NotImplementedError("Subclass must define property")


@dataclass
class NFConfiguration(Configuration):
    """Network Function configuration."""

    nf_name: str = ""
    version: str = ""

    @classmethod
    def helptext(cls) -> "NFConfiguration":
        """
        Build an object where each value is helptext for that field.
        """
        return NFConfiguration(
            nf_name="Name of NF definition",
            version="Version of the NF definition in A.B.C format.",
            **asdict(Configuration.helptext()),
        )

    def validate(self):
        """
        Validate the configuration.
        """
        super().validate()
        if not self.nf_name:
            raise ValidationError("nf_name must be set")
        if not self.version:
            raise ValidationError("version must be set")

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
    blob_artifact_store_name: str = ""
    image_name_parameter: str = ""
    arm_template: Union[Dict[str, str], ArtifactConfig] = field(default_factory=ArtifactConfig)
    vhd: Union[Dict[str, str], VhdArtifactConfig] = field(default_factory=VhdArtifactConfig)

    @classmethod
    def helptext(cls) -> "VNFConfiguration":
        """
        Build an object where each value is helptext for that field.
        """
        return VNFConfiguration(
            blob_artifact_store_name=(
                "Optional. Name of the storage account Artifact Store resource. Will be created if it "
                "does not exist (with a default name if none is supplied)."
            ),
            image_name_parameter=(
                "The parameter name in the VM ARM template which specifies the name of the "
                "image to use for the VM."
            ),
            arm_template=ArtifactConfig.helptext(),
            vhd=VhdArtifactConfig.helptext(),
            **asdict(NFConfiguration.helptext()),
        )

    def __post_init__(self):
        """
        Cope with deserializing subclasses from dicts to ArtifactConfig.

        Used when creating VNFConfiguration object from a loaded json config file.
        """
        super().__post_init__()
        if self.publisher_name and not self.blob_artifact_store_name:
            self.blob_artifact_store_name = f"{self.publisher_name}-sa"

        if isinstance(self.arm_template, dict):
            if self.arm_template.get("file_path"):
                self.arm_template["file_path"] = self.path_from_cli_dir(
                    self.arm_template["file_path"]
                )
            self.arm_template = ArtifactConfig(**self.arm_template)

        if isinstance(self.vhd, dict):
            if self.vhd.get("file_path"):
                self.vhd["file_path"] = self.path_from_cli_dir(self.vhd["file_path"])
            self.vhd = VhdArtifactConfig(**self.vhd)

    def validate(self) -> None:
        """
        Validate the configuration passed in.

        :raises ValidationError for any invalid config
        """
        super().validate()

        assert isinstance(self.vhd, VhdArtifactConfig)
        assert isinstance(self.arm_template, ArtifactConfig)
        self.vhd.validate()
        self.arm_template.validate()

        assert self.vhd.version
        assert self.arm_template.version

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

    @property
    def sa_manifest_name(self) -> str:
        """Return the Storage account manifest name from the NFD name."""
        sanitized_nf_name = self.nf_name.lower().replace("_", "-")
        return f"{sanitized_nf_name}-sa-manifest-{self.version.replace('.', '-')}"

    @property
    def output_directory_for_build(self) -> Path:
        """Return the local folder for generating the bicep template to."""
        assert isinstance(self.arm_template, ArtifactConfig)
        assert self.arm_template.file_path
        arm_template_name = Path(self.arm_template.file_path).stem
        return Path(f"{NF_DEFINITION_OUTPUT_BICEP_PREFIX}{arm_template_name}")


@dataclass
class HelmPackageConfig:
    name: str = ""
    path_to_chart: str = ""
    path_to_mappings: str = ""
    depends_on: List[str] = field(default_factory=lambda: [])

    @classmethod
    def helptext(cls):
        """
        Build an object where each value is helptext for that field.
        """
        return HelmPackageConfig(
            name="Name of the Helm package",
            path_to_chart=(
                "File path of Helm Chart on local disk. Accepts .tgz, .tar or .tar.gz."
                " Use Linux slash (/) file separator even if running on Windows."
            ),
            path_to_mappings=(
                "File path of value mappings on local disk where chosen values are replaced "
                "with deploymentParameter placeholders. Accepts .yaml or .yml. If left as a "
                "blank string, a value mappings file will be generated with every value "
                "mapped to a deployment parameter. Use a blank string and --interactive on "
                "the build command to interactively choose which values to map."
            ),
            depends_on=(
                "Names of the Helm packages this package depends on. "
                "Leave as an empty array if no dependencies"
            ),
        )

    def validate(self):
        """
        Validate the configuration.
        """
        if not self.name:
            raise ValidationError("name must be set")
        if not self.path_to_chart:
            raise ValidationError("path_to_chart must be set")


@dataclass
class CNFImageConfig:
    """CNF Image config settings."""

    source_registry: str = ""
    source_registry_namespace: str = ""
    source_local_docker_image: str = ""

    def __post_init__(self):
        """
        Ensure that all config is lower case.

        ACR names can be uppercase but the login server is always lower case and docker
        and az acr import commands require lower case. Might as well do the namespace
        and docker image too although much less likely that the user has accidentally
        pasted these with upper case.
        """
        self.source_registry = self.source_registry.lower()
        self.source_registry_namespace = self.source_registry_namespace.lower()
        self.source_local_docker_image = self.source_local_docker_image.lower()

    @classmethod
    def helptext(cls) -> "CNFImageConfig":
        """
        Build an object where each value is helptext for that field.
        """
        return CNFImageConfig(
            source_registry=(
                "Optional. Login server of the source acr registry from which to pull the "
                "image(s). For example sourceacr.azurecr.io. Leave blank if you have set "
                "source_local_docker_image."
            ),
            source_registry_namespace=(
                "Optional. Namespace of the repository of the source acr registry from which "
                "to pull. For example if your repository is samples/prod/nginx then set this to"
                " samples/prod . Leave blank if the image is in the root namespace or you have "
                "set source_local_docker_image."
                "See https://learn.microsoft.com/en-us/azure/container-registry/"
                "container-registry-best-practices#repository-namespaces for further details."
            ),
            source_local_docker_image=(
                "Optional. Image name of the source docker image from local machine. For "
                "limited use case where the CNF only requires a single docker image and exists "
                "in the local docker repository. Set to blank of not required."
            ),
        )

    def validate(self):
        """
        Validate the configuration.
        """
        if self.source_registry_namespace and not self.source_registry:
            raise ValidationError(
                "Config validation error. The image source registry namespace should "
                "only be configured if a source registry is configured."
            )

        if self.source_registry and self.source_local_docker_image:
            raise ValidationError(
                "Only one of source_registry and source_local_docker_image can be set."
            )

        if not (self.source_registry or self.source_local_docker_image):
            raise ValidationError(
                "One of source_registry or source_local_docker_image must be set."
            )


@dataclass
class CNFConfiguration(NFConfiguration):
    images: Union[Dict[str, str], CNFImageConfig] = field(default_factory=CNFImageConfig)
    helm_packages: List[Union[Dict[str, Any], HelmPackageConfig]] = field(
        default_factory=lambda: []
    )

    def __post_init__(self):
        """
        Cope with deserializing subclasses from dicts to HelmPackageConfig.

        Used when creating CNFConfiguration object from a loaded json config file.
        """
        super().__post_init__()
        for package_index, package in enumerate(self.helm_packages):
            if isinstance(package, dict):
                package["path_to_chart"] = self.path_from_cli_dir(
                    package["path_to_chart"]
                )
                package["path_to_mappings"] = self.path_from_cli_dir(
                    package["path_to_mappings"]
                )
                self.helm_packages[package_index] = HelmPackageConfig(**dict(package))
        if isinstance(self.images, dict):
            self.images = CNFImageConfig(**self.images)

    @classmethod
    def helptext(cls) -> "CNFConfiguration":
        """
        Build an object where each value is helptext for that field.
        """
        return CNFConfiguration(
            images=CNFImageConfig.helptext(),
            helm_packages=[HelmPackageConfig.helptext()],
            **asdict(NFConfiguration.helptext()),
        )

    @property
    def output_directory_for_build(self) -> Path:
        """Return the directory the build command will writes its output to."""
        return Path(f"{NF_DEFINITION_OUTPUT_BICEP_PREFIX}{self.nf_name}")

    def validate(self):
        """
        Validate the CNF config.

        :raises ValidationError: If source registry ID doesn't match the regex
        """
        assert isinstance(self.images, CNFImageConfig)
        super().validate()

        self.images.validate()

        for helm_package in self.helm_packages:
            assert isinstance(helm_package, HelmPackageConfig)
            helm_package.validate()


@dataclass
class NFDRETConfiguration:  # pylint: disable=too-many-instance-attributes
    """The configuration required for an NFDV that you want to include in an NSDV."""

    publisher: str = ""
    publisher_resource_group: str = ""
    name: str = ""
    version: str = ""
    publisher_offering_location: str = ""
    type: str = ""
    multiple_instances: Union[str, bool] = False

    def __post_init__(self):
        """
        Convert parameters to the correct types.
        """
        # Cope with multiple_instances being supplied as a string, rather than a bool.
        if isinstance(self.multiple_instances, str):
            if self.multiple_instances.lower() == "true":
                self.multiple_instances = True
            elif self.multiple_instances.lower() == "false":
                self.multiple_instances = False

    @classmethod
    def helptext(cls) -> "NFDRETConfiguration":
        """
        Build an object where each value is helptext for that field.
        """
        return NFDRETConfiguration(
            publisher="The name of the existing Network Function Definition Group to deploy using this NSD",
            publisher_resource_group="The resource group that the publisher is hosted in.",
            name="The name of the existing Network Function Definition Group to deploy using this NSD",
            version=(
                "The version of the existing Network Function Definition to base this NSD on.  "
                "This NSD will be able to deploy any NFDV with deployment parameters compatible "
                "with this version."
            ),
            publisher_offering_location="The region that the NFDV is published to.",
            type="Type of Network Function. Valid values are 'cnf' or 'vnf'",
            multiple_instances=(
                "Set to true or false.  Whether the NSD should allow arbitrary numbers of this "
                "type of NF.  If set to false only a single instance will be allowed.  Only "
                "supported on VNFs, must be set to false on CNFs."
            ),
        )

    def validate(self) -> None:
        """
        Validate the configuration passed in.

        :raises ValidationError for any invalid config
        """
        if not self.name:
            raise ValidationError("Network function definition name must be set")

        if not self.publisher:
            raise ValidationError(f"Publisher name must be set for {self.name}")

        if not self.publisher_resource_group:
            raise ValidationError(
                f"Publisher resource group name must be set for {self.name}"
            )

        if not self.version:
            raise ValidationError(
                f"Network function definition version must be set for {self.name}"
            )

        if not self.publisher_offering_location:
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
        """Return the parameters of the ARM template for this RET to be uploaded as part of
        the NSDV."""
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
    def nf_bicep_filename(self) -> str:
        """Return the name of the bicep template for deploying the NFs."""
        return f"{self.name}_nf.bicep"

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
    network_functions: List[Union[NFDRETConfiguration, Dict[str, Any]]] = field(
        default_factory=lambda: []
    )
    nsd_name: str = ""
    nsd_version: str = ""
    nsdv_description: str = ""

    def __post_init__(self):
        """Covert things to the correct format."""
        super().__post_init__()
        if self.network_functions and isinstance(self.network_functions[0], dict):
            nf_ret_list = [
                NFDRETConfiguration(**config) for config in self.network_functions
            ]
            self.network_functions = nf_ret_list

    @classmethod
    def helptext(cls) -> "NSConfiguration":
        """
        Build a NSConfiguration object where each value is helptext for that field.
        """
        nsd_helptext = NSConfiguration(
            network_functions=[asdict(NFDRETConfiguration.helptext())],
            nsd_name=(
                "Network Service Design (NSD) name. This is the collection of Network Service"
                " Design Versions. Will be created if it does not exist."
            ),
            nsd_version=(
                "Version of the NSD to be created. This should be in the format A.B.C"
            ),
            nsdv_description="Description of the NSDV.",
            **asdict(Configuration.helptext()),
        )

        return nsd_helptext

    def validate(self):
        """
        Validate the configuration passed in.

        :raises ValueError for any invalid config
        """
        super().validate()
        if not self.network_functions:
            raise ValueError(("At least one network function must be included."))

        for configuration in self.network_functions:
            configuration.validate()
        if not self.nsd_name:
            raise ValueError("nsd_name must be set")
        if not self.nsd_version:
            raise ValueError("nsd_version must be set")

    @property
    def output_directory_for_build(self) -> Path:
        """Return the local folder for generating the bicep template to."""
        current_working_directory = os.getcwd()
        return Path(current_working_directory, NSD_OUTPUT_BICEP_PREFIX)

    @property
    def nfvi_site_name(self) -> str:
        """Return the name of the NFVI used for the NSDV."""
        return f"{self.nsd_name}_NFVI"

    @property
    def cg_schema_name(self) -> str:
        """Return the name of the Configuration Schema used for the NSDV."""
        return f"{self.nsd_name.replace('-', '_')}_ConfigGroupSchema"

    @property
    def acr_manifest_names(self) -> List[str]:
        """The list of ACR manifest names for all the NF ARM templates."""
        acr_manifest_names = []
        for nf in self.network_functions:
            assert isinstance(nf, NFDRETConfiguration)
            acr_manifest_names.append(nf.acr_manifest_name(self.nsd_version))

        logger.debug("ACR manifest names: %s", acr_manifest_names)
        return acr_manifest_names


def get_configuration(configuration_type: str, config_file: str) -> Configuration:
    """
    Return the correct configuration object based on the type.

    :param configuration_type: The type of configuration to return
    :param config_file: The path to the config file
    :return: The configuration object
    """
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config_as_dict = json.loads(f.read())
    except json.decoder.JSONDecodeError as e:
        raise InvalidArgumentValueError(
            f"Config file {config_file} is not valid JSON: {e}"
        ) from e

    config: Configuration
    try:
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
    except TypeError as typeerr:
        raise InvalidArgumentValueError(
            f"Config file {config_file} is not valid: {typeerr}"
        ) from typeerr

    config.validate()

    return config
