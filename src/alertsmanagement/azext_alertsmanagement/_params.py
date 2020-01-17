# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from azure.cli.core.commands.parameters import (
    tags_type,
    get_three_state_flag,
    get_enum_type,
    resource_group_name_type,
    get_location_type
)


def load_arguments(self, _):

    with self.argument_context('alertsmanagement operation list') as c:
        pass

    with self.argument_context('alertsmanagement alert change-state') as c:
        c.argument('alert_id', id_part=None, help='Unique ID of an alert instance.')
        c.argument('new_state', id_part=None, help='New state of the alert.')

    with self.argument_context('alertsmanagement alert meta-data') as c:
        c.argument('identifier', id_part=None, help='Identification of the information to be retrieved by API call.')

    with self.argument_context('alertsmanagement alert get-all') as c:
        c.argument('target_resource', id_part=None, help='Filter by target resource( which is full ARM ID) Default value is select all.')
        c.argument('target_resource_type', id_part=None, help='Filter by target resource type. Default value is select all.')
        c.argument('target_resource_group', id_part=None, help='Filter by target resource group name. Default value is select all.')
        c.argument('monitor_service', id_part=None, help='Filter by monitor service which generates the alert instance. Default value is select all.')
        c.argument('monitor_condition', id_part=None, help='Filter by monitor condition which is either \'Fired\' or \'Resolved\'. Default value is to select all.')
        c.argument('severity', id_part=None, help='Filter by severity.  Default value is select all.')
        c.argument('alert_state', id_part=None, help='Filter by state of the alert instance. Default value is to select all.')
        c.argument('alert_rule', id_part=None, help='Filter by specific alert rule.  Default value is to select all.')
        c.argument('smart_group_id', id_part=None, help='Filter the alerts list by the Smart Group Id. Default value is none.')
        c.argument('include_context', arg_type=get_three_state_flag(), id_part=None, help='Include context which has contextual data specific to the monitor service. Default value is false\'')
        c.argument('include_egress_config', arg_type=get_three_state_flag(), id_part=None, help='Include egress config which would be used for displaying the content in portal.  Default value is \'false\'.')
        c.argument('page_count', id_part=None, help='Determines number of alerts returned per page in response. Permissible value is between 1 to 250. When the "includeContent"  filter is selected, maximum value allowed is 25. Default value is 25.')
        c.argument('sort_by', id_part=None, help='Sort the query results by input field,  Default value is \'lastModifiedDateTime\'.')
        c.argument('sort_order', id_part=None, help='Sort the query results order in either ascending or descending.  Default value is \'desc\' for time fields and \'asc\' for others.')
        c.argument('select', id_part=None, help='This filter allows to selection of the fields(comma separated) which would  be part of the essential section. This would allow to project only the  required fields rather than getting entire content.  Default is to fetch all the fields in the essentials section.')
        c.argument('time_range', id_part=None, help='Filter by time range by below listed values. Default value is 1 day.')
        c.argument('custom_time_range', id_part=None, help='Filter by custom time range in the format <start-time>/<end-time>  where time is in (ISO-8601 format)\'. Permissible values is within 30 days from  query time. Either timeRange or customTimeRange could be used but not both. Default is none.')

    with self.argument_context('alertsmanagement alert get-by-id') as c:
        c.argument('alert_id', id_part=None, help='Unique ID of an alert instance.')

    with self.argument_context('alertsmanagement alert get-history') as c:
        c.argument('alert_id', id_part=None, help='Unique ID of an alert instance.')

    with self.argument_context('alertsmanagement alert get-summary') as c:
        c.argument('groupby', id_part=None, help='This parameter allows the result set to be grouped by input fields (Maximum 2 comma separated fields supported). For example, groupby=severity or groupby=severity,alertstate.')
        c.argument('include_smart_groups_count', arg_type=get_three_state_flag(), id_part=None, help='Include count of the SmartGroups as part of the summary. Default value is \'false\'.')
        c.argument('target_resource', id_part=None, help='Filter by target resource( which is full ARM ID) Default value is select all.')
        c.argument('target_resource_type', id_part=None, help='Filter by target resource type. Default value is select all.')
        c.argument('target_resource_group', id_part=None, help='Filter by target resource group name. Default value is select all.')
        c.argument('monitor_service', id_part=None, help='Filter by monitor service which generates the alert instance. Default value is select all.')
        c.argument('monitor_condition', id_part=None, help='Filter by monitor condition which is either \'Fired\' or \'Resolved\'. Default value is to select all.')
        c.argument('severity', id_part=None, help='Filter by severity.  Default value is select all.')
        c.argument('alert_state', id_part=None, help='Filter by state of the alert instance. Default value is to select all.')
        c.argument('alert_rule', id_part=None, help='Filter by specific alert rule.  Default value is to select all.')
        c.argument('time_range', id_part=None, help='Filter by time range by below listed values. Default value is 1 day.')
        c.argument('custom_time_range', id_part=None, help='Filter by custom time range in the format <start-time>/<end-time>  where time is in (ISO-8601 format)\'. Permissible values is within 30 days from  query time. Either timeRange or customTimeRange could be used but not both. Default is none.')

    with self.argument_context('alertsmanagement smart-group change-state') as c:
        c.argument('smart_group_id', id_part=None, help='Smart group unique id. ')
        c.argument('new_state', id_part=None, help='New state of the alert.')

    with self.argument_context('alertsmanagement smart-group get-all') as c:
        c.argument('target_resource', id_part=None, help='Filter by target resource( which is full ARM ID) Default value is select all.')
        c.argument('target_resource_group', id_part=None, help='Filter by target resource group name. Default value is select all.')
        c.argument('target_resource_type', id_part=None, help='Filter by target resource type. Default value is select all.')
        c.argument('monitor_service', id_part=None, help='Filter by monitor service which generates the alert instance. Default value is select all.')
        c.argument('monitor_condition', id_part=None, help='Filter by monitor condition which is either \'Fired\' or \'Resolved\'. Default value is to select all.')
        c.argument('severity', id_part=None, help='Filter by severity.  Default value is select all.')
        c.argument('smart_group_state', id_part=None, help='Filter by state of the smart group. Default value is to select all.')
        c.argument('time_range', id_part=None, help='Filter by time range by below listed values. Default value is 1 day.')
        c.argument('page_count', id_part=None, help='Determines number of alerts returned per page in response. Permissible value is between 1 to 250. When the "includeContent"  filter is selected, maximum value allowed is 25. Default value is 25.')
        c.argument('sort_by', id_part=None, help='Sort the query results by input field. Default value is sort by \'lastModifiedDateTime\'.')
        c.argument('sort_order', id_part=None, help='Sort the query results order in either ascending or descending.  Default value is \'desc\' for time fields and \'asc\' for others.')

    with self.argument_context('alertsmanagement smart-group get-by-id') as c:
        c.argument('smart_group_id', id_part=None, help='Smart group unique id. ')

    with self.argument_context('alertsmanagement smart-group get-history') as c:
        c.argument('smart_group_id', id_part=None, help='Smart group unique id. ')

    with self.argument_context('alertsmanagement action-rule create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name that needs to be updated')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)
        c.argument('status', arg_type=get_enum_type(['Enabled', 'Disabled']), id_part=None, help='Indicates if the given action rule is enabled or disabled')

    with self.argument_context('alertsmanagement action-rule update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name that needs to be updated')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)
        c.argument('status', arg_type=get_enum_type(['Enabled', 'Disabled']), id_part=None, help='Indicates if the given action rule is enabled or disabled')

    with self.argument_context('alertsmanagement action-rule delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name that needs to be updated')

    with self.argument_context('alertsmanagement action-rule show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name that needs to be updated')

    with self.argument_context('alertsmanagement action-rule list') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('target_resource_group', id_part=None, help='Filter by target resource group name. Default value is select all.')
        c.argument('target_resource_type', id_part=None, help='Filter by target resource type. Default value is select all.')
        c.argument('target_resource', id_part=None, help='Filter by target resource( which is full ARM ID) Default value is select all.')
        c.argument('severity', id_part=None, help='Filter by severity.  Default value is select all.')
        c.argument('monitor_service', id_part=None, help='Filter by monitor service which generates the alert instance. Default value is select all.')
        c.argument('impacted_scope', id_part=None, help='filter by impacted/target scope (provide comma separated list for multiple scopes). The value should be an well constructed ARM id of the scope.')
        c.argument('description', id_part=None, help='filter by alert rule description')
        c.argument('alert_rule_id', id_part=None, help='filter by alert rule id')
        c.argument('action_group', id_part=None, help='filter by action group configured as part of action rule')
        c.argument('name', id_part=None, help='filter by action rule name')

    with self.argument_context('alertsmanagement smart-detector-alert-rule create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the alert rule.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)
        c.argument('description', id_part=None, help='The alert rule description.')
        c.argument('state', arg_type=get_enum_type(['Enabled', 'Disabled']), id_part=None, help='The alert rule state.')
        c.argument('severity', arg_type=get_enum_type(['Sev0', 'Sev1', 'Sev2', 'Sev3', 'Sev4']), id_part=None, help='The alert rule severity.')
        c.argument('frequency', id_part=None, help='The alert rule frequency in ISO8601 format. The time granularity must be in minutes and minimum value is 5 minutes.')
        c.argument('action_groups', id_part=None, help='The alert rule actions.')
        c.argument('throttling', id_part=None, help='The alert rule throttling information.')

    with self.argument_context('alertsmanagement smart-detector-alert-rule update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the alert rule.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)
        c.argument('description', id_part=None, help='The alert rule description.')
        c.argument('state', arg_type=get_enum_type(['Enabled', 'Disabled']), id_part=None, help='The alert rule state.')
        c.argument('severity', arg_type=get_enum_type(['Sev0', 'Sev1', 'Sev2', 'Sev3', 'Sev4']), id_part=None, help='The alert rule severity.')
        c.argument('frequency', id_part=None, help='The alert rule frequency in ISO8601 format. The time granularity must be in minutes and minimum value is 5 minutes.')
        c.argument('action_groups', id_part=None, help='The alert rule actions.')
        c.argument('throttling', id_part=None, help='The alert rule throttling information.')

    with self.argument_context('alertsmanagement smart-detector-alert-rule delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the alert rule.')

    with self.argument_context('alertsmanagement smart-detector-alert-rule show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the alert rule.')
        c.argument('expand_detector', arg_type=get_three_state_flag(), id_part=None, help='Indicates if Smart Detector should be expanded.')

    with self.argument_context('alertsmanagement smart-detector-alert-rule list') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('expand_detector', arg_type=get_three_state_flag(), id_part=None, help='Indicates if Smart Detector should be expanded.')
