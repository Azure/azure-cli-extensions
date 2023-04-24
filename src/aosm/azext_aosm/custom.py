# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json

from dataclasses import asdict
from knack.log import get_logger
from knack.util import CLIError
from .vendored_sdks import HybridNetworkManagementClient
from .vendored_sdks.models import Publisher
from ._configuration import Configuration, VNFConfiguration

logger = get_logger(__name__)

def build_definition(cmd, definition_type, config_file, publish=False):
    with open(config_file, "r") as f:
        config_dict = json.loads(f)

    if definition_type == "vnf":
        config = VNFConfiguration(**config_dict)
    elif definition_type == "cnf":
        config = Configuration(**config_dict)
    elif definition_type == "nsd":
        config = Configuration(**config_dict)
    else:
        raise CLIError("Definition type not recognized, options are: vnf, cnf or nsd")

    if publish:


def generate_definition_config(cmd, definition_type, output_file="input.json"):
    if definition_type == "vnf":
        config = VNFConfiguration()
    elif definition_type == "cnf":
        config = Configuration()
    elif definition_type == "nsd":
        config = Configuration()
    else:
        raise CLIError("Definition type not recognized, options are: vnf, cnf or nsd")

    with open(output_file, "w", encoding="utf-8") as f:
        config_as_dict = json.dumps(asdict(config), indent=4)
        f.write(config_as_dict)
        logger.info("Empty definition configuration has been written to %s", output_file)

def show_publisher(cmd, client: HybridNetworkManagementClient, resource_group_name, publisher_name):
    publisher: Publisher = client.publishers.get(resource_group_name, publisher_name)
    print(f"Publisher id = {publisher.id}")
