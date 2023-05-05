from dataclasses import dataclass, field
from typing import Optional, Any, List
from azure.cli.core.azclierror import ValidationError, InvalidArgumentValueError
from ._constants import VNF, CNF, NSD


@dataclass
class ArtifactConfig:
    artifact_name: str = "Name of the artifact"
    file_path: Optional[
        str
    ] = "File path of the artifact you wish to upload from your local disk"
    blob_sas_url: Optional[
        str
    ] = "SAS URL of the blob artifact you wish to copy to your Artifact Store"
    version: str = (
        "Version of the artifact. For VHDs this must be in format A-B-C. "
        "For ARM templates this must be in format A.B.C"
    )


@dataclass
class Configuration:
    publisher_name: str = (
        "Name of the Publisher resource you want you definition published to"
    )
    publisher_resource_group_name: str = (
        "Resource group the Publisher resource is in or you want it to be in"
    )
    nf_name: str = "Name of NF definition"
    version: str = "Version of the NF definition"
    acr_artifact_store_name: str = "Name of the ACR Artifact Store resource"
    location: str = "Azure location of the resources"

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
    blob_artifact_store_name: str = (
        "Name of the storage account Artifact Store resource"
    )
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

@dataclass
class HelmPackageConfig:
    name: str = "Name of the Helm package"
    path_to_chart: str = "Path to the Helm chart"
    depends_on: List[str] = field(default_factory=lambda: ["Names of the Helm packages this package depends on"])

@dataclass
class CNFConfiguration(Configuration):
    helm_packages: List[Any] = field(default_factory=lambda: [HelmPackageConfig()])

    def __post_init__(self):
        """
        Cope with deserializing subclasses from dicts to HelmPackageConfig.
        
        Used when creating CNFConfiguration object from a loaded json config file.
        """
        for package in self.helm_packages:
            if isinstance(package, dict):
                package = HelmPackageConfig(**dict(package))


def get_configuration(definition_type, config_as_dict=None) -> Configuration:
    
    if config_as_dict is None:
        config_as_dict = {}

    if definition_type == VNF:
        config = VNFConfiguration(**config_as_dict)
    elif definition_type == CNF:
        config = CNFConfiguration(**config_as_dict)
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
        if (
            "." not in config.arm_template.version
            or "-" in config.arm_template.version
        ):
            raise ValidationError(
                "Config validation error. ARM template artifact version should be in format A.B.C"
            )
