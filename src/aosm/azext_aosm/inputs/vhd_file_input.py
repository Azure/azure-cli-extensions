# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import copy
import json
from pathlib import Path
from typing import Any, Dict, Optional

from knack.log import get_logger
from azext_aosm.common.utils import snake_case_to_camel_case
from azext_aosm.common.constants import BASE_SCHEMA
from azext_aosm.inputs.base_input import BaseInput

logger = get_logger(__name__)


class VHDFileInput(BaseInput):
    """
    A utility class for working with VHD file inputs.

    :param artifact_name: The name of the artifact.
    :type artifact_name: str
    :param artifact_version: The version of the artifact.
    :type artifact_version: str
    :param file_path: The path to the VHD file.
    :type file_path: Path
    :param default_config: The default configuration.
    :type default_config: Optional[Dict[str, Any]]
    :param blob_sas_uri: The blob SAS URI.
    :type blob_sas_uri: Optional[str]
    """

    def __init__(  # pylint: disable=too-many-positional-arguments
        self,
        artifact_name: str,
        artifact_version: str,
        file_path: Optional[Path] = None,
        blob_sas_uri: Optional[str] = None,
        default_config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(artifact_name, artifact_version, default_config)
        self.file_path = file_path
        self.blob_sas_uri = blob_sas_uri

        formatted_config = {}
        for (key, value) in self.default_config.items():
            # This must be an integer, but is a string in the input file
            if key == "image_disk_size_GB":
                value = int(value)
            if key == "image_api_version":
                key = "apiVersion"
            formatted_key = snake_case_to_camel_case(key)
            formatted_config[formatted_key] = value
        self.default_config = formatted_config

    def get_defaults(self) -> Dict[str, Any]:
        """
        Gets the default values for configuring the input.

        :return: A dictionary containing the default values.
        :rtype: Dict[str, Any]
        """
        logger.info("Getting default values for VHD file input")
        default_config = self.default_config or {}
        logger.debug(
            "Default values for VHD file Input: %s",
            json.dumps(default_config, indent=4),
        )
        return copy.deepcopy(default_config)

    def get_schema(self) -> Dict[str, Any]:
        """
        Gets the schema for the VHD file input.

        :return: A dictionary containing the schema.
        :rtype: Dict[str, Any]
        """
        logger.debug("Getting schema for VHD file input %s.", self.artifact_name)
        vhd_properties = {
            "imageName": {"type": "string"},
            "azureDeployLocation": {"type": "string"},
            "imageDiskSizeGB": {"type": "integer"},
            "imageOsState": {"type": "string"},
            "imageHyperVGeneration": {"type": "string"},
            "apiVersion": {"type": "string"},
        }
        vhd_required = ["imageName"]

        schema = copy.deepcopy(BASE_SCHEMA)
        schema["properties"].update(vhd_properties)
        schema["required"] += vhd_required

        logger.debug("Schema for VHD file input: %s", json.dumps(schema, indent=4))
        return copy.deepcopy(schema)
