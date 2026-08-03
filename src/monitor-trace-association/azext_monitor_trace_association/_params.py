# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long


def load_arguments(self, _):
    with self.argument_context('monitor trace-association') as c:
        c.argument('resource_uri',
                   options_list=['--resource-uri', '--scope'],
                   help="The fully qualified Azure Resource Manager identifier of the resource "
                        "(scope) the trace association applies to, e.g. an Application Insights "
                        "component, a resource group, or a subscription.")
        c.argument('name',
                   options_list=['--name', '-n'],
                   default='default',
                   help="The trace association singleton name. Only 'default' is valid.")

    with self.argument_context('monitor trace-association create') as c:
        c.argument('azure_monitor_workspace_resource_id',
                   options_list=['--azure-monitor-workspace-resource-id', '--amw-id'],
                   help="Resource ID of the target Azure Monitor Workspace "
                        "(Microsoft.Monitor/accounts). Must exist at creation time.")

    with self.argument_context('monitor trace-association update') as c:
        c.argument('azure_monitor_workspace_resource_id',
                   options_list=['--azure-monitor-workspace-resource-id', '--amw-id'],
                   help="Resource ID of the target Azure Monitor Workspace "
                        "(Microsoft.Monitor/accounts).")
