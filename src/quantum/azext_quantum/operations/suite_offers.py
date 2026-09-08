# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from .._client_factory import cf_suite_offers


def list_suite_offers(cmd):
    """
    List the Azure Quantum suite offers available to the current subscription.
    """
    client = cf_suite_offers(cmd.cli_ctx)
    return client.list_by_subscription()
