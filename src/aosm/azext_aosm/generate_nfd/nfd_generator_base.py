# --------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT
# License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------
"""Contains a base class for generating NFDs."""
from knack.log import get_logger
from azext_aosm._configuration import Configuration


logger = get_logger(__name__)

class NFDGenerator:
    """A class for generating an NFD from a config file."""

    def __init__(
        self,
        #config: Configuration
    ) -> None:
        """_summary_

        :param definition_type: _description_
        :type definition_type: str
        :param config: _description_
        :type config: Configuration
        """
        #self.config = config

    def generate_nfd(self) -> None:
        """No-op on base class
        """
        logger.error("Generate NFD called on base class. No-op")
        return
