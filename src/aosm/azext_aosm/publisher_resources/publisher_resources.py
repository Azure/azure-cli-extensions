# --------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT
# License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------
"""Shared publisher resources."""
from dataclasses import dataclass
from knack.log import get_logger
from azext_aosm.vendored_sdks.models import NetworkFunctionDefinitionGroup
from azext_aosm._configuration import Configuration


logger = get_logger(__name__)


@dataclass
class PublisherResourceGenerator:
    """Class for generating publisher resources used by various other classes."""

    config: Configuration

    def generate_nfd_group(self) -> NetworkFunctionDefinitionGroup:
        """
        Generate a NFD group with location and description from config.

        :return: _description_
        :rtype: NetworkFunctionDefinitionGroup
        """
        return NetworkFunctionDefinitionGroup(
            location=self.config.location,
            description=f"NFD Group for versions of NFDs for {self.config.nf_name}",
        )
