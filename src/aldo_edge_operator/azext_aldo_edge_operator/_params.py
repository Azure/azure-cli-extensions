# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

def load_arguments(self, _):
    with self.argument_context('aldo-edge-operator billing-configuration create-or-update') as c:
        c.argument('resource_id', options_list=['--resource-id'], required=True, help='ARM resource ID of the associated disconnected operations resource.')
        c.argument('resource_name', options_list=['--resource-name'], required=True, help='Name of the associated disconnected operations resource.')
        c.argument('stamp_id', options_list=['--stamp-id'], required=True, help='Stamp identifier assigned by Azure.')
        c.argument('location', options_list=['--location'], required=True, help='Azure region of the associated resource.')
        c.argument('billing_model', options_list=['--billing-model'], required=True, help='Billing model for the configuration.')
        c.argument('connection_intent', options_list=['--connection-intent'], required=True, help='Connection intent for the configuration.')
        c.argument('auto_renew', options_list=['--auto-renew'], required=True, help='Auto-renewal setting for the billing configuration.')
        c.argument('billing_status', options_list=['--billing-status'], required=True, help='Current billing status.')
        c.argument('current_cores', options_list=['--current-cores'], required=True, type=int, help='Number of cores for the current billing period.')
        c.argument('current_pricing_model', options_list=['--current-pricing-model'], required=True, help='Pricing model for the current billing period.')
        c.argument('current_start_date', options_list=['--current-start-date'], required=True, help='Start date for the current billing period in YYYY-MM-DD format.')
        c.argument('current_end_date', options_list=['--current-end-date'], help='End date for the current billing period in YYYY-MM-DD format.')
        c.argument('cloud', options_list=['--cloud'], help='Cloud environment where the associated resource operates.')
        c.argument('upcoming_cores', options_list=['--upcoming-cores'], type=int, help='Number of cores for the upcoming billing period.')
        c.argument('upcoming_pricing_model', options_list=['--upcoming-pricing-model'], help='Pricing model for the upcoming billing period.')
        c.argument('upcoming_start_date', options_list=['--upcoming-start-date'], help='Start date for the upcoming billing period in YYYY-MM-DD format.')
        c.argument('upcoming_end_date', options_list=['--upcoming-end-date'], help='End date for the upcoming billing period in YYYY-MM-DD format.')
        c.argument('azure_hybrid_windows_server_benefit', options_list=['--azure-hybrid-windows-server-benefit'], help='Azure Hybrid Windows Server Benefit plan status.')
        c.argument('windows_server_vm_count', options_list=['--windows-server-vm-count'], type=int, help='Number of Windows Server VMs licensed under the benefit plan.')

    with self.argument_context('aldo-edge-operator billing-configuration snapshot show') as c:
        c.argument('snapshot_name', options_list=['--snapshot-name', '-n'], required=True, help='Billing configuration snapshot name.')
