# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import pytest

from azure.cli.testsdk import ScenarioTest
from .utils import issue_cmd_with_param_missing


class QuantumOfferingsScenarioTest(ScenarioTest):

    def test_offerings_errors(self):
        issue_cmd_with_param_missing(self, "az quantum offerings accept-terms", "az quantum offerings accept-terms -p MyProviderId -k MySKU -l MyLocation\nOnce terms have been reviewed, accept the invoking this command.")
        issue_cmd_with_param_missing(self, "az quantum offerings show-terms", "az quantum offerings show-terms -p MyProviderId -k MySKU -l MyLocation\nUse a Provider Id and SKU from `az quantum offerings list` to review the terms.")
