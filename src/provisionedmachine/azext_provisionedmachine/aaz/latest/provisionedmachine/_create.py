# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: skip-file
# flake8: noqa

import base64
import os
import re
from azure.cli.core.aaz import *


@register_command(
    "provisionedmachine create",
    is_preview=True,
)
class Create(AAZCommand):
    """Create a Provisioned Machine resource.

    :example: Create an AzureLinux provisioned machine
        az provisionedmachine create -g myResourceGroup -n myProvisionedMachine -l eastus --site-resource-id /subscriptions/.../sites/mySite --os-image AzureLinux --version 3.0 --ownership-voucher /path/to/voucher.pem --ssh-public-key "ssh-rsa AAAAB3..."
    """

    _aaz_info = {
        "version": "2025-12-01-preview",
        "resources": [
            ["mgmt-plane", "/subscriptions/{}/resourcegroups/{}/providers/microsoft.azurestackhci/edgemachines/{}", "2025-12-01-preview"],
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
        _args_schema.location = AAZResourceLocationArg(
            options=["-l", "--location"],
            help="The geo-location for the resource.",
            required=True,
            fmt=AAZResourceLocationArgFormat(
                resource_group_arg="resource_group",
            ),
        )
        _args_schema.tags = AAZDictArg(
            options=["--tags"],
            help="Resource tags. Format: key1=value1 key2=value2",
        )
        _args_schema.tags.Element = AAZStrArg()

        # Define Arg Group "Provisioning"
        _args_schema.ownership_voucher = AAZStrArg(
            options=["--ownership-voucher", "--ov"],
            arg_group="Provisioning",
            help="Path to the ownership voucher PEM file for the provisioned machine.",
            required=True,
        )
        _args_schema.site_resource_id = AAZStrArg(
            options=["--site-resource-id"],
            arg_group="Provisioning",
            help="The resource ID of the site.",
            required=True,
        )

        # Define Arg Group "OS Configuration"
        _args_schema.os_image = AAZStrArg(
            options=["--os-image"],
            arg_group="OS Configuration",
            help="Name of the OS image for this provisioned machine. Allowed values: HCI, AzureLinux.",
            enum={"HCI": "HCI", "AzureLinux": "AzureLinux"},
        )
        _args_schema.version = AAZStrArg(
            options=["-v", "--version"],
            arg_group="OS Configuration",
            help="Version string. Required for HCI (VSR version). Optional for AzureLinux (OS version).",
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

        # Define Arg Group "Arc"
        _args_schema.arc_gateway_resource_id = AAZStrArg(
            options=["--arc-gateway-resource-id"],
            arg_group="Arc Gateway",
            help="The resource ID of the Arc gateway.",
        )

        return cls._args_schema

    def _execute_operations(self):
        self.pre_operations()
        # First validate the ownership voucher
        self.ValidateOwnershipVoucher(ctx=self.ctx)()
        self._validate_voucher_response()
        # If validation passed, proceed with create
        yield self.EdgeMachinesCreateOrUpdate(ctx=self.ctx)()
        #self.post_operations()

    # Store validation result as class variable
    _validation_result = None

    def _validate_voucher_response(self):
        """Check the validation response and raise error if invalid."""
        from azure.cli.core.azclierror import InvalidArgumentValueError
        
        validation_result = Create._validation_result
        if validation_result:
            details = validation_result.get("ownershipVoucherValidationDetails", [])
            for detail in details:
                status = detail.get("validationStatus", "")
                if status.lower() == "invalid":
                    error_info = detail.get("error", {})
                    error_message = error_info.get("message", "Unknown error")
                    error_details = error_info.get("details", [])
                    
                    # Build detailed error message
                    full_message = f"Ownership voucher validation failed: {error_message}"
                    if error_details:
                        for err_detail in error_details:
                            full_message += f"\n  - {err_detail.get('code', '')}: {err_detail.get('message', '')}"
                    
                    raise InvalidArgumentValueError(full_message)

    @register_callback
    def pre_operations(self):
        from azure.cli.core.azclierror import FileOperationError, InvalidArgumentValueError, RequiredArgumentMissingError, MutuallyExclusiveArgumentError

        args = self.ctx.args

        # Validate ownership voucher file
        file_path = args.ownership_voucher.to_serialized_data()
        if not os.path.exists(file_path):
            raise FileOperationError(f"The specified ownership voucher file '{file_path}' does not exist.")
        
        if not os.path.isfile(file_path):
            raise FileOperationError(f"The specified path '{file_path}' is not a file.")

        # Read and encode the ownership voucher file
        try:
            with open(file_path, "rb") as f:
                file_content = f.read()
        except PermissionError:
            raise FileOperationError(f"Permission denied: Unable to read the file '{file_path}'.")
        except IOError as e:
            raise FileOperationError(f"Error reading file '{file_path}': {str(e)}")

        if len(file_content) == 0:
            raise InvalidArgumentValueError(f"The specified file '{file_path}' is empty.")

        # Validate site-resource-id format
        site_resource_id = args.site_resource_id.to_serialized_data() if has_value(args.site_resource_id) else None
        if site_resource_id:
            self._validate_resource_id(site_resource_id, "--site-resource-id")

        # Validate arc-gateway-resource-id format if provided
        if has_value(args.arc_gateway_resource_id):
            arc_gateway_id = args.arc_gateway_resource_id.to_serialized_data()
            self._validate_resource_id(arc_gateway_id, "--arc-gateway-resource-id")


        has_ssh_key = has_value(args.ssh_public_key) and args.ssh_public_key.to_serialized_data()
        has_kv_secret = has_value(args.key_vault_secret_id) and args.key_vault_secret_id.to_serialized_data()
        

        # Validate OS image specific requirements (only if os_image is provided)
        if has_value(args.os_image):
            os_image = args.os_image.to_serialized_data()
            
            if os_image == "AzureLinux":
                # AzureLinux requires: os-image + ssh-public-key (version is optional)
                if not has_ssh_key:
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
                if not has_kv_secret:
                    raise RequiredArgumentMissingError(
                        "Key Vault secret ID (--key-vault-secret-id) is required when using HCI OS image."
                    )
                # Validate Key Vault secret ID format
                kv_secret = args.key_vault_secret_id.to_serialized_data()
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


    def _validate_resource_id(self, resource_id, param_name):
        """Validate Azure resource ID format."""
        from azure.cli.core.azclierror import InvalidArgumentValueError
        from azure.mgmt.core.tools import is_valid_resource_id
        
        if not is_valid_resource_id(resource_id):
            raise InvalidArgumentValueError(
                f"Invalid resource ID format for {param_name}. "
                f"Expected format: /subscriptions/{{subscriptionId}}/resourceGroups/{{resourceGroup}}/providers/{{provider}}/..."
            )

    def _validate_key_vault_secret_id(self, secret_id):
        """Validate Key Vault secret ID format."""
        from azure.cli.core.azclierror import InvalidArgumentValueError
        
        # Format: /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.KeyVault/vaults/{vault}/secrets/{secret}
        kv_pattern = r'^/subscriptions/[a-fA-F0-9-]+/resourceGroups/[^/]+/providers/Microsoft\.KeyVault/vaults/[^/]+/secrets/[^/]+(/[^/]+)?$'
        if not re.match(kv_pattern, secret_id, re.IGNORECASE):
            raise InvalidArgumentValueError(
                "Invalid Key Vault secret ID format. Expected format: "
                "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroup}/providers/Microsoft.KeyVault/vaults/{vaultName}/secrets/{secretName}"
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

    @register_callback
    def post_operations(self):
        """Assign roles to the provisioned machine identity if HCI."""
        import time
        
        args = self.ctx.args
        
        # Only assign roles when HCI OS image is specified
        if not has_value(args.os_image):
            return
        
        os_image = args.os_image.to_serialized_data()
        if os_image != "HCI":
            return
        
        # Get the principal ID by fetching the edge machine
        principal_id = self._get_edge_machine_principal_id()
        
        if not principal_id:
            from knack.log import get_logger
            logger = get_logger(__name__)
            logger.warning("Could not retrieve principal ID from edge machine. Skipping role assignments.")
            return
        
        # Initial delay to allow Azure AD replication of the newly created managed identity
        from knack.log import get_logger
        logger = get_logger(__name__)
        logger.info("Waiting 30 seconds for managed identity to replicate to Azure AD...")
        time.sleep(30)
        
        # Role definition IDs
        # Role Based Access Control Administrator - allows managing RBAC role assignments
        RBAC_ADMIN_ROLE = "f58310d9-a9f6-439a-9e8d-f62e7b41a168"
        
        # 1. RBAC Administrator role assignment scoped to Resource Group
        # Condition allows constrained delegation for Azure Connected Machine Resource Manager role only
        resource_group_scope = f"/subscriptions/{self.ctx.subscription_id}/resourceGroups/{args.resource_group.to_serialized_data()}"
        
        rg_condition = (
            "((!(ActionMatches{'Microsoft.Authorization/roleAssignments/write'})) "
            "OR (@Request[Microsoft.Authorization/roleAssignments:RoleDefinitionId] "
            "ForAnyOfAnyValues:GuidEquals {cd570a14-e51a-42ad-bac8-bafd67325302})) "
            "AND ((!(ActionMatches{'Microsoft.Authorization/roleAssignments/delete'})) "
            "OR (@Resource[Microsoft.Authorization/roleAssignments:RoleDefinitionId] "
            "ForAnyOfAnyValues:GuidEquals {cd570a14-e51a-42ad-bac8-bafd67325302}))"
        )
        
        self._create_role_assignment(
            scope=resource_group_scope,
            principal_id=principal_id,
            role_definition_id=RBAC_ADMIN_ROLE,
            role_name="Role Based Access Control Administrator (Resource Group)",
            condition=rg_condition,
            condition_version="2.0"
        )
        
        # 2. RBAC Administrator role assignment scoped to Key Vault
        # Condition allows constrained delegation for Key Vault Administrator role only
        kv_secret_id = args.key_vault_secret_id.to_serialized_data()
        
        # Parse to get the Key Vault scope (remove /secrets/{secretName} part)
        kv_scope_match = re.match(
            r'(/subscriptions/[^/]+/resourceGroups/[^/]+/providers/Microsoft\.KeyVault/vaults/[^/]+)',
            kv_secret_id,
            re.IGNORECASE
        )
        
        if kv_scope_match:
            kv_scope = kv_scope_match.group(1)
            
            kv_condition = (
                "((!(ActionMatches{'Microsoft.Authorization/roleAssignments/write'})) "
                "OR (@Request[Microsoft.Authorization/roleAssignments:RoleDefinitionId] "
                "ForAnyOfAnyValues:GuidEquals {4633458b-17de-408a-b874-0445c86b69e6})) "
                "AND ((!(ActionMatches{'Microsoft.Authorization/roleAssignments/delete'})) "
                "OR (@Resource[Microsoft.Authorization/roleAssignments:RoleDefinitionId] "
                "ForAnyOfAnyValues:GuidEquals {4633458b-17de-408a-b874-0445c86b69e6}))"
            )
            
            self._create_role_assignment(
                scope=kv_scope,
                principal_id=principal_id,
                role_definition_id=RBAC_ADMIN_ROLE,
                role_name="Role Based Access Control Administrator (Key Vault)",
                condition=kv_condition,
                condition_version="2.0"
            )
        else:
            from knack.log import get_logger
            logger = get_logger(__name__)
            logger.warning("Could not parse Key Vault scope from secret ID. Skipping Key Vault role assignment.")

    def _create_role_assignment(self, scope, principal_id, role_definition_id, role_name, condition=None, condition_version=None):
        """Create role assignment with retry for service principal replication delay."""
        import time
        from knack.log import get_logger
        from azure.cli.command_modules.role.custom import list_role_assignments, create_role_assignment
        
        logger = get_logger(__name__)
        max_retries = 12  # 12 retries
        retry_delay = 15  # 15 seconds between retries = up to 3 minutes total wait
        
        for attempt in range(max_retries):
            try:
                # Check if role assignment already exists
                existing_assignments = list_role_assignments(
                    self,
                    assignee=principal_id,
                    role=role_definition_id,
                    scope=scope
                )
                
                if existing_assignments:
                    logger.info("%s role assignment already exists for principal %s", role_name, principal_id)
                    return
                
                # Create the role assignment
                logger.info("Creating %s role assignment for principal %s on scope %s (attempt %d/%d)", 
                           role_name, principal_id, scope, attempt + 1, max_retries)
                
                create_kwargs = {
                    'role': role_definition_id,
                    'assignee_object_id': principal_id,
                    'scope': scope,
                    'assignee_principal_type': 'ServicePrincipal'
                }
                
                if condition:
                    create_kwargs['condition'] = condition
                if condition_version:
                    create_kwargs['condition_version'] = condition_version
                
                create_role_assignment(self, **create_kwargs)
                logger.info("Successfully created %s role assignment", role_name)
                return
                
            except Exception as e:
                error_msg = str(e)
                # Check if it's a replication delay issue
                if "Cannot find user or service principal in graph database" in error_msg:
                    if attempt < max_retries - 1:
                        logger.info(
                            "Service principal not yet replicated. Waiting %d seconds before retry... (attempt %d/%d)",
                            retry_delay, attempt + 1, max_retries
                        )
                        time.sleep(retry_delay)
                        continue
                
                # Final attempt failed or different error
                logger.warning(
                    "Failed to create %s role assignment: %s. "
                    "You may need to manually assign the role using: "
                    "az role assignment create --assignee-object-id %s --assignee-principal-type ServicePrincipal "
                    "--role '%s' --scope %s --condition \"<condition>\" --condition-version 2.0",
                    role_name, error_msg, principal_id, role_definition_id, scope
                )
                return

    def _get_edge_machine_principal_id(self):
        """Fetch the edge machine to get its principal ID."""
        from azure.cli.core.util import send_raw_request
        from knack.log import get_logger
        
        logger = get_logger(__name__)
        args = self.ctx.args
        
        try:
            # Build the GET URL for the edge machine
            url = (
                f"/subscriptions/{self.ctx.subscription_id}"
                f"/resourceGroups/{args.resource_group.to_serialized_data()}"
                f"/providers/Microsoft.AzureStackHCI/edgeMachines/{args.edge_machine_name.to_serialized_data()}"
                f"?api-version=2025-12-01-preview"
            )
            
            # Make GET request using ctx.cli_ctx
            response = send_raw_request(self.ctx.cli_ctx, "GET", url)
            
            if response.status_code == 200:
                data = response.json()
                identity = data.get('identity', {})
                principal_id = identity.get('principalId')
                if principal_id:
                    logger.info("Retrieved principal ID: %s", principal_id)
                    return principal_id
            
            logger.warning("Failed to get provisioned machine: HTTP %s", response.status_code)
            return None
            
        except Exception as e:
            logger.warning("Error fetching provisioned machine: %s", str(e))
            return None

    def _output(self, *args, **kwargs):
        result = self.deserialize_output(self.ctx.vars.instance, client_flatten=True)
        return result

    class ValidateOwnershipVoucher(AAZHttpOperation):
        """Validate ownership voucher before creating provisioned machine."""
        CLIENT_TYPE = "MgmtClient"

        def __call__(self, *args, **kwargs):
            request = self.make_request()
            session = self.client.send_request(request=request, stream=False, **kwargs)
            if session.http_response.status_code in [200]:
                return self.on_200(session)
            return self.on_error(session.http_response)

        @property
        def url(self):
            return self.client.format_url(
                "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.AzureStackHCI/locations/{location}/validateOwnershipVouchers",
                **self.url_parameters
            )

        @property
        def method(self):
            return "POST"

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
                    "location", self.ctx.args.location,
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
            # Read the PEM file and convert to base64
            file_path = self.ctx.args.ownership_voucher.to_serialized_data()
            with open(file_path, "rb") as f:
                file_content = f.read()
            base64_encoded = base64.b64encode(file_content).decode('utf-8')
            
            return {
                "ownershipVoucherDetails": [
                    {
                        "ownershipVoucher": base64_encoded,
                        "ownerKeyType": "MicrosoftManaged"
                    }
                ]
            }

        def on_200(self, session):
            data = self.deserialize_http_content(session)
            Create._validation_result = data

    class EdgeMachinesCreateOrUpdate(AAZHttpOperation):
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
                "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.AzureStackHCI/edgeMachines/{edgeMachineName}",
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
            location = args.location.to_serialized_data()
            edge_machine_name = args.edge_machine_name.to_serialized_data()
            site_resource_id = args.site_resource_id.to_serialized_data()
            os_image = args.os_image.to_serialized_data() if has_value(args.os_image) else None
            
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

            # Build time configuration (null if empty)
            time_config = None
            if has_value(args.ntp_server) or has_value(args.timezone):
                time_config = {}
                if has_value(args.ntp_server):
                    time_config["primaryTimeServer"] = args.ntp_server.to_serialized_data()
                if has_value(args.timezone):
                    time_config["timeZone"] = args.timezone.to_serialized_data()

            # Build web proxy configuration (empty object by default)
            web_proxy = {}
            if has_value(args.proxy_settings):
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

            # Build provisioning details based on OS image type (only if os_image is provided)
            provisioning_details = None
            if os_image == "HCI":
                provisioning_details = {
                    "osProfile": {
                        "osType": "HCI"
                    },
                    "userDetails": [
                        {
                            "secretType": "KeyVault",
                            "userName": "admin",
                            "secretLocation": args.key_vault_secret_id.to_serialized_data()
                        }
                    ]
                }
                if has_value(args.version):
                    provisioning_details["osProfile"]["vsrVersion"] = args.version.to_serialized_data()
            elif os_image == "AzureLinux":
                provisioning_details = {
                    "osProfile": {
                        "osType": "AzureLinux",
                        "osName": "AzureLinux",
                        "osVersion": "3.0",
                        "osImageLocation": "https://aka.ms/aep/sff/azurelinux/2604a"
                    },
                    "userDetails": [
                        {
                            "secretType": "SshPubKey",
                            "userName": "admin",
                            "sshPubKey": [args.ssh_public_key.to_serialized_data()]
                        }
                    ]
                }
                if has_value(args.version):
                    provisioning_details["osProfile"]["osVersion"] = args.version.to_serialized_data()

            # Read and encode the ownership voucher file
            file_path = args.ownership_voucher.to_serialized_data()
            with open(file_path, "rb") as f:
                file_content = f.read()
            ownership_voucher_base64 = base64.b64encode(file_content).decode('utf-8')

            # Build the full payload
            payload = {
                "location": location,
                "identity": {
                    "type": "SystemAssigned"
                },
                "properties": {
                    "edgeMachineKind": "Standard",
                    "siteDetails": {
                        "siteResourceId": site_resource_id,
                        "deviceConfiguration": device_configuration
                    },
                    "ownershipVoucherDetails": {
                        "ownerKeyType": "MicrosoftManaged",
                        "ownershipVoucher": ownership_voucher_base64
                    }
                }
            }

            # Add provisioning details if os_image is provided
            if provisioning_details:
                payload["properties"]["provisioningDetails"] = provisioning_details

            # Add optional arc gateway resource id
            if has_value(args.arc_gateway_resource_id):
                payload["properties"]["arcGatewayResourceId"] = args.arc_gateway_resource_id.to_serialized_data()

            # Add tags if provided
            if has_value(args.tags):
                payload["tags"] = args.tags.to_serialized_data()

            return payload

        def on_200_201(self, session):
            data = self.deserialize_http_content(session)
            self.ctx.set_var("instance", data, schema_builder=self._build_schema_on_200_201)

        _schema_on_200_201 = None

        @classmethod
        def _build_schema_on_200_201(cls):
            if cls._schema_on_200_201 is not None:
                return cls._schema_on_200_201

            cls._schema_on_200_201 = AAZObjectType()

            _schema_on_200_201 = cls._schema_on_200_201
            _schema_on_200_201.id = AAZStrType()
            _schema_on_200_201.location = AAZStrType()
            _schema_on_200_201.name = AAZStrType()
            _schema_on_200_201.type = AAZStrType()
            _schema_on_200_201.identity = AAZObjectType()
            _schema_on_200_201.properties = AAZObjectType()
            _schema_on_200_201.system_data = AAZObjectType(
                serialized_name="systemData",
            )
            _schema_on_200_201.tags = AAZDictType()

            identity = cls._schema_on_200_201.identity
            identity.type = AAZStrType()
            identity.principal_id = AAZStrType(
                serialized_name="principalId",
            )
            identity.tenant_id = AAZStrType(
                serialized_name="tenantId",
            )

            properties = cls._schema_on_200_201.properties
            properties.provisioning_state = AAZStrType(
                serialized_name="provisioningState",
            )
            properties.edge_machine_kind = AAZStrType(
                serialized_name="edgeMachineKind",
            )
            properties.arc_gateway_resource_id = AAZStrType(
                serialized_name="arcGatewayResourceId",
            )
            properties.site_details = AAZObjectType(
                serialized_name="siteDetails",
            )
            properties.ownership_voucher_details = AAZObjectType(
                serialized_name="ownershipVoucherDetails",
            )
            properties.provisioning_details = AAZObjectType(
                serialized_name="provisioningDetails",
            )

            site_details = cls._schema_on_200_201.properties.site_details
            site_details.site_resource_id = AAZStrType(
                serialized_name="siteResourceId",
            )

            ownership_voucher_details = cls._schema_on_200_201.properties.ownership_voucher_details
            ownership_voucher_details.owner_key_type = AAZStrType(
                serialized_name="ownerKeyType",
            )
            ownership_voucher_details.status = AAZStrType()

            provisioning_details = cls._schema_on_200_201.properties.provisioning_details
            provisioning_details.os_profile = AAZObjectType(
                serialized_name="osProfile",
            )

            os_profile = cls._schema_on_200_201.properties.provisioning_details.os_profile
            os_profile.os_type = AAZStrType(
                serialized_name="osType",
            )
            os_profile.os_name = AAZStrType(
                serialized_name="osName",
            )
            os_profile.os_version = AAZStrType(
                serialized_name="osVersion",
            )
            os_profile.vsr_version = AAZStrType(
                serialized_name="vsrVersion",
            )

            system_data = cls._schema_on_200_201.system_data
            system_data.created_at = AAZStrType(
                serialized_name="createdAt",
            )
            system_data.created_by = AAZStrType(
                serialized_name="createdBy",
            )
            system_data.created_by_type = AAZStrType(
                serialized_name="createdByType",
            )
            system_data.last_modified_at = AAZStrType(
                serialized_name="lastModifiedAt",
            )
            system_data.last_modified_by = AAZStrType(
                serialized_name="lastModifiedBy",
            )
            system_data.last_modified_by_type = AAZStrType(
                serialized_name="lastModifiedByType",
            )

            tags = cls._schema_on_200_201.tags
            tags.Element = AAZStrType()

            return cls._schema_on_200_201
