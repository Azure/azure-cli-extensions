# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from azure.cli.core.commands.parameters import (
    tags_type,
    get_enum_type,
    resource_group_name_type,
    get_location_type
)
from azext_migrate.actions import (
    AddMachines
)


def load_arguments(self, _):

    with self.argument_context('migrate location check-name-availability') as c:
        c.argument('location_name', id_part=None, help='The desired region for the name check.')
        c.argument('name', id_part=None, help='The name to check for availability')

    with self.argument_context('migrate assessment-options show') as c:
        c.argument('location_name', id_part=None, help='Azure region in which the project is created.')

    with self.argument_context('migrate projects list') as c:
        c.argument('resource_group_name', resource_group_name_type)

    with self.argument_context('migrate projects show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', id_part=None, help='Name of the Azure Migrate project.')

    with self.argument_context('migrate projects create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', id_part=None, help='Name of the Azure Migrate project.')
        c.argument('e_tag', id_part=None, help='For optimistic concurrency control.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('customer_workspace_id', id_part=None, help='ARM ID of the Service Map workspace created by user.')
        c.argument('customer_workspace_location', id_part=None, help='Location of the Service Map workspace created by user.')
        c.argument('provisioning_state', arg_type=get_enum_type(['Accepted', 'Creating', 'Deleting', 'Failed', 'Moving', 'Succeeded']), id_part=None, help='Provisioning state of the project.')

    with self.argument_context('migrate projects update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', id_part=None, help='Name of the Azure Migrate project.')
        c.argument('e_tag', id_part=None, help='For optimistic concurrency control.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('customer_workspace_id', id_part=None, help='ARM ID of the Service Map workspace created by user.')
        c.argument('customer_workspace_location', id_part=None, help='Location of the Service Map workspace created by user.')
        c.argument('provisioning_state', arg_type=get_enum_type(['Accepted', 'Creating', 'Deleting', 'Failed', 'Moving', 'Succeeded']), id_part=None, help='Provisioning state of the project.')

    with self.argument_context('migrate projects delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', id_part=None, help='Name of the Azure Migrate project.')

    with self.argument_context('migrate projects get-keys') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', id_part=None, help='Name of the Azure Migrate project.')

    with self.argument_context('migrate machines list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', id_part=None, help='Name of the Azure Migrate project.')

    with self.argument_context('migrate machines show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', id_part=None, help='Name of the Azure Migrate project.')
        c.argument('machine_name', id_part=None, help='Unique name of a machine in private datacenter.')

    with self.argument_context('migrate groups list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', id_part=None, help='Name of the Azure Migrate project.')

    with self.argument_context('migrate groups show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', id_part=None, help='Name of the Azure Migrate project.')
        c.argument('group_name', id_part=None, help='Unique name of a group within a project.')

    with self.argument_context('migrate groups create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', id_part=None, help='Name of the Azure Migrate project.')
        c.argument('group_name', id_part=None, help='Unique name of a group within a project.')
        c.argument('e_tag', id_part=None, help='For optimistic concurrency control.')
        c.argument('machines', id_part=None, help='List of machine names that are part of this group.', action=AddMachines, nargs='+')

    with self.argument_context('migrate groups delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', id_part=None, help='Name of the Azure Migrate project.')
        c.argument('group_name', id_part=None, help='Unique name of a group within a project.')

    with self.argument_context('migrate assessments list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', id_part=None, help='Name of the Azure Migrate project.')
        c.argument('group_name', id_part=None, help='Unique name of a group within a project.')

    with self.argument_context('migrate assessments show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', id_part=None, help='Name of the Azure Migrate project.')
        c.argument('group_name', id_part=None, help='Unique name of a group within a project.')
        c.argument('assessment_name', id_part=None, help='Unique name of an assessment within a project.')

    with self.argument_context('migrate assessments create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', id_part=None, help='Name of the Azure Migrate project.')
        c.argument('group_name', id_part=None, help='Unique name of a group within a project.')
        c.argument('assessment_name', id_part=None, help='Unique name of an assessment within a project.')
        c.argument('e_tag', id_part=None, help='For optimistic concurrency control.')
        c.argument('azure_location', arg_type=get_enum_type(['Unknown', 'EastAsia', 'SoutheastAsia', 'AustraliaEast', 'AustraliaSoutheast', 'BrazilSouth', 'CanadaCentral', 'CanadaEast', 'WestEurope', 'NorthEurope', 'CentralIndia', 'SouthIndia', 'WestIndia', 'JapanEast', 'JapanWest', 'KoreaCentral', 'KoreaSouth', 'UkWest', 'UkSouth', 'NorthCentralUs', 'EastUs', 'WestUs2', 'SouthCentralUs', 'CentralUs', 'EastUs2', 'WestUs', 'WestCentralUs', 'GermanyCentral', 'GermanyNortheast', 'ChinaNorth', 'ChinaEast']), id_part=None, help='Target Azure location for which the machines should be assessed. These enums are the same as used by Compute API.')
        c.argument('azure_offer_code', arg_type=get_enum_type(['Unknown', 'MSAZR0003P', 'MSAZR0044P', 'MSAZR0059P', 'MSAZR0060P', 'MSAZR0062P', 'MSAZR0063P', 'MSAZR0064P', 'MSAZR0029P', 'MSAZR0022P', 'MSAZR0023P', 'MSAZR0148P', 'MSAZR0025P', 'MSAZR0036P', 'MSAZR0120P', 'MSAZR0121P', 'MSAZR0122P', 'MSAZR0123P', 'MSAZR0124P', 'MSAZR0125P', 'MSAZR0126P', 'MSAZR0127P', 'MSAZR0128P', 'MSAZR0129P', 'MSAZR0130P', 'MSAZR0111P', 'MSAZR0144P', 'MSAZR0149P', 'MSMCAZR0044P', 'MSMCAZR0059P', 'MSMCAZR0060P', 'MSMCAZR0063P', 'MSMCAZR0120P', 'MSMCAZR0121P', 'MSMCAZR0125P', 'MSMCAZR0128P', 'MSAZRDE0003P', 'MSAZRDE0044P']), id_part=None, help='Offer code according to which cost estimation is done.')
        c.argument('azure_pricing_tier', arg_type=get_enum_type(['Standard', 'Basic']), id_part=None, help='Pricing tier for Size evaluation.')
        c.argument('azure_storage_redundancy', arg_type=get_enum_type(['Unknown', 'LocallyRedundant', 'ZoneRedundant', 'GeoRedundant', 'ReadAccessGeoRedundant']), id_part=None, help='Storage Redundancy type offered by Azure.')
        c.argument('scaling_factor', id_part=None, help='Scaling factor used over utilization data to add a performance buffer for new machines to be created in Azure. Min Value = 1.0, Max value = 1.9, Default = 1.3.')
        c.argument('percentile', arg_type=get_enum_type(['Percentile50', 'Percentile90', 'Percentile95', 'Percentile99']), id_part=None, help='Percentile of performance data used to recommend Azure size.')
        c.argument('time_range', arg_type=get_enum_type(['Day', 'Week', 'Month']), id_part=None, help='Time range of performance data used to recommend a size.')
        c.argument('stage', arg_type=get_enum_type(['InProgress', 'UnderReview', 'Approved']), id_part=None, help='User configurable setting that describes the status of the assessment.')
        c.argument('currency', arg_type=get_enum_type(['Unknown', 'USD', 'DKK', 'CAD', 'IDR', 'JPY', 'KRW', 'NZD', 'NOK', 'RUB', 'SAR', 'ZAR', 'SEK', 'TRY', 'GBP', 'MXN', 'MYR', 'INR', 'HKD', 'BRL', 'TWD', 'EUR', 'CHF', 'ARS', 'AUD', 'CNY']), id_part=None, help='Currency to report prices in.')
        c.argument('azure_hybrid_use_benefit', arg_type=get_enum_type(['Unknown', 'Yes', 'No']), id_part=None, help='AHUB discount on windows virtual machines.')
        c.argument('discount_percentage', id_part=None, help='Custom discount percentage to be applied on final costs. Can be in the range [0, 100].')
        c.argument('sizing_criterion', arg_type=get_enum_type(['PerformanceBased', 'AsOnPremises']), id_part=None, help='Assessment sizing criterion.')

    with self.argument_context('migrate assessments delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', id_part=None, help='Name of the Azure Migrate project.')
        c.argument('group_name', id_part=None, help='Unique name of a group within a project.')
        c.argument('assessment_name', id_part=None, help='Unique name of an assessment within a project.')

    with self.argument_context('migrate assessments get-report-download-url') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', id_part=None, help='Name of the Azure Migrate project.')
        c.argument('group_name', id_part=None, help='Unique name of a group within a project.')
        c.argument('assessment_name', id_part=None, help='Unique name of an assessment within a project.')

    with self.argument_context('migrate assessed-machines list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', id_part=None, help='Name of the Azure Migrate project.')
        c.argument('group_name', id_part=None, help='Unique name of a group within a project.')
        c.argument('assessment_name', id_part=None, help='Unique name of an assessment within a project.')

    with self.argument_context('migrate assessed-machines show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', id_part=None, help='Name of the Azure Migrate project.')
        c.argument('group_name', id_part=None, help='Unique name of a group within a project.')
        c.argument('assessment_name', id_part=None, help='Unique name of an assessment within a project.')
        c.argument('assessed_machine_name', id_part=None, help='Unique name of an assessed machine evaluated as part of an assessment.')

    with self.argument_context('migrate operations list') as c:
        pass
