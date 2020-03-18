# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_blueprint(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .vendored_sdks.blueprint import BlueprintManagementClient
    return get_mgmt_service_client(cli_ctx, BlueprintManagementClient, subscription_bound=False)


def cf_blueprints(cli_ctx, *_):
    return cf_blueprint(cli_ctx).blueprints


def cf_artifacts(cli_ctx, *_):
    return cf_blueprint(cli_ctx).artifacts


def cf_published_blueprints(cli_ctx, *_):
    return cf_blueprint(cli_ctx).published_blueprints


def cf_published_artifacts(cli_ctx, *_):
    return cf_blueprint(cli_ctx).published_artifacts


def cf_assignments(cli_ctx, *_):
    return cf_blueprint(cli_ctx).assignments


def cf_assignment_operations(cli_ctx, *_):
    return cf_blueprint(cli_ctx).assignment_operations
