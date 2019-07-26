# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
from azure.cli.core.commands import CliCommandType
from ._client_factory import cf_apim


def load_command_table(self, _):

    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#ApiManagementOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim api', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_api')
        g.custom_command('update', 'update_apim_api')
        g.custom_command('delete', 'delete_apim_api')
        g.custom_command('list', 'list_apim_api')
        g.custom_command('show', 'show_apim_api')
    with self.command_group('apim api release', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_api_release')
        g.custom_command('update', 'update_apim_api_release')
        g.custom_command('delete', 'delete_apim_api_release')
        g.custom_command('list', 'list_apim_api_release')
        g.custom_command('show', 'show_apim_api_release')
    with self.command_group('apim api operation', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_api_operation')
        g.custom_command('update', 'update_apim_api_operation')
        g.custom_command('delete', 'delete_apim_api_operation')
        g.custom_command('list', 'list_apim_api_operation')
        g.custom_command('show', 'show_apim_api_operation')
    with self.command_group('apim api operation policy', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_api_operation_policy')
        g.custom_command('update', 'update_apim_api_operation_policy')
        g.custom_command('delete', 'delete_apim_api_operation_policy')
        g.custom_command('list', 'list_apim_api_operation_policy')
        g.custom_command('show', 'show_apim_api_operation_policy')
    with self.command_group('apim tag', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_tag')
        g.custom_command('update', 'update_apim_tag')
        g.custom_command('delete', 'delete_apim_tag')
        g.custom_command('list', 'list_apim_tag')
        g.custom_command('show', 'show_apim_tag')
    with self.command_group('apim api policy', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_api_policy')
        g.custom_command('update', 'update_apim_api_policy')
        g.custom_command('delete', 'delete_apim_api_policy')
        g.custom_command('list', 'list_apim_api_policy')
        g.custom_command('show', 'show_apim_api_policy')
    with self.command_group('apim api schema', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_api_schema')
        g.custom_command('update', 'update_apim_api_schema')
        g.custom_command('delete', 'delete_apim_api_schema')
        g.custom_command('list', 'list_apim_api_schema')
        g.custom_command('show', 'show_apim_api_schema')
    with self.command_group('apim api diagnostic', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_api_diagnostic')
        g.custom_command('update', 'update_apim_api_diagnostic')
        g.custom_command('delete', 'delete_apim_api_diagnostic')
        g.custom_command('list', 'list_apim_api_diagnostic')
        g.custom_command('show', 'show_apim_api_diagnostic')
    with self.command_group('apim api issue', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_api_issue')
        g.custom_command('update', 'update_apim_api_issue')
        g.custom_command('delete', 'delete_apim_api_issue')
        g.custom_command('list', 'list_apim_api_issue')
        g.custom_command('show', 'show_apim_api_issue')
    with self.command_group('apim api issue comment', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_api_issue_comment')
        g.custom_command('update', 'update_apim_api_issue_comment')
        g.custom_command('delete', 'delete_apim_api_issue_comment')
        g.custom_command('list', 'list_apim_api_issue_comment')
        g.custom_command('show', 'show_apim_api_issue_comment')
    with self.command_group('apim api issue attachment', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_api_issue_attachment')
        g.custom_command('update', 'update_apim_api_issue_attachment')
        g.custom_command('delete', 'delete_apim_api_issue_attachment')
        g.custom_command('list', 'list_apim_api_issue_attachment')
        g.custom_command('show', 'show_apim_api_issue_attachment')
    with self.command_group('apim api tagdescription', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_api_tagdescription')
        g.custom_command('update', 'update_apim_api_tagdescription')
        g.custom_command('delete', 'delete_apim_api_tagdescription')
        g.custom_command('list', 'list_apim_api_tagdescription')
        g.custom_command('show', 'show_apim_api_tagdescription')
    with self.command_group('apim apiversionset', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_apiversionset')
        g.custom_command('update', 'update_apim_apiversionset')
        g.custom_command('delete', 'delete_apim_apiversionset')
        g.custom_command('list', 'list_apim_apiversionset')
        g.custom_command('show', 'show_apim_apiversionset')
    with self.command_group('apim authorizationserver', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_authorizationserver')
        g.custom_command('update', 'update_apim_authorizationserver')
        g.custom_command('delete', 'delete_apim_authorizationserver')
        g.custom_command('list', 'list_apim_authorizationserver')
        g.custom_command('show', 'show_apim_authorizationserver')
    with self.command_group('apim backend', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_backend')
        g.custom_command('update', 'update_apim_backend')
        g.custom_command('delete', 'delete_apim_backend')
        g.custom_command('list', 'list_apim_backend')
        g.custom_command('show', 'show_apim_backend')
    with self.command_group('apim cache', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_cache')
        g.custom_command('update', 'update_apim_cache')
        g.custom_command('delete', 'delete_apim_cache')
        g.custom_command('list', 'list_apim_cache')
        g.custom_command('show', 'show_apim_cache')
    with self.command_group('apim certificate', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_certificate')
        g.custom_command('update', 'update_apim_certificate')
        g.custom_command('delete', 'delete_apim_certificate')
        g.custom_command('list', 'list_apim_certificate')
        g.custom_command('show', 'show_apim_certificate')
    with self.command_group('apim', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim')
        g.custom_command('update', 'update_apim')
        g.custom_command('delete', 'delete_apim')
        g.custom_command('list', 'list_apim')
        g.custom_command('show', 'show_apim')
    with self.command_group('apim diagnostic', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_diagnostic')
        g.custom_command('update', 'update_apim_diagnostic')
        g.custom_command('delete', 'delete_apim_diagnostic')
        g.custom_command('list', 'list_apim_diagnostic')
        g.custom_command('show', 'show_apim_diagnostic')
    with self.command_group('apim template', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_template')
        g.custom_command('update', 'update_apim_template')
        g.custom_command('delete', 'delete_apim_template')
        g.custom_command('list', 'list_apim_template')
        g.custom_command('show', 'show_apim_template')
    with self.command_group('apim group', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_group')
        g.custom_command('update', 'update_apim_group')
        g.custom_command('delete', 'delete_apim_group')
        g.custom_command('list', 'list_apim_group')
        g.custom_command('show', 'show_apim_group')
    with self.command_group('apim group user', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_group_user')
        g.custom_command('delete', 'delete_apim_group_user')
        g.custom_command('list', 'list_apim_group_user')
    with self.command_group('apim identityprovider', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_identityprovider')
        g.custom_command('update', 'update_apim_identityprovider')
        g.custom_command('delete', 'delete_apim_identityprovider')
        g.custom_command('list', 'list_apim_identityprovider')
        g.custom_command('show', 'show_apim_identityprovider')
    with self.command_group('apim logger', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_logger')
        g.custom_command('update', 'update_apim_logger')
        g.custom_command('delete', 'delete_apim_logger')
        g.custom_command('list', 'list_apim_logger')
        g.custom_command('show', 'show_apim_logger')
    with self.command_group('apim notification', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_notification')
        g.custom_command('update', 'update_apim_notification')
        g.custom_command('list', 'list_apim_notification')
        g.custom_command('show', 'show_apim_notification')
    with self.command_group('apim notification recipientuser', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_notification_recipientuser')
        g.custom_command('update', 'update_apim_notification_recipientuser')
        g.custom_command('delete', 'delete_apim_notification_recipientuser')
        g.custom_command('list', 'list_apim_notification_recipientuser')
    with self.command_group('apim notification recipientemail', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_notification_recipientemail')
        g.custom_command('update', 'update_apim_notification_recipientemail')
        g.custom_command('delete', 'delete_apim_notification_recipientemail')
        g.custom_command('list', 'list_apim_notification_recipientemail')
    with self.command_group('apim openidconnectprovider', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_openidconnectprovider')
        g.custom_command('update', 'update_apim_openidconnectprovider')
        g.custom_command('delete', 'delete_apim_openidconnectprovider')
        g.custom_command('list', 'list_apim_openidconnectprovider')
        g.custom_command('show', 'show_apim_openidconnectprovider')
    with self.command_group('apim policy', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_policy')
        g.custom_command('update', 'update_apim_policy')
        g.custom_command('delete', 'delete_apim_policy')
        g.custom_command('list', 'list_apim_policy')
        g.custom_command('show', 'show_apim_policy')
    with self.command_group('apim portalsetting signin', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_portalsetting_signin')
        g.custom_command('update', 'update_apim_portalsetting_signin')
        g.custom_command('show', 'show_apim_portalsetting_signin')
    with self.command_group('apim portalsetting signup', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_portalsetting_signup')
        g.custom_command('update', 'update_apim_portalsetting_signup')
        g.custom_command('show', 'show_apim_portalsetting_signup')
    with self.command_group('apim portalsetting delegation', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_portalsetting_delegation')
        g.custom_command('update', 'update_apim_portalsetting_delegation')
        g.custom_command('show', 'show_apim_portalsetting_delegation')
    with self.command_group('apim product', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_product')
        g.custom_command('update', 'update_apim_product')
        g.custom_command('delete', 'delete_apim_product')
        g.custom_command('list', 'list_apim_product')
        g.custom_command('show', 'show_apim_product')
    with self.command_group('apim product api', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_product_api')
        g.custom_command('update', 'update_apim_product_api')
        g.custom_command('delete', 'delete_apim_product_api')
        g.custom_command('list', 'list_apim_product_api')
    with self.command_group('apim product group', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_product_group')
        g.custom_command('update', 'update_apim_product_group')
        g.custom_command('delete', 'delete_apim_product_group')
        g.custom_command('list', 'list_apim_product_group')
    with self.command_group('apim product policy', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_product_policy')
        g.custom_command('update', 'update_apim_product_policy')
        g.custom_command('delete', 'delete_apim_product_policy')
        g.custom_command('list', 'list_apim_product_policy')
        g.custom_command('show', 'show_apim_product_policy')
    with self.command_group('apim property', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_property')
        g.custom_command('update', 'update_apim_property')
        g.custom_command('delete', 'delete_apim_property')
        g.custom_command('list', 'list_apim_property')
        g.custom_command('show', 'show_apim_property')
    with self.command_group('apim subscription', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_subscription')
        g.custom_command('update', 'update_apim_subscription')
        g.custom_command('delete', 'delete_apim_subscription')
        g.custom_command('list', 'list_apim_subscription')
        g.custom_command('show', 'show_apim_subscription')
    with self.command_group('apim user', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_user')
        g.custom_command('update', 'update_apim_user')
        g.custom_command('delete', 'delete_apim_user')
        g.custom_command('list', 'list_apim_user')
        g.custom_command('show', 'show_apim_user')
