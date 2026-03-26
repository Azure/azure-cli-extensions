# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def load_arguments(self, _):

    load_file_argument(self, _)


def load_file_argument(self, _):
    with self.argument_context('support in-subscription file upload') as c:
        c.argument('file-workspace-name', help='File Workspace Name', required=True)
        c.argument('file-path', help='File Path', required=True)

    with self.argument_context('support no-subscription file upload') as c:
        c.argument('file-workspace-name', help='File Workspace Name', required=True)
        c.argument('file-path', help='File Path', required=True)
