# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
from unittest.mock import Mock
from azext_aks_preview.agentpool_decorator import AKSPreviewAgentPoolContext, AKSPreviewAgentPoolModels, AKSPreviewAgentPoolUpdateDecorator
from azure.cli.command_modules.acs.agentpool_decorator import AKSAgentPoolParamDict
from azure.cli.command_modules.acs._consts import AgentPoolDecoratorMode, DecoratorMode
from azure.cli.core.azclierror import InvalidArgumentValueError, MutuallyExclusiveArgumentError
from types import SimpleNamespace
import tempfile
import json

class TestLocalDNSProfile(unittest.TestCase):
    def setUp(self):
        self.cmd = Mock()
        self.models = Mock()
        self.models.AgentPoolLocalDNSProfile = lambda **kwargs: SimpleNamespace(**kwargs)
        self.agentpool_decorator_mode = AgentPoolDecoratorMode.STANDALONE

    def test_localdns_mode(self):
        ctx = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({
                "set_localdns": True,
                "localdns_mode": "preferred",
                "localdns_config": None
            }),
            self.models,
            DecoratorMode.UPDATE,
            self.agentpool_decorator_mode,
        )
        profile = ctx.get_localdns_profile()
        self.assertEqual(profile, {"mode": "preferred"})

    def test_localdns_config(self):
        config = {"mode": "required", "custom": "foo"}
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
            json.dump(config, f)
            f.flush()
            ctx = AKSPreviewAgentPoolContext(
                self.cmd,
                AKSAgentPoolParamDict({
                    "set_localdns": True,
                    "localdns_mode": None,
                    "localdns_config": f.name
                }),
                self.models,
                DecoratorMode.UPDATE,
                self.agentpool_decorator_mode,
            )
            profile = ctx.get_localdns_profile()
            self.assertEqual(profile, config)

    def test_localdns_validation(self):
        # Missing --set-localdns
        ctx = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({
                "set_localdns": False,
                "localdns_mode": "preferred",
                "localdns_config": None
            }),
            self.models,
            DecoratorMode.UPDATE,
            self.agentpool_decorator_mode,
        )
        with self.assertRaises(InvalidArgumentValueError):
            ctx.get_localdns_profile()
        # Both config and mode
        ctx = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({
                "set_localdns": True,
                "localdns_mode": "preferred",
                "localdns_config": "foo.json"
            }),
            self.models,
            DecoratorMode.UPDATE,
            self.agentpool_decorator_mode,
        )
        with self.assertRaises(MutuallyExclusiveArgumentError):
            ctx.get_localdns_profile()
        # Neither config nor mode
        ctx = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({
                "set_localdns": True,
                "localdns_mode": None,
                "localdns_config": None
            }),
            self.models,
            DecoratorMode.UPDATE,
            self.agentpool_decorator_mode,
        )
        with self.assertRaises(InvalidArgumentValueError):
            ctx.get_localdns_profile()

if __name__ == "__main__":
    unittest.main()
