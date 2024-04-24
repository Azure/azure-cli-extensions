# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, protected-access

from .aaz.latest.monitor.log_analytics.solution import Create as _SolutionCreate, Update as _SolutionUpdate, Delete as _SolutionDelete, Show as _SolutionShow, List as _SolutionList
from .aaz.latest.monitor.log_analytics.workspace import Show as _WorkspaceShow


class SolutionCreate(_SolutionCreate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZStrArg, AAZResourceIdArg, AAZResourceIdArgFormat
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.workspace = AAZResourceIdArg(
            options=['--workspace', '-w'],
            help='The name or resource ID of the log analytics workspace with which the solution will be linked.',
            required=True,
            fmt=AAZResourceIdArgFormat(
                "/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/Microsoft.OperationalInsights/workspaces/{}"
            )
        )
        args_schema.solution_type = AAZStrArg(
            options=['--solution-type', '-t'],
            required=True,
            help='Type of the log-analytics solution. '
                 'The most used are: SecurityCenterFree, Security, Updates, ContainerInsights, ServiceMap, AzureActivity, ChangeTracking, VMInsights, SecurityInsights, NetworkMonitoring, SQLVulnerabilityAssessment, SQLAdvancedThreatProtection, AntiMalware, AzureAutomation, LogicAppsManagement, SQLDataClassification.'
        )
        args_schema.workspace_id._registered = False
        args_schema.plan._registered = False
        args_schema.location._registered = False
        args_schema.name._required = False
        args_schema.name._registered = False
        return args_schema

    def pre_operations(self):
        from msrestazure.tools import parse_resource_id
        from azure.cli.core.azclierror import ArgumentUsageError
        args = self.ctx.args
        args.workspace_id = args.workspace

        workspace_param = parse_resource_id(args.workspace.to_serialized_data())
        if workspace_param['resource_group'] != args.resource_group.to_serialized_data():
            raise ArgumentUsageError('usage error: workspace and solution must be under the same resource group')
        workspace = _WorkspaceShow(cli_ctx=self.cli_ctx)(command_args={
            "resource_group": workspace_param['resource_group'],
            "workspace_name": workspace_param['resource_name']
        })

        args.location = workspace['location']
        args.plan = {
            "name": args.solution_type.to_serialized_data(),
            "product": "OMSGallery/" + args.solution_type.to_serialized_data(),
            "publisher": "Microsoft",
            "promotion_code": ""
        }
        args.name = args.solution_type.to_serialized_data() + "(" + args.workspace.to_serialized_data().split("/")[-1] + ")"


class SolutionUpdate(_SolutionUpdate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.name._id_part = ''
        return args_schema


class SolutionDelete(_SolutionDelete):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.name._id_part = ''
        return args_schema


class SolutionShow(_SolutionShow):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.name._id_part = ''
        return args_schema
