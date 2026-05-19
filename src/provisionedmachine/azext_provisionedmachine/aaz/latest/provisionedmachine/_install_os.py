# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: skip-file
# flake8: noqa

from azure.cli.core.aaz import *


@register_command(
    "provisionedmachine install-os",
    is_preview=True,
)
class InstallOs(AAZCommand):
    """Install Operating System on a specific Provisioned Machine resource.

    :example: Install AzureLinux Operating System on a provisioned machine
        az provisionedmachine install-os -g myResourceGroup -n myProvisionedMachine --os-image AzureLinux --version 3.0 --ssh-public-key "ssh-rsa AAAAB3..."

    """

    _aaz_info = {
        "version": "2025-12-01-preview",
        "resources": [
            ["mgmt-plane", "/subscriptions/{}/resourcegroups/{}/providers/microsoft.azurestackhci/edgemachines/{}/jobs/ProvisionOs", "2025-12-01-preview"],
        ]
    }

    AZ_SUPPORT_NO_WAIT = True

    def _handler(self, command_args):
        super()._handler(command_args)
        return self.build_lro_poller(self._execute_operations, self._output)

    _args_schema = None

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        if cls._args_schema is not None:
            return cls._args_schema
        cls._args_schema = super()._build_arguments_schema(*args, **kwargs)

        _args_schema = cls._args_schema

        # Define Arg Group "" (default - Resource identifiers)
        _args_schema.edge_machine_name = AAZStrArg(
            options=["-n", "--name", "--provisioned-machine-name"],
            help="Name of the provisioned machine. Must be 4-128 characters, start and end with alphanumeric, and contain only alphanumeric characters and hyphens.",
            required=True,
            fmt=AAZStrArgFormat(
                pattern="^[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]$",
                max_length=128,
                min_length=4,
            ),
        )
        _args_schema.resource_group = AAZResourceGroupNameArg(
            required=True,
        )

        # Define Arg Group "OS Configuration"
        _args_schema.os_image = AAZStrArg(
            options=["--os-image"],
            arg_group="OS Configuration",
            help="Name of the OS image for this provisioned machine. Allowed values: HCI, AzureLinux.",
            enum={"HCI": "HCI", "AzureLinux": "AzureLinux"},
            required=True,
        )
        _args_schema.version = AAZStrArg(
            options=["-v", "--version"],
            arg_group="OS Configuration",
            help="Version string. Required for HCI (VSR version). Optional for AzureLinux (OS version, defaults to 3.0).",
        )

        # Define Arg Group "Authentication"
        _args_schema.ssh_public_key = AAZStrArg(
            options=["--ssh-public-key"],
            arg_group="Authentication",
            help="SSH public key for the machine. Required for AzureLinux OS image.",
        )
        _args_schema.key_vault_secret_id = AAZStrArg(
            options=["--key-vault-secret-id", "--kv-secret-id"],
            arg_group="Authentication",
            help="Key Vault secret ID for user credentials. Required for HCI OS image.",
        )

        # Define Arg Group "Network"
        _args_schema.hostname = AAZStrArg(
            options=["--hostname"],
            arg_group="Network",
            help="Hostname for the machine. Defaults to provisioned machine name if not provided.",
        )
        _args_schema.ip_address = AAZStrArg(
            options=["--ip-address"],
            arg_group="Network",
            help="IP address for the management NIC.",
        )
        _args_schema.subnet_mask = AAZStrArg(
            options=["--subnet-mask"],
            arg_group="Network",
            help="Subnet mask for the machine.",
        )
        _args_schema.gateway = AAZStrArg(
            options=["--gateway"],
            arg_group="Network",
            help="Gateway IP address.",
        )
        _args_schema.dns_servers = AAZListArg(
            options=["--dns-servers"],
            arg_group="Network",
            help="Space-separated list of DNS server IP addresses.",
        )
        _args_schema.dns_servers.Element = AAZStrArg()
        _args_schema.vlan_id = AAZStrArg(
            options=["--vlan-id"],
            arg_group="Network",
            help="VLAN ID assignment.",
        )

        # Define Arg Group "Time"
        _args_schema.ntp_server = AAZStrArg(
            options=["--ntp-server"],
            arg_group="Time",
            help="NTP server IP address.",
        )
        _args_schema.timezone = AAZStrArg(
            options=["--timezone"],
            arg_group="Time",
            help="Timezone for this machine.",
        )

        # Define Arg Group "Proxy"
        _args_schema.proxy_settings = AAZStrArg(
            options=["--proxy-settings"],
            arg_group="Proxy",
            help="Proxy configuration for outbound connectivity. Format: http=<url>,https=<url>,noProxy=[list]",
        )

        return cls._args_schema

    def _execute_operations(self):
        self.pre_operations()
        yield self.EdgeMachinesJobsProvisionOs(ctx=self.ctx)()
        self.post_operations()

    @register_callback
    def pre_operations(self):
        from azure.cli.core.azclierror import RequiredArgumentMissingError

        # Validate machine state first
        self._validate_machine_state()

        args = self.ctx.args
        os_image = args.os_image.to_serialized_data()

        if os_image == "AzureLinux":
            # AzureLinux requires: os-image + ssh-public-key
            ssh_key = args.ssh_public_key.to_serialized_data() if has_value(args.ssh_public_key) else None
            if not ssh_key:
                raise RequiredArgumentMissingError(
                    "SSH public key (--ssh-public-key) is required when using AzureLinux OS image."
                )
        elif os_image == "HCI":
            # HCI requires: os-image + version + key-vault-secret-id
            version = args.version.to_serialized_data() if has_value(args.version) else None
            if not version:
                raise RequiredArgumentMissingError(
                    "Version (--version) is required when using HCI OS image."
                )
            kv_secret = args.key_vault_secret_id.to_serialized_data() if has_value(args.key_vault_secret_id) else None
            if not kv_secret:
                raise RequiredArgumentMissingError(
                    "Key Vault secret ID (--key-vault-secret-id) is required when using HCI OS image."
                )
            # Validate Key Vault secret ID format
            self._validate_key_vault_secret_id(kv_secret)

        # Validate IP address format
        if has_value(args.ip_address):
            ip_address = args.ip_address.to_serialized_data()
            self._validate_ipv4_address(ip_address, "--ip-address")

        # Validate subnet mask format
        if has_value(args.subnet_mask):
            subnet_mask = args.subnet_mask.to_serialized_data()
            self._validate_subnet_mask(subnet_mask)

        # Validate gateway format
        if has_value(args.gateway):
            gateway = args.gateway.to_serialized_data()
            self._validate_ipv4_address(gateway, "--gateway")
            
            # Validate gateway is within the subnet (if ip_address and subnet_mask are provided)
            if has_value(args.ip_address) and has_value(args.subnet_mask):
                ip_address = args.ip_address.to_serialized_data()
                subnet_mask = args.subnet_mask.to_serialized_data()
                self._validate_gateway_in_subnet(gateway, ip_address, subnet_mask)

        # Validate DNS servers
        if has_value(args.dns_servers):
            dns_servers = args.dns_servers.to_serialized_data()
            if dns_servers:
                for dns_server in dns_servers:
                    self._validate_ipv4_address(dns_server, "--dns-servers")

        # Validate VLAN ID
        if has_value(args.vlan_id):
            vlan_id = args.vlan_id.to_serialized_data()
            self._validate_vlan_id(vlan_id)

        # Validate NTP server (IP address or hostname)
        if has_value(args.ntp_server):
            ntp_server = args.ntp_server.to_serialized_data()
            self._validate_ntp_server(ntp_server)

        # Validate hostname format
        if has_value(args.hostname):
            hostname = args.hostname.to_serialized_data()
            self._validate_hostname(hostname)

    def _validate_machine_state(self):
        """Validate that the provisioned machine is in 'Unpurposed' or 'Transitioning' state before install-os."""
        from azure.cli.core.util import send_raw_request
        from azure.cli.core.azclierror import InvalidArgumentValueError
        import logging

        logger = logging.getLogger(__name__)
        args = self.ctx.args
        allowed_states = ['Unpurposed', 'Transitioning']

        try:
            url = (
                f"/subscriptions/{self.ctx.subscription_id}"
                f"/resourceGroups/{args.resource_group.to_serialized_data()}"
                f"/providers/Microsoft.AzureStackHCI/edgeMachines/{args.edge_machine_name.to_serialized_data()}"
                f"?api-version=2025-12-01-preview"
            )

            response = send_raw_request(self.ctx.cli_ctx, "GET", url)

            if response.status_code == 200:
                data = response.json()
                machine_state = data.get('properties', {}).get('machineState', '')
                
                if machine_state not in allowed_states:
                    raise InvalidArgumentValueError(
                        f"Cannot install OS on provisioned machine '{args.edge_machine_name.to_serialized_data()}'. "
                        f"Machine is in '{machine_state}' state. Install-os is only allowed when machine is in 'Unpurposed' or 'Transitioning' state."
                    )
                logger.info("Machine state validated: %s", machine_state)
            else:
                raise InvalidArgumentValueError(
                    f"Failed to get provisioned machine '{args.edge_machine_name.to_serialized_data()}': HTTP {response.status_code}"
                )

        except InvalidArgumentValueError:
            raise
        except Exception as e:
            raise InvalidArgumentValueError(
                f"Error validating machine state: {str(e)}"
            )

    def _validate_ipv4_address(self, ip_address, param_name):
        """Validate IPv4 address format."""
        import ipaddress as ipaddr
        from azure.cli.core.azclierror import InvalidArgumentValueError
        
        try:
            ipaddr.IPv4Address(ip_address)
        except ValueError:
            raise InvalidArgumentValueError(
                f"Invalid IPv4 address format for {param_name}: '{ip_address}'. Expected format: x.x.x.x (e.g., 192.168.1.1)"
            )

    def _validate_subnet_mask(self, subnet_mask):
        """Validate subnet mask format."""
        import ipaddress as ipaddr
        from azure.cli.core.azclierror import InvalidArgumentValueError
        
        try:
            # First check if it's a valid IPv4 address
            ipaddr.IPv4Address(subnet_mask)
            
            # Convert to integer and check if it's a valid subnet mask (contiguous 1s followed by 0s)
            mask_int = int(ipaddr.IPv4Address(subnet_mask))

            if mask_int == 0 or mask_int == 0xFFFFFFFF:
                raise InvalidArgumentValueError(
                    f"Invalid subnet mask: '{subnet_mask}'. Subnet mask cannot be all 0s or all 1s."
                )

            # A valid subnet mask in binary should be all 1s followed by all 0s
            # When we add 1 to the inverted mask, it should be a power of 2
            inverted = ~mask_int & 0xFFFFFFFF
            if (inverted & (inverted + 1)) != 0:
                raise InvalidArgumentValueError(
                    f"Invalid subnet mask: '{subnet_mask}'. Must be a valid subnet mask (e.g., 255.255.255.0, 255.255.0.0)"
                )
        except ValueError:
            raise InvalidArgumentValueError(
                f"Invalid subnet mask format: '{subnet_mask}'. Expected format: x.x.x.x (e.g., 255.255.255.0)"
            )

    def _validate_gateway_in_subnet(self, gateway, ip_address, subnet_mask):
        """Validate that the gateway is within the subnet defined by ip_address and subnet_mask."""
        import ipaddress as ipaddr
        from azure.cli.core.azclierror import InvalidArgumentValueError
        
        try:
            ip = ipaddr.IPv4Address(ip_address)
            gw = ipaddr.IPv4Address(gateway)
            network = ipaddr.IPv4Network(f"{ip_address}/{subnet_mask}", strict=False)
        except ipaddr.AddressValueError:
            raise InvalidArgumentValueError(
                "Invalid IP/Subnet/Gateway format"
            )

        # Must be in subnet
        if gw not in network:
            raise InvalidArgumentValueError(
                f"Gateway '{gateway}' is not in the same subnet as IP '{ip_address}' "
                f"(subnet: {network})"
            )

        # Cannot be network address
        if gw == network.network_address:
            raise InvalidArgumentValueError(
                f"Gateway '{gateway}' cannot be network address"
            )

        # Cannot be broadcast address
        if gw == network.broadcast_address:
            raise InvalidArgumentValueError(
                f"Gateway '{gateway}' cannot be broadcast address"
            )

        # Cannot be same as host IP
        if gw == ip:
            raise InvalidArgumentValueError(
                f"Gateway '{gateway}' cannot be same as host IP"
            )

    def _validate_vlan_id(self, vlan_id):
        """Validate VLAN ID (1-4094)."""
        from azure.cli.core.azclierror import InvalidArgumentValueError
        
        try:
            vlan_num = int(vlan_id)
            if vlan_num < 1 or vlan_num > 4094:
                raise InvalidArgumentValueError(
                    f"Invalid VLAN ID: '{vlan_id}'. VLAN ID must be between 1 and 4094."
                )
        except ValueError:
            raise InvalidArgumentValueError(
                f"Invalid VLAN ID: '{vlan_id}'. VLAN ID must be a numeric value between 1 and 4094."
            )

    def _validate_ntp_server(self, ntp_server):
        """Validate NTP server (IP address or hostname)."""
        import ipaddress as ipaddr
        import re
        from azure.cli.core.azclierror import InvalidArgumentValueError
        
        if not ntp_server:
            raise InvalidArgumentValueError("NTP server cannot be empty.")

        # Accept IPv4 / IPv6
        try:
            ipaddr.ip_address(ntp_server)
            return
        except ValueError:
            pass

        # Max hostname length
        if len(ntp_server) > 253:
            raise InvalidArgumentValueError(
                f"Invalid NTP server '{ntp_server}'. Hostname exceeds 253 characters."
            )

        # Reject double dots
        if ".." in ntp_server:
            raise InvalidArgumentValueError(
                f"Invalid NTP server '{ntp_server}'. Contains empty label."
            )

        # RFC-1123 hostname
        pattern = (
            r'^[A-Za-z0-9]'
            r'([A-Za-z0-9\-]{0,61}[A-Za-z0-9])?'
            r'(\.[A-Za-z0-9]'
            r'([A-Za-z0-9\-]{0,61}[A-Za-z0-9])?)*$'
        )

        if not re.fullmatch(pattern, ntp_server):
            raise InvalidArgumentValueError(
                f"Invalid NTP server '{ntp_server}'. Must be valid IP or hostname."
            )

    def _validate_hostname(self, hostname):
        """Validate hostname format."""
        import re
        import ipaddress as ipaddr
        from azure.cli.core.azclierror import InvalidArgumentValueError
        
        if not hostname or len(hostname) > 253:
            raise InvalidArgumentValueError("Invalid hostname length.")

        # Reject IPv4 input
        try:
            ipaddr.IPv4Address(hostname)
            raise InvalidArgumentValueError("Hostname cannot be an IP address.")
        except ipaddr.AddressValueError:
            pass

        if ".." in hostname:
            raise InvalidArgumentValueError("Hostname contains empty label.")

        pattern = r'^[A-Za-z0-9]([A-Za-z0-9\-]{0,61}[A-Za-z0-9])?(\.[A-Za-z0-9]([A-Za-z0-9\-]{0,61}[A-Za-z0-9])?)*$'

        if not re.fullmatch(pattern, hostname):
            raise InvalidArgumentValueError("Invalid hostname format.")

    def _validate_key_vault_secret_id(self, secret_id):
        """Validate Key Vault secret ID format."""
        import re
        from azure.cli.core.azclierror import InvalidArgumentValueError
        
        # Format: /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.KeyVault/vaults/{vault}/secrets/{secret}
        kv_pattern = r'^/subscriptions/[a-fA-F0-9-]+/resourceGroups/[^/]+/providers/Microsoft\.KeyVault/vaults/[^/]+/secrets/[^/]+(/[^/]+)?$'
        if not re.match(kv_pattern, secret_id, re.IGNORECASE):
            raise InvalidArgumentValueError(
                "Invalid Key Vault secret ID format. Expected format: "
                "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroup}/providers/Microsoft.KeyVault/vaults/{vaultName}/secrets/{secretName}"
            )

    @register_callback
    def post_operations(self):
        pass

    def _output(self, *args, **kwargs):
        return self.ctx.vars.instance

    class EdgeMachinesJobsProvisionOs(AAZHttpOperation):
        CLIENT_TYPE = "MgmtClient"

        def __call__(self, *args, **kwargs):
            request = self.make_request()
            session = self.client.send_request(request=request, stream=False, **kwargs)
            if session.http_response.status_code in [202]:
                return self.client.build_lro_polling(
                    self.ctx.args.no_wait,
                    session,
                    self.on_200_201,
                    self.on_error,
                    lro_options={"final-state-via": "azure-async-operation"},
                    path_format_arguments=self.url_parameters,
                )
            if session.http_response.status_code in [200, 201]:
                return self.client.build_lro_polling(
                    self.ctx.args.no_wait,
                    session,
                    self.on_200_201,
                    self.on_error,
                    lro_options={"final-state-via": "azure-async-operation"},
                    path_format_arguments=self.url_parameters,
                )

            return self.on_error(session.http_response)

        @property
        def url(self):
            return self.client.format_url(
                "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.AzureStackHCI/edgeMachines/{edgeMachineName}/jobs/ProvisionOs",
                **self.url_parameters
            )

        @property
        def method(self):
            return "PUT"

        @property
        def error_format(self):
            return "MgmtErrorFormat"

        @property
        def url_parameters(self):
            parameters = {
                **self.serialize_url_param(
                    "subscriptionId", self.ctx.subscription_id,
                    required=True,
                ),
                **self.serialize_url_param(
                    "resourceGroupName", self.ctx.args.resource_group,
                    required=True,
                ),
                **self.serialize_url_param(
                    "edgeMachineName", self.ctx.args.edge_machine_name,
                    required=True,
                ),
            }
            return parameters

        @property
        def query_parameters(self):
            parameters = {
                **self.serialize_query_param(
                    "api-version", "2025-12-01-preview",
                    required=True,
                ),
            }
            return parameters

        @property
        def header_parameters(self):
            parameters = {
                **self.serialize_header_param(
                    "Content-Type", "application/json",
                ),
                **self.serialize_header_param(
                    "Accept", "application/json",
                ),
            }
            return parameters

        @property
        def content(self):
            args = self.ctx.args

            # Get values from args
            edge_machine_name = args.edge_machine_name.to_serialized_data()
            os_image = args.os_image.to_serialized_data()

            # Build network adapter configuration
            # Auto-determine IP allocation method: Manual if ip_address, subnet_mask, and gateway are all provided
            has_ip = has_value(args.ip_address)
            has_subnet = has_value(args.subnet_mask)
            has_gateway = has_value(args.gateway)
            
            if has_ip and has_subnet and has_gateway:
                ip_assignment_type = "Manual"
            else:
                ip_assignment_type = "Automatic"
            
            network_adapter = {
                "ipAssignmentType": ip_assignment_type
            }

            if has_ip:
                network_adapter["ipAddress"] = args.ip_address.to_serialized_data()

            if has_gateway:
                network_adapter["gateway"] = args.gateway.to_serialized_data()

            if has_subnet:
                network_adapter["subnetMask"] = args.subnet_mask.to_serialized_data()

            if has_value(args.dns_servers):
                network_adapter["dnsAddressArray"] = args.dns_servers.to_serialized_data()

            if has_value(args.vlan_id):
                network_adapter["vlanId"] = args.vlan_id.to_serialized_data()

            # Build time configuration
            time_config = None
            if has_value(args.ntp_server) or has_value(args.timezone):
                time_config = {}
                if has_value(args.ntp_server):
                    time_config["primaryTimeServer"] = args.ntp_server.to_serialized_data()
                if has_value(args.timezone):
                    time_config["timeZone"] = args.timezone.to_serialized_data()

            # Build web proxy configuration (None if not provided)
            web_proxy = None
            if has_value(args.proxy_settings):
                web_proxy = {}
                proxy_str = args.proxy_settings.to_serialized_data()
                # Parse proxy settings string like: http=url,https=url,noProxy=[list]
                for part in proxy_str.split(","):
                    if "=" in part:
                        key, value = part.split("=", 1)
                        web_proxy[key.strip()] = value.strip()

            # Build device configuration
            hostname = args.hostname.to_serialized_data() if has_value(args.hostname) else edge_machine_name
            device_configuration = {
                "network": {
                    "networkAdapters": [network_adapter]
                },
                "hostName": hostname,
                "webProxy": web_proxy,
                "time": time_config
            }

            # Build provisioning request based on OS image type
            if os_image == "HCI":
                os_profile = {
                    "osType": "HCI"
                }
                if has_value(args.version):
                    os_profile["vsrVersion"] = args.version.to_serialized_data()

                user_details = [
                    {
                        "userName": "admin",
                        "secretType": "KeyVault",
                        "secretLocation": args.key_vault_secret_id.to_serialized_data()
                    }
                ]

                provisioning_request = {
                    "target": "HCI",
                    "osProfile": os_profile,
                    "userDetails": user_details,
                    "deviceConfiguration": device_configuration
                }

            elif os_image == "AzureLinux":
                os_version = args.version.to_serialized_data() if has_value(args.version) else "3.0"

                os_profile = {
                    "osName": "AzureLinux",
                    "osType": "AzureLinux",
                    "osVersion": os_version,
                    "osImageLocation": "https://aka.ms/aep/sff/azurelinux/2604a"
                }

                user_details = [
                    {
                        "userName": "admin",
                        "secretType": "SshPubKey",
                        "sshPubKey": [args.ssh_public_key.to_serialized_data()]
                    }
                ]

                provisioning_request = {
                    "target": "AzureLinux",
                    "osProfile": os_profile,
                    "userDetails": user_details,
                    "deviceConfiguration": device_configuration
                }

            # Build the full payload
            payload = {
                "properties": {
                    "jobType": "ProvisionOs",
                    "deploymentMode": "Deploy",
                    "provisioningRequest": provisioning_request
                }
            }

            return payload

        def on_200_201(self, session):
            data = self.deserialize_http_content(session)
            self.ctx.set_var("instance", data, schema_builder=lambda: AAZAnyType())
