# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from enum import Enum
from azure.cli.core.azclierror  import InvalidArgumentValueError
from knack.log import get_logger
from msrestazure.tools import is_valid_resource_id


# Bastion Service Constants 
class BastionSku(Enum):
    Developer = "Developer"


class BastionSession():
    def __init__(self):
        self.resource_group_name = None
        
    def ssh_bastion_host(self, cmd, bastion, resource_port, target_resource_id):
        
    def _get_bastion_endpoint(cmd, bastion, resource_port, target_resource_id):
        from .developer_sku_helper import (_get_data_pod)
        bastion_endpoint = _get_data_pod(cmd, resource_port, target_resource_id, bastion)
        return bastion_endpoint

