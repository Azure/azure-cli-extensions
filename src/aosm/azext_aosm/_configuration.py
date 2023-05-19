from dataclasses import dataclass, field
from typing import Dict, Optional, Any, List
from pathlib import Path
from azure.cli.core.azclierror import ValidationError, InvalidArgumentValueError
from azext_aosm.util.constants import VNF_DEFINITION_OUTPUT_BICEP_PREFIX, VNF, CNF, NSD

DESCRIPTION_MAP: Dict[str, str] = {
    "publisher_resource_group_name": (
        "Resource group for the Publisher resource. Will be "
        "created if it does not exist."
    ),
    "publisher_name": ("Name of the Publisher resource you want your definition "
                       "published to. Will be created if it does not exist."
    ),
    "nf_name": "Name of NF definition",
    "version": "Version of the NF definition",
    "acr_artifact_store_name": "Name of the ACR Artifact Store resource",
    "location": "Azure location to use when creating resources",
    "blob_artifact_store_name": "Name of the storage account Artifact Store resource",
    "artifact_name": "Name of the artifact",
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
}


@dataclass
class ArtifactConfig:
    artifact_name: str = DESCRIPTION_MAP["artifact_name"]
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
        return (
            f"{VNF_DEFINITION_OUTPUT_BICEP_PREFIX}{Path(str(arm_template_path)).stem}"
        )

@dataclass
class HelmPackageConfig:
    name: str = "Name of the Helm package"
    path_to_chart: str = "Path to the Helm chart"
    depends_on: List[str] = field(default_factory=lambda: ["Names of the Helm packages this package depends on"])

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
        return (
            f"{VNF_DEFINITION_OUTPUT_BICEP_PREFIX}{self.nf_name}"
        )

def get_configuration(
    definition_type: str, config_as_dict: Optional[Dict[Any, Any]] = None
) -> NFConfiguration:
    if config_as_dict is None:
        config_as_dict = {}

    if definition_type == VNF:
        config = VNFConfiguration(**config_as_dict)
    elif definition_type == CNF:
        config = CNFConfiguration(**config_as_dict)
    elif definition_type == NSD:
        config = NFConfiguration(**config_as_dict)
    else:
        raise InvalidArgumentValueError(
            "Definition type not recognized, options are: vnf, cnf or nsd"
        )

    return config

