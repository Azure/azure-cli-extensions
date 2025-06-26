# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from itertools import islice
from knack.log import get_logger
from azure.cli.core.commands import LongRunningOperation
from azure.ai.ml.entities import FqdnDestination, ServiceTagDestination, PrivateEndpointDestination
from .raise_error import log_and_raise_error
from .utils import _dump_entity_with_warnings, get_ml_client
module_logger = get_logger()


def ml_workspace_outbound_rule_show(cmd, resource_group_name, workspace_name, rule):
    ml_client, debug = get_ml_client(cli_ctx=cmd.cli_ctx, resource_group_name=resource_group_name)
    try:
        result = ml_client.workspace_outbound_rules.get(workspace_name=workspace_name, outbound_rule_name=rule, resource_group=resource_group_name)
        return _dump_entity_with_warnings(result)
    except Exception as err:
        log_and_raise_error(err, debug)


def ml_workspace_outbound_rule_list(cmd, resource_group_name, workspace_name):
    ml_client, debug = get_ml_client(cli_ctx=cmd.cli_ctx, resource_group_name=resource_group_name)
    try:
        results = ml_client.workspace_outbound_rules.list(workspace_name=workspace_name, resource_group=resource_group_name)
        
        return list(map(lambda x: _dump_entity_with_warnings(x), results))
    except Exception as err:
        log_and_raise_error(err, debug)


def ml_workspace_outbound_rule_set(
    cmd,
    resource_group_name,
    workspace_name,
    rule,
    type,
    destination=None,
    service_tag=None,
    protocol=None,
    port_ranges=None,
    address_prefixes=None,
    service_resource_id=None,
    subresource_target=None,
    spark_enabled=None,
    fqdns=None,
    no_wait=False
    ):
    ml_client, debug = get_ml_client(cli_ctx=cmd.cli_ctx, resource_group_name=resource_group_name)
    if type=="fqdn":
        if destination==None or service_tag!=None or protocol!=None or port_ranges!=None or service_resource_id!=None or subresource_target!=None:
            log_and_raise_error('fqdn outbound rule should specify the following parameter: "--destination"')
        rule = FqdnDestination(name=rule, destination=destination)
    elif type=="service_tag":
        if service_tag==None or protocol==None or port_ranges==None or destination!=None or service_resource_id!=None or subresource_target!=None:
            log_and_raise_error('service_tag outbound rule should specify the following parameters: "--service-tag", "--protocol", and "--port-ranges", [Optional]: "--address-prefixes"')
        if address_prefixes!=None:
            address_prefixes = [prefix.strip() for prefix in address_prefixes.split(',')]
        rule = ServiceTagDestination(name=rule, service_tag=service_tag, protocol=protocol, port_ranges=port_ranges, address_prefixes=address_prefixes)
    elif type=="private_endpoint":
        if service_resource_id==None or subresource_target==None or destination!=None or service_tag!=None or protocol!=None or port_ranges!=None:
            log_and_raise_error('private_endpoint outbound rule should specify the following parameters: "--service-resource-id", and "--subresource-target". [Optional]: "--spark-enabled", "--fqdns"')
        if fqdns!=None:
            fqdns = [fqdn.strip() for fqdn in fqdns.split(',')]
        rule = PrivateEndpointDestination(name=rule, service_resource_id=service_resource_id, subresource_target=subresource_target, spark_enabled=spark_enabled, fqdns=fqdns)
    else:
        log_and_raise_error('--type must be one of the following: fqdn, service_tag, private_endpoint')

    try:
        set_result = ml_client.workspace_outbound_rules.begin_create(
            workspace_name=workspace_name,
            rule=rule,
            resource_group=resource_group_name)
        if not no_wait:
            set_result = LongRunningOperation(cmd.cli_ctx)(set_result)
            return _dump_entity_with_warnings(set_result)
        return set_result
    except Exception as err:
        log_and_raise_error(err, debug)


def ml_workspace_outbound_rule_remove(cmd, resource_group_name, workspace_name, rule, no_wait=False):
    ml_client, debug = get_ml_client(cli_ctx=cmd.cli_ctx, resource_group_name=resource_group_name)

    try:
        del_result = ml_client.workspace_outbound_rules.begin_remove(workspace_name=workspace_name, outbound_rule_name=rule, resource_group=resource_group_name)
        if not no_wait:
            del_result = LongRunningOperation(cmd.cli_ctx)(del_result)
        return del_result
    except Exception as err:
        log_and_raise_error(err, debug)

