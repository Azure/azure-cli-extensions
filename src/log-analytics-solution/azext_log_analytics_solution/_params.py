# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from azure.cli.core.commands.parameters import tags_type
from knack.arguments import CLIArgumentType
from ._validators import validate_workspace_resource_id

solution_name = CLIArgumentType(options_list=['--name', '-n'],
                                help='Name of the log-analytics solution. It should be in the format of '
                                     'solutionType(workspaceName). SolutionType part is case sensitive. ')


def load_arguments(self, _):

    with self.argument_context('monitor log-analytics solution create') as c:
        c.ignore('location')
        c.argument('solution_type', options_list=['--solution-type', '-t'],
                   help='Type of the log-analytics solution. The most used are: SecurityCenterFree, Security, Updates, '
                        'ContainerInsights, ServiceMap, AzureActivity, ChangeTracking, VMInsights, SecurityInsights, '
                        'NetworkMonitoring, SQLVulnerabilityAssessment, SQLAdvancedThreatProtection, AntiMalware, '
                        'AzureAutomation, LogicAppsManagement, SQLDataClassification')
        c.argument('solution_name', solution_name, deprecate_info=c.deprecate(hide=True))
        c.argument('tags', tags_type)
        c.argument('plan_publisher',
                   help='Publisher name of the plan for solution. For gallery solution, it is Microsoft.',
                   deprecate_info=c.deprecate(hide=True))
        c.argument('plan_product',
                   help='Product name of the plan for solution. It should be in the format of OMSGallery/<solutionType>. This is case sensitive.',
                   deprecate_info=c.deprecate(hide=True))
        c.argument('workspace_resource_id', options_list=['--workspace', '-w'],
                   validator=validate_workspace_resource_id,
                   help='The name or resource ID of the log analytics workspace with which the solution will be linked.')

    with self.argument_context('monitor log-analytics solution update') as c:
        c.argument('solution_name', solution_name)
        c.argument('tags', tags_type)

    with self.argument_context('monitor log-analytics solution delete') as c:
        c.argument('solution_name', solution_name)

    with self.argument_context('monitor log-analytics solution show') as c:
        c.argument('solution_name', solution_name)
