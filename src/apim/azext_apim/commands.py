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
        operations_tmpl='azure.mgmt.apim.operations#ApiOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim api', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_api')
        g.custom_command('update', 'update_apim_api')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api')
        g.custom_command('show', 'show_apim_api')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#ApiReleaseOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim api release', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_api_release')
        g.custom_command('update', 'update_apim_api_release')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_release')
        g.custom_command('show', 'show_apim_api_release')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#ApiOperationOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim api operation', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_api_operation')
        g.custom_command('update', 'update_apim_api_operation')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_operation')
        g.custom_command('show', 'show_apim_api_operation')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#ApiOperationPolicyOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim api operation policy', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_api_operation_policy')
        g.custom_command('update', 'update_apim_api_operation_policy')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_operation_policy')
        g.custom_command('show', 'show_apim_api_operation_policy')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#TagOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim tag', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_tag')
        g.custom_command('update', 'update_apim_tag')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_tag')
        g.custom_command('show', 'show_apim_tag')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#ApiPolicyOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim api policy', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_api_policy')
        g.custom_command('update', 'update_apim_api_policy')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_policy')
        g.custom_command('show', 'show_apim_api_policy')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#ApiSchemaOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim api schema', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_api_schema')
        g.custom_command('update', 'update_apim_api_schema')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_schema')
        g.custom_command('show', 'show_apim_api_schema')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#ApiDiagnosticOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim api diagnostic', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_api_diagnostic')
        g.custom_command('update', 'update_apim_api_diagnostic')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_diagnostic')
        g.custom_command('show', 'show_apim_api_diagnostic')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#ApiIssueOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim api issue', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_api_issue')
        g.custom_command('update', 'update_apim_api_issue')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_issue')
        g.custom_command('show', 'show_apim_api_issue')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#ApiIssueCommentOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim api issue comment', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_api_issue_comment')
        g.custom_command('update', 'update_apim_api_issue_comment')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_issue_comment')
        g.custom_command('show', 'show_apim_api_issue_comment')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#ApiIssueAttachmentOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim api issue attachment', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_api_issue_attachment')
        g.custom_command('update', 'update_apim_api_issue_attachment')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_issue_attachment')
        g.custom_command('show', 'show_apim_api_issue_attachment')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#ApiTagDescriptionOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim api tag-description', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_api_tag_description')
        g.custom_command('update', 'update_apim_api_tag_description')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_tag_description')
        g.custom_command('show', 'show_apim_api_tag_description')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#ApiVersionSetOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim api-version-set', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_api_version_set')
        g.custom_command('update', 'update_apim_api_version_set')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_version_set')
        g.custom_command('show', 'show_apim_api_version_set')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#AuthorizationServerOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim authorization-server', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_authorization_server')
        g.custom_command('update', 'update_apim_authorization_server')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_authorization_server')
        g.custom_command('show', 'show_apim_authorization_server')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#BackendOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim backend', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_backend')
        g.custom_command('update', 'update_apim_backend')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_backend')
        g.custom_command('show', 'show_apim_backend')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#CacheOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim cache', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_cache')
        g.custom_command('update', 'update_apim_cache')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_cache')
        g.custom_command('show', 'show_apim_cache')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#CertificateOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim certificate', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_certificate')
        g.custom_command('update', 'update_apim_certificate')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_certificate')
        g.custom_command('show', 'show_apim_certificate')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#ApiManagementServiceOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim')
        g.custom_command('update', 'update_apim')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim')
        g.custom_command('show', 'show_apim')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#DiagnosticOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim diagnostic', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_diagnostic')
        g.custom_command('update', 'update_apim_diagnostic')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_diagnostic')
        g.custom_command('show', 'show_apim_diagnostic')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#EmailTemplateOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim template', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_template')
        g.custom_command('update', 'update_apim_template')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_template')
        g.custom_command('show', 'show_apim_template')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#GroupOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim group', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_group')
        g.custom_command('update', 'update_apim_group')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_group')
        g.custom_command('show', 'show_apim_group')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#GroupUserOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim group user', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_group_user')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_group_user')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#IdentityProviderOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim identity-provider', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_identity_provider')
        g.custom_command('update', 'update_apim_identity_provider')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_identity_provider')
        g.custom_command('show', 'show_apim_identity_provider')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#LoggerOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim logger', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_logger')
        g.custom_command('update', 'update_apim_logger')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_logger')
        g.custom_command('show', 'show_apim_logger')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#NotificationOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim notification', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_notification')
        g.custom_command('update', 'update_apim_notification')
        g.custom_command('list', 'list_apim_notification')
        g.custom_command('show', 'show_apim_notification')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#NotificationRecipientUserOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim notification recipient-user', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_notification_recipient_user')
        g.custom_command('update', 'update_apim_notification_recipient_user')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_notification_recipient_user')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#NotificationRecipientEmailOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim notification recipient-email', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_notification_recipient_email')
        g.custom_command('update', 'update_apim_notification_recipient_email')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_notification_recipient_email')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#OpenIdConnectProviderOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim openid-connect-provider', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_openid_connect_provider')
        g.custom_command('update', 'update_apim_openid_connect_provider')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_openid_connect_provider')
        g.custom_command('show', 'show_apim_openid_connect_provider')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#PolicyOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim policy', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_policy')
        g.custom_command('update', 'update_apim_policy')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_policy')
        g.custom_command('show', 'show_apim_policy')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#SignInSettingsOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim portalsetting signin', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_portalsetting_signin')
        g.custom_command('update', 'update_apim_portalsetting_signin')
        g.custom_command('show', 'show_apim_portalsetting_signin')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#SignUpSettingsOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim portalsetting signup', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_portalsetting_signup')
        g.custom_command('update', 'update_apim_portalsetting_signup')
        g.custom_command('show', 'show_apim_portalsetting_signup')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#DelegationSettingsOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim portalsetting delegation', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_portalsetting_delegation')
        g.custom_command('update', 'update_apim_portalsetting_delegation')
        g.custom_command('show', 'show_apim_portalsetting_delegation')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#ProductOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim product', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_product')
        g.custom_command('update', 'update_apim_product')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_product')
        g.custom_command('show', 'show_apim_product')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#ProductApiOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim product api', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_product_api')
        g.custom_command('update', 'update_apim_product_api')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_product_api')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#ProductGroupOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim product group', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_product_group')
        g.custom_command('update', 'update_apim_product_group')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_product_group')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#ProductPolicyOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim product policy', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_product_policy')
        g.custom_command('update', 'update_apim_product_policy')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_product_policy')
        g.custom_command('show', 'show_apim_product_policy')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#PropertyOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim property', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_property')
        g.custom_command('update', 'update_apim_property')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_property')
        g.custom_command('show', 'show_apim_property')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#SubscriptionOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim subscription', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_subscription')
        g.custom_command('update', 'update_apim_subscription')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_subscription')
        g.custom_command('show', 'show_apim_subscription')
    apim_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.apim.operations#UserOperations.{}',
        client_factory=cf_apim)

    with self.command_group('apim user', apim_sdk, client_factory=cf_apim) as g:
        g.custom_command('create', 'create_apim_user')
        g.custom_command('update', 'update_apim_user')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_user')
        g.custom_command('show', 'show_apim_user')
