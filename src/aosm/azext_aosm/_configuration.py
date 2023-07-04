import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from azure.cli.core.azclierror import InvalidArgumentValueError, ValidationError

from azext_aosm.util.constants import (
    CNF,
    NF_DEFINITION_OUTPUT_BICEP_PREFIX,
    NF_DEFINITION_JSON_FILENAME,
    NSD,
    NSD_OUTPUT_BICEP_PREFIX,
    VNF,
    SOURCE_ACR_REGEX
)

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
    "network_function_definition_group_name": (
        "Existing Network Function Definition Group Name. "
        "This can be created using the 'az aosm nfd' commands."
    ),
    "network_function_definition_version_name": (
        "Existing Network Function Definition Version Name. "
        "This can be created using the 'az aosm nfd' commands."
    ),
    "network_function_definition_offering_location": (
        "Offering location of the Network Function Definition"
    ),
    "network_function_type": (
        "Type of nf in the definition. Valid values are 'cnf' or 'vnf'"
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
    # artifact.py checks for the presence of the default descriptions, change there if
    # you change the descriptions.
    file_path: Optional[str] = DESCRIPTION_MAP["file_path"]
    blob_sas_url: Optional[str] = DESCRIPTION_MAP["blob_sas_url"]
    version: str = DESCRIPTION_MAP["artifact_version"]


@dataclass
class NFConfiguration:
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
    def acr_manifest_name(self) -> str:
        """Return the ACR manifest name from the NFD name."""
        sanitized_nf_name = self.nf_name.lower().replace("_", "-")
        return f"{sanitized_nf_name}-acr-manifest-{self.version.replace('.', '-')}"


@dataclass
class NSConfiguration:
    # pylint: disable=too-many-instance-attributes
    location: str = DESCRIPTION_MAP["location"]
    publisher_name: str = DESCRIPTION_MAP["publisher_name_nsd"]
    publisher_resource_group_name: str = DESCRIPTION_MAP[
        "publisher_resource_group_name_nsd"
    ]
    acr_artifact_store_name: str = DESCRIPTION_MAP["acr_artifact_store_name"]
    network_function_definition_group_name: str = DESCRIPTION_MAP[
        "network_function_definition_group_name"
    ]
    network_function_definition_version_name: str = DESCRIPTION_MAP[
        "network_function_definition_version_name"
    ]
    network_function_definition_offering_location: str = DESCRIPTION_MAP[
        "network_function_definition_offering_location"
    ]
    network_function_type: str = DESCRIPTION_MAP["network_function_type"]
    nsdg_name: str = DESCRIPTION_MAP["nsdg_name"]
    nsd_version: str = DESCRIPTION_MAP["nsd_version"]
    nsdv_description: str = DESCRIPTION_MAP["nsdv_description"]

    def validate(self):
        """Validate that all of the configuration parameters are set."""

        # Exemption for pylint as explicitly including the empty string makes the code clearer
        # pylint: disable=simplifiable-condition

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
        if (
            self.network_function_definition_group_name
            == DESCRIPTION_MAP["network_function_definition_group_name"]
            or ""
        ):
            raise ValueError("Network Function Definition Group name must be set")
        if (
            self.network_function_definition_version_name
            == DESCRIPTION_MAP["network_function_definition_version_name"]
            or ""
        ):
            raise ValueError("Network Function Definition Version name must be set")
        if (
            self.network_function_definition_offering_location
            == DESCRIPTION_MAP["network_function_definition_offering_location"]
            or ""
        ):
            raise ValueError(
                "Network Function Definition Offering Location must be set"
            )
        if self.network_function_type not in [CNF, VNF]:
            raise ValueError("Network Function Type must be cnf or vnf")
        if self.nsdg_name == DESCRIPTION_MAP["nsdg_name"] or "":
            raise ValueError("NSDG name must be set")
        if self.nsd_version == DESCRIPTION_MAP["nsd_version"] or "":
            raise ValueError("NSD Version must be set")

    @property
    def build_output_folder_name(self) -> str:
        """Return the local folder for generating the bicep template to."""
        current_working_directory = os.getcwd()
        return f"{current_working_directory}/{NSD_OUTPUT_BICEP_PREFIX}"

    @property
    def resource_element_name(self) -> str:
        """Return the name of the resource element."""
        return f"{self.nsdg_name.lower()}-resource-element"

    @property
    def network_function_name(self) -> str:
        """Return the name of the NFVI used for the NSDV."""
        return f"{self.nsdg_name}_NF"

    @property
    def acr_manifest_name(self) -> str:
        """Return the ACR manifest name from the NFD name."""
        sanitised_nf_name = self.network_function_name.lower().replace('_', '-')
        return (
            f"{sanitised_nf_name}-nsd-acr-manifest-{self.nsd_version.replace('.', '-')}"
        )

    @property
    def nfvi_site_name(self) -> str:
        """Return the name of the NFVI used for the NSDV."""
        return f"{self.nsdg_name}_NFVI"

    @property
    def cg_schema_name(self) -> str:
        """Return the name of the Configuration Schema used for the NSDV."""
        return f"{self.nsdg_name.replace('-', '_')}_ConfigGroupSchema"

    @property
    def arm_template(self) -> ArtifactConfig:
        """Return the parameters of the ARM template to be uploaded as part of the NSDV."""
        artifact = ArtifactConfig()
        artifact.version = self.nsd_version
        artifact.file_path = os.path.join(
            self.build_output_folder_name, NF_DEFINITION_JSON_FILENAME
        )
        return artifact

    @property
    def arm_template_artifact_name(self) -> str:
        """Return the artifact name for the ARM template."""
        return f"{self.network_function_definition_group_name}-nfd-artifact"


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
            self.arm_template = ArtifactConfig(**self.arm_template)

        if isinstance(self.vhd, dict):
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
    def build_output_folder_name(self) -> str:
        """Return the local folder for generating the bicep template to."""
        arm_template_path = self.arm_template.file_path
        return f"{NF_DEFINITION_OUTPUT_BICEP_PREFIX}{Path(str(arm_template_path)).stem}"


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
                self.helm_packages[package_index] = HelmPackageConfig(**dict(package))

    @property
    def build_output_folder_name(self) -> str:
        """Return the local folder for generating the bicep template to."""
        return f"{NF_DEFINITION_OUTPUT_BICEP_PREFIX}{self.nf_name}"

    def validate(self):
        """Validate the CNF config

        :raises ValidationError: If source registry ID doesn't match the regex
        """
        if self.source_registry_id == DESCRIPTION_MAP["source_registry_id"]:
            # Config has not been filled in. Don't validate.
            return

        source_registry_match = re.search(SOURCE_ACR_REGEX, self.source_registry_id)
        if not source_registry_match or len(source_registry_match.groups()) < 2:
            raise ValidationError(
                "CNF config has an invalid source registry ID. Please run `az aosm "
                "nfd generate-config` to see the valid formats.")

def get_configuration(
    configuration_type: str, config_as_dict: Optional[Dict[Any, Any]] = None
) -> NFConfiguration or NSConfiguration:
    """
    Return the correct configuration object based on the type.

    :param configuration_type: The type of configuration to return
    :param config_as_dict: The configuration as a dictionary
    :return: The configuration object
    """
    if config_as_dict is None:
        config_as_dict = {}

    if configuration_type == VNF:
        config = VNFConfiguration(**config_as_dict)
    elif configuration_type == CNF:
        config = CNFConfiguration(**config_as_dict)
    elif configuration_type == NSD:
        config = NSConfiguration(**config_as_dict)
    else:
        raise InvalidArgumentValueError(
            "Definition type not recognized, options are: vnf, cnf or nsd"
        )

    return config
