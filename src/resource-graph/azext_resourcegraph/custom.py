# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-import

from collections import OrderedDict
import json

from azure.cli.core._profile import Profile
from knack.util import todict, CLIError

from .vendored_sdks.resourcegraph import ResourceGraphClient
from .vendored_sdks.resourcegraph.models import \
    QueryRequest, QueryRequestOptions, QueryResponse, ResultFormat, ErrorResponseException, ErrorResponse

__ROWS_PER_PAGE = 1000


def execute_query(client, graph_query, first, skip, subscriptions):
    # type: (ResourceGraphClient, str, int, int, list[str]) -> object

    subs_list = subscriptions or _get_cached_subscriptions()

    results = []
    skip_token = None

    try:
        while True:
            request_options = QueryRequestOptions(
                top=min(first - len(results), __ROWS_PER_PAGE),
                skip=skip + len(results),
                skip_token=skip_token,
                result_format=ResultFormat.object_array
            )

            request = QueryRequest(query=graph_query, subscriptions=subs_list, options=request_options)
            response = client.resources(request)  # type: QueryResponse
            skip_token = response.skip_token
            results.extend(response.data)

            if len(results) >= first or skip_token is None:
                break

    except ErrorResponseException as ex:
        raise CLIError(json.dumps(_to_dict(ex.error), indent=4))

    return results


def _get_cached_subscriptions():
    # type: () -> list[str]

    cached_subs = Profile().load_cached_subscriptions()
    return [sub['id'] for sub in cached_subs]


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
