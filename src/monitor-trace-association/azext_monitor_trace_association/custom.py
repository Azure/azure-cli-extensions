# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# NOTE (DRAFT): These command bodies call ARM directly via send_raw_request as a functional
# prototype for the 2026-01-01-preview API. They will be replaced by aaz-dev-generated code
# once the spec is published to the public Azure/azure-rest-api-specs repo.

import json

from knack.log import get_logger

from azure.cli.core.util import send_raw_request

logger = get_logger(__name__)

API_VERSION = '2026-01-01-preview'
RESOURCE_TYPE = 'Microsoft.Monitor/traceAssociations'


def _build_url(cli_ctx, resource_uri, name=None):
    arm_endpoint = cli_ctx.cloud.endpoints.resource_manager.rstrip('/')
    scope = resource_uri.strip('/')
    url = '{}/{}/providers/{}'.format(arm_endpoint, scope, RESOURCE_TYPE)
    if name:
        url = '{}/{}'.format(url, name)
    return '{}?api-version={}'.format(url, API_VERSION)


def create_trace_association(cmd, resource_uri, azure_monitor_workspace_resource_id, name='default'):
    url = _build_url(cmd.cli_ctx, resource_uri, name)
    body = json.dumps({
        'properties': {
            'azureMonitorWorkspaceResourceId': azure_monitor_workspace_resource_id
        }
    })
    response = send_raw_request(cmd.cli_ctx, 'PUT', url,
                                headers=['Content-Type=application/json'], body=body)
    return response.json()


def update_trace_association(cmd, resource_uri, azure_monitor_workspace_resource_id=None, name='default'):
    url = _build_url(cmd.cli_ctx, resource_uri, name)
    existing = send_raw_request(cmd.cli_ctx, 'GET', url).json()
    properties = existing.get('properties') or {}
    if azure_monitor_workspace_resource_id:
        properties['azureMonitorWorkspaceResourceId'] = azure_monitor_workspace_resource_id
    body = json.dumps({'properties': properties})
    response = send_raw_request(cmd.cli_ctx, 'PUT', url,
                                headers=['Content-Type=application/json'], body=body)
    return response.json()


def show_trace_association(cmd, resource_uri, name='default'):
    url = _build_url(cmd.cli_ctx, resource_uri, name)
    return send_raw_request(cmd.cli_ctx, 'GET', url).json()


def delete_trace_association(cmd, resource_uri, name='default'):
    url = _build_url(cmd.cli_ctx, resource_uri, name)
    send_raw_request(cmd.cli_ctx, 'DELETE', url)


def list_trace_association(cmd, resource_uri):
    url = _build_url(cmd.cli_ctx, resource_uri)
    data = send_raw_request(cmd.cli_ctx, 'GET', url).json()
    return data.get('value', data)
