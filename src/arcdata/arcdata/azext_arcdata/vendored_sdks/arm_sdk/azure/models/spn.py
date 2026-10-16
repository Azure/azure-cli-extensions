# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------


class Spn(object):
    authority = ""
    tenant_id = ""
    client_id = ""
    client_secret = ""

    def __init__(self, **entries):
        self.__dict__.update(entries)
