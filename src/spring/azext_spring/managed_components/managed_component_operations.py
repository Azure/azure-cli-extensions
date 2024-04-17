# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from knack.log import get_logger
from threading import Thread
from time import sleep

from .managed_component import (ManagedComponentInstance, supported_components)

from ..log_stream.writer import (DefaultWriter, PrefixWriter)
from ..log_stream.log_stream_operations import (attach_logs_query_options, log_stream_from_url,
                                                LogStreamBaseQueryOptions)
from ..log_stream.log_stream_validators import validate_thread_number
from .._utils import (get_bearer_auth, get_hostname)


logger = get_logger(__name__)


class ManagedComponentInstanceInfo:  # pylint: disable=too-few-public-methods
    component: str
    instance: str

    def __init__(self, component, instance):
        self.component = component
        self.instance = instance


def managed_component_logs(cmd, client, resource_group, service,
                           name=None, all_instances=None, instance=None,
                           follow=None, max_log_requests=5, lines=50, since=None, limit=2048):
    auth = get_bearer_auth(cmd.cli_ctx)
    exceptions = []
    threads = None
    queryOptions = LogStreamBaseQueryOptions(follow=follow, lines=lines, since=since, limit=limit)
    if not name and instance:
        threads = _get_log_threads_without_component(cmd, client, resource_group, service,
                                                     instance, auth, exceptions, queryOptions)
    else:
        url_dict = _get_log_stream_urls(cmd, client, resource_group, service, name, all_instances,
                                        instance, queryOptions)
        validate_thread_number(follow, len(url_dict), max_log_requests)
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
                         all_instances, instance, queryOptions: LogStreamBaseQueryOptions):
    component_api_name = _get_component(component_name).get_api_name()
    hostname = get_hostname(cmd.cli_ctx, client, resource_group, service)
    url_dict = {}

    if component_name and not all_instances and not instance:
        logger.warning("No `-i/--instance` or `--all-instances` parameters specified.")
        instances: [ManagedComponentInstance] = _list_managed_component_instances(cmd, client, resource_group, service,
                                                                                  component_name)
        if instances is None or len(instances) == 0:
            # No instances found is handle by each component by provider better error handling.
            return url_dict
        elif instances is not None and len(instances) > 1:
            logger.warning("Multiple instances found:")
            for temp_instance in instances:
                logger.warning("{}".format(temp_instance.name))
            logger.warning("Please use '-i/--instance' parameter to specify the instance name, "
                           "or use `--all-instance` parameter to get logs for all instances.")
            return url_dict
        elif instances is not None and len(instances) == 1:
            logger.warning("Exact one instance found, will get logs for it:")
            logger.warning('{}'.format(instances[0].name))
            # Make it as if user has specified exact instance name
            instance = instances[0].name

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


def _get_stream_url(hostname, component_name, instance_name, queryOptions: LogStreamBaseQueryOptions):
    url_template = "https://{}/api/logstream/managedComponents/{}/instances/{}"
    url = url_template.format(hostname, component_name, instance_name)
    url = attach_logs_query_options(url, queryOptions)
    return url


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


def _get_log_threads_without_component(cmd, client, resource_group, service, instance_name, auth, exceptions,
                                       queryOptions: LogStreamBaseQueryOptions):
    hostname = get_hostname(cmd.cli_ctx, client, resource_group, service)
    url_template = "https://{}/api/logstream/managedComponentInstances/{}"
    url = url_template.format(hostname, instance_name)
    url = attach_logs_query_options(url, queryOptions)

    return [Thread(target=log_stream_from_url, args=(url, auth, None, exceptions, _get_default_writer()))]


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
