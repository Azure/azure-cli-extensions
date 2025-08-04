# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from azure.cli.core.breaking_change import register_command_group_deprecate, register_other_breaking_change


register_command_group_deprecate('az blueprint')

message = """Blueprints and associated commands will be deprecated
as early as July 2026. Customers are encouraged to transition to
Template Specs and Deployments Stacks to support their scenarios beyond that date.
Migration documentation is available at
https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/migrate-blueprint."""

register_other_breaking_change('az blueprint', message)
