# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from types import SimpleNamespace

import pytest

from azure.cli.testsdk import ScenarioTest
from .utils import issue_cmd_with_param_missing
from ...operations.offerings import (
    _get_publisher_and_offer_from_provider_id,
    PUBLISHER_NOT_AVAILABLE,
    OFFER_NOT_AVAILABLE,
)


class QuantumOfferingsScenarioTest(ScenarioTest):

    def test_offerings_errors(self):
        issue_cmd_with_param_missing(self, "az quantum offerings accept-terms", "az quantum offerings accept-terms -p MyProviderId -k MySKU -l MyLocation\nOnce terms have been reviewed, accept the invoking this command.")
        issue_cmd_with_param_missing(self, "az quantum offerings show-terms", "az quantum offerings show-terms -p MyProviderId -k MySKU -l MyLocation\nUse a Provider Id and SKU from `az quantum offerings list` to review the terms.")


class QuantumOfferingsUnitTest(unittest.TestCase):

    def _make_provider(self, provider_id, managed_application):
        return SimpleNamespace(
            id=provider_id,
            properties=SimpleNamespace(managed_application=managed_application),
        )

    def test_get_publisher_and_offer_from_provider_id_returns_values(self):
        providers = [
            self._make_provider(
                "rigetti",
                SimpleNamespace(publisher_id="rigetti-computing", offer_id="rigetti-azure-basic"),
            ),
        ]

        self.assertEqual(
            _get_publisher_and_offer_from_provider_id(providers, "rigetti"),
            ("rigetti-computing", "rigetti-azure-basic"),
        )

    def test_get_publisher_and_offer_from_provider_id_matches_case_insensitively(self):
        providers = [
            self._make_provider(
                "Rigetti",
                SimpleNamespace(publisher_id="rigetti-computing", offer_id="rigetti-azure-basic"),
            ),
        ]

        self.assertEqual(
            _get_publisher_and_offer_from_provider_id(providers, "RIGETTI"),
            ("rigetti-computing", "rigetti-azure-basic"),
        )

    def test_get_publisher_and_offer_from_provider_id_returns_none_when_not_found(self):
        providers = [
            self._make_provider(
                "rigetti",
                SimpleNamespace(publisher_id="rigetti-computing", offer_id="rigetti-azure-basic"),
            ),
        ]

        self.assertEqual(
            _get_publisher_and_offer_from_provider_id(providers, "atom-boulder"),
            (None, None),
        )

    def test_get_publisher_and_offer_from_provider_id_handles_missing_managed_application(self):
        # V2-only providers (e.g. atom-boulder) have no legacy marketplace ManagedApplication
        # association at all; this must not raise and should be treated like the existing
        # "N/A" sentinel (no terms to accept) instead of crashing.
        providers = [self._make_provider("atom-boulder", None)]

        self.assertEqual(
            _get_publisher_and_offer_from_provider_id(providers, "atom-boulder"),
            (PUBLISHER_NOT_AVAILABLE, OFFER_NOT_AVAILABLE),
        )

