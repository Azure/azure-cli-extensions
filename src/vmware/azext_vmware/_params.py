# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long,too-many-statements


from azext_vmware.action import ScriptExecutionNamedOutputAction, ScriptExecutionParameterAction


def load_arguments(self, _):

    from azure.cli.core.commands.parameters import tags_type
    from azure.cli.core.commands.validators import get_default_location_from_resource_group

    with self.argument_context('vmware') as c:
        c.argument('tags', tags_type)
        c.argument('location', validator=get_default_location_from_resource_group)
        c.argument('private_cloud', options_list=['--private-cloud', '-c'], help='Name of the private cloud.')

    with self.argument_context('vmware location') as c:
        c.argument('sku', help='The name of the SKU')

    with self.argument_context('vmware private-cloud') as c:
        c.argument('cluster_size', help='Number of hosts for the default management cluster. Minimum of 3 and maximum of 16.')
        c.argument('internet', help='Connectivity to internet. Specify "Enabled" or "Disabled".')

    with self.argument_context('vmware private-cloud delete-cmk-encryption') as c:
        c.argument('yes', help='Delete without confirmation.')

    with self.argument_context('vmware private-cloud disable-cmk-encryption') as c:
        c.argument('yes', help='Delete without confirmation.')

    with self.argument_context('vmware private-cloud add-cmk-encryption') as c:
        c.argument('enc_kv_key_name', help='The name of the encryption key vault key.')
        c.argument('enc_kv_url', help='The URL of the encryption key vault.')
        c.argument('enc_kv_key_version', help='The version of the encryption key vault key.')

    with self.argument_context('vmware private-cloud enable-cmk-encryption') as c:
        c.argument('enc_kv_key_name', help='The name of the encryption key vault key.')
        c.argument('enc_kv_url', help='The URL of the encryption key vault.')
        c.argument('enc_kv_key_version', help='The version of the encryption key vault key.')

    with self.argument_context('vmware private-cloud add-identity-source') as c:
        c.argument('alias', help='The domain\'s NetBIOS name.')
        c.argument('base_group_dn', help='The base distinguished name for groups.')
        c.argument('base_user_dn', help='The base distinguished name for users.')
        c.argument('domain', help='The domain\'s dns name.')
        c.argument('name', options_list=['--name', '-n'], help='The name of the identity source.')
        c.argument('password', help='The password of the Active Directory user with a minimum of read-only access to Base DN for users and groups.')
        c.argument('primary_server', help='Primary server URL.')
        c.argument('secondary_server', help='Secondary server URL.')
        c.argument('ssl', help='Protect LDAP communication using SSL certificate (LDAPS). Specify "Enabled" or "Disabled".')
        c.argument('username', help='The ID of an Active Directory user with a minimum of read-only access to Base DN for users and group.')

    with self.argument_context('vmware private-cloud addidentitysource') as c:
        c.argument('alias', help='The domain\'s NetBIOS name.')
        c.argument('base_group_dn', help='The base distinguished name for groups.')
        c.argument('base_user_dn', help='The base distinguished name for users.')
        c.argument('domain', help='The domain\'s dns name.')
        c.argument('name', options_list=['--name', '-n'], help='The name of the identity source.')
        c.argument('password', help='The password of the Active Directory user with a minimum of read-only access to Base DN for users and groups.')
        c.argument('primary_server', help='Primary server URL.')
        c.argument('secondary_server', help='Secondary server URL.')
        c.argument('ssl', help='Protect LDAP communication using SSL certificate (LDAPS). Specify "Enabled" or "Disabled".')
        c.argument('username', help='The ID of an Active Directory user with a minimum of read-only access to Base DN for users and group.')

    with self.argument_context('vmware private-cloud delete-identity-source') as c:
        c.argument('alias', help='The domain\'s NetBIOS name.')
        c.argument('domain', help='The domain\'s dns name.')
        c.argument('name', options_list=['--name', '-n'], help='The name of the identity source.')
        c.argument('yes', help='Delete without confirmation.')

    with self.argument_context('vmware private-cloud deleteidentitysource') as c:
        c.argument('alias', help='The domain\'s NetBIOS name.')
        c.argument('domain', help='The domain\'s dns name.')
        c.argument('name', options_list=['--name', '-n'], help='The name of the identity source.')
        c.argument('yes', help='Delete without confirmation.')

    with self.argument_context('vmware private-cloud identity assign') as c:
        c.argument('system_assigned', help='Enable a system assigned identity.')

    with self.argument_context('vmware private-cloud identity remove') as c:
        c.argument('system_assigned', help='Disable a system assigned identity.')
        c.argument('yes', help='Delete without confirmation.')

    with self.argument_context('vmware datastore') as c:
        c.argument('name', options_list=['--name', '-n'], help='The name of the datastore.')
        c.argument('cluster', help='The name of the cluster.')
        c.argument('lun_name', help='Name of the LUN to be used.')

    with self.argument_context('vmware datastore create') as c:
        c.argument('nfs_provider_ip', help='IP address of the NFS provider.')
        c.argument('nfs_file_path', help='File path through which the NFS volume is exposed by the provider.')
        c.argument('endpoints', nargs='*', help='iSCSI provider target IP address list.')

    with self.argument_context('vmware script-execution') as c:
        c.argument('name', options_list=['--name', '-n'], help='Name of the script execution.')

    with self.argument_context('vmware script-execution create') as c:
        c.argument('timeout', help='Time limit for execution.')
        c.argument('parameters', options_list=['--parameter', '-p'], action=ScriptExecutionParameterAction, nargs='*', help='Parameters the script will accept.')
        c.argument('hidden_parameters', options_list=['--hidden-parameter'], action=ScriptExecutionParameterAction, nargs='*', help='Parameters that will be hidden/not visible to ARM, such as passwords and credentials.')
        c.argument('failure_reason', help='Error message if the script was able to run, but if the script itself had errors or powershell threw an exception.')
        c.argument('retention', help='Time to live for the resource. If not provided, will be available for 60 days.')
        c.argument('out', nargs='*', help='Standard output stream from the powershell execution.')
        c.argument('named_outputs', action=ScriptExecutionNamedOutputAction, nargs='*', help='User-defined dictionary.')
        c.argument('script_cmdlet_id', help='A reference to the script cmdlet resource if user is running a AVS script.')
