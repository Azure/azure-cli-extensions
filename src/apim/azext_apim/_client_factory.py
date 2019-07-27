# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_api(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.api_operations import ApiOperations
    return get_mgmt_service_client(cli_ctx, ApiOperations)

def cf_api_release(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.api_release_operations import ApiReleaseOperations
    return get_mgmt_service_client(cli_ctx, ApiReleaseOperations)

def cf_api_operation(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.api_operation_operations import ApiOperationOperations
    return get_mgmt_service_client(cli_ctx, ApiOperationOperations)

def cf_api_operation_policy(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.api_operation_policy_operations import ApiOperationPolicyOperations
    return get_mgmt_service_client(cli_ctx, ApiOperationPolicyOperations)

def cf_tag(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.tag_operations import TagOperations
    return get_mgmt_service_client(cli_ctx, TagOperations)

def cf_api_policy(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.api_policy_operations import ApiPolicyOperations
    return get_mgmt_service_client(cli_ctx, ApiPolicyOperations)

def cf_api_schema(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.api_schema_operations import ApiSchemaOperations
    return get_mgmt_service_client(cli_ctx, ApiSchemaOperations)

def cf_api_diagnostic(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.api_diagnostic_operations import ApiDiagnosticOperations
    return get_mgmt_service_client(cli_ctx, ApiDiagnosticOperations)

def cf_api_issue(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.api_issue_operations import ApiIssueOperations
    return get_mgmt_service_client(cli_ctx, ApiIssueOperations)

def cf_api_issue_comment(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.api_issue_comment_operations import ApiIssueCommentOperations
    return get_mgmt_service_client(cli_ctx, ApiIssueCommentOperations)

def cf_api_issue_attachment(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.api_issue_attachment_operations import ApiIssueAttachmentOperations
    return get_mgmt_service_client(cli_ctx, ApiIssueAttachmentOperations)

def cf_api_tag_description(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.api_tag_description_operations import ApiTagDescriptionOperations
    return get_mgmt_service_client(cli_ctx, ApiTagDescriptionOperations)

def cf_api_version_set(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.api_version_set_operations import ApiVersionSetOperations
    return get_mgmt_service_client(cli_ctx, ApiVersionSetOperations)

def cf_authorization_server(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.authorization_server_operations import AuthorizationServerOperations
    return get_mgmt_service_client(cli_ctx, AuthorizationServerOperations)

def cf_backend(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.backend_operations import BackendOperations
    return get_mgmt_service_client(cli_ctx, BackendOperations)

def cf_cache(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.cache_operations import CacheOperations
    return get_mgmt_service_client(cli_ctx, CacheOperations)

def cf_certificate(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.certificate_operations import CertificateOperations
    return get_mgmt_service_client(cli_ctx, CertificateOperations)

def cf_api_management_service(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.api_management_service_operations import ApiManagementServiceOperations
    return get_mgmt_service_client(cli_ctx, ApiManagementServiceOperations)

def cf_diagnostic(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.diagnostic_operations import DiagnosticOperations
    return get_mgmt_service_client(cli_ctx, DiagnosticOperations)

def cf_email_template(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.email_template_operations import EmailTemplateOperations
    return get_mgmt_service_client(cli_ctx, EmailTemplateOperations)

def cf_group(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.group_operations import GroupOperations
    return get_mgmt_service_client(cli_ctx, GroupOperations)

def cf_group_user(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.group_user_operations import GroupUserOperations
    return get_mgmt_service_client(cli_ctx, GroupUserOperations)

def cf_identity_provider(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.identity_provider_operations import IdentityProviderOperations
    return get_mgmt_service_client(cli_ctx, IdentityProviderOperations)

def cf_logger(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.logger_operations import LoggerOperations
    return get_mgmt_service_client(cli_ctx, LoggerOperations)

def cf_notification(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.notification_operations import NotificationOperations
    return get_mgmt_service_client(cli_ctx, NotificationOperations)

def cf_notification_recipient_user(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.notification_recipient_user_operations import NotificationRecipientUserOperations
    return get_mgmt_service_client(cli_ctx, NotificationRecipientUserOperations)

def cf_notification_recipient_email(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.notification_recipient_email_operations import NotificationRecipientEmailOperations
    return get_mgmt_service_client(cli_ctx, NotificationRecipientEmailOperations)

def cf_open_id_connect_provider(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.open_id_connect_provider_operations import OpenIdConnectProviderOperations
    return get_mgmt_service_client(cli_ctx, OpenIdConnectProviderOperations)

def cf_policy(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.policy_operations import PolicyOperations
    return get_mgmt_service_client(cli_ctx, PolicyOperations)

def cf_sign_in_settings(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.sign_in_settings_operations import SignInSettingsOperations
    return get_mgmt_service_client(cli_ctx, SignInSettingsOperations)

def cf_sign_up_settings(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.sign_up_settings_operations import SignUpSettingsOperations
    return get_mgmt_service_client(cli_ctx, SignUpSettingsOperations)

def cf_delegation_settings(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.delegation_settings_operations import DelegationSettingsOperations
    return get_mgmt_service_client(cli_ctx, DelegationSettingsOperations)

def cf_product(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.product_operations import ProductOperations
    return get_mgmt_service_client(cli_ctx, ProductOperations)

def cf_product_api(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.product_api_operations import ProductApiOperations
    return get_mgmt_service_client(cli_ctx, ProductApiOperations)

def cf_product_group(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.product_group_operations import ProductGroupOperations
    return get_mgmt_service_client(cli_ctx, ProductGroupOperations)

def cf_product_policy(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.product_policy_operations import ProductPolicyOperations
    return get_mgmt_service_client(cli_ctx, ProductPolicyOperations)

def cf_property(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.property_operations import PropertyOperations
    return get_mgmt_service_client(cli_ctx, PropertyOperations)

def cf_subscription(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.subscription_operations import SubscriptionOperations
    return get_mgmt_service_client(cli_ctx, SubscriptionOperations)

def cf_user(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement.operations.user_operations import UserOperations
    return get_mgmt_service_client(cli_ctx, UserOperations)
