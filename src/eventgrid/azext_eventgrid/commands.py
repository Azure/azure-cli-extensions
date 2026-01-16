# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-statements


def load_command_table(self, _):

    with self.command_group('eventgrid namespace'):
        from .custom import NamespaceListKey, NamespaceRegenerateKey
        self.command_table['eventgrid namespace list-key'] = NamespaceListKey(loader=self)
        self.command_table['eventgrid namespace regenerate-key'] = NamespaceRegenerateKey(loader=self)

    with self.command_group('eventgrid namespace ca-certificate'):
        from .custom import CaCertificateCreate, CaCertificateUpdate
        self.command_table['eventgrid namespace ca-certificate create'] = CaCertificateCreate(loader=self)
        self.command_table['eventgrid namespace ca-certificate update'] = CaCertificateUpdate(loader=self)
