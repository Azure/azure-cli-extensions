# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from distutils.version import StrictVersion  # pylint: disable=no-name-in-module,import-error
# pylint: disable=no-name-in-module,import-error
from knack.util import CLIError

# pylint: disable=no-name-in-module,import-error
from .vendored_sdks.azure_mgmt_preview_aks.v2020_11_01.models import ManagedClusterAPIServerAccessProfile
from ._consts import CONST_CONTAINER_NAME_MAX_LENGTH
from ._consts import CONST_OUTBOUND_TYPE_LOAD_BALANCER, CONST_OUTBOUND_TYPE_USER_DEFINED_ROUTING


def _populate_api_server_access_profile(api_server_authorized_ip_ranges, instance=None):
    if instance is None or instance.api_server_access_profile is None:
        profile = ManagedClusterAPIServerAccessProfile()
    else:
        profile = instance.api_server_access_profile

    if api_server_authorized_ip_ranges == "":
        authorized_ip_ranges = []
    else:
        authorized_ip_ranges = [ip.strip() for ip in api_server_authorized_ip_ranges.split(",")]

    profile.authorized_ip_ranges = authorized_ip_ranges
    return profile


def _set_vm_set_type(vm_set_type, kubernetes_version):
    if not vm_set_type:
        if kubernetes_version and StrictVersion(kubernetes_version) < StrictVersion("1.12.9"):
            print('Setting vm_set_type to availabilityset as it is \
            not specified and kubernetes version(%s) less than 1.12.9 only supports \
            availabilityset\n' % (kubernetes_version))
            vm_set_type = "AvailabilitySet"

    if not vm_set_type:
        vm_set_type = "VirtualMachineScaleSets"

    # normalize as server validation is case-sensitive
    if vm_set_type.lower() == "AvailabilitySet".lower():
        vm_set_type = "AvailabilitySet"

    if vm_set_type.lower() == "VirtualMachineScaleSets".lower():
        vm_set_type = "VirtualMachineScaleSets"
    return vm_set_type


def _set_outbound_type(outbound_type, vnet_subnet_id, load_balancer_sku, load_balancer_profile):
    if outbound_type != CONST_OUTBOUND_TYPE_USER_DEFINED_ROUTING:
        return CONST_OUTBOUND_TYPE_LOAD_BALANCER

    if vnet_subnet_id in ["", None]:
        raise CLIError("--vnet-subnet-id must be specified for userDefinedRouting and it must \
        be pre-configured with a route table with egress rules")

    if load_balancer_sku == "basic":
        raise CLIError("userDefinedRouting doesn't support basic load balancer sku")

    if load_balancer_profile:
        if (load_balancer_profile.managed_outbound_ips or
                load_balancer_profile.outbound_ips or
                load_balancer_profile.outbound_ip_prefixes):
            raise CLIError("userDefinedRouting doesn't support customizing a standard load balancer with IP addresses")

    return CONST_OUTBOUND_TYPE_USER_DEFINED_ROUTING


def _parse_comma_separated_list(text):
    if text is None:
        return None
    if text == "":
        return []
    return text.split(",")


def _trim_fqdn_name_containing_hcp(normalized_fqdn: str) -> str:
    """
    Trims the storage blob name and takes everything prior to "-hcp-".
    Currently it is displayed wrong: i.e. at time of creation cli has
    following limitation:
    https://docs.microsoft.com/en-us/azure/azure-resource-manager/templates/
    error-storage-account-name

    :param normalized_fqdn: storage blob name
    :return: storage_name_without_hcp: Storage name without the hcp value
    attached
    """
    storage_name_without_hcp, _, _ = normalized_fqdn.partition('-hcp-')
    if len(storage_name_without_hcp) > CONST_CONTAINER_NAME_MAX_LENGTH:
        storage_name_without_hcp = storage_name_without_hcp[:CONST_CONTAINER_NAME_MAX_LENGTH]
    return storage_name_without_hcp.rstrip('-')


def _fuzzy_match(query, arr):
    """
    will compare all elements in @arr against the @query to see if they are similar

    similar implies one is a substring of the other or the two words are 1 change apart

    Ex. bird and bord are similar
    Ex. bird and birdwaj are similar
    Ex. bird and bead are not similar
    """
    def similar_word(a, b):
        a_len = len(a)
        b_len = len(b)
        if a_len > b_len:  # @a should always be the shorter string
            return similar_word(b, a)
        if a in b:
            return True
        if b_len - a_len > 1:
            return False
        i = 0
        j = 0
        found_difference = False
        while i < a_len:
            if a[i] != b[j]:
                if found_difference:
                    return False
                found_difference = True
                if a_len == b_len:
                    i += 1
                j += 1
            else:
                i += 1
                j += 1
        return True

    matches = []

    for word in arr:
        if similar_word(query, word):
            matches.append(word)

    return matches
