# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long


def load_arguments(self, _):
    with self.argument_context('monitor app-insights query') as c:
        c.argument('application', options_list=['--app', '-a'], help='GUID of the Application Insights applications')
        c.argument('analytics_query', help='Query to execute over Application Insights data.')
        c.argument('timespan', options_list=['--timespan', '-t'], help='Timespan over which to query. Defaults to querying all available data.')
        c.argument('applications', nargs='+', help='Additional applications over which to union data for querying. Specify additional workspace IDs separated by space.')
    