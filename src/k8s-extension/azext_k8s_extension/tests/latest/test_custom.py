# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from typing import no_type_check
import unittest

from .MockClasses import MockCLIContext, MockCommand
from azext_k8s_extension.custom import is_dogfood_cluster


class TestIsDogfoodCluster(unittest.TestCase):
    def test_dogfood_cluster(self):
        cmd = MockCommand()
        cmd.cli_ctx.cloud.endpoints.resource_manager = (
            "https://api-dogfood.resources.windows-int.net"
        )
        assert is_dogfood_cluster(cmd)

    def test_dogfood_cluster_with_slash(self):
        cmd = MockCommand()
        cmd.cli_ctx.cloud.endpoints.resource_manager = (
            "https://api-dogfood.resources.windows-int.net/"
        )
        assert is_dogfood_cluster(cmd)

    def test_longer_hostname(self):
        cmd = MockCommand()
        cmd.cli_ctx.cloud.endpoints.resource_manager = (
            "https://api-dogfood.resources.windows-int.otherwebsite.net/"
        )
        assert not is_dogfood_cluster(cmd)

    def malformed_url(self):
        cmd = MockCommand()
        cmd.cli_ctx.cloud.endpoints.resource_manager = "htmalformed~2987493"
        assert not is_dogfood_cluster(cmd)

    def test_prod_cluster(self):
        cmd = MockCommand()
        cmd.cli_ctx.cloud.endpoints.resource_manager = "https://management.azure.com"
        assert not is_dogfood_cluster(cmd)
