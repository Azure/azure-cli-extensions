# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_support.custom import (
    FileWorkspaceCreateNoSubscription,
    FileWorkspaceCreateSubscription,
    CommunicationCreate,
    CommunicationNoSubscriptionCreate,
    TicketUpdateNoSubscription,
    TicketUpdate,
    TicketCreateNoSubscription,
    TicketCreate,
    TicketList,
    TicketListNoSubscription,
)


def load_command_table(self, _):
    self.command_table["support in-subscription tickets update"] = TicketUpdate(
        loader=self
    )
    self.command_table["support no-subscription tickets update"] = TicketUpdateNoSubscription(
        loader=self
    )
    self.command_table["support in-subscription tickets create"] = TicketCreate(
        loader=self
    )
    self.command_table["support no-subscription tickets create"] = TicketCreateNoSubscription(
        loader=self
    )
    self.command_table["support in-subscription communication create"] = CommunicationCreate(
        loader=self
    )
    self.command_table["support no-subscription communication create"] = CommunicationNoSubscriptionCreate(
        loader=self
    )
    self.command_table["support in-subscription tickets list"] = TicketList(
        loader=self
    )
    self.command_table["support no-subscription tickets list"] = TicketListNoSubscription(
        loader=self
    )
    with self.command_group("support no-subscription file") as g:
        g.custom_command("upload", "upload_files_no_subscription")

    with self.command_group("support in-subscription file") as g:
        g.custom_command("upload", "upload_files_in_subscription")

    self.command_table["support in-subscription file-workspace create"] = FileWorkspaceCreateSubscription(
        loader=self
    )
    self.command_table["support no-subscription file-workspace create"] = FileWorkspaceCreateNoSubscription(
        loader=self
    )
