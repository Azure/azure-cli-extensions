# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):


    from ._client_factory import cf_api
    apim_api = CliCommandType(
        operations_tmpl='azure.mgmt.apim.api_operations#ApiOperations.{}',
        client_factory=cf_api)
    with self.command_group('apim api', apim_api, client_factory=cf_api) as g:
        g.custom_command('create', 'create_apim_api')
        g.custom_command('update', 'update_apim_api')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api')
        g.custom_command('show', 'show_apim_api')

    from ._client_factory import cf_api_release
    apim_api_release = CliCommandType(
        operations_tmpl='azure.mgmt.apim.api_release_operations#ApiReleaseOperations.{}',
        client_factory=cf_api_release)
    with self.command_group('apim api release', apim_api_release, client_factory=cf_api_release) as g:
        g.custom_command('create', 'create_apim_api_release')
        g.custom_command('update', 'update_apim_api_release')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_release')
        g.custom_command('show', 'show_apim_api_release')

    from ._client_factory import cf_api_operation
    apim_api_operation = CliCommandType(
        operations_tmpl='azure.mgmt.apim.api_operation_operations#ApiOperationOperations.{}',
        client_factory=cf_api_operation)
    with self.command_group('apim api operation', apim_api_operation, client_factory=cf_api_operation) as g:
        g.custom_command('create', 'create_apim_api_operation')
        g.custom_command('update', 'update_apim_api_operation')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_operation')
        g.custom_command('show', 'show_apim_api_operation')

    from ._client_factory import cf_api_operation_policy
    apim_api_operation_policy = CliCommandType(
        operations_tmpl='azure.mgmt.apim.api_operation_policy_operations#ApiOperationPolicyOperations.{}',
        client_factory=cf_api_operation_policy)
    with self.command_group('apim api operation policy', apim_api_operation_policy, client_factory=cf_api_operation_policy) as g:
        g.custom_command('create', 'create_apim_api_operation_policy')
        g.custom_command('update', 'update_apim_api_operation_policy')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_operation_policy')
        g.custom_command('show', 'show_apim_api_operation_policy')

    from ._client_factory import cf_tag
    apim_tag = CliCommandType(
        operations_tmpl='azure.mgmt.apim.tag_operations#TagOperations.{}',
        client_factory=cf_tag)
    with self.command_group('apim tag', apim_tag, client_factory=cf_tag) as g:
        g.custom_command('create', 'create_apim_tag')
        g.custom_command('update', 'update_apim_tag')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_tag')
        g.custom_command('show', 'show_apim_tag')

    from ._client_factory import cf_api_policy
    apim_api_policy = CliCommandType(
        operations_tmpl='azure.mgmt.apim.api_policy_operations#ApiPolicyOperations.{}',
        client_factory=cf_api_policy)
    with self.command_group('apim api policy', apim_api_policy, client_factory=cf_api_policy) as g:
        g.custom_command('create', 'create_apim_api_policy')
        g.custom_command('update', 'update_apim_api_policy')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_policy')
        g.custom_command('show', 'show_apim_api_policy')

    from ._client_factory import cf_api_schema
    apim_api_schema = CliCommandType(
        operations_tmpl='azure.mgmt.apim.api_schema_operations#ApiSchemaOperations.{}',
        client_factory=cf_api_schema)
    with self.command_group('apim api schema', apim_api_schema, client_factory=cf_api_schema) as g:
        g.custom_command('create', 'create_apim_api_schema')
        g.custom_command('update', 'update_apim_api_schema')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_schema')
        g.custom_command('show', 'show_apim_api_schema')

    from ._client_factory import cf_api_diagnostic
    apim_api_diagnostic = CliCommandType(
        operations_tmpl='azure.mgmt.apim.api_diagnostic_operations#ApiDiagnosticOperations.{}',
        client_factory=cf_api_diagnostic)
    with self.command_group('apim api diagnostic', apim_api_diagnostic, client_factory=cf_api_diagnostic) as g:
        g.custom_command('create', 'create_apim_api_diagnostic')
        g.custom_command('update', 'update_apim_api_diagnostic')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_diagnostic')
        g.custom_command('show', 'show_apim_api_diagnostic')

    from ._client_factory import cf_api_issue
    apim_api_issue = CliCommandType(
        operations_tmpl='azure.mgmt.apim.api_issue_operations#ApiIssueOperations.{}',
        client_factory=cf_api_issue)
    with self.command_group('apim api issue', apim_api_issue, client_factory=cf_api_issue) as g:
        g.custom_command('create', 'create_apim_api_issue')
        g.custom_command('update', 'update_apim_api_issue')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_issue')
        g.custom_command('show', 'show_apim_api_issue')

    from ._client_factory import cf_api_issue_comment
    apim_api_issue_comment = CliCommandType(
        operations_tmpl='azure.mgmt.apim.api_issue_comment_operations#ApiIssueCommentOperations.{}',
        client_factory=cf_api_issue_comment)
    with self.command_group('apim api issue comment', apim_api_issue_comment, client_factory=cf_api_issue_comment) as g:
        g.custom_command('create', 'create_apim_api_issue_comment')
        g.custom_command('update', 'update_apim_api_issue_comment')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_issue_comment')
        g.custom_command('show', 'show_apim_api_issue_comment')

    from ._client_factory import cf_api_issue_attachment
    apim_api_issue_attachment = CliCommandType(
        operations_tmpl='azure.mgmt.apim.api_issue_attachment_operations#ApiIssueAttachmentOperations.{}',
        client_factory=cf_api_issue_attachment)
    with self.command_group('apim api issue attachment', apim_api_issue_attachment, client_factory=cf_api_issue_attachment) as g:
        g.custom_command('create', 'create_apim_api_issue_attachment')
        g.custom_command('update', 'update_apim_api_issue_attachment')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_issue_attachment')
        g.custom_command('show', 'show_apim_api_issue_attachment')

    from ._client_factory import cf_api_tag_description
    apim_api_tag_description = CliCommandType(
        operations_tmpl='azure.mgmt.apim.api_tag_description_operations#ApiTagDescriptionOperations.{}',
        client_factory=cf_api_tag_description)
    with self.command_group('apim api tag-description', apim_api_tag_description, client_factory=cf_api_tag_description) as g:
        g.custom_command('create', 'create_apim_api_tag_description')
        g.custom_command('update', 'update_apim_api_tag_description')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_tag_description')
        g.custom_command('show', 'show_apim_api_tag_description')

    from ._client_factory import cf_api_version_set
    apim_api_version_set = CliCommandType(
        operations_tmpl='azure.mgmt.apim.api_version_set_operations#ApiVersionSetOperations.{}',
        client_factory=cf_api_version_set)
    with self.command_group('apim api-version-set', apim_api_version_set, client_factory=cf_api_version_set) as g:
        g.custom_command('create', 'create_apim_api_version_set')
        g.custom_command('update', 'update_apim_api_version_set')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_api_version_set')
        g.custom_command('show', 'show_apim_api_version_set')

    from ._client_factory import cf_authorization_server
    apim_authorization_server = CliCommandType(
        operations_tmpl='azure.mgmt.apim.authorization_server_operations#AuthorizationServerOperations.{}',
        client_factory=cf_authorization_server)
    with self.command_group('apim authorization-server', apim_authorization_server, client_factory=cf_authorization_server) as g:
        g.custom_command('create', 'create_apim_authorization_server')
        g.custom_command('update', 'update_apim_authorization_server')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_authorization_server')
        g.custom_command('show', 'show_apim_authorization_server')

    from ._client_factory import cf_backend
    apim_backend = CliCommandType(
        operations_tmpl='azure.mgmt.apim.backend_operations#BackendOperations.{}',
        client_factory=cf_backend)
    with self.command_group('apim backend', apim_backend, client_factory=cf_backend) as g:
        g.custom_command('create', 'create_apim_backend')
        g.custom_command('update', 'update_apim_backend')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_backend')
        g.custom_command('show', 'show_apim_backend')

    from ._client_factory import cf_cache
    apim_cache = CliCommandType(
        operations_tmpl='azure.mgmt.apim.cache_operations#CacheOperations.{}',
        client_factory=cf_cache)
    with self.command_group('apim cache', apim_cache, client_factory=cf_cache) as g:
        g.custom_command('create', 'create_apim_cache')
        g.custom_command('update', 'update_apim_cache')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_cache')
        g.custom_command('show', 'show_apim_cache')

    from ._client_factory import cf_certificate
    apim_certificate = CliCommandType(
        operations_tmpl='azure.mgmt.apim.certificate_operations#CertificateOperations.{}',
        client_factory=cf_certificate)
    with self.command_group('apim certificate', apim_certificate, client_factory=cf_certificate) as g:
        g.custom_command('create', 'create_apim_certificate')
        g.custom_command('update', 'update_apim_certificate')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_certificate')
        g.custom_command('show', 'show_apim_certificate')

    from ._client_factory import cf_api_management_service
    apim_api_management_service = CliCommandType(
        operations_tmpl='azure.mgmt.apim.api_management_service_operations#ApiManagementServiceOperations.{}',
        client_factory=cf_api_management_service)
    with self.command_group('apim', apim_api_management_service, client_factory=cf_api_management_service) as g:
        g.custom_command('create', 'create_apim')
        g.custom_command('update', 'update_apim')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim')
        g.custom_command('show', 'show_apim')

    from ._client_factory import cf_diagnostic
    apim_diagnostic = CliCommandType(
        operations_tmpl='azure.mgmt.apim.diagnostic_operations#DiagnosticOperations.{}',
        client_factory=cf_diagnostic)
    with self.command_group('apim diagnostic', apim_diagnostic, client_factory=cf_diagnostic) as g:
        g.custom_command('create', 'create_apim_diagnostic')
        g.custom_command('update', 'update_apim_diagnostic')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_diagnostic')
        g.custom_command('show', 'show_apim_diagnostic')

    from ._client_factory import cf_email_template
    apim_email_template = CliCommandType(
        operations_tmpl='azure.mgmt.apim.email_template_operations#EmailTemplateOperations.{}',
        client_factory=cf_email_template)
    with self.command_group('apim template', apim_email_template, client_factory=cf_email_template) as g:
        g.custom_command('create', 'create_apim_template')
        g.custom_command('update', 'update_apim_template')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_template')
        g.custom_command('show', 'show_apim_template')

    from ._client_factory import cf_group
    apim_group = CliCommandType(
        operations_tmpl='azure.mgmt.apim.group_operations#GroupOperations.{}',
        client_factory=cf_group)
    with self.command_group('apim group', apim_group, client_factory=cf_group) as g:
        g.custom_command('create', 'create_apim_group')
        g.custom_command('update', 'update_apim_group')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_group')
        g.custom_command('show', 'show_apim_group')

    from ._client_factory import cf_group_user
    apim_group_user = CliCommandType(
        operations_tmpl='azure.mgmt.apim.group_user_operations#GroupUserOperations.{}',
        client_factory=cf_group_user)
    with self.command_group('apim group user', apim_group_user, client_factory=cf_group_user) as g:
        g.custom_command('create', 'create_apim_group_user')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_group_user')

    from ._client_factory import cf_identity_provider
    apim_identity_provider = CliCommandType(
        operations_tmpl='azure.mgmt.apim.identity_provider_operations#IdentityProviderOperations.{}',
        client_factory=cf_identity_provider)
    with self.command_group('apim identity-provider', apim_identity_provider, client_factory=cf_identity_provider) as g:
        g.custom_command('create', 'create_apim_identity_provider')
        g.custom_command('update', 'update_apim_identity_provider')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_identity_provider')
        g.custom_command('show', 'show_apim_identity_provider')

    from ._client_factory import cf_logger
    apim_logger = CliCommandType(
        operations_tmpl='azure.mgmt.apim.logger_operations#LoggerOperations.{}',
        client_factory=cf_logger)
    with self.command_group('apim logger', apim_logger, client_factory=cf_logger) as g:
        g.custom_command('create', 'create_apim_logger')
        g.custom_command('update', 'update_apim_logger')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_logger')
        g.custom_command('show', 'show_apim_logger')

    from ._client_factory import cf_notification
    apim_notification = CliCommandType(
        operations_tmpl='azure.mgmt.apim.notification_operations#NotificationOperations.{}',
        client_factory=cf_notification)
    with self.command_group('apim notification', apim_notification, client_factory=cf_notification) as g:
        g.custom_command('create', 'create_apim_notification')
        g.custom_command('update', 'update_apim_notification')
        g.custom_command('list', 'list_apim_notification')
        g.custom_command('show', 'show_apim_notification')

    from ._client_factory import cf_notification_recipient_user
    apim_notification_recipient_user = CliCommandType(
        operations_tmpl='azure.mgmt.apim.notification_recipient_user_operations#NotificationRecipientUserOperations.{}',
        client_factory=cf_notification_recipient_user)
    with self.command_group('apim notification recipient-user', apim_notification_recipient_user, client_factory=cf_notification_recipient_user) as g:
        g.custom_command('create', 'create_apim_notification_recipient_user')
        g.custom_command('update', 'update_apim_notification_recipient_user')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_notification_recipient_user')

    from ._client_factory import cf_notification_recipient_email
    apim_notification_recipient_email = CliCommandType(
        operations_tmpl='azure.mgmt.apim.notification_recipient_email_operations#NotificationRecipientEmailOperations.{}',
        client_factory=cf_notification_recipient_email)
    with self.command_group('apim notification recipient-email', apim_notification_recipient_email, client_factory=cf_notification_recipient_email) as g:
        g.custom_command('create', 'create_apim_notification_recipient_email')
        g.custom_command('update', 'update_apim_notification_recipient_email')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_notification_recipient_email')

    from ._client_factory import cf_open_id_connect_provider
    apim_open_id_connect_provider = CliCommandType(
        operations_tmpl='azure.mgmt.apim.open_id_connect_provider_operations#OpenIdConnectProviderOperations.{}',
        client_factory=cf_open_id_connect_provider)
    with self.command_group('apim openid-connect-provider', apim_open_id_connect_provider, client_factory=cf_open_id_connect_provider) as g:
        g.custom_command('create', 'create_apim_openid_connect_provider')
        g.custom_command('update', 'update_apim_openid_connect_provider')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_openid_connect_provider')
        g.custom_command('show', 'show_apim_openid_connect_provider')

    from ._client_factory import cf_policy
    apim_policy = CliCommandType(
        operations_tmpl='azure.mgmt.apim.policy_operations#PolicyOperations.{}',
        client_factory=cf_policy)
    with self.command_group('apim policy', apim_policy, client_factory=cf_policy) as g:
        g.custom_command('create', 'create_apim_policy')
        g.custom_command('update', 'update_apim_policy')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_policy')
        g.custom_command('show', 'show_apim_policy')

    from ._client_factory import cf_sign_in_settings
    apim_sign_in_settings = CliCommandType(
        operations_tmpl='azure.mgmt.apim.sign_in_settings_operations#SignInSettingsOperations.{}',
        client_factory=cf_sign_in_settings)
    with self.command_group('apim portalsetting signin', apim_sign_in_settings, client_factory=cf_sign_in_settings) as g:
        g.custom_command('create', 'create_apim_portalsetting_signin')
        g.custom_command('update', 'update_apim_portalsetting_signin')
        g.custom_command('show', 'show_apim_portalsetting_signin')

    from ._client_factory import cf_sign_up_settings
    apim_sign_up_settings = CliCommandType(
        operations_tmpl='azure.mgmt.apim.sign_up_settings_operations#SignUpSettingsOperations.{}',
        client_factory=cf_sign_up_settings)
    with self.command_group('apim portalsetting signup', apim_sign_up_settings, client_factory=cf_sign_up_settings) as g:
        g.custom_command('create', 'create_apim_portalsetting_signup')
        g.custom_command('update', 'update_apim_portalsetting_signup')
        g.custom_command('show', 'show_apim_portalsetting_signup')

    from ._client_factory import cf_delegation_settings
    apim_delegation_settings = CliCommandType(
        operations_tmpl='azure.mgmt.apim.delegation_settings_operations#DelegationSettingsOperations.{}',
        client_factory=cf_delegation_settings)
    with self.command_group('apim portalsetting delegation', apim_delegation_settings, client_factory=cf_delegation_settings) as g:
        g.custom_command('create', 'create_apim_portalsetting_delegation')
        g.custom_command('update', 'update_apim_portalsetting_delegation')
        g.custom_command('show', 'show_apim_portalsetting_delegation')

    from ._client_factory import cf_product
    apim_product = CliCommandType(
        operations_tmpl='azure.mgmt.apim.product_operations#ProductOperations.{}',
        client_factory=cf_product)
    with self.command_group('apim product', apim_product, client_factory=cf_product) as g:
        g.custom_command('create', 'create_apim_product')
        g.custom_command('update', 'update_apim_product')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_product')
        g.custom_command('show', 'show_apim_product')

    from ._client_factory import cf_product_api
    apim_product_api = CliCommandType(
        operations_tmpl='azure.mgmt.apim.product_api_operations#ProductApiOperations.{}',
        client_factory=cf_product_api)
    with self.command_group('apim product api', apim_product_api, client_factory=cf_product_api) as g:
        g.custom_command('create', 'create_apim_product_api')
        g.custom_command('update', 'update_apim_product_api')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_product_api')

    from ._client_factory import cf_product_group
    apim_product_group = CliCommandType(
        operations_tmpl='azure.mgmt.apim.product_group_operations#ProductGroupOperations.{}',
        client_factory=cf_product_group)
    with self.command_group('apim product group', apim_product_group, client_factory=cf_product_group) as g:
        g.custom_command('create', 'create_apim_product_group')
        g.custom_command('update', 'update_apim_product_group')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_product_group')

    from ._client_factory import cf_product_policy
    apim_product_policy = CliCommandType(
        operations_tmpl='azure.mgmt.apim.product_policy_operations#ProductPolicyOperations.{}',
        client_factory=cf_product_policy)
    with self.command_group('apim product policy', apim_product_policy, client_factory=cf_product_policy) as g:
        g.custom_command('create', 'create_apim_product_policy')
        g.custom_command('update', 'update_apim_product_policy')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_product_policy')
        g.custom_command('show', 'show_apim_product_policy')

    from ._client_factory import cf_property
    apim_property = CliCommandType(
        operations_tmpl='azure.mgmt.apim.property_operations#PropertyOperations.{}',
        client_factory=cf_property)
    with self.command_group('apim property', apim_property, client_factory=cf_property) as g:
        g.custom_command('create', 'create_apim_property')
        g.custom_command('update', 'update_apim_property')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_property')
        g.custom_command('show', 'show_apim_property')

    from ._client_factory import cf_subscription
    apim_subscription = CliCommandType(
        operations_tmpl='azure.mgmt.apim.subscription_operations#SubscriptionOperations.{}',
        client_factory=cf_subscription)
    with self.command_group('apim subscription', apim_subscription, client_factory=cf_subscription) as g:
        g.custom_command('create', 'create_apim_subscription')
        g.custom_command('update', 'update_apim_subscription')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_subscription')
        g.custom_command('show', 'show_apim_subscription')

    from ._client_factory import cf_user
    apim_user = CliCommandType(
        operations_tmpl='azure.mgmt.apim.user_operations#UserOperations.{}',
        client_factory=cf_user)
    with self.command_group('apim user', apim_user, client_factory=cf_user) as g:
        g.custom_command('create', 'create_apim_user')
        g.custom_command('update', 'update_apim_user')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_apim_user')
        g.custom_command('show', 'show_apim_user')
