# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Tests for end-to-end correlation id propagation in `az connectedk8s proxy`.

Covers:
  * ``utils.ensure_correlation_id`` — mints one ``uuid.uuid4()`` per command
    session, stamps it into the az-cli header bag for outbound ARM calls,
    and is idempotent (subsequent calls in the same session reuse the same
    id). ARM honors the client-supplied id and echoes it back, so the same
    value flows through ARM Geneva, arcProxy, Relay, and ConnectedProxyAgent
    logs end to end.
  * ``proxylogic.get_cluster_user_credentials`` — when called with a
    ``correlation_id``, forwards it to the SDK as a ``headers=`` kwarg so
    the outbound ARM request carries ``x-ms-correlation-request-id``.
  * ``clientproxyhelper._utils.make_api_call_with_retries`` — when called
    with a ``correlation_id``, sends the ``x-ms-correlation-request-id``
    header on the outbound localhost request.

These are pure unit tests: no Azure, no live cluster, no recordings.
"""

import os
import re
import sys
import uuid
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

import azext_connectedk8s._constants as consts
from azext_connectedk8s._utils import ensure_correlation_id
from azext_connectedk8s.clientproxyhelper._proxylogic import (
    get_cluster_user_credentials,
)
from azext_connectedk8s.clientproxyhelper._utils import (
    make_api_call_with_retries,
)

UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


def _make_cmd():
    cmd = MagicMock()
    cmd.cli_ctx.data = {}
    return cmd


# ---------------------------------------------------------------------------
# ensure_correlation_id
# ---------------------------------------------------------------------------


def test_ensure_correlation_id_mints_uuid4_when_header_absent():
    """With no upstream header, a fresh uuid4 must be minted and stamped.

    az-cli core does not stamp ``x-ms-correlation-request-id`` on outbound
    ARM requests today, so the CLI extension always mints. ARM honors and
    echoes the client-supplied id, which gives the customer one id end to
    end across CLI debug, ARM Geneva, arcProxy, Relay, and agent logs.
    """
    cmd = _make_cmd()

    cid = ensure_correlation_id(cmd, log_prefix="test")

    assert UUID_RE.match(cid), f"expected RFC 4122 uuid, got {cid!r}"
    assert cmd.cli_ctx.data["headers"][consts.Correlation_Request_Id_Header] == cid


def test_ensure_correlation_id_is_idempotent_within_session():
    cmd = _make_cmd()

    first = ensure_correlation_id(cmd, log_prefix="test")
    second = ensure_correlation_id(cmd, log_prefix="test")

    assert first == second
    assert cmd.cli_ctx.data["headers"][consts.Correlation_Request_Id_Header] == first


def test_ensure_correlation_id_reuses_existing_header_value():
    """If something upstream pre-populated the header bag, reuse that value."""
    cmd = _make_cmd()
    preset = str(uuid.uuid4())
    cmd.cli_ctx.data["headers"] = {
        consts.Correlation_Request_Id_Header: preset,
    }

    cid = ensure_correlation_id(cmd, log_prefix="test")

    assert cid == preset
    assert cmd.cli_ctx.data["headers"][consts.Correlation_Request_Id_Header] == preset


def test_ensure_correlation_id_creates_headers_dict_when_missing():
    cmd = _make_cmd()
    assert "headers" not in cmd.cli_ctx.data

    cid = ensure_correlation_id(cmd, log_prefix="test")

    assert "headers" in cmd.cli_ctx.data
    assert cmd.cli_ctx.data["headers"][consts.Correlation_Request_Id_Header] == cid


def test_ensure_correlation_id_distinct_across_sessions():
    """Each command session gets its own uuid — sessions never share an id."""
    cid_a = ensure_correlation_id(_make_cmd(), log_prefix="test")
    cid_b = ensure_correlation_id(_make_cmd(), log_prefix="test")

    assert cid_a != cid_b
    assert UUID_RE.match(cid_a)
    assert UUID_RE.match(cid_b)


# ---------------------------------------------------------------------------
# get_cluster_user_credentials — ARM call site
# ---------------------------------------------------------------------------


def test_get_cluster_user_credentials_forwards_correlation_id_to_sdk():
    """The SDK call must receive ``headers={x-ms-correlation-request-id: <cid>}``.

    This is what makes ARM honor and echo the client-supplied id.
    """
    fake_client = MagicMock()
    cid = str(uuid.uuid4())

    get_cluster_user_credentials(
        client=fake_client,
        resource_group_name="rg",
        cluster_name="cluster",
        auth_method="AAD",
        correlation_id=cid,
    )

    fake_client.list_cluster_user_credential.assert_called_once()
    _, kwargs = fake_client.list_cluster_user_credential.call_args
    assert kwargs["headers"] == {consts.Correlation_Request_Id_Header: cid}


def test_get_cluster_user_credentials_omits_headers_when_no_correlation_id():
    """No correlation_id -> no ``headers`` kwarg (preserves prior behavior)."""
    fake_client = MagicMock()

    get_cluster_user_credentials(
        client=fake_client,
        resource_group_name="rg",
        cluster_name="cluster",
        auth_method="AAD",
    )

    fake_client.list_cluster_user_credential.assert_called_once()
    _, kwargs = fake_client.list_cluster_user_credential.call_args
    assert "headers" not in kwargs


# ---------------------------------------------------------------------------
# make_api_call_with_retries — localhost chokepoint
# ---------------------------------------------------------------------------


def test_make_api_call_with_retries_sends_correlation_header():
    """When a correlation_id is supplied, it MUST be on the outbound request."""
    cid = str(uuid.uuid4())
    fake_response = MagicMock()

    with patch(
        "azext_connectedk8s.clientproxyhelper._utils.requests.request",
        return_value=fake_response,
    ) as mock_request:
        result = make_api_call_with_retries(
            uri="https://localhost:1234/identity/at",
            data={"foo": "bar"},
            method="post",
            tls_verify=False,
            fault_type="test-fault",
            summary="test summary",
            cli_error="test cli error",
            clientproxy_process=MagicMock(),
            correlation_id=cid,
        )

    assert result is fake_response
    mock_request.assert_called_once()
    _, kwargs = mock_request.call_args
    assert kwargs["headers"] == {consts.Correlation_Request_Id_Header: cid}


def test_make_api_call_with_retries_omits_header_when_no_correlation_id():
    """No correlation_id -> headers is None (no behavior change for old callers)."""
    fake_response = MagicMock()

    with patch(
        "azext_connectedk8s.clientproxyhelper._utils.requests.request",
        return_value=fake_response,
    ) as mock_request:
        make_api_call_with_retries(
            uri="https://localhost:1234/identity/at",
            data={"foo": "bar"},
            method="post",
            tls_verify=False,
            fault_type="test-fault",
            summary="test summary",
            cli_error="test cli error",
            clientproxy_process=MagicMock(),
        )

    _, kwargs = mock_request.call_args
    assert kwargs["headers"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
