# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):

    from ._client_factory import cf_api
    apim_api = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.api_operations#ApiOperations.{}',
        client_factory=cf_api)
    with self.command_group('apim api', apim_api, client_factory=cf_api) as g:
        g.custom_command('create', 'create_apim_api')
        g.generic_update_command('update', custom_func_name='update_apim_api')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api')
        g.show_command('show', 'get')

    from ._client_factory import cf_api_release
    apim_api_release = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.api_release_operations#ApiReleaseOperations.{}',
        client_factory=cf_api_release)
    with self.command_group('apim api release', apim_api_release, client_factory=cf_api_release) as g:
        g.custom_command('create', 'create_apim_api_release')
        g.generic_update_command('update', custom_func_name='update_apim_api_release')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_release')
        g.show_command('show', 'get')

    from ._client_factory import cf_api_operation
    apim_api_operation = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.api_operation_operations#ApiOperationOperations.{}',
        client_factory=cf_api_operation)
    with self.command_group('apim api operation', apim_api_operation, client_factory=cf_api_operation) as g:
        g.custom_command('create', 'create_apim_api_operation')
        g.generic_update_command('update', custom_func_name='update_apim_api_operation')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_operation')
        g.show_command('show', 'get')

    from ._client_factory import cf_api_operation_policy
    apim_api_operation_policy = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.api_operation_policy_operations#ApiOperationPolicyOperations.{}',
        client_factory=cf_api_operation_policy)
    with self.command_group('apim api operation policy', apim_api_operation_policy, client_factory=cf_api_operation_policy) as g:
        g.custom_command('create', 'create_apim_api_operation_policy')
        g.generic_update_command('update', custom_func_name='update_apim_api_operation_policy')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_operation_policy')
        g.show_command('show', 'get')

    from ._client_factory import cf_tag
    apim_tag = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.tag_operations#TagOperations.{}',
        client_factory=cf_tag)
    with self.command_group('apim tag', apim_tag, client_factory=cf_tag) as g:
        g.custom_command('create', 'create_apim_tag')
        g.generic_update_command('update', custom_func_name='update_apim_tag')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_tag')
        g.show_command('show', 'get')

    from ._client_factory import cf_api_policy
    apim_api_policy = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.api_policy_operations#ApiPolicyOperations.{}',
        client_factory=cf_api_policy)
    with self.command_group('apim api policy', apim_api_policy, client_factory=cf_api_policy) as g:
        g.custom_command('create', 'create_apim_api_policy')
        g.generic_update_command('update', custom_func_name='update_apim_api_policy')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_policy')
        g.show_command('show', 'get')

    from ._client_factory import cf_api_schema
    apim_api_schema = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.api_schema_operations#ApiSchemaOperations.{}',
        client_factory=cf_api_schema)
    with self.command_group('apim api schema', apim_api_schema, client_factory=cf_api_schema) as g:
        g.custom_command('create', 'create_apim_api_schema')
        g.generic_update_command('update', custom_func_name='update_apim_api_schema')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_schema')
        g.show_command('show', 'get')

    from ._client_factory import cf_api_diagnostic
    apim_api_diagnostic = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.api_diagnostic_operations#ApiDiagnosticOperations.{}',
        client_factory=cf_api_diagnostic)
    with self.command_group('apim api diagnostic', apim_api_diagnostic, client_factory=cf_api_diagnostic) as g:
        g.custom_command('create', 'create_apim_api_diagnostic')
        g.generic_update_command('update', custom_func_name='update_apim_api_diagnostic')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_diagnostic')
        g.show_command('show', 'get')

    from ._client_factory import cf_api_issue
    apim_api_issue = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.api_issue_operations#ApiIssueOperations.{}',
        client_factory=cf_api_issue)
    with self.command_group('apim api issue', apim_api_issue, client_factory=cf_api_issue) as g:
        g.custom_command('create', 'create_apim_api_issue')
        g.generic_update_command('update', custom_func_name='update_apim_api_issue')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_issue')
        g.show_command('show', 'get')

    from ._client_factory import cf_api_issue_comment
    apim_api_issue_comment = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.api_issue_comment_operations#ApiIssueCommentOperations.{}',
        client_factory=cf_api_issue_comment)
    with self.command_group('apim api issue comment', apim_api_issue_comment, client_factory=cf_api_issue_comment) as g:
        g.custom_command('create', 'create_apim_api_issue_comment')
        g.generic_update_command('update', custom_func_name='update_apim_api_issue_comment')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_issue_comment')
        g.show_command('show', 'get')

    from ._client_factory import cf_api_issue_attachment
    apim_api_issue_attachment = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.api_issue_attachment_operations#ApiIssueAttachmentOperations.{}',
        client_factory=cf_api_issue_attachment)
    with self.command_group('apim api issue attachment', apim_api_issue_attachment, client_factory=cf_api_issue_attachment) as g:
        g.custom_command('create', 'create_apim_api_issue_attachment')
        g.generic_update_command('update', custom_func_name='update_apim_api_issue_attachment')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_issue_attachment')
        g.show_command('show', 'get')

    from ._client_factory import cf_api_tag_description
    apim_api_tag_description = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.api_tag_description_operations#ApiTagDescriptionOperations.{}',
        client_factory=cf_api_tag_description)
    with self.command_group('apim api tag-description', apim_api_tag_description, client_factory=cf_api_tag_description) as g:
        g.custom_command('create', 'create_apim_api_tag_description')
        g.generic_update_command('update', custom_func_name='update_apim_api_tag_description')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_tag_description')
        g.show_command('show', 'get')

    from ._client_factory import cf_api_version_set
    apim_api_version_set = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.api_version_set_operations#ApiVersionSetOperations.{}',
        client_factory=cf_api_version_set)
    with self.command_group('apim api-version-set', apim_api_version_set, client_factory=cf_api_version_set) as g:
        g.custom_command('create', 'create_apim_api_version_set')
        g.generic_update_command('update', custom_func_name='update_apim_api_version_set')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_version_set')
        g.show_command('show', 'get')

    from ._client_factory import cf_authorization_server
    apim_authorization_server = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.authorization_server_operations#AuthorizationServerOperations.{}',
        client_factory=cf_authorization_server)
    with self.command_group('apim authorization-server', apim_authorization_server, client_factory=cf_authorization_server) as g:
        g.custom_command('create', 'create_apim_authorization_server')
        g.generic_update_command('update', custom_func_name='update_apim_authorization_server')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_authorization_server')
        g.show_command('show', 'get')

    from ._client_factory import cf_backend
    apim_backend = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.backend_operations#BackendOperations.{}',
        client_factory=cf_backend)
    with self.command_group('apim backend', apim_backend, client_factory=cf_backend) as g:
        g.custom_command('create', 'create_apim_backend')
        g.generic_update_command('update', custom_func_name='update_apim_backend')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_backend')
        g.show_command('show', 'get')

    from ._client_factory import cf_cache
    apim_cache = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.cache_operations#CacheOperations.{}',
        client_factory=cf_cache)
    with self.command_group('apim cache', apim_cache, client_factory=cf_cache) as g:
        g.custom_command('create', 'create_apim_cache')
        g.generic_update_command('update', custom_func_name='update_apim_cache')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_cache')
        g.show_command('show', 'get')

    from ._client_factory import cf_certificate
    apim_certificate = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.certificate_operations#CertificateOperations.{}',
        client_factory=cf_certificate)
    with self.command_group('apim certificate', apim_certificate, client_factory=cf_certificate) as g:
        g.custom_command('create', 'create_apim_certificate')
        g.generic_update_command('update', custom_func_name='update_apim_certificate')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_certificate')
        g.show_command('show', 'get')

    from ._client_factory import cf_api_management_service
    apim_api_management_service = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.api_management_service_operations#ApiManagementServiceOperations.{}',
        client_factory=cf_api_management_service)
    with self.command_group('apim', apim_api_management_service, client_factory=cf_api_management_service) as g:
        g.custom_command('create', 'create_apim')
        g.generic_update_command('update', custom_func_name='update_apim')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim')
        g.show_command('show', 'get')

    from ._client_factory import cf_diagnostic
    apim_diagnostic = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.diagnostic_operations#DiagnosticOperations.{}',
        client_factory=cf_diagnostic)
    with self.command_group('apim diagnostic', apim_diagnostic, client_factory=cf_diagnostic) as g:
        g.custom_command('create', 'create_apim_diagnostic')
        g.generic_update_command('update', custom_func_name='update_apim_diagnostic')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_diagnostic')
        g.show_command('show', 'get')

    from ._client_factory import cf_email_template
    apim_email_template = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.email_template_operations#EmailTemplateOperations.{}',
        client_factory=cf_email_template)
    with self.command_group('apim template', apim_email_template, client_factory=cf_email_template) as g:
        g.custom_command('create', 'create_apim_template')
        g.generic_update_command('update', custom_func_name='update_apim_template')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_template')
        g.show_command('show', 'get')

    from ._client_factory import cf_group
    apim_group = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.group_operations#GroupOperations.{}',
        client_factory=cf_group)
    with self.command_group('apim group', apim_group, client_factory=cf_group) as g:
        g.custom_command('create', 'create_apim_group')
        g.generic_update_command('update', custom_func_name='update_apim_group')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_group')
        g.show_command('show', 'get')

    from ._client_factory import cf_group_user
    apim_group_user = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.group_user_operations#GroupUserOperations.{}',
        client_factory=cf_group_user)
    with self.command_group('apim group user', apim_group_user, client_factory=cf_group_user) as g:
        g.custom_command('create', 'create_apim_group_user')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_group_user')

    from ._client_factory import cf_identity_provider
    apim_identity_provider = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.identity_provider_operations#IdentityProviderOperations.{}',
        client_factory=cf_identity_provider)
    with self.command_group('apim identity-provider', apim_identity_provider, client_factory=cf_identity_provider) as g:
        g.custom_command('create', 'create_apim_identity_provider')
        g.generic_update_command('update', custom_func_name='update_apim_identity_provider')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_identity_provider')
        g.show_command('show', 'get')

    from ._client_factory import cf_logger
    apim_logger = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.logger_operations#LoggerOperations.{}',
        client_factory=cf_logger)
    with self.command_group('apim logger', apim_logger, client_factory=cf_logger) as g:
        g.custom_command('create', 'create_apim_logger')
        g.generic_update_command('update', custom_func_name='update_apim_logger')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_logger')
        g.show_command('show', 'get')

    from ._client_factory import cf_notification
    apim_notification = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.notification_operations#NotificationOperations.{}',
        client_factory=cf_notification)
    with self.command_group('apim notification', apim_notification, client_factory=cf_notification) as g:
        g.custom_command('create', 'create_apim_notification')
        g.generic_update_command('update', custom_func_name='update_apim_notification')
        g.custom_command('list', 'list_apim_notification')
        g.show_command('show', 'get')

    from ._client_factory import cf_notification_recipient_user
    apim_notification_recipient_user = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.notification_recipient_user_operations#NotificationRecipientUserOperations.{}',
        client_factory=cf_notification_recipient_user)
    with self.command_group('apim notification recipient-user', apim_notification_recipient_user, client_factory=cf_notification_recipient_user) as g:
        g.custom_command('create', 'create_apim_notification_recipient_user')
        g.generic_update_command('update', custom_func_name='update_apim_notification_recipient_user')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_notification_recipient_user')

    from ._client_factory import cf_notification_recipient_email
    apim_notification_recipient_email = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.notification_recipient_email_operations#NotificationRecipientEmailOperations.{}',
        client_factory=cf_notification_recipient_email)
    with self.command_group('apim notification recipient-email', apim_notification_recipient_email, client_factory=cf_notification_recipient_email) as g:
        g.custom_command('create', 'create_apim_notification_recipient_email')
        g.generic_update_command('update', custom_func_name='update_apim_notification_recipient_email')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_notification_recipient_email')

    from ._client_factory import cf_open_id_connect_provider
    apim_open_id_connect_provider = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.open_id_connect_provider_operations#OpenIdConnectProviderOperations.{}',
        client_factory=cf_open_id_connect_provider)
    with self.command_group('apim openid-connect-provider', apim_open_id_connect_provider, client_factory=cf_open_id_connect_provider) as g:
        g.custom_command('create', 'create_apim_openid_connect_provider')
        g.generic_update_command('update', custom_func_name='update_apim_openid_connect_provider')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_openid_connect_provider')
        g.show_command('show', 'get')

    from ._client_factory import cf_policy
    apim_policy = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.policy_operations#PolicyOperations.{}',
        client_factory=cf_policy)
    with self.command_group('apim policy', apim_policy, client_factory=cf_policy) as g:
        g.custom_command('create', 'create_apim_policy')
        g.generic_update_command('update', custom_func_name='update_apim_policy')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_policy')
        g.show_command('show', 'get')

    from ._client_factory import cf_sign_in_settings
    apim_sign_in_settings = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.sign_in_settings_operations#SignInSettingsOperations.{}',
        client_factory=cf_sign_in_settings)
    with self.command_group('apim portalsetting signin', apim_sign_in_settings, client_factory=cf_sign_in_settings) as g:
        g.custom_command('create', 'create_apim_portalsetting_signin')
        g.generic_update_command('update', custom_func_name='update_apim_portalsetting_signin')
        g.show_command('show', 'get')

    from ._client_factory import cf_sign_up_settings
    apim_sign_up_settings = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.sign_up_settings_operations#SignUpSettingsOperations.{}',
        client_factory=cf_sign_up_settings)
    with self.command_group('apim portalsetting signup', apim_sign_up_settings, client_factory=cf_sign_up_settings) as g:
        g.custom_command('create', 'create_apim_portalsetting_signup')
        g.generic_update_command('update', custom_func_name='update_apim_portalsetting_signup')
        g.show_command('show', 'get')

    from ._client_factory import cf_delegation_settings
    apim_delegation_settings = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.delegation_settings_operations#DelegationSettingsOperations.{}',
        client_factory=cf_delegation_settings)
    with self.command_group('apim portalsetting delegation', apim_delegation_settings, client_factory=cf_delegation_settings) as g:
        g.custom_command('create', 'create_apim_portalsetting_delegation')
        g.generic_update_command('update', custom_func_name='update_apim_portalsetting_delegation')
        g.show_command('show', 'get')

    from ._client_factory import cf_product
    apim_product = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.product_operations#ProductOperations.{}',
        client_factory=cf_product)
    with self.command_group('apim product', apim_product, client_factory=cf_product) as g:
        g.custom_command('create', 'create_apim_product')
        g.generic_update_command('update', custom_func_name='update_apim_product')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_product')
        g.show_command('show', 'get')

    from ._client_factory import cf_product_api
    apim_product_api = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.product_api_operations#ProductApiOperations.{}',
        client_factory=cf_product_api)
    with self.command_group('apim product api', apim_product_api, client_factory=cf_product_api) as g:
        g.custom_command('create', 'create_apim_product_api')
        g.generic_update_command('update', custom_func_name='update_apim_product_api')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_product_api')

    from ._client_factory import cf_product_group
    apim_product_group = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.product_group_operations#ProductGroupOperations.{}',
        client_factory=cf_product_group)
    with self.command_group('apim product group', apim_product_group, client_factory=cf_product_group) as g:
        g.custom_command('create', 'create_apim_product_group')
        g.generic_update_command('update', custom_func_name='update_apim_product_group')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_product_group')

    from ._client_factory import cf_product_policy
    apim_product_policy = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.product_policy_operations#ProductPolicyOperations.{}',
        client_factory=cf_product_policy)
    with self.command_group('apim product policy', apim_product_policy, client_factory=cf_product_policy) as g:
        g.custom_command('create', 'create_apim_product_policy')
        g.generic_update_command('update', custom_func_name='update_apim_product_policy')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_product_policy')
        g.show_command('show', 'get')

    from ._client_factory import cf_property
    apim_property = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.property_operations#PropertyOperations.{}',
        client_factory=cf_property)
    with self.command_group('apim property', apim_property, client_factory=cf_property) as g:
        g.custom_command('create', 'create_apim_property')
        g.generic_update_command('update', custom_func_name='update_apim_property')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_property')
        g.show_command('show', 'get')

    from ._client_factory import cf_subscription
    apim_subscription = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.subscription_operations#SubscriptionOperations.{}',
        client_factory=cf_subscription)
    with self.command_group('apim subscription', apim_subscription, client_factory=cf_subscription) as g:
        g.custom_command('create', 'create_apim_subscription')
        g.generic_update_command('update', custom_func_name='update_apim_subscription')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_subscription')
        g.show_command('show', 'get')

    from ._client_factory import cf_user
    apim_user = CliCommandType(
        operations_tmpl='azure.mgmt.apimanagement.operations.user_operations#UserOperations.{}',
        client_factory=cf_user)
    with self.command_group('apim user', apim_user, client_factory=cf_user) as g:
        g.custom_command('create', 'create_apim_user')
        g.generic_update_command('update', custom_func_name='update_apim_user')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_user')
        g.show_command('show', 'get')
