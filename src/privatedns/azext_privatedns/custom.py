# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from __future__ import print_function
from collections import Counter
from knack.log import get_logger
from azure.cli.core.util import CLIError
from msrestazure.azure_exceptions import CloudError
from azext_privatedns.vendored_sdks.models import (PrivateZone, VirtualNetworkLink, RecordSet, AaaaRecord, ARecord, SrvRecord, TxtRecord, MxRecord, PtrRecord, CnameRecord)


logger = get_logger(__name__)


def list_privatedns_zones(client, resource_group_name=None):
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name)
    return client.list()


def create_privatedns_zone(client, resource_group_name, private_zone_name, tags=None):
    zone = PrivateZone(location='global', tags=tags)
    return client.create_or_update(resource_group_name, private_zone_name, zone, if_none_match='*')


def update_privatedns_zone(instance, tags=None):
    if tags is not None:
        instance.tags = tags
    return instance


def create_privatedns_link(client, resource_group_name, private_zone_name, virtual_network_link_name, virtual_network, registration_enabled, tags=None):
    link = VirtualNetworkLink(location='global', tags=tags)

    if registration_enabled is not None:
        link.registration_enabled = registration_enabled

    if virtual_network is not None:
        link.virtual_network = virtual_network

    return client.create_or_update(resource_group_name, private_zone_name, virtual_network_link_name, link, if_none_match='*')


def update_privatedns_link(instance, registration_enabled=None, tags=None):
    if registration_enabled is not None:
        instance.registration_enabled = registration_enabled

    if tags is not None:
        instance.tags = tags

    return instance


def create_privatedns_record_set(client, resource_group_name, private_zone_name, relative_record_set_name, record_type, metadata=None, ttl=3600):

    record_set = RecordSet(ttl=ttl, metadata=metadata)
    return client.create_or_update(resource_group_name, private_zone_name, record_type, relative_record_set_name, record_set, if_none_match='*')


def list_privatedns_record_set(client, resource_group_name, private_zone_name, record_type=None):
    if record_type is not None:
        return client.list_by_type(resource_group_name, private_zone_name, record_type)

    return client.list(resource_group_name, private_zone_name)


def _type_to_property_name(key):
    type_dict = {
        'a': 'a_records',
        'aaaa': 'aaaa_records',
        'cname': 'cname_record',
        'mx': 'mx_records',
        'ptr': 'ptr_records',
        'soa': 'soa_record',
        'srv': 'srv_records',
        'txt': 'txt_records',
    }
    return type_dict[key.lower()]


def _add_record(record_set, record, record_type, is_list=False):
    record_property = _type_to_property_name(record_type)

    if is_list:
        record_list = getattr(record_set, record_property)
        if record_list is None:
            setattr(record_set, record_property, [])
            record_list = getattr(record_set, record_property)
        record_list.append(record)
    else:
        setattr(record_set, record_property, record)


def _add_save_record(client, record, record_type, relative_record_set_name, resource_group_name, private_zone_name, is_list=True):
    try:
        record_set = client.get(resource_group_name, private_zone_name, record_type, relative_record_set_name)
    except CloudError:
        record_set = RecordSet(ttl=3600)

    _add_record(record_set, record, record_type, is_list)

    return client.create_or_update(resource_group_name, private_zone_name, record_type, relative_record_set_name, record_set)


def add_privatedns_aaaa_record(client, resource_group_name, private_zone_name, relative_record_set_name, ipv6_address):
    record = AaaaRecord(ipv6_address=ipv6_address)
    record_type = 'aaaa'
    return _add_save_record(client, record, record_type, relative_record_set_name, resource_group_name, private_zone_name)


def add_privatedns_a_record(client, resource_group_name, private_zone_name, relative_record_set_name, ipv4_address):
    record = ARecord(ipv4_address=ipv4_address)
    record_type = 'a'
    return _add_save_record(client, record, record_type, relative_record_set_name, resource_group_name, private_zone_name)


def add_privatedns_mx_record(client, resource_group_name, private_zone_name, relative_record_set_name, preference, exchange):
    record = MxRecord(preference=int(preference), exchange=exchange)
    record_type = 'mx'
    return _add_save_record(client, record, record_type, relative_record_set_name, resource_group_name, private_zone_name)


def add_privatedns_ptr_record(client, resource_group_name, private_zone_name, relative_record_set_name, dname):
    record = PtrRecord(ptrdname=dname)
    record_type = 'ptr'
    return _add_save_record(client, record, record_type, relative_record_set_name, resource_group_name, private_zone_name)


def add_privatedns_srv_record(client, resource_group_name, private_zone_name, relative_record_set_name, priority, weight, port, target):
    record = SrvRecord(priority=priority, weight=weight, port=port, target=target)
    record_type = 'srv'
    return _add_save_record(client, record, record_type, relative_record_set_name, resource_group_name, private_zone_name)


def add_privatedns_txt_record(client, resource_group_name, private_zone_name, relative_record_set_name, value):
    record = TxtRecord(value=value)
    record_type = 'txt'
    long_text = ''.join(x for x in record.value)
    original_len = len(long_text)
    record.value = []
    while len(long_text) > 255:
        record.value.append(long_text[:255])
        long_text = long_text[255:]
    record.value.append(long_text)
    final_str = ''.join(record.value)
    final_len = len(final_str)
    assert original_len == final_len
    return _add_save_record(client, record, record_type, relative_record_set_name, resource_group_name, private_zone_name)


def add_privatedns_cname_record(client, resource_group_name, private_zone_name, relative_record_set_name, cname):
    record = CnameRecord(cname=cname)
    record_type = 'cname'
    return _add_save_record(client, record, record_type, relative_record_set_name, resource_group_name, private_zone_name, is_list=False)


def update_privatedns_record_set(instance, metadata=None):
    if metadata is not None:
        instance.metadata = metadata

    return instance


def update_privatedns_soa_record(client, resource_group_name, private_zone_name, host=None, email=None,
                                 serial_number=None, refresh_time=None, retry_time=None, expire_time=None,
                                 minimum_ttl=None):
    relative_record_set_name = '@'
    record_type = 'soa'

    record_set = client.get(resource_group_name, private_zone_name, record_type, relative_record_set_name)
    record = record_set.soa_record

    record.host = host or record.host
    record.email = email or record.email
    record.serial_number = serial_number or record.serial_number
    record.refresh_time = refresh_time or record.refresh_time
    record.retry_time = retry_time or record.retry_time
    record.expire_time = expire_time or record.expire_time
    record.minimum_ttl = minimum_ttl or record.minimum_ttl

    return _add_save_record(client, record, record_type, relative_record_set_name, resource_group_name, private_zone_name, is_list=False)


def remove_privatedns_aaaa_record(client, resource_group_name, private_zone_name, relative_record_set_name, ipv6_address, keep_empty_record_set=False):
    record = AaaaRecord(ipv6_address=ipv6_address)
    record_type = 'aaaa'
    return _remove_record(client, record, record_type, relative_record_set_name, resource_group_name, private_zone_name, keep_empty_record_set=keep_empty_record_set)


def remove_privatedns_a_record(client, resource_group_name, private_zone_name, relative_record_set_name, ipv4_address, keep_empty_record_set=False):
    record = ARecord(ipv4_address=ipv4_address)
    record_type = 'a'
    return _remove_record(client, record, record_type, relative_record_set_name, resource_group_name, private_zone_name, keep_empty_record_set=keep_empty_record_set)


def remove_privatedns_cname_record(client, resource_group_name, private_zone_name, relative_record_set_name, cname, keep_empty_record_set=False):
    record = CnameRecord(cname=cname)
    record_type = 'cname'
    return _remove_record(client, record, record_type, relative_record_set_name, resource_group_name, private_zone_name, is_list=False, keep_empty_record_set=keep_empty_record_set)


def remove_privatedns_mx_record(client, resource_group_name, private_zone_name, relative_record_set_name, preference, exchange, keep_empty_record_set=False):
    record = MxRecord(preference=int(preference), exchange=exchange)
    record_type = 'mx'
    return _remove_record(client, record, record_type, relative_record_set_name, resource_group_name, private_zone_name, keep_empty_record_set=keep_empty_record_set)


def remove_privatedns_ptr_record(client, resource_group_name, private_zone_name, relative_record_set_name, dname, keep_empty_record_set=False):
    record = PtrRecord(ptrdname=dname)
    record_type = 'ptr'
    return _remove_record(client, record, record_type, relative_record_set_name, resource_group_name, private_zone_name, keep_empty_record_set=keep_empty_record_set)


def remove_privatedns_srv_record(client, resource_group_name, private_zone_name, relative_record_set_name, priority, weight, port, target, keep_empty_record_set=False):
    record = SrvRecord(priority=priority, weight=weight, port=port, target=target)
    record_type = 'srv'
    return _remove_record(client, record, record_type, relative_record_set_name, resource_group_name, private_zone_name, keep_empty_record_set=keep_empty_record_set)


def remove_privatedns_txt_record(client, resource_group_name, private_zone_name, relative_record_set_name, value, keep_empty_record_set=False):
    record = TxtRecord(value=value)
    record_type = 'txt'
    return _remove_record(client, record, record_type, relative_record_set_name, resource_group_name, private_zone_name, keep_empty_record_set=keep_empty_record_set)


def _remove_record(client, record, record_type, relative_record_set_name, resource_group_name, private_zone_name, keep_empty_record_set, is_list=True):
    record_set = client.get(resource_group_name, private_zone_name, record_type, relative_record_set_name)
    record_property = _type_to_property_name(record_type)

    if is_list:
        record_list = getattr(record_set, record_property)
        if record_list is not None:
            keep_list = [r for r in record_list
                         if not dict_matches_filter(r.__dict__, record.__dict__)]
            if len(keep_list) == len(record_list):
                raise CLIError('Record {} not found.'.format(str(record)))
            setattr(record_set, record_property, keep_list)
    else:
        setattr(record_set, record_property, None)

    if is_list:
        records_remaining = len(getattr(record_set, record_property))
    else:
        records_remaining = 1 if getattr(record_set, record_property) is not None else 0

    if not records_remaining and not keep_empty_record_set:
        logger.info('Removing empty %s record set: %s', record_type, relative_record_set_name)
        return client.delete(resource_group_name, private_zone_name, record_type, relative_record_set_name)

    return client.create_or_update(resource_group_name, private_zone_name, record_type, relative_record_set_name, record_set)


def dict_matches_filter(d, filter_dict):
    sentinel = object()
    return all(not filter_dict.get(key, None)
               or str(filter_dict[key]) == str(d.get(key, sentinel)) # noqa
               or lists_match(filter_dict[key], d.get(key, [])) for key in filter_dict)  # noqa


def lists_match(l1, l2):
    try:
        return Counter(l1) == Counter(l2)
    except TypeError:
        return False
