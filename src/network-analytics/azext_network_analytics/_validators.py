# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.log import get_logger
from azure.cli.core.azclierror import InvalidArgumentValueError
import re, os

logger = get_logger(__name__)


def validate_data_product_name(namespace):
    name = namespace.data_product_name
    length = len(name)

    pattern="^[a-z][a-z0-9]*$"
    match = re.match(pattern, name)
    if not match or length < 3 or length > 63:
        raise InvalidArgumentValueError("Invalid data product name. Please provide a data product name constisting of letter and/or numbers only, ")

def validate_source_path(namespace):
    source_path = namespace.source
    valid = os.path.exists(source_path)

    if not valid:
        raise InvalidArgumentValueError("The source path provided does not exist locally.")
    
def validate_destination_path(namespace):
    destination = namespace.destination

    pattern="^[^\/]+(?:\/[^\/]+)+\/[^\/]+$"
    match = re.match(pattern, destination)
    if not match:
        raise InvalidArgumentValueError("Invalid destination path. Please provide a path that is at least two directories deep such as 'folder1/folder2/file3'.")