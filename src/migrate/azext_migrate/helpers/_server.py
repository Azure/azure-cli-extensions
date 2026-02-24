# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
import json


def validate_get_discovered_server_params(project_name,
                                          resource_group_name,
                                          source_machine_type):
    """Validate required parameters for get_discovered_server."""
    if not project_name:
        raise CLIError("project_name is required.")
    if not resource_group_name:
        raise CLIError("resource_group_name is required.")
    if source_machine_type and source_machine_type not in ["VMware", "HyperV"]:
        raise CLIError("source_machine_type is not 'VMware' or 'HyperV'.")


def extract_machine_name_from_id(name_or_id):
    """
    Extract the machine name from a full resource ID or return the name as-is.

    Handles formats like:
    - Full ID: /subscriptions/.../Machines/5939691e-5505-4016-b4cd-4fa2d862a975
    - Simple name: 5939691e-5505-4016-b4cd-4fa2d862a975
    """
    if not name_or_id:
        return None

    # If it looks like a full resource ID, extract the machine name
    if name_or_id.startswith('/subscriptions/') or name_or_id.startswith('/Subscriptions/'):
        parts = name_or_id.rstrip('/').split('/')
        # The machine name should be the last part after "machines" or "Machines"
        for i, part in enumerate(parts):
            if part.lower() == 'machines' and i + 1 < len(parts):
                return parts[i + 1]
        # If we can't find machines, return the last segment
        return parts[-1] if parts else name_or_id

    return name_or_id


def build_base_uri(subscription_id, resource_group_name, project_name,
                   appliance_name, name, source_machine_type):
    """Build the base URI for the API request."""
    if appliance_name and name:
        # GetInSite: Get specific machine in specific site
        if source_machine_type == "HyperV":
            return (f"/subscriptions/{subscription_id}"
                    f"/resourceGroups/{resource_group_name}/"
                    f"providers/Microsoft.OffAzure/HyperVSites"
                    f"/{appliance_name}/machines/{name}")
        # VMware or default
        return (f"/subscriptions/{subscription_id}"
                f"/resourceGroups/{resource_group_name}/"
                f"providers/Microsoft.OffAzure/VMwareSites"
                f"/{appliance_name}/machines/{name}")

    if appliance_name:
        # ListInSite: List machines in specific site
        if source_machine_type == "HyperV":
            return (f"/subscriptions/{subscription_id}"
                    f"/resourceGroups/{resource_group_name}/"
                    f"providers/Microsoft.OffAzure/HyperVSites"
                    f"/{appliance_name}/machines")
        # VMware or default
        return (f"/subscriptions/{subscription_id}"
                f"/resourceGroups/{resource_group_name}/"
                f"providers/Microsoft.OffAzure"
                f"/VMwareSites/{appliance_name}/machines")

    if name:
        # Get: Get specific machine from project
        return (f"/subscriptions/{subscription_id}"
                f"/resourceGroups/{resource_group_name}/"
                f"providers/Microsoft.Migrate/migrateprojects"
                f"/{project_name}/machines/{name}")

    # List: List all machines in project
    return (f"/subscriptions/{subscription_id}"
            f"/resourceGroups/{resource_group_name}/"
            f"providers/Microsoft.Migrate/migrateprojects"
            f"/{project_name}/machines")


def fetch_all_servers(cmd, request_uri, send_get_request):
    """Fetch all servers including paginated results."""
    response = send_get_request(cmd, request_uri)
    data = response.json()

    # Handle single item response (when fetching by name/ID)
    # Single items have 'id' and 'properties' at root level, not 'value'
    if 'value' in data:
        values = data.get('value', [])
        while data.get('nextLink'):
            response = send_get_request(cmd, data.get('nextLink'))
            data = response.json()
            values += data.get('value', [])
        return values
    if 'id' in data and 'properties' in data:
        # Single machine response - wrap in list
        return [data]
    return []


def filter_servers_by_display_name(servers, display_name):
    """Filter servers by display name or machine name."""
    filtered = []
    for server in servers:
        properties = server.get('properties', {})

        # Check properties.displayName first
        if properties.get('displayName', '') == display_name:
            filtered.append(server)
            continue

        # Also check discoveryData[0].machineName
        discovery_data = properties.get('discoveryData', [])
        if discovery_data:
            machine_name = discovery_data[0].get('machineName', '')
            if machine_name == display_name:
                filtered.append(server)
    return filtered


# pylint: disable=too-many-locals
def extract_server_info(server, index):
    """Extract server information from discovery data."""
    properties = server.get('properties', {})
    discovery_data = properties.get('discoveryData', [])

    # Default values
    machine_name = "N/A"
    machine_id = server.get('id', 'N/A')
    ip_addresses_str = 'N/A'
    os_name = "N/A"
    boot_type = "N/A"
    os_disk_id = "N/A"

    if discovery_data:
        # Format from Microsoft.Migrate/migrateprojects/machines
        latest_discovery = discovery_data[0]
        machine_name = latest_discovery.get('machineName', 'N/A')
        ip_addresses = latest_discovery.get('ipAddresses', [])
        ip_addresses_str = ', '.join(ip_addresses) if ip_addresses else 'N/A'
        os_name = latest_discovery.get('osName', 'N/A')

        extended_info = latest_discovery.get('extendedInfo', {})
        boot_type = extended_info.get('bootType', 'N/A')

        disk_details_json = extended_info.get('diskDetails', '[]')
        disk_details = json.loads(disk_details_json)
        if disk_details:
            os_disk_id = disk_details[0].get("InstanceId", "N/A")
    else:
        # Format from Microsoft.OffAzure/VMwareSites/machines or HyperVSites/machines
        machine_name = properties.get('displayName', 'N/A')

        # Try to get IP addresses from different locations
        network_adapters = properties.get('networkAdapters', [])
        if network_adapters:
            all_ips = []
            for adapter in network_adapters:
                ips = adapter.get('ipAddressList', [])
                all_ips.extend(ips)
            ip_addresses_str = ', '.join(all_ips) if all_ips else 'N/A'

        # Get OS info from guestOSDetails or operatingSystemDetails
        guest_os = properties.get('guestOSDetails', {})
        if guest_os:
            os_name = guest_os.get('osName', 'N/A')
        else:
            os_details = properties.get('operatingSystemDetails', {})
            os_name = os_details.get('osName', os_details.get('osType', 'N/A'))

        # Get firmware/boot type
        firmware = properties.get('firmware', 'N/A')
        boot_type = firmware.lower() if firmware and firmware != 'N/A' else 'N/A'

        # Get disk info
        disks = properties.get('disks', [])
        if disks:
            os_disk_id = disks[0].get('uuid', disks[0].get('diskId', 'N/A'))

    return {
        'index': index,
        'machine_name': machine_name,
        'machine_id': machine_id,
        'ip_addresses': ip_addresses_str,
        'operating_system': os_name,
        'boot_type': boot_type,
        'os_disk_id': os_disk_id
    }


def print_server_info(server_info):
    """Print formatted server information."""
    index_str = f"[{server_info['index']}]"
    print(f"{index_str} Machine Name: "
          f"{server_info['machine_name']}")
    print(f"{' ' * len(index_str)} Machine Id: "
          f"{server_info['machine_id']}")
    print(f"{' ' * len(index_str)} IP Addresses: "
          f"{server_info['ip_addresses']}")
    print(f"{' ' * len(index_str)} Operating System: "
          f"{server_info['operating_system']}")
    print(f"{' ' * len(index_str)} Boot Type: "
          f"{server_info['boot_type']}")
    print(f"{' ' * len(index_str)} OS Disk ID: "
          f"{server_info['os_disk_id']}")
    print()
