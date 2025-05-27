# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: skip-file
# flake8: noqa


def load_command_table(self, _):
    with self.command_group("remote-rendering-account"):
        from .custom import RemoteRenderingCreate, RemoteRenderingKeyRenew

        self.command_table["remote-rendering-account create"] = RemoteRenderingCreate(
            loader=self
        )
        self.command_table["remote-rendering-account key renew"] = (
            RemoteRenderingKeyRenew(loader=self)
        )
