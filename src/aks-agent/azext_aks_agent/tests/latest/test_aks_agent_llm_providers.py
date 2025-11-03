# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest

from azext_aks_agent.agent.llm_providers import (
    PROVIDER_REGISTRY,
    AnthropicProvider,
    AzureProvider,
    GeminiProvider,
    OpenAICompatibleProvider,
    OpenAIProvider,
)


class TestLLMProviders(unittest.TestCase):
    def test_provider_registry(self):
        """Test that provider registry maps names to correct classes."""
        self.assertIs(PROVIDER_REGISTRY['azure'], AzureProvider)
        self.assertIs(PROVIDER_REGISTRY['openai'], OpenAIProvider)
        self.assertIs(PROVIDER_REGISTRY['anthropic'], AnthropicProvider)
        self.assertIs(PROVIDER_REGISTRY['gemini'], GeminiProvider)
        self.assertIs(PROVIDER_REGISTRY['openai_compatible'], OpenAICompatibleProvider)

    def test_provider_choices_numbered(self):
        """Test numbered provider choices are correct and ordered."""
        from azext_aks_agent.agent.llm_providers import (
            _available_providers,
            _provider_choices_numbered,
        )
        choices = _provider_choices_numbered()
        providers = _available_providers()
        for idx, name in choices:
            self.assertEqual(name, providers[idx - 1]().readable_name)


if __name__ == '__main__':
    unittest.main()
