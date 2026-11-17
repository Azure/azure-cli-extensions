# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from azure.cli.core.commands.parameters import (
    get_location_type,
    resource_group_name_type,
    tags_type,
)
from azure.cli.core.commands.validators import get_default_location_from_resource_group


def load_arguments(self, _):  # pylint: disable=unused-argument
    with self.argument_context('workload-manager workload-space up') as c:
        c.argument('resource_group_name', arg_type=resource_group_name_type)
        c.argument('space_name', options_list=['--space-name', '--name', '-n'], help='Name of the workload space.')
        c.argument(
            'location',
            arg_type=get_location_type(self.cli_ctx),
            required=False,
            validator=get_default_location_from_resource_group,
            help='Deployment location. Defaults to the configured location or the resource group location.',
        )
        c.argument('tags', arg_type=tags_type)
        c.argument('deployment_name', validator=None, help='ARM deployment name. Defaults to the workload-space name.')
        c.argument(
            'managed_cluster_resource_id',
            options_list=['--managed-cluster-resource-id', '--managed-cluster-id'],
            help='Resource ID of an existing AKS cluster in the selected subscription and location. '
                 'Requires both subnet IDs.',
        )
        c.argument(
            'workload_execution_subnet_id',
            options_list=['--workload-execution-subnet-id', '--execution-subnet-id'],
            help='ACI execution subnet resource ID. Requires --managed-cluster-resource-id and --runtime-link-subnet-id.',
        )
        c.argument(
            'runtime_link_subnet_id',
            help='Empty subnet resource ID for the runtime link. Must be distinct from the execution subnet, '
                 'in the same VNet. Requires --managed-cluster-resource-id and --workload-execution-subnet-id.',
        )
