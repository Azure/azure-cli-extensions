# --------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT
# License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------
"""Contains a base class for generating NFDs."""
from knack.log import get_logger


logger = get_logger(__name__)


class NFDGenerator:
    """A class for generating an NFD from a config file."""
    # pylint: disable=too-few-public-methods
    def __init__(
        self,
    ) -> None:
        """
        Superclass for NFD generators.

        The sub-classes do the actual work
        """

    def generate_nfd(self) -> None:
        """No-op on base class."""
        logger.error("Generate NFD called on base class. No-op")
