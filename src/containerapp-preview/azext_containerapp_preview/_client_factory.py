# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from ._utils import (_get_azext_containerapp_module)


def handle_raw_exception(e):
    azext_client_factory = _get_azext_containerapp_module("azext_containerapp._client_factory")
    return azext_client_factory.handle_raw_exception(e)
