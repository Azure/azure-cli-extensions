# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from azure.cli.core.breaking_change import register_command_group_deprecate, register_other_breaking_change


register_command_group_deprecate('az blueprint', target_version='July 2026')

message = """Azure Blueprints is retiring on 31 January 2027, with phased restrictions starting 31 July 2026.
After retirement, the service API stops responding and these commands will stop functioning; they will be removed from the Azure CLI in a later release.
Migrate blueprint definitions to Template Specs and assignments to Azure Deployment Stacks (recommended).
Migration guidance: https://aka.ms/AzureBlueprintsRetirement"""

register_other_breaking_change('az blueprint', message)
