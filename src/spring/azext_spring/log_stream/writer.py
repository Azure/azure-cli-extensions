# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


class DefaultWriter:  # pylint: disable=too-few-public-methods
    def write(self, data, end='', file=None):
        print(data, end=end, file=file)


class PrefixWriter(DefaultWriter):  # pylint: disable=too-few-public-methods
    def __init__(self, prefix):
        self.prefix = prefix

    def write(self, data, end='', file=None):
        super().write("{} {}".format(self.prefix, data), end=end, file=file)
