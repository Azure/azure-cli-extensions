# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from distutils.version import StrictVersion  # pylint: disable=no-name-in-module,import-error
# pylint: disable=no-name-in-module,import-error
from knack.util import CLIError

# pylint: disable=no-name-in-module,import-error
from .vendored_sdks.azure_mgmt_preview_aks.v2020_02_01.models import ManagedClusterAPIServerAccessProfile
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


def _set_outbound_type(outbound_type, network_plugin, load_balancer_sku, load_balancer_profile):
    if outbound_type != CONST_OUTBOUND_TYPE_USER_DEFINED_ROUTING:
        return CONST_OUTBOUND_TYPE_LOAD_BALANCER

    if load_balancer_sku == "basic":
        raise CLIError("userDefinedRouting doesn't support basic load balancer sku")

    if load_balancer_profile:
        if (load_balancer_profile.managed_outbound_ips or
                load_balancer_profile.outbound_ips or
                load_balancer_profile.outbound_ip_prefixes):
            raise CLIError("userDefinedRouting doesn't support customizing a standard load balancer with IP addresses")

    if network_plugin != "azure":
        raise CLIError("userDefinedRouting requires --network-plugin to be azure")

    return CONST_OUTBOUND_TYPE_USER_DEFINED_ROUTING
