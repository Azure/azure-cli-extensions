# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import annotations

import pytest
from pytest import StashKey


BRAINTRUST_LAST_LINK = StashKey[str]()


@pytest.fixture
def aks_skip_setup(pytestconfig: pytest.Config) -> bool:
    return bool(pytestconfig.getoption("aks_skip_setup"))


@pytest.fixture
def aks_skip_cleanup(pytestconfig: pytest.Config) -> bool:
    return bool(pytestconfig.getoption("aks_skip_cleanup"))


@pytest.fixture(autouse=True)
def aks_braintrust_link(request: pytest.FixtureRequest) -> None:
    yield
    if not request.node.get_closest_marker('aks_eval'):
        return

    span_id = None
    root_span_id = None
    url = None
    for key, value in getattr(request.node, 'user_properties', []):
        if key == 'braintrust_span_id':
            span_id = value
        elif key == 'braintrust_root_span_id':
            root_span_id = value
        elif key == 'braintrust_experiment_url':
            url = value

    if not url:
        return

    if span_id and root_span_id and '?' not in url:
        url = f"{url}?r={span_id}&s={root_span_id}"

    clickable_url = f"\u001b]8;;{url}\u001b\\{url}\u001b]8;;\u001b\\"
    request.config.stash[BRAINTRUST_LAST_LINK] = clickable_url


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    try:
        link = session.config.stash[BRAINTRUST_LAST_LINK]
    except KeyError:
        return
    if not link:
        return

    print(f"\n🔍 Braintrust: {link}\n")
