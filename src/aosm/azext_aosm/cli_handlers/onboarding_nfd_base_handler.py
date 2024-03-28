# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azext_aosm.cli_handlers.onboarding_base_handler import OnboardingBaseCLIHandler


class OnboardingNFDBaseCLIHandler(OnboardingBaseCLIHandler):
    """Abstract base class for NFD CLI handlers."""

    @property
    def default_config_file_name(self) -> str:
        """Get the default configuration file name."""
        raise NotImplementedError

    def build_base_bicep(self):
        # TODO: Implement
        raise NotImplementedError
