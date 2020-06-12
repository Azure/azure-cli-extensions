# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

DEFAULT_SERVICE_DOMAIN = "online.visualstudio.com"

CONFIG_SECTION = 'codespaces'
KEY_RESOURCE_PROVIDER_API_VERSION = 'resource_provider_api_version'
KEY_SERVICE_DOMAIN = 'service_domain'


def get_rp_api_version(cli_ctx):
    return cli_ctx.config.get(CONFIG_SECTION, KEY_RESOURCE_PROVIDER_API_VERSION, fallback=None)


def get_service_domain(cli_ctx):
    return cli_ctx.config.get(CONFIG_SECTION, KEY_SERVICE_DOMAIN, fallback=None) or DEFAULT_SERVICE_DOMAIN


def get_current_config(cli_ctx):
    return cli_ctx.config.items(CONFIG_SECTION)


def set_rp_api_version(cli_ctx, val):
    cli_ctx.config.set_value(CONFIG_SECTION, KEY_RESOURCE_PROVIDER_API_VERSION, val)


def set_service_domain(cli_ctx, val):
    cli_ctx.config.set_value(CONFIG_SECTION, KEY_SERVICE_DOMAIN, val)
