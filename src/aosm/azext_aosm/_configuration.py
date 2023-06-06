from dataclasses import dataclass, field
from typing import Dict, Optional, Any, List
from pathlib import Path
from azure.cli.core.azclierror import ValidationError, InvalidArgumentValueError
from azext_aosm.util.constants import (
    DEFINITION_OUTPUT_BICEP_PREFIX,
    VNF,
    CNF,
    NSD,
    SCHEMA,
    NSD_DEFINITION_OUTPUT_BICEP_PREFIX,
    NF_DEFINITION_JSON_FILE,
)
import os

DESCRIPTION_MAP: Dict[str, str] = {
    "publisher_resource_group_name": (
        "Resource group for the Publisher resource. Will be "
        "created if it does not exist."
    ),
    "publisher_name": (
        "Name of the Publisher resource you want your definition "
        "published to. Will be created if it does not exist."
    ),
    "publisher_name_nsd": (
        "Name of the Publisher resource you want your design published to. This published should be the same as the publisher used for your NFDVs"
    ),
    "publisher_resource_group_name_nsd": ("Resource group for the Publisher resource."),
    "nf_name": "Name of NF definition",
    "version": "Version of the NF definition",
    "acr_artifact_store_name": "Name of the ACR Artifact Store resource. Will be created if it does not exist.",
    "location": "Azure location to use when creating resources.",
    "blob_artifact_store_name": "Name of the storage account Artifact Store resource. Will be created if it does not exist.",
    "file_path": (
        "Optional. File path of the artifact you wish to upload from your "
        "local disk. Delete if not required."
    ),
    "blob_sas_url": (
        "Optional. SAS URL of the blob artifact you wish to copy to your "
        "Artifact Store. Delete if not required."
    ),
    "artifact_version": (
        "Version of the artifact. For VHDs this must be in format A-B-C. "
        "For ARM templates this must be in format A.B.C"
    ),
    "nsdv_description": "Description of the NSDV",
    "nsdg_name": "Network Service Design Group Name. This is the collection of Network Service Design Versions. Will be "
    "created if it does not exist.",
    "nsd_version": "Version of the NSD to be created. This should be in the format A.B.C",
    "network_function_definition_group_name": "Exising Network Function Definition Group Name. This can be created using the 'az aosm nfd' commands.",
    "network_function_definition_version_name": "Exising Network Function Definition Version Name. This can be created using the 'az aosm nfd' commands.",
    "network_function_definition_offering_location": "Offering location of the Network Function Definition",
    "helm_package_name": "Name of the Helm package",
    "path_to_chart": (
        "File path of Helm Chart on local disk. Accepts .tgz, .tar or .tar.gz"
    ),
    "path_to_mappings": (
        "File path of value mappings on local disk. Accepts .yaml or .yml"
    ),
    "helm_depends_on": (
        "Names of the Helm packages this package depends on. "
        "Leave as an empty array if no dependencies"
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
        return f"{self.nf_name}-acr-manifest-{self.version.replace('.', '-')}"


@dataclass
class NSConfiguration:
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
    nsdg_name: str = DESCRIPTION_MAP["nsdg_name"]
    nsd_version: str = DESCRIPTION_MAP["nsd_version"]
    nsdv_description: str = DESCRIPTION_MAP["nsdv_description"]

    def validate(self):
        ## validate that all of the configuration parameters are set

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
        if self.nsdg_name == DESCRIPTION_MAP["nsdg_name"] or "":
            raise ValueError("NSDG name must be set")
        if self.nsd_version == DESCRIPTION_MAP["nsd_version"] or "":
            raise ValueError("NSD Version must be set")

    @property
    def build_output_folder_name(self) -> str:
        """Return the local folder for generating the bicep template to."""
        current_working_directory = os.getcwd()
        return f"{current_working_directory}/{NSD_DEFINITION_OUTPUT_BICEP_PREFIX}"

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
        return f"{self.network_function_name.lower().replace('_', '-')}-acr-manifest-{self.nsd_version.replace('.', '-')}"

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
            self.build_output_folder_name, NF_DEFINITION_JSON_FILE
        )
        return artifact
    
    @property
    def arm_template_artifact_name(self) -> str:
        """Return the artifact name for the ARM template"""
        return f"{self.network_function_definition_group_name}_nfd_artifact"


@dataclass
class VNFConfiguration(NFConfiguration):
    blob_artifact_store_name: str = DESCRIPTION_MAP["blob_artifact_store_name"]
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
                "Config validation error. VHD artifact version should be in format A-B-C"
            )
        if "." not in self.arm_template.version or "-" in self.arm_template.version:
            raise ValidationError(
                "Config validation error. ARM template artifact version should be in format A.B.C"
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
                "Config validation error. VHD config must have either a local filepath or a blob SAS URL"
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
        return f"{self.nf_name}-sa-manifest-{self.version.replace('.', '-')}"

    @property
    def build_output_folder_name(self) -> str:
        """Return the local folder for generating the bicep template to."""
        arm_template_path = self.arm_template.file_path
        return f"{DEFINITION_OUTPUT_BICEP_PREFIX}{Path(str(arm_template_path)).stem}"


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
    helm_packages: List[Any] = field(default_factory=lambda: [HelmPackageConfig()])

    def __post_init__(self):
        """
        Cope with deserializing subclasses from dicts to HelmPackageConfig.

        Used when creating CNFConfiguration object from a loaded json config file.
        """
        for package in self.helm_packages:
            if isinstance(package, dict):
                package = HelmPackageConfig(**dict(package))

    @property
    def build_output_folder_name(self) -> str:
        """Return the local folder for generating the bicep template to."""
        return f"{DEFINITION_OUTPUT_BICEP_PREFIX}{self.nf_name}"


def get_configuration(
    configuration_type: str, config_as_dict: Optional[Dict[Any, Any]] = None
) -> NFConfiguration or NSConfiguration:
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
