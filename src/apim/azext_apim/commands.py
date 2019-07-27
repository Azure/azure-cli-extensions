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
        operations_tmpl='azure.mgmt.apimanagement.operations#ApiManagementServiceOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim api', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_api')
        g.custom_command('update', 'update_apim_api')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api')
        g.custom_command('show', 'show_apim_api')
    with self.command_group('apim api release', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_api_release')
        g.custom_command('update', 'update_apim_api_release')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_release')
        g.custom_command('show', 'show_apim_api_release')
    with self.command_group('apim api operation', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_api_operation')
        g.custom_command('update', 'update_apim_api_operation')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_operation')
        g.custom_command('show', 'show_apim_api_operation')
    with self.command_group('apim api operation policy', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_api_operation_policy')
        g.custom_command('update', 'update_apim_api_operation_policy')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_operation_policy')
        g.custom_command('show', 'show_apim_api_operation_policy')
    with self.command_group('apim tag', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_tag')
        g.custom_command('update', 'update_apim_tag')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_tag')
        g.custom_command('show', 'show_apim_tag')
    with self.command_group('apim api policy', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_api_policy')
        g.custom_command('update', 'update_apim_api_policy')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_policy')
        g.custom_command('show', 'show_apim_api_policy')
    with self.command_group('apim api schema', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_api_schema')
        g.custom_command('update', 'update_apim_api_schema')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_schema')
        g.custom_command('show', 'show_apim_api_schema')
    with self.command_group('apim api diagnostic', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_api_diagnostic')
        g.custom_command('update', 'update_apim_api_diagnostic')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_diagnostic')
        g.custom_command('show', 'show_apim_api_diagnostic')
    with self.command_group('apim api issue', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_api_issue')
        g.custom_command('update', 'update_apim_api_issue')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_issue')
        g.custom_command('show', 'show_apim_api_issue')
    with self.command_group('apim api issue comment', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_api_issue_comment')
        g.custom_command('update', 'update_apim_api_issue_comment')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_issue_comment')
        g.custom_command('show', 'show_apim_api_issue_comment')
    with self.command_group('apim api issue attachment', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_api_issue_attachment')
        g.custom_command('update', 'update_apim_api_issue_attachment')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_issue_attachment')
        g.custom_command('show', 'show_apim_api_issue_attachment')
    with self.command_group('apim api tag-description', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_api_tag_description')
        g.custom_command('update', 'update_apim_api_tag_description')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_tag_description')
        g.custom_command('show', 'show_apim_api_tag_description')
    with self.command_group('apim api-version-set', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_api_version_set')
        g.custom_command('update', 'update_apim_api_version_set')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_version_set')
        g.custom_command('show', 'show_apim_api_version_set')
    with self.command_group('apim authorization-server', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_authorization_server')
        g.custom_command('update', 'update_apim_authorization_server')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_authorization_server')
        g.custom_command('show', 'show_apim_authorization_server')
    with self.command_group('apim backend', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_backend')
        g.custom_command('update', 'update_apim_backend')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_backend')
        g.custom_command('show', 'show_apim_backend')
    with self.command_group('apim cache', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_cache')
        g.custom_command('update', 'update_apim_cache')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_cache')
        g.custom_command('show', 'show_apim_cache')
    with self.command_group('apim certificate', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_certificate')
        g.custom_command('update', 'update_apim_certificate')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_certificate')
        g.custom_command('show', 'show_apim_certificate')
    with self.command_group('apim', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim')
        g.custom_command('update', 'update_apim')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim')
        g.custom_command('show', 'show_apim')
    with self.command_group('apim diagnostic', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_diagnostic')
        g.custom_command('update', 'update_apim_diagnostic')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_diagnostic')
        g.custom_command('show', 'show_apim_diagnostic')
    with self.command_group('apim template', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_template')
        g.custom_command('update', 'update_apim_template')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_template')
        g.custom_command('show', 'show_apim_template')
    with self.command_group('apim group', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_group')
        g.custom_command('update', 'update_apim_group')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_group')
        g.custom_command('show', 'show_apim_group')
    with self.command_group('apim group user', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_group_user')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_group_user')
    with self.command_group('apim identity-provider', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_identity_provider')
        g.custom_command('update', 'update_apim_identity_provider')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_identity_provider')
        g.custom_command('show', 'show_apim_identity_provider')
    with self.command_group('apim logger', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_logger')
        g.custom_command('update', 'update_apim_logger')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_logger')
        g.custom_command('show', 'show_apim_logger')
    with self.command_group('apim notification', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_notification')
        g.custom_command('update', 'update_apim_notification')
        g.custom_command('list', 'list_apim_notification')
        g.custom_command('show', 'show_apim_notification')
    with self.command_group('apim notification recipient-user', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_notification_recipient_user')
        g.custom_command('update', 'update_apim_notification_recipient_user')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_notification_recipient_user')
    with self.command_group('apim notification recipient-email', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_notification_recipient_email')
        g.custom_command('update', 'update_apim_notification_recipient_email')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_notification_recipient_email')
    with self.command_group('apim openid-connect-provider', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_openid_connect_provider')
        g.custom_command('update', 'update_apim_openid_connect_provider')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_openid_connect_provider')
        g.custom_command('show', 'show_apim_openid_connect_provider')
    with self.command_group('apim policy', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_policy')
        g.custom_command('update', 'update_apim_policy')
        g.command('delete', 'delete')
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
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_product')
        g.custom_command('show', 'show_apim_product')
    with self.command_group('apim product api', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_product_api')
        g.custom_command('update', 'update_apim_product_api')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_product_api')
    with self.command_group('apim product group', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_product_group')
        g.custom_command('update', 'update_apim_product_group')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_product_group')
    with self.command_group('apim product policy', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_product_policy')
        g.custom_command('update', 'update_apim_product_policy')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_product_policy')
        g.custom_command('show', 'show_apim_product_policy')
    with self.command_group('apim property', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_property')
        g.custom_command('update', 'update_apim_property')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_property')
        g.custom_command('show', 'show_apim_property')
    with self.command_group('apim subscription', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_subscription')
        g.custom_command('update', 'update_apim_subscription')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_subscription')
        g.custom_command('show', 'show_apim_subscription')
    with self.command_group('apim user', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_user')
        g.custom_command('update', 'update_apim_user')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_user')
        g.custom_command('show', 'show_apim_user')
