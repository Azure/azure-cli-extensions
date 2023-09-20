# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import sys
from knack.log import get_logger

logger = get_logger(__name__)


class AccContainerError(Exception):
    """Generic ACC Container errors"""


def eprint(*args, **kwargs):
    # print to stderr with formatting to be noticeable in the terminal
    logger.error(*args, **kwargs)
    sys.exit(1)
