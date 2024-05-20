# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import Any, Dict, Optional
from knack.log import get_logger
from azext_aosm.inputs.base_input import BaseInput

logger = get_logger(__name__)


class NexusImageFileInput(BaseInput):
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

    def __init__(
        self,
        artifact_name: str,
        artifact_version: str,
        source_acr_registry: str,
        default_config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(artifact_name, artifact_version, default_config)
        self.source_acr_registry = source_acr_registry

    def get_defaults(self) -> Dict[str, Any]:
        """
        Gets the default values for configuring the input.

        For Nexus images, there are no defaults.
        :return: An empty dictionary.
        :rtype: Dict[str, Any]
        """
        return {}

    def get_schema(self) -> Dict[str, Any]:
        """
        Gets the schema for the file input.

        For Nexus images, there is no schema.
        :return: An empty dictionary.
        :rtype: Dict[str, Any]
        """
        return {}
