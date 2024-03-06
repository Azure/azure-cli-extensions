# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.core._profile import Profile
from azure.cli.core.commands.client_factory import get_subscription_id
from knack.log import get_logger
from knack.util import CLIError
from six.moves.urllib import parse
from threading import Thread
from time import sleep

from .managed_component import (Acs, Flux, Scg, ScgOperator,
                                ManagedComponentInstance, supported_components, get_component)

from ..log_stream.writer import (DefaultWriter, PrefixWriter)
from ..log_stream.log_stream_operations import log_stream_from_url
from .._utils import (get_proxy_api_endpoint, BearerAuth)


logger = get_logger(__name__)


class ManagedComponentInstanceInfo:
    component: str
    instance: str

    def __init__(self, component, instance):
        self.component = component
        self.instance = instance


class QueryOptions:
    def __init__(self, follow, lines, since, limit):
        self.follow = follow
        self.lines = lines
        self.since = since
        self.limit = limit


def managed_component_logs(cmd, client, resource_group, service,
                           name=None, all_instances=None, instance=None,
                           follow=None, max_log_requests=5, lines=50, since=None, limit=2048):
    auth = _get_bearer_auth(cmd)
    exceptions = []
    threads = None
    queryOptions = QueryOptions(follow=follow, lines=lines, since=since, limit=limit)
    if not name and instance:
        threads = _get_log_threads_without_component(cmd, client, resource_group, service,
                                                     instance, auth, exceptions, queryOptions)
    else:
        url_dict = _get_log_stream_urls(cmd, client, resource_group, service, name, all_instances,
                                        instance, queryOptions)
        if (follow is True and len(url_dict) > max_log_requests):
            raise CLIError("You are attempting to follow {} log streams, but maximum allowed concurrency is {}, "
                           "use --max-log-requests to increase the limit".format(len(url_dict), max_log_requests))
        threads = _get_log_threads(all_instances, url_dict, auth, exceptions)

    if follow and len(threads) > 1:
        _parallel_start_threads(threads)
    else:
        _sequential_start_threads(threads)

    if exceptions:
        raise exceptions[0]


def managed_component_list(cmd, client, resource_group, service):
    return supported_components


def managed_component_instance_list(cmd, client, resource_group, service, component):
    instances = _list_managed_component_instances(cmd, client, resource_group, service, component)
    if instances is None or len(instances) == 0:
        logger.warning("No instance found for component '{}'".format(component))
    return instances


def _list_managed_component_instances(cmd, client, resource_group, service, component):
    managed_component = _get_component(component)
    return managed_component.list_instances(client, resource_group, service)


def _get_component(component):
    for c in supported_components:
        if c.match(component):
            return c

    return None


def _get_log_stream_urls(cmd, client, resource_group, service, component_name,
                         all_instances, instance, queryOptions: QueryOptions):
    component_api_name = _get_component(component_name).get_api_name()
    hostname = _get_hostname(cmd, client, resource_group, service)
    url_dict = {}

    if component_name and all_instances is True:
        instances: [ManagedComponentInstance] = _list_managed_component_instances(cmd, client, resource_group, service, component_name)
        if instances is None or len(instances) == 0:
            return url_dict
        for i in instances:
            url = _get_stream_url(hostname, component_api_name, i.name, queryOptions)
            url_dict[url] = ManagedComponentInstanceInfo(component_name, i.name)
    elif instance:
        url = _get_stream_url(hostname, component_api_name, instance, queryOptions)
        url_dict[url] = ManagedComponentInstanceInfo(component_name, instance)

    return url_dict


def _get_stream_url(hostname, component_name, instance_name, queryOptions: QueryOptions):
    url_template = "https://{}/api/logstream/managedComponents/{}/instances/{}"
    url = url_template.format(hostname, component_name, instance_name)
    url = _attach_logs_query_options(url, queryOptions)
    return url


def _get_bearer_auth(cmd):
    profile = Profile(cli_ctx=cmd.cli_ctx)
    creds, _, tenant = profile.get_raw_token()
    token = creds[1]
    return BearerAuth(token)


def _get_hostname(cmd, client, resource_group, service):
    resource = client.services.get(resource_group, service)
    return get_proxy_api_endpoint(cmd.cli_ctx, resource)


def _get_log_threads(all_instances, url_dict, auth, exceptions):
    threads = []
    need_prefix = all_instances is True
    for url in url_dict.keys():
        writer = _get_default_writer()
        if need_prefix:
            instance_info = url_dict[url]
            prefix = "[{}]".format(instance_info.instance)
            writer = _get_prefix_writer(prefix)
        threads.append(Thread(target=log_stream_from_url, args=(url, auth, None, exceptions, writer)))
    return threads


def _contains_alive_thread(threads: [Thread]):
    for t in threads:
        if t.is_alive():
            return True


def _parallel_start_threads(threads: [Thread]):
    for t in threads:
        t.daemon = True
        t.start()

    while _contains_alive_thread(threads):
        sleep(1)
        # so that ctrl+c can stop the command


def _sequential_start_threads(threads: [Thread]):
    for idx, t in enumerate(threads):
        t.daemon = True
        t.start()

        while t.is_alive():
            sleep(1)
            # so that ctrl+c can stop the command


def _get_log_threads_without_component(cmd, client, resource_group, service, instance_name, auth, exceptions, queryOptions: QueryOptions):
    hostname = _get_hostname(cmd, client, resource_group, service)
    url_template = "https://{}/api/logstream/managedComponentInstances/{}"
    url = url_template.format(hostname, instance_name)
    url = _attach_logs_query_options(url, queryOptions)

    return [Thread(target=log_stream_from_url, args=(url, auth, None, exceptions, _get_default_writer()))]


def _attach_logs_query_options(url, queryOptions: QueryOptions):
    params = {}
    params["tailLines"] = queryOptions.lines
    params["limitBytes"] = queryOptions.limit
    if queryOptions.since:
        params["sinceSeconds"] = queryOptions.since
    if queryOptions.follow:
        params["follow"] = True

    url += "?{}".format(parse.urlencode(params)) if params else ""
    return url


def _get_prefix_writer(prefix):
    """
    Define this method, so that we can mock this method in scenario test to test output
    """
    return PrefixWriter(prefix)


def _get_default_writer():
    """
    Define this method, so that we can mock this method in scenario test to test output
    """
    return DefaultWriter()
