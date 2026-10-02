# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from knack.log import get_logger
from azure.cli.core.aaz import has_value
from azure.cli.core.azclierror import InvalidArgumentValueError

from azext_workload_manager.aaz.latest.workload_manager.workload_space.runtime_binding import (
    Create as _RuntimeBindingCreate,
)


logger = get_logger(__name__)


class RuntimeBindingCreate(_RuntimeBindingCreate):

    def pre_operations(self):
        args = self.ctx.args
        if has_value(args.managed) and has_value(args.referenced):
            raise InvalidArgumentValueError(
                "Specify exactly one of --managed or --referenced."
            )

        execution_identity = args.identity_profile.execution_identity
        if has_value(execution_identity.referenced) and has_value(execution_identity.service_managed):
            raise InvalidArgumentValueError(
                "Specify exactly one execution identity variant: referenced or service-managed."
            )
