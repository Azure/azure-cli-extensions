# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from abc import ABC, abstractmethod
from pathlib import Path

from azext_aosm.common.command_context import CommandContext
from azext_aosm.configuration_models.common_parameters_config import (
    BaseCommonParametersConfig,
)


class BaseDefinitionElement(ABC):
    """Base element definition."""

    def __init__(self, path: Path, only_delete_on_clean: bool):
        self.path = path
        self.only_delete_on_clean = only_delete_on_clean

    @abstractmethod
    def deploy(
        self, config: BaseCommonParametersConfig, command_context: CommandContext
    ):
        """Deploy the element."""
        return NotImplementedError

    @abstractmethod
    def delete(
        self, config: BaseCommonParametersConfig, command_context: CommandContext
    ):
        """Delete the element."""
        return NotImplementedError
