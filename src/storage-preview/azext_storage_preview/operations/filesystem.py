# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError


def list_deleted_path(client, marker=None, num_results=None, path_prefix=None, timeout=None, **kwargs):
    from ..track2_util import list_generator

    generator = client.list_deleted_path(path_prefix=path_prefix, timeout=timeout, **kwargs)

    pages = generator.by_page(continuation_token=marker)  # BlobPropertiesPaged
    result = list_generator(pages=pages, num_results=num_results)

    return result


def set_service_properties(client, delete_retention=None, delete_retention_period=None,
                           static_website=None, index_document=None, error_document_404_path=None):
    parameters = client.get_service_properties()
    # update
    kwargs = {}
    if parameters.get('delete_retention_policy', None):
        kwargs['delete_retention_policy'] = parameters['delete_retention_policy']
    if delete_retention is not None:
        kwargs['delete_retention_policy'].enabled = delete_retention
    if delete_retention_period is not None:
        kwargs['delete_retention_policy'].days = delete_retention_period
    kwargs['delete_retention_policy'].allow_permanent_delete = False
    if parameters.get('static_website', None):
        kwargs['static_website'] = parameters['static_website']

    if static_website is not None:
        kwargs['static_website'].enabled = static_website
    if index_document is not None:
        kwargs['static_website'].index_document = index_document
    if error_document_404_path is not None:
        kwargs['static_website'].error_document_404_path = error_document_404_path
    if parameters.get('hour_metrics', None):
        kwargs['hour_metrics'] = parameters['hour_metrics']
    if parameters.get('logging', None):
        kwargs['logging'] = parameters['logging']
    if parameters.get('minute_metrics', None):
        kwargs['minute_metrics'] = parameters['minute_metrics']
    if parameters.get('cors', None):
        kwargs['cors'] = parameters['cors']

    # checks
    policy = kwargs.get('delete_retention_policy', None)
    if policy and policy.enabled and not policy.days:
        raise CLIError("must specify days-retained")

    client.set_service_properties(**kwargs)
    return client.get_service_properties()
