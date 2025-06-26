# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from knack.help_files import helps


def get_marketplace_subscription_help():
    helps[
        "ml marketplace-subscription"
    ] = """
        type: group
        short-summary: Manage Azure ML marketplace subscriptions.
    """
    helps[
        "ml marketplace-subscription list"
    ] = """
        type: command
        short-summary: List marketplace subscriptions in a workspace.
    """
    helps[
        "ml marketplace-subscription show"
    ] = """
        type: command
        short-summary: Shows details for a marketplace subscription.
    """
    helps[
        "ml marketplace-subscription create"
    ] = """
        type: command
        short-summary: Create a marketplace subscription.
    """
    helps[
        "ml marketplace-subscription delete"
    ] = """
        type: command
        short-summary: Delete a marketplace subscription.
    """
