# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import annotations

import importlib
import sys
from types import SimpleNamespace

import pytest

MODULE_PATH = "azext_aks_agent.tests.evals.classifier"


@pytest.fixture(autouse=True)
def _reset_classifier_module(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("ENABLE_CLASSIFIER", raising=False)
    monkeypatch.delenv("CLASSIFIER_MODEL", raising=False)
    monkeypatch.delenv("MODEL", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("AZURE_API_KEY", raising=False)
    monkeypatch.delenv("AZURE_API_BASE", raising=False)
    monkeypatch.delenv("AZURE_API_VERSION", raising=False)
    monkeypatch.delenv("CLASSIFIER_EVALUATION", raising=False)
    if MODULE_PATH in sys.modules:
        del sys.modules[MODULE_PATH]
    yield
    if MODULE_PATH in sys.modules:
        del sys.modules[MODULE_PATH]


def test_evaluate_correctness_disabled(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ENABLE_CLASSIFIER", "false")
    monkeypatch.setenv("AZURE_API_BASE", "https://example.openai.azure.com")
    monkeypatch.setenv("AZURE_API_KEY", "key")
    monkeypatch.setenv("AZURE_API_VERSION", "2024-02-15-preview")
    classifier = importlib.import_module(MODULE_PATH)
    result = classifier.evaluate_correctness(
        expected_elements=["foo"], output="bar", evaluation_type="strict"
    )
    assert result is None


def test_evaluate_correctness_success(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ENABLE_CLASSIFIER", "true")
    monkeypatch.setenv("MODEL", "azure/my-deployment")
    monkeypatch.setenv("CLASSIFIER_MODEL", "azure/my-deployment")
    monkeypatch.setenv("AZURE_API_BASE", "https://example.openai.azure.com")
    monkeypatch.setenv("AZURE_API_KEY", "key")
    monkeypatch.setenv("AZURE_API_VERSION", "2024-02-15-preview")

    stub_eval = SimpleNamespace(score=1, metadata={"rationale": "looks good"})

    class StubClassifier:
        def __init__(self, **_: object) -> None:
            self.calls: list[tuple] = []

        def __call__(self, **_: object):
            return stub_eval

    def fake_create_client():
        return object(), "my-deployment"

    classifier = importlib.import_module(MODULE_PATH)
    classifier._client_initialised = False
    classifier._client_available = False
    classifier._AUTOEVALS_AVAILABLE = True  # type: ignore[attr-defined]
    monkeypatch.setattr(classifier, "create_llm_client", fake_create_client)
    monkeypatch.setattr(classifier, "LLMClassifier", StubClassifier)
    monkeypatch.setattr(classifier, "autoevals_init", lambda client: None)
    monkeypatch.setattr(classifier, "wrap_openai", lambda client: client)

    result = classifier.evaluate_correctness(
        expected_elements=["foo"],
        output="foo bar",
        evaluation_type="strict",
    )
    assert result is stub_eval
