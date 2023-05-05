from dataclasses import dataclass
from typing import Dict, Optional, Any
from azure.cli.core.azclierror import ValidationError, InvalidArgumentValueError
from pathlib import Path
from azext_aosm.util.constants import VNF_DEFINITION_OUTPUT_BICEP_PREFIX, VNF, CNF, NSD

DESCRIPTION_MAP: Dict[str, str] = {
    "publisher_name": "Name of the Publisher resource you want you definition published to",
    "publisher_resource_group_name": "Resource group the Publisher resource is in or you want it to be in",
    "nf_name": "Name of NF definition",
    "version": "Version of the NF definition",
    "acr_artifact_store_name": "Name of the ACR Artifact Store resource",
    "location": "Azure location of the resources",
    "blob_artifact_store_name": "Name of the storage account Artifact Store resource",
    "artifact_name": "Name of the artifact",
    "file_path": "Optional. File path of the artifact you wish to upload from your local disk. Delete if not required.",
    "blob_sas_url": "Optional. SAS URL of the blob artifact you wish to copy to your Artifact Store. Delete if not required.",
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
class Configuration:
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
class VNFConfiguration(Configuration):
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


def get_configuration(
    definition_type: str, config_as_dict: Optional[Dict[Any, Any]] = None
) -> Configuration:
    if config_as_dict is None:
        config_as_dict = {}

    if definition_type == VNF:
        config = VNFConfiguration(**config_as_dict)
    elif definition_type == CNF:
        config = Configuration(**config_as_dict)
    elif definition_type == NSD:
        config = Configuration(**config_as_dict)
    else:
        raise InvalidArgumentValueError(
            "Definition type not recognized, options are: vnf, cnf or nsd"
        )

    return config


def validate_configuration(config: Configuration) -> None:
    """
    Validate the configuration passed in.

    :param config: _description_
    :type config: Configuration
    """
    # Do we want to do this validation here or pass it to the service?? If the service
    # had good error messages I'd say let the service do the validation. But it would
    # certainly be quicker to catch here.
    if isinstance(config, VNFConfiguration):
        if "." in config.vhd.version or "-" not in config.vhd.version:
            # Not sure about raising this particular one.
            raise ValidationError(
                "Config validation error. VHD artifact version should be in format A-B-C"
            )
        if "." not in config.arm_template.version or "-" in config.arm_template.version:
            raise ValidationError(
                "Config validation error. ARM template artifact version should be in format A.B.C"
            )

        if not (
            (config.vhd.file_path or config.vhd.blob_sas_url)
            or (
                config.vhd.file_path == DESCRIPTION_MAP["file_path"]
                and config.vhd.blob_sas_url == DESCRIPTION_MAP["blob_sas_url"]
            )
        ):
            raise ValidationError(
                "Config validation error. VHD config must have either a local filepath or a blob SAS URL"
            )
