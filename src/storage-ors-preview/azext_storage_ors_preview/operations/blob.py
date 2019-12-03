# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError


def set_service_properties(client, parameters, delete_retention=None, delete_retention_period=None,
                           static_website=None, index_document=None, error_document_404_path=None):
    # update
    kwargs = {}
    if hasattr(parameters, 'delete_retention_policy'):
        kwargs['delete_retention_policy'] = parameters.delete_retention_policy
    if delete_retention is not None:
        parameters.delete_retention_policy.enabled = delete_retention
    if delete_retention_period is not None:
        parameters.delete_retention_policy.days = delete_retention_period

    if hasattr(parameters, 'static_website'):
        kwargs['static_website'] = parameters.static_website
    elif any(param is not None for param in [static_website, index_document, error_document_404_path]):
        raise CLIError('Static websites are only supported for StorageV2 (general-purpose v2) accounts.')
    if static_website is not None:
        parameters.static_website.enabled = static_website
    if index_document is not None:
        parameters.static_website.index_document = index_document
    if error_document_404_path is not None:
        parameters.static_website.error_document_404_path = error_document_404_path
    if hasattr(parameters, 'hour_metrics'):
        kwargs['hour_metrics'] = parameters.hour_metrics
    if hasattr(parameters, 'logging'):
        kwargs['logging'] = parameters.logging
    if hasattr(parameters, 'minute_metrics'):
        kwargs['minute_metrics'] = parameters.minute_metrics
    if hasattr(parameters, 'cors'):
        kwargs['cors'] = parameters.cors

    # checks
    policy = kwargs.get('delete_retention_policy', None)
    if policy and policy.enabled and not policy.days:
        raise CLIError("must specify days-retained")

    client.set_blob_service_properties(**kwargs)
    return client.get_blob_service_properties()