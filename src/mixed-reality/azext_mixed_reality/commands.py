# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


# pylint: disable=line-too-long
def load_command_table(self, _):

    with self.command_group('spatial-anchors-account'):
        from .custom import SpatialAnchorsCreate, SpatialAnchorsKeyRenew
        self.command_table['spatial-anchors-account create'] = SpatialAnchorsCreate(loader=self)
        self.command_table['spatial-anchors-account key renew'] = SpatialAnchorsKeyRenew(loader=self)

    with self.command_group('remote-rendering-account'):
        from .custom import RemoteRenderingCreate, RemoteRenderingKeyRenew
        self.command_table['remote-rendering-account create'] = RemoteRenderingCreate(loader=self)
        self.command_table['remote-rendering-account key renew'] = RemoteRenderingKeyRenew(loader=self)
