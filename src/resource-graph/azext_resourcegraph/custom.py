# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-import, broad-except

import json
import os
from collections import OrderedDict
from datetime import datetime, timedelta

import requests
from azure.cli.core._config import GLOBAL_CONFIG_DIR
from azure.cli.core._profile import Profile
from azure.cli.core._session import SESSION
from azure.core.exceptions import HttpResponseError
from azure.mgmt.core.exceptions import ARMErrorFormat
from azure.cli.core.azclierror import BadRequestError, AzureInternalError
from knack.log import get_logger
from knack.util import todict

from azext_resourcegraph.vendored_sdks.resourcegraph.models import ResultTruncated
from .vendored_sdks.resourcegraph import ResourceGraphClient
from .vendored_sdks.resourcegraph.models import \
    QueryRequest, QueryRequestOptions, QueryResponse, ResultFormat, ErrorResponse, Error

__SUBSCRIPTION_LIMIT = 1000
__MANAGEMENT_GROUP_LIMIT = 10
__logger = get_logger(__name__)


def execute_query(client, graph_query, first, skip, subscriptions, management_groups, allow_partial_scopes, skip_token):
    # type: (ResourceGraphClient, str, int, int, list[str], list[str], bool, str) -> object
    mgs_list = management_groups
    if mgs_list is not None and len(mgs_list) > __MANAGEMENT_GROUP_LIMIT:
        mgs_list = mgs_list[:__MANAGEMENT_GROUP_LIMIT]
        warning_message = "The query included more management groups than allowed. "\
                          "Only the first {0} management groups were included for the results. "\
                          "To use more than {0} management groups, "\
                          "see the docs for examples: "\
                          "https://aka.ms/arg-error-toomanysubs".format(__MANAGEMENT_GROUP_LIMIT)
        __logger.warning(warning_message)

    subs_list = None
    if mgs_list is None:
        subs_list = subscriptions or _get_cached_subscriptions()
        if subs_list is not None and len(subs_list) > __SUBSCRIPTION_LIMIT:
            subs_list = subs_list[:__SUBSCRIPTION_LIMIT]
            warning_message = "The query included more subscriptions than allowed. "\
                              "Only the first {0} subscriptions were included for the results. "\
                              "To use more than {0} subscriptions, "\
                              "see the docs for examples: "\
                              "https://aka.ms/arg-error-toomanysubs".format(__SUBSCRIPTION_LIMIT)
            __logger.warning(warning_message)

    response = None
    try:
        result_truncated = False

        request_options = QueryRequestOptions(
            top=first,
            skip=skip,
            skip_token=skip_token,
            result_format=ResultFormat.object_array,
            allow_partial_scopes=allow_partial_scopes
        )

        request = QueryRequest(
            query=graph_query,
            subscriptions=subs_list,
            management_groups=mgs_list,
            options=request_options)
        response = client.resources(request)  # type: QueryResponse
        if response.result_truncated == ResultTruncated.true:
            result_truncated = True

        if result_truncated and first is not None and len(response.data) < first:
            __logger.warning("Unable to paginate the results of the query. "
                             "Some resources may be missing from the results. "
                             "To rewrite the query and enable paging, "
                             "see the docs for an example: https://aka.ms/arg-results-truncated")

    except HttpResponseError as ex:
        if ex.model.error.code == 'BadRequest':
            raise BadRequestError(json.dumps(_to_dict(ex.model.error), indent=4)) from ex

        raise AzureInternalError(json.dumps(_to_dict(ex.model.error), indent=4)) from ex

    result_dict = dict()
    result_dict['data'] = response.data
    result_dict['count'] = response.count
    result_dict['total_records'] = response.total_records
    result_dict['skip_token'] = response.skip_token

    return result_dict


def create_shared_query(client, resource_group_name,
                        resource_name, description,
                        graph_query, location='global', tags=None):
    from azext_resourcegraph.vendored_sdks.resourcegraph.models import GraphQueryResource
    graph_shared_query = GraphQueryResource(description=description,
                                            query=graph_query,
                                            tags=tags,
                                            location=location)
    return client.graph_query.create_or_update(resource_group_name=resource_group_name,
                                               resource_name=resource_name,
                                               properties=graph_shared_query)


def _get_cached_subscriptions():
    # type: () -> list[str]

    cached_subs = Profile().load_cached_subscriptions()
    return [sub['id'] for sub in cached_subs]


def _to_dict(obj):
    if isinstance(obj, Error):
        return _to_dict(todict(obj))

    if isinstance(obj, dict):
        result = OrderedDict()

        # Complex objects should be displayed last
        sorted_keys = sorted(obj.keys(), key=lambda k: (isinstance(obj[k], dict), isinstance(obj[k], list), k))
        for key in sorted_keys:
            if obj[key] is None or obj[key] == [] or obj[key] == {}:
                continue

            result[key] = _to_dict(obj[key])
        return result

    if isinstance(obj, list):
        return [_to_dict(v) for v in obj]

    return obj
