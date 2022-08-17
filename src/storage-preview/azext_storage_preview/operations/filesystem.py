# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from ..profiles import CUSTOM_DATA_STORAGE_FILEDATALAKE


def list_deleted_path(client, marker=None, num_results=None, path_prefix=None, timeout=None, **kwargs):
    from ..track2_util import list_generator

    generator = client.list_deleted_paths(path_prefix=path_prefix, timeout=timeout, max_results=num_results, **kwargs)

    pages = generator.by_page(continuation_token=marker)  # BlobPropertiesPaged
    result = list_generator(pages=pages, num_results=num_results)

    return result


def set_service_properties(cmd, client, delete_retention=None, delete_retention_period=None,
                           enable_static_website=False, index_document=None, error_document_404_path=None):
    parameters = client.get_service_properties()
    # update
    kwargs = {}
    delete_retention_policy = cmd.get_models('_models#RetentionPolicy', resource_type=CUSTOM_DATA_STORAGE_FILEDATALAKE)()
    if parameters.get('delete_retention_policy', None):
        delete_retention_policy = parameters['delete_retention_policy']
    if delete_retention is not None:
        delete_retention_policy.enabled = delete_retention
    if delete_retention_period is not None:
        delete_retention_policy.days = delete_retention_period
    delete_retention_policy.allow_permanent_delete = False

    static_website = cmd.get_models('_models#StaticWebsite', resource_type=CUSTOM_DATA_STORAGE_FILEDATALAKE)()
    if parameters.get('static_website', None):
        static_website = parameters['static_website']

    if static_website is not None:
        static_website.enabled = enable_static_website
    if index_document is not None:
        static_website.index_document = index_document
    if error_document_404_path is not None:
        static_website.error_document_404_path = error_document_404_path

    if parameters.get('hour_metrics', None):
        kwargs['hour_metrics'] = parameters['hour_metrics']
    if parameters.get('logging', None):
        kwargs['logging'] = parameters['logging']
    if parameters.get('minute_metrics', None):
        kwargs['minute_metrics'] = parameters['minute_metrics']
    if parameters.get('cors', None):
        kwargs['cors'] = parameters['cors']

    # checks
    if delete_retention_policy and delete_retention_policy.enabled and not delete_retention_policy.days:
        raise CLIError("must specify days-retained")

    client.set_service_properties(delete_retention_policy=delete_retention_policy, static_website=static_website,
                                  **kwargs)
    return client.get_service_properties()
