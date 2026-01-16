# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from collections import OrderedDict
from knack.util import todict
from knack.log import get_logger

from .vendored_sdks.resourcegraph.models import ResultTruncated
from .vendored_sdks.resourcegraph.models import QueryRequest, QueryRequestOptions, QueryResponse, ResultFormat, Error
from azure.cli.core._profile import Profile
from azure.core.exceptions import HttpResponseError
from azure.cli.core.azclierror import BadRequestError, AzureInternalError


__SUBSCRIPTION_LIMIT = 1000
__MANAGEMENT_GROUP_LIMIT = 10
__logger = get_logger(__name__)


def build_arg_query(resource_groups, tags):
    # type: (list[str], list[str]) -> str

    query = "Resources"
    if resource_groups is not None and len(resource_groups) > 0:
        # ARG returns all resource groups as lowercase, so we need to lowercase the input
        resource_groups = resource_groups.lower()

        query += " | where resourceGroup in ({0})".format(','.join(f"'{item}'" for item in resource_groups.split(',')))

    if tags is not None:
        tagquery = []
        for tag in tags.split(','):
            tag = tag.strip()
            if not tag:  # Skip empty tags
                continue

            if '=' in tag:
                # Tag with a value (TagA=ValueA)
                tag_name, tag_value = tag.split('=', 1)
                # Escape single quotes in the value
                tag_value = tag_value.replace("'", "''")
                tagquery.append(f"tags['{tag_name}'] == '{tag_value}'")
            else:
                # Tag without a value. We don't support those.
                pass

        if tagquery:  # Only proceed if tagquery has items
            query += " | where " + " and ".join(tagquery)

    return query


def execute_arg_query(
        client, graph_query, first, skip, subscriptions, management_groups, allow_partial_scopes, skip_token):

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
