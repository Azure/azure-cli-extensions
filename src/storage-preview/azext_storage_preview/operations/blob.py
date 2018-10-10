# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import print_function


def set_service_properties(client, parameters, delete_retention=None, days_retained=None, static_website=None,
                           index_document=None, error_document_404_path=None):
    # update
    kwargs = {}
    if any([delete_retention, days_retained]):
        kwargs['delete_retention_policy'] = parameters.delete_retention_policy
    if delete_retention is not None:
        parameters.delete_retention_policy.enabled = delete_retention
    if days_retained is not None:
        parameters.delete_retention_policy.days = days_retained

    if any([static_website, index_document, error_document_404_path]):
        kwargs['static_website'] = parameters.static_website
    if static_website is not None:
        parameters.static_website.enabled = static_website
    if index_document is not None:
        parameters.static_website.index_document = index_document
    if error_document_404_path is not None:
        parameters.static_website.error_document_404_path = error_document_404_path

    # checks
    policy = parameters.delete_retention_policy
    if policy.enabled and not policy.days:
        from knack.util import CLIError
        raise CLIError("must specify days-retained")

    client.set_blob_service_properties(**kwargs)
    return client.get_blob_service_properties()
