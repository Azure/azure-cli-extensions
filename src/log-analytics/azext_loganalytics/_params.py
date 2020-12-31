# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long


def load_arguments(self, _):
    with self.argument_context('monitor log-analytics query') as c:
        c.argument('workspace', options_list=['--workspace', '-w'], help='GUID of the Log Analytics Workspace')
        c.argument('analytics_query', help='Query to execute over Log Analytics data.')
        c.argument('timespan', options_list=['--timespan', '-t'], help='Timespan over which to query. Defaults to querying all available data.')
        c.argument('workspaces', nargs='+', help='Additional workspaces to union data for querying. Specify additional workspace IDs separated by space.')
