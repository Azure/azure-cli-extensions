# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
This custom code inherits the auto-generated code for Cluster update,
disables the --identity parameter and adds the --mi-user-assigned and --mi-system-assigned parameters
"""

from azext_networkcloud.aaz.latest.networkcloud.cluster._update import Update as _Update
from azure.cli.core.aaz import register_callback

from ..common_analyticsoutputsettings import AnalyticsOutputSettings
from ..common_commandoutputsettings import CommandOutputSettings
from ..common_managedidentity import ManagedIdentity
from ..common_secretarchivesettings import SecretArchiveSettings


class Update(_Update):
    """Custom class for update operation of Cluster"""

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        return ManagedIdentity.build_arguments_schema(args_schema)

    @register_callback
    def pre_operations(self):
        ManagedIdentity.pre_operations_update(self.ctx.args)
        CommandOutputSettings.pre_operations_update(self.ctx.args)
        AnalyticsOutputSettings.pre_operations_update(self.ctx.args)
        SecretArchiveSettings.pre_operations_create(self.ctx.args)
