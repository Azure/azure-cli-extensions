# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import annotations

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("aks-agent-evals")
    group.addoption(
        "--skip-setup",
        action="store_true",
        dest="aks_skip_setup",
        default=False,
        help="Skip executing before_test commands in AKS Agent evals.",
    )
    group.addoption(
        "--skip-cleanup",
        action="store_true",
        dest="aks_skip_cleanup",
        default=False,
        help="Skip executing after_test commands in AKS Agent evals.",
    )
