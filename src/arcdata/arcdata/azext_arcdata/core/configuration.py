# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

"""
Read and modify configuration settings related to the extension
"""

from __future__ import absolute_import
from azext_arcdata.__version__ import __title__, __version__
from azext_arcdata.core.util import singleton
from knack.log import get_logger

import sys
import os

logger = get_logger(__name__)


@singleton
class Configuration(object):
    """
    The CLI Configuration singleton.
    """

    EXT_NAME = "arcdata"
    """
    The name of the CLI extension.
    """

    def __init__(self):
        """
        Configuration runtime constructor.
        """
        pass

    @property
    def extension_dir(self):
        ext_dir = os.environ.get("AZURE_EXTENSION_DIR")
        logger.debug("AZURE_EXTENSION_DIR: %s", ext_dir)

        if not ext_dir:
            az_config_dir = os.getenv("AZURE_CONFIG_DIR")
            logger.debug("AZURE_CONFIG_DIR: %s", az_config_dir)
            if not az_config_dir:
                az_config_dir = os.path.expanduser(os.path.join("~", ".azure"))

            logger.debug(".azure location: %s", az_config_dir)
            ext_dir = os.path.join(az_config_dir, "cliextensions")
            logger.debug("Extension location: %s", ext_dir)

        return os.path.join(ext_dir, self.EXT_NAME)

    @property
    def version(self):
        """
        Gets the client CLI version.
        """
        return __version__

    def to_debug_report(self):
        """
        Gets the essential information for debugging.

        :return: The report for debugging.
        """
        return (
            "azure-cli extension debug report:\n OS: {env}\n "
            "Package {name} Version: {version} "
            "Python Version: {pyversion}".format(
                name=__title__,
                version=self.version,
                env=sys.platform,
                pyversion=sys.version,
            )
        )
