from dataclasses import dataclass
from typing import Optional
from knack.util import CLIError

@dataclass
class ArtifactConfig:
    artifact_name: str = "Name of the artifact"
    file_path: Optional[str] = "File path of the artifact you wish to upload from your local disk"
    blob_sas_url: Optional[str] = "SAS URL of the blob artifact you wish to copy to your Artifact Store"


@dataclass
class Configuration():
    publisher_name: str = "Name of the Publisher resource you want you definition published to"
    publisher_resource_group_name: str = "Resource group the Publisher resource is in or you want it to be in"
    name: str = "Name of NF definition"
    version: str = "Version of the NF definition"
    acr_artifact_store_name: str = "Name of the ACR Artifact Store resource"


@dataclass
class VNFConfiguration(Configuration):
    blob_artifact_store_name: str = "Name of the storage account Artifact Store resource"
    arm_template: ArtifactConfig = ArtifactConfig()
    vhd: ArtifactConfig = ArtifactConfig()


def get_configuration(definition_type, config_as_dict=None):
    if config_as_dict is None:
        config_as_dict = {}

    if definition_type == "vnf":
        config = VNFConfiguration(**config_as_dict)
    elif definition_type == "cnf":
        config = Configuration(**config_as_dict)
    elif definition_type == "nsd":
        config = Configuration(**config_as_dict)
    else:
        raise CLIError("Definition type not recognized, options are: vnf, cnf or nsd")

    return config
