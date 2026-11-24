# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------

"""Network Fabric run-validation customization."""

from azext_managednetworkfabric.aaz.latest.networkfabric.fabric import (
    RunValidation as _RunValidation,
)
from azext_managednetworkfabric.operations.run_validation import (
    RunValidationCommandConfig,
    RunValidationContent,
)


class RunValidation(RunValidationCommandConfig, _RunValidation):
    """Support file-based and inline device command configurations."""

    _args_schema = None

    class NetworkFabricsRunValidation(
        RunValidationContent, _RunValidation.NetworkFabricsRunValidation
    ):
        """Serialize the complete device command configuration."""
