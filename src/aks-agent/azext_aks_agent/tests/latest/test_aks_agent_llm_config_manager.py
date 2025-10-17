# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import tempfile
import unittest
from azext_aks_agent.agent.llm_config_manager import LLMConfigManager


class TestLLMConfigManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary config file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.config_path = self.temp_file.name
        self.manager = LLMConfigManager(config_path=self.config_path)

    def tearDown(self):
        # Remove the temporary file after each test
        if os.path.exists(self.config_path):
            os.unlink(self.config_path)

    def test_save_and_load(self):
        params = {"MODEL_NAME": "test-model", "param1": "value1"}
        self.manager.save("openai", params)
        loaded = self.manager.load()
        self.assertIn("llms", loaded)
        self.assertEqual(loaded["llms"][0]["MODEL_NAME"], "test-model")
        self.assertEqual(loaded["llms"][0]["provider"], "openai")

    def test_get_list_and_latest(self):
        params1 = {"MODEL_NAME": "model1", "param": "v1"}
        params2 = {"MODEL_NAME": "model2", "param": "v2"}
        self.manager.save("openai", params1)
        self.manager.save("openai", params2)
        model_list = self.manager.get_list()
        self.assertEqual(len(model_list), 2)
        latest = self.manager.get_latest()
        self.assertEqual(latest["MODEL_NAME"], "model2")

    def test_get_specific(self):
        params1 = {"MODEL_NAME": "modelA", "param": "foo"}
        params2 = {"MODEL_NAME": "modelB", "param": "bar"}
        self.manager.save("openai", params1)
        self.manager.save("openai", params2)
        specific = self.manager.get_specific("openai", "modelA")
        self.assertEqual(specific["param"], "foo")
        with self.assertRaises(ValueError):
            self.manager.get_specific("openai", "not_exist")

    def test_is_config_complete(self):
        config = {"key1": "val1", "key2": "val2"}
        schema = {
            "key1": {"validator": lambda v: v == "val1"},
            "key2": {"validator": lambda v: v == "val2"}
        }
        self.assertTrue(self.manager.is_config_complete(config, schema))
        config["key2"] = "wrong"
        self.assertFalse(self.manager.is_config_complete(config, schema))

    def test_load_returns_empty_when_file_missing(self):
        # Remove file and test load fallback
        os.unlink(self.config_path)
        self.assertEqual(self.manager.load(), {})


if __name__ == '__main__':
    unittest.main()
