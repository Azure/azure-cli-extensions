# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json

from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.util import send_raw_request
from knack.util import CLIError


API_VERSION = '2026-06-01-preview'


def _management_endpoint(cmd):
    return cmd.cli_ctx.cloud.endpoints.resource_manager.rstrip('/')


def _subscription_id(cmd):
    return get_subscription_id(cmd.cli_ctx)


def _billing_configuration_path(cmd):
    return 'subscriptions/{}/providers/Microsoft.EdgeOperator/billingConfigurations/default'.format(
        _subscription_id(cmd))


def _billing_configuration_snapshots_path(cmd):
    return _billing_configuration_path(cmd) + '/snapshots'


def _billing_configuration_snapshot_path(cmd, snapshot_name):
    return _billing_configuration_snapshots_path(cmd) + '/{}'.format(snapshot_name)


def _request_url(cmd, resource_path):
    return '{}/{}?api-version={}'.format(_management_endpoint(cmd), resource_path, API_VERSION)


def _send_request(cmd, method, resource_path, body=None):
    request_body = None
    if body is not None:
        request_body = body if isinstance(body, str) else json.dumps(body)
    return send_raw_request(cmd.cli_ctx, method, _request_url(cmd, resource_path), body=request_body)


def _build_billing_period(cores, pricing_model, start_date, end_date=None):
    period = {
        'cores': cores,
        'pricingModel': pricing_model,
        'startDate': start_date,
    }
    if end_date is not None:
        period['endDate'] = end_date
    return period


def _build_billing_configuration_payload(resource_id, resource_name, stamp_id, location, billing_model,
                                         connection_intent, auto_renew, billing_status, current_cores,
                                         current_pricing_model, current_start_date, current_end_date=None,
                                         cloud=None, upcoming_cores=None, upcoming_pricing_model=None,
                                         upcoming_start_date=None, upcoming_end_date=None,
                                         azure_hybrid_windows_server_benefit=None,
                                         windows_server_vm_count=None):
    upcoming_values = [upcoming_cores, upcoming_pricing_model, upcoming_start_date, upcoming_end_date]
    if any(value is not None for value in upcoming_values) and any(
        value is None for value in [upcoming_cores, upcoming_pricing_model, upcoming_start_date]
    ):
        raise CLIError(
            'When specifying an upcoming billing period, --upcoming-cores, --upcoming-pricing-model, '
            'and --upcoming-start-date are required.'
        )

    billing_configuration = {
        'autoRenew': auto_renew,
        'billingStatus': billing_status,
        'current': _build_billing_period(current_cores, current_pricing_model, current_start_date, current_end_date),
    }

    if any(value is not None for value in [upcoming_cores, upcoming_pricing_model, upcoming_start_date, upcoming_end_date]):
        billing_configuration['upcoming'] = _build_billing_period(
            upcoming_cores,
            upcoming_pricing_model,
            upcoming_start_date,
            upcoming_end_date,
        )

    properties = {
        'resourceId': resource_id,
        'resourceName': resource_name,
        'stampId': stamp_id,
        'location': location,
        'billingModel': billing_model,
        'connectionIntent': connection_intent,
        'billingConfiguration': billing_configuration,
    }

    if cloud is not None:
        properties['cloud'] = cloud

    benefit_plans = {}
    if azure_hybrid_windows_server_benefit is not None:
        benefit_plans['azureHybridWindowsServerBenefit'] = azure_hybrid_windows_server_benefit
    if windows_server_vm_count is not None:
        benefit_plans['windowsServerVmCount'] = windows_server_vm_count
    if benefit_plans:
        properties['benefitPlans'] = benefit_plans

    return {'properties': properties}


def show_billing_configuration(cmd):
    response = _send_request(cmd, 'GET', _billing_configuration_path(cmd))
    return response.json()


def create_or_update_billing_configuration(cmd, resource_id, resource_name, stamp_id, location, billing_model,
                                           connection_intent, auto_renew, billing_status, current_cores,
                                           current_pricing_model, current_start_date, current_end_date=None,
                                           cloud=None, upcoming_cores=None, upcoming_pricing_model=None,
                                           upcoming_start_date=None, upcoming_end_date=None,
                                           azure_hybrid_windows_server_benefit=None,
                                           windows_server_vm_count=None):
    payload = _build_billing_configuration_payload(
        resource_id,
        resource_name,
        stamp_id,
        location,
        billing_model,
        connection_intent,
        auto_renew,
        billing_status,
        current_cores,
        current_pricing_model,
        current_start_date,
        current_end_date,
        cloud,
        upcoming_cores,
        upcoming_pricing_model,
        upcoming_start_date,
        upcoming_end_date,
        azure_hybrid_windows_server_benefit,
        windows_server_vm_count,
    )
    response = _send_request(cmd, 'PUT', _billing_configuration_path(cmd), body=payload)
    return response.json()


def list_billing_configurations(cmd):
    response = _send_request(cmd, 'GET', 'subscriptions/{}/providers/Microsoft.EdgeOperator/billingConfigurations'.format(
        _subscription_id(cmd)))
    return response.json().get('value', [])


def show_billing_configuration_snapshot(cmd, snapshot_name):
    response = _send_request(cmd, 'GET', _billing_configuration_snapshot_path(cmd, snapshot_name))
    return response.json()


def list_billing_configuration_snapshots(cmd):
    response = _send_request(cmd, 'GET', _billing_configuration_snapshots_path(cmd))
    return response.json().get('value', [])