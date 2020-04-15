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
from knack.log import get_logger
from knack.util import todict, CLIError, ensure_dir

from azext_resourcegraph.resource_graph_enums import IncludeOptionsEnum
from azext_resourcegraph.vendored_sdks.resourcegraph.models import ResultTruncated
from .vendored_sdks.resourcegraph import ResourceGraphClient
from .vendored_sdks.resourcegraph.models import \
    QueryRequest, QueryRequestOptions, QueryResponse, ResultFormat, ErrorResponseException, ErrorResponse

__ROWS_PER_PAGE = 1000
__CACHE_FILE_NAME = ".azgraphcache"
__CACHE_KEY = "query_extension"
__SUBSCRIPTION_LIMIT = 1000
__logger = get_logger(__name__)


def execute_query(client, graph_query, first, skip, subscriptions, include):
    # type: (ResourceGraphClient, str, int, int, list[str], str) -> object

    subs_list = subscriptions or _get_cached_subscriptions()

    if len(subs_list) > __SUBSCRIPTION_LIMIT:
        subs_list = subs_list[:__SUBSCRIPTION_LIMIT]
        warning_message = "The query included more subscriptions than allowed. "\
                          "Only the first {0} subscriptions were included for the results. "\
                          "To use more than {0} subscriptions, "\
                          "see the docs for examples: https://aka.ms/arg-error-toomanysubs".format(__SUBSCRIPTION_LIMIT)
        __logger.warning(warning_message)

    results = []
    skip_token = None
    full_query = graph_query

    if include == IncludeOptionsEnum.display_names:
        try:
            full_query = _get_extension() + "| " + graph_query

        except Exception as e:
            __logger.warning("Failed to include displayNames to result. Error: %s", e)

    try:
        result_truncated = False
        while True:
            request_options = QueryRequestOptions(
                top=min(first - len(results), __ROWS_PER_PAGE),
                skip=skip + len(results),
                skip_token=skip_token,
                result_format=ResultFormat.object_array
            )

            request = QueryRequest(query=full_query, subscriptions=subs_list, options=request_options)
            response = client.resources(request)  # type: QueryResponse
            if response.result_truncated == ResultTruncated.true:
                result_truncated = True

            skip_token = response.skip_token
            results.extend(response.data)

            if len(results) >= first or skip_token is None:
                break

        if result_truncated and len(results) < first:
            __logger.warning("Unable to paginate the results of the query. "
                             "Some resources may be missing from the results. "
                             "To rewrite the query and enable paging, "
                             "see the docs for an example: https://aka.ms/arg-results-truncated")

    except ErrorResponseException as ex:
        raise CLIError(json.dumps(_to_dict(ex.error), indent=4))

    return results


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


def _get_cached_detailed_subscriptions():
    # type: () -> list[tuple[any, any]]

    cached_subs = Profile().load_cached_subscriptions()
    return [(sub['id'], sub["name"]) for sub in cached_subs]


def _get_cached_detailed_tenant():
    # type: () -> list[tuple[any, any]]

    token = Profile().get_raw_token()
    bearer_token = token[0][0] + " " + token[0][1]
    result = requests.get(url="https://management.azure.com/tenants?api-version=2019-05-10",
                          headers={'Authorization': bearer_token})
    return [(tenant['tenantId'], tenant["displayName"]) for tenant in result.json()["value"]]


def _to_dict(obj):
    if isinstance(obj, ErrorResponse):
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


def _get_extension():
    # try to get from cache
    ensure_dir(GLOBAL_CONFIG_DIR)
    path_cache = os.path.join(GLOBAL_CONFIG_DIR, __CACHE_FILE_NAME)
    SESSION.data = {}
    SESSION.load(path_cache)
    query_extension = SESSION.data.get(__CACHE_KEY)

    # if cache is older than 1 day, we don't want to use it
    if datetime.utcnow() - datetime.utcfromtimestamp(os.path.getmtime(path_cache)) < timedelta(days=1) \
            and query_extension is not None:
        return query_extension

    queries_parts = []
    subscription_list = _get_cached_detailed_subscriptions()
    if subscription_list:
        sub_query = "extend subscriptionDisplayName=case("
        for sub in subscription_list:
            sub_query += "subscriptionId=='" + sub[0] + "', '" + sub[1] + "',"
        sub_query += "'')"
        queries_parts.append(sub_query)

    tenant_list = _get_cached_detailed_tenant()
    if tenant_list:
        tenant_query = "extend tenantDisplayName=case("
        for tenant in tenant_list:
            tenant_query += "tenantId=='" + tenant[0] + "', '" + tenant[1] + "',"
        tenant_query += "'')"
        queries_parts.append(tenant_query)

    query_extension = "| ".join(queries_parts)

    # save to cache
    SESSION.filename = path_cache
    SESSION.data.update({__CACHE_KEY: query_extension})
    SESSION.save()
    return query_extension
