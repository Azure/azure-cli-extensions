# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_apim(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.apimanagement import ApiManagementClient
    return get_mgmt_service_client(cli_ctx, ApiManagementClient)


def cf_api(cli_ctx, *_):
    return cf_apim(cli_ctx).api


def cf_api_release(cli_ctx, *_):
    return cf_apim(cli_ctx).api_release


def cf_api_operation(cli_ctx, *_):
    return cf_apim(cli_ctx).api_operation


def cf_api_operation_policy(cli_ctx, *_):
    return cf_apim(cli_ctx).api_operation_policy


def cf_tag(cli_ctx, *_):
    return cf_apim(cli_ctx).tag


def cf_api_policy(cli_ctx, *_):
    return cf_apim(cli_ctx).api_policy


def cf_api_schema(cli_ctx, *_):
    return cf_apim(cli_ctx).api_schema


def cf_api_diagnostic(cli_ctx, *_):
    return cf_apim(cli_ctx).api_diagnostic


def cf_api_issue(cli_ctx, *_):
    return cf_apim(cli_ctx).api_issue


def cf_api_issue_comment(cli_ctx, *_):
    return cf_apim(cli_ctx).api_issue_comment


def cf_api_issue_attachment(cli_ctx, *_):
    return cf_apim(cli_ctx).api_issue_attachment


def cf_api_tag_description(cli_ctx, *_):
    return cf_apim(cli_ctx).api_tag_description


def cf_api_version_set(cli_ctx, *_):
    return cf_apim(cli_ctx).api_version_set


def cf_authorization_server(cli_ctx, *_):
    return cf_apim(cli_ctx).authorization_server


def cf_backend(cli_ctx, *_):
    return cf_apim(cli_ctx).backend


def cf_cache(cli_ctx, *_):
    return cf_apim(cli_ctx).cache


def cf_certificate(cli_ctx, *_):
    return cf_apim(cli_ctx).certificate


def cf_api_management_service(cli_ctx, *_):
    return cf_apim(cli_ctx).api_management_service


def cf_diagnostic(cli_ctx, *_):
    return cf_apim(cli_ctx).diagnostic


def cf_email_template(cli_ctx, *_):
    return cf_apim(cli_ctx).email_template


def cf_group(cli_ctx, *_):
    return cf_apim(cli_ctx).group


def cf_group_user(cli_ctx, *_):
    return cf_apim(cli_ctx).group_user


def cf_identity_provider(cli_ctx, *_):
    return cf_apim(cli_ctx).identity_provider


def cf_logger(cli_ctx, *_):
    return cf_apim(cli_ctx).logger


def cf_notification(cli_ctx, *_):
    return cf_apim(cli_ctx).notification


def cf_notification_recipient_user(cli_ctx, *_):
    return cf_apim(cli_ctx).notification_recipient_user


def cf_notification_recipient_email(cli_ctx, *_):
    return cf_apim(cli_ctx).notification_recipient_email


def cf_open_id_connect_provider(cli_ctx, *_):
    return cf_apim(cli_ctx).open_id_connect_provider


def cf_policy(cli_ctx, *_):
    return cf_apim(cli_ctx).policy


def cf_sign_in_settings(cli_ctx, *_):
    return cf_apim(cli_ctx).sign_in_settings


def cf_sign_up_settings(cli_ctx, *_):
    return cf_apim(cli_ctx).sign_up_settings


def cf_delegation_settings(cli_ctx, *_):
    return cf_apim(cli_ctx).delegation_settings


def cf_product(cli_ctx, *_):
    return cf_apim(cli_ctx).product


def cf_product_api(cli_ctx, *_):
    return cf_apim(cli_ctx).product_api


def cf_product_group(cli_ctx, *_):
    return cf_apim(cli_ctx).product_group


def cf_product_policy(cli_ctx, *_):
    return cf_apim(cli_ctx).product_policy


def cf_property(cli_ctx, *_):
    return cf_apim(cli_ctx).property


def cf_subscription(cli_ctx, *_):
    return cf_apim(cli_ctx).subscription


def cf_user(cli_ctx, *_):
    return cf_apim(cli_ctx).user
