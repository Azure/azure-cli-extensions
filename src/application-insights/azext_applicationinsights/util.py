# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from msrestazure.tools import is_valid_resource_id, parse_resource_id
from azext_applicationinsights._client_factory import cf_components


def get_id_from_azure_resource(cli_ctx, app):
    if is_valid_resource_id(app):
        parsed = parse_resource_id(app)
        resource_group, name = parsed["resource_group"], parsed["name"]
        return cf_components(cli_ctx, None).get(resource_group, name).app_id
    return app
