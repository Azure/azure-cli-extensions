# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: skip-file

import os


class PrivateEndpointUtil:

    PUBLIC_NAMESPACE = "Microsoft.CleanRoom"

    PRIVATE_NAMESPACE = "Private.CleanRoom"

    PRIVATE_NAMESPACE_ENVIRONMENT_VARIABLE = "UsePrivateCleanRoomNamespace"

    @staticmethod
    def get_configured_namespace():
        use_private_namespace = os.getenv(
            PrivateEndpointUtil.PRIVATE_NAMESPACE_ENVIRONMENT_VARIABLE, "false"
        ).lower()

        if use_private_namespace == "true":
            return PrivateEndpointUtil.PRIVATE_NAMESPACE
        return PrivateEndpointUtil.PUBLIC_NAMESPACE
