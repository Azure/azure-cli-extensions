# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=protected-access,duplicate-code

"""
This code inherits the auto-generated code for fabric rotate-certificate command, and adds
custom error formatting.
"""

from azure.core.exceptions import HttpResponseError

from azext_managednetworkfabric.aaz.latest.networkfabric.fabric import (
    RotateCertificate as _RotateCertificateCommand,
)
from azext_managednetworkfabric.operations.error_format import ErrorFormat


class RotateCertificateCommand(_RotateCertificateCommand):
    """Custom class for networkfabric fabric rotate-certificate"""

    def _handler(self, command_args):
        poller = super()._handler(command_args)
        if poller is None:
            return None
        if self.ctx.args.no_wait:
            return poller
        try:
            return poller.result()
        except HttpResponseError as e:
            ErrorFormat.handle_lro_error(e)

    def _output(self, *args, **kwargs):
        return ErrorFormat._output(self, *args, **kwargs)
