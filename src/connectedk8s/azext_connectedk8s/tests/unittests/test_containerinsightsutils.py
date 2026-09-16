# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Unit tests for the Container Insights proxy bypass in _containerinsightsutils.py."""

from __future__ import annotations

import os
import sys
from unittest.mock import MagicMock

import pytest
from azure.cli.core.azclierror import ValidationError
from kubernetes.client.models import V1ConfigMap, V1ObjectMeta
from kubernetes.client.rest import ApiException

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
import azext_connectedk8s._constants as consts
import azext_connectedk8s._containerinsightsutils as ciutils
import azext_connectedk8s._errors as errors
from azext_connectedk8s._containerinsightsutils import (
    create_container_insights_proxy_bypass_configmap,
    ensure_container_insights_proxy_bypass_configmap,
    find_active_proxy_bypass_setting,
    merge_proxy_bypass_into_agent_settings,
    remove_container_insights_proxy_bypass_configmap,
    remove_proxy_bypass_from_agent_settings,
    report_container_insights_configmap_failure,
    sync_container_insights_proxy_bypass_configmap,
)

ANNOTATION = consts.CI_ConfigMap_Proxy_Bypass_Annotation
SETTINGS_KEY = consts.CI_ConfigMap_Agent_Settings_Key

# Spelled out rather than built from the constants, so a change to what actually lands on the
# cluster has to be made here too instead of passing silently.
ENABLED = '[agent_settings.proxy_config]\n    ignore_proxy_settings = "true"'
DISABLED = '[agent_settings.proxy_config]\n    ignore_proxy_settings = "false"'


class _ApiError(Exception):
    """Stands in for ApiException, which the module identifies by its status code."""

    def __init__(self, status: int) -> None:
        super().__init__(f"api error {status}")
        self.status = status


def _configmap(
    agent_settings: str | None = None,
    annotated: bool = False,
    with_metadata: bool = True,
) -> V1ConfigMap:
    metadata = None
    if with_metadata:
        metadata = V1ObjectMeta(
            name=consts.CI_ConfigMap_Name,
            namespace=consts.CI_ConfigMap_Namespace,
            annotations={ANNOTATION: "azure-cli"} if annotated else {},
        )
    data = {} if agent_settings is None else {SETTINGS_KEY: agent_settings}
    return V1ConfigMap(metadata=metadata, data=data)


def _api(
    read_result: V1ConfigMap | None = None,
    read_error: Exception | None = None,
) -> MagicMock:
    api = MagicMock()
    if read_error is not None:
        api.read_namespaced_config_map.side_effect = read_error
    else:
        api.read_namespaced_config_map.return_value = read_result
    return api


def _written_body(api: MagicMock) -> V1ConfigMap:
    return api.replace_namespaced_config_map.call_args.kwargs["body"]


# ---------------- Tests for find_active_proxy_bypass_setting ----------------
@pytest.mark.parametrize(
    "agent_settings, expected",
    [
        # The setting inside proxy_config is the one that drives the bypass.
        (ENABLED, (0, 1)),
        # A section with no setting still reports its header, so one can be inserted.
        ('[agent_settings.proxy_config]\n    other = "1"', (0, None)),
        # The same setting name in another section is not a proxy bypass.
        ('[agent_settings.other]\n    ignore_proxy_settings = "true"', (None, None)),
        # Commented-out settings are inactive and must not be treated as a match.
        (
            '[agent_settings.proxy_config]\n    # ignore_proxy_settings = "true"',
            (0, None),
        ),
        # The header is matched with whitespace removed.
        ('[ agent_settings.proxy_config ]\n  ignore_proxy_settings = "true"', (0, 1)),
        # Nothing resembling a section.
        ("schema-version: v1", (None, None)),
        ("", (None, None)),
    ],
)
def test_find_active_proxy_bypass_setting(agent_settings, expected):
    assert find_active_proxy_bypass_setting(agent_settings.splitlines()) == expected


def test_find_active_proxy_bypass_setting_uses_the_section_it_sits_in():
    # The setting belongs to the header directly above it, not to the first one in the file.
    agent_settings = (
        "[agent_settings.proxy_config]\n"
        "[agent_settings.other]\n"
        "[agent_settings.proxy_config]\n"
        '    ignore_proxy_settings = "false"'
    )
    assert find_active_proxy_bypass_setting(agent_settings.splitlines()) == (2, 3)


# ---------------- Tests for merge_proxy_bypass_into_agent_settings ----------------
@pytest.mark.parametrize(
    "current, expected",
    [
        # Nothing configured yet: the whole section is written.
        ("", ENABLED),
        # Already bypassing: returned untouched, so re-running connect changes nothing.
        (ENABLED, ENABLED),
        # Spacing around the value does not hide an existing bypass.
        (
            '[agent_settings.proxy_config]\n    ignore_proxy_settings="true"',
            '[agent_settings.proxy_config]\n    ignore_proxy_settings="true"',
        ),
        # Previously withdrawn: turned back on rather than duplicated.
        (DISABLED, ENABLED),
        # Indentation of the existing line is preserved.
        (
            '[agent_settings.proxy_config]\n\t\tignore_proxy_settings = "false"',
            '[agent_settings.proxy_config]\n\t\tignore_proxy_settings = "true"',
        ),
        # Section present without the setting: inserted under it, other settings kept.
        (
            '[agent_settings.proxy_config]\n    other = "1"',
            (
                '[agent_settings.proxy_config]\n    ignore_proxy_settings = "true"\n'
                '    other = "1"'
            ),
        ),
        # No proxy_config section: a fresh one is appended and the rest survives.
        (
            '[agent_settings.other]\n    foo = "1"',
            '[agent_settings.other]\n    foo = "1"\n' + ENABLED,
        ),
    ],
)
def test_merge_proxy_bypass_into_agent_settings(current, expected):
    assert merge_proxy_bypass_into_agent_settings(current) == expected


# ---------------- Tests for remove_proxy_bypass_from_agent_settings ----------------
@pytest.mark.parametrize(
    "current, expected",
    [
        # The bypass is withdrawn by writing "false", never by deleting the line.
        (ENABLED, DISABLED),
        # Already withdrawn.
        (DISABLED, DISABLED),
        # Nothing to undo: the settings are handed back as they were.
        ("[agent_settings.proxy_config]", "[agent_settings.proxy_config]"),
        ("", ""),
        # A setting in another section belongs to something else and is left alone.
        (
            '[agent_settings.other]\n    ignore_proxy_settings = "true"',
            '[agent_settings.other]\n    ignore_proxy_settings = "true"',
        ),
    ],
)
def test_remove_proxy_bypass_from_agent_settings(current, expected):
    assert remove_proxy_bypass_from_agent_settings(current) == expected


# ---------------- Tests for ensure_container_insights_proxy_bypass_configmap ----------------
def test_ensure_creates_the_configmap_when_it_is_absent():
    api = _api(read_error=_ApiError(404))

    ensure_container_insights_proxy_bypass_configmap(api)

    body = api.create_namespaced_config_map.call_args.kwargs["body"]
    assert body.data[SETTINGS_KEY] == ENABLED
    assert body.metadata.annotations[ANNOTATION] == "azure-cli"
    api.replace_namespaced_config_map.assert_not_called()


def test_ensure_does_not_write_when_the_bypass_is_already_set():
    api = _api(_configmap(ENABLED))

    ensure_container_insights_proxy_bypass_configmap(api)

    api.replace_namespaced_config_map.assert_not_called()
    api.create_namespaced_config_map.assert_not_called()


def test_ensure_turns_a_withdrawn_bypass_back_on_and_stamps_it():
    api = _api(_configmap(DISABLED))

    ensure_container_insights_proxy_bypass_configmap(api)

    body = _written_body(api)
    assert body.data[SETTINGS_KEY] == ENABLED
    assert body.metadata.annotations[ANNOTATION] == "azure-cli"
    kwargs = api.replace_namespaced_config_map.call_args.kwargs
    assert kwargs["name"] == consts.CI_ConfigMap_Name
    assert kwargs["namespace"] == consts.CI_ConfigMap_Namespace


def test_ensure_keeps_settings_it_did_not_write():
    api = _api(_configmap('[agent_settings.other]\n    foo = "1"'))

    ensure_container_insights_proxy_bypass_configmap(api)

    written = _written_body(api).data[SETTINGS_KEY]
    assert '[agent_settings.other]\n    foo = "1"' in written
    assert ENABLED in written


def test_ensure_stamps_the_annotation_when_the_configmap_has_no_metadata():
    api = _api(_configmap(DISABLED, with_metadata=False))

    ensure_container_insights_proxy_bypass_configmap(api)

    assert _written_body(api).metadata.annotations[ANNOTATION] == "azure-cli"


def test_ensure_reports_a_read_failure(monkeypatch):
    report = MagicMock()
    monkeypatch.setattr(ciutils, "report_container_insights_configmap_failure", report)
    api = _api(read_error=_ApiError(500))

    ensure_container_insights_proxy_bypass_configmap(api)

    assert report.call_args.args[1] is errors.CONFIGMAP_READ_FAILED
    api.create_namespaced_config_map.assert_not_called()
    api.replace_namespaced_config_map.assert_not_called()


def test_ensure_reports_a_write_failure(monkeypatch):
    report = MagicMock()
    monkeypatch.setattr(ciutils, "report_container_insights_configmap_failure", report)
    api = _api(_configmap(DISABLED))
    api.replace_namespaced_config_map.side_effect = _ApiError(403)

    ensure_container_insights_proxy_bypass_configmap(api)

    assert report.call_args.args[1] is errors.CONFIGMAP_WRITE_FAILED


# ---------------- Tests for create_container_insights_proxy_bypass_configmap ----------------
def test_create_writes_only_the_bypass_setting():
    api = MagicMock()

    create_container_insights_proxy_bypass_configmap(api)

    kwargs = api.create_namespaced_config_map.call_args.kwargs
    assert kwargs["namespace"] == consts.CI_ConfigMap_Namespace
    assert kwargs["body"].data[SETTINGS_KEY] == ENABLED
    assert kwargs["body"].metadata.name == consts.CI_ConfigMap_Name


def test_create_merges_when_the_configmap_appears_concurrently(monkeypatch):
    ensure = MagicMock()
    monkeypatch.setattr(
        ciutils, "ensure_container_insights_proxy_bypass_configmap", ensure
    )
    api = MagicMock()
    api.create_namespaced_config_map.side_effect = _ApiError(409)

    create_container_insights_proxy_bypass_configmap(api)

    ensure.assert_called_once_with(api, cmd=None)


def test_create_reports_a_failure(monkeypatch):
    report = MagicMock()
    monkeypatch.setattr(ciutils, "report_container_insights_configmap_failure", report)
    api = MagicMock()
    api.create_namespaced_config_map.side_effect = _ApiError(403)

    create_container_insights_proxy_bypass_configmap(api)

    assert report.call_args.args[1] is errors.CONFIGMAP_WRITE_FAILED


# ---------------- Tests for remove_container_insights_proxy_bypass_configmap ----------------
def test_remove_does_nothing_when_the_configmap_is_absent():
    api = _api(read_error=_ApiError(404))

    remove_container_insights_proxy_bypass_configmap(api)

    api.replace_namespaced_config_map.assert_not_called()
    api.create_namespaced_config_map.assert_not_called()


def test_remove_leaves_a_setting_this_cli_did_not_add():
    # Without the annotation the bypass is the customer's, so it must survive a delete.
    api = _api(_configmap(ENABLED, annotated=False))

    remove_container_insights_proxy_bypass_configmap(api)

    api.replace_namespaced_config_map.assert_not_called()


def test_remove_leaves_a_setting_alone_when_there_is_no_metadata():
    api = _api(_configmap(ENABLED, with_metadata=False))

    remove_container_insights_proxy_bypass_configmap(api)

    api.replace_namespaced_config_map.assert_not_called()


def test_remove_withdraws_a_setting_this_cli_added():
    api = _api(_configmap(ENABLED, annotated=True))

    remove_container_insights_proxy_bypass_configmap(api)

    body = _written_body(api)
    assert body.data[SETTINGS_KEY] == DISABLED
    # The annotation goes with it, so the disabled line is not claimed on a later run.
    assert ANNOTATION not in body.metadata.annotations


def test_remove_keeps_settings_it_did_not_write():
    current = '[agent_settings.other]\n    foo = "1"\n' + ENABLED
    api = _api(_configmap(current, annotated=True))

    remove_container_insights_proxy_bypass_configmap(api)

    written = _written_body(api).data[SETTINGS_KEY]
    assert '[agent_settings.other]\n    foo = "1"' in written
    assert written.endswith('ignore_proxy_settings = "false"')


@pytest.mark.parametrize("raise_on_failure", [True, False])
def test_remove_passes_the_raise_flag_to_the_reporter(monkeypatch, raise_on_failure):
    report = MagicMock()
    monkeypatch.setattr(ciutils, "report_container_insights_configmap_failure", report)
    api = _api(read_error=_ApiError(500))

    remove_container_insights_proxy_bypass_configmap(api, raise_on_failure)

    assert report.call_args.args[1] is errors.CONFIGMAP_READ_FAILED
    assert report.call_args.args[3] is raise_on_failure


def test_remove_reports_a_write_failure(monkeypatch):
    report = MagicMock()
    monkeypatch.setattr(ciutils, "report_container_insights_configmap_failure", report)
    api = _api(_configmap(ENABLED, annotated=True))
    api.replace_namespaced_config_map.side_effect = _ApiError(403)

    remove_container_insights_proxy_bypass_configmap(api, False)

    assert report.call_args.args[1] is errors.CONFIGMAP_WRITE_FAILED
    assert report.call_args.args[3] is False


# ---------------- Tests for sync_container_insights_proxy_bypass_configmap ----------------
@pytest.mark.parametrize("requested", [True, False])
def test_sync_dispatches_on_whether_the_bypass_was_requested(monkeypatch, requested):
    ensure = MagicMock()
    remove = MagicMock()
    monkeypatch.setattr(
        ciutils, "ensure_container_insights_proxy_bypass_configmap", ensure
    )
    monkeypatch.setattr(
        ciutils, "remove_container_insights_proxy_bypass_configmap", remove
    )
    api = MagicMock()

    sync_container_insights_proxy_bypass_configmap(api, requested)

    assert ensure.called is requested
    assert remove.called is (not requested)


# ---------------- Tests for report_container_insights_configmap_failure ----------------
def test_report_failure_warns_without_raising_when_not_fatal(monkeypatch):
    diagnostic = MagicMock()
    monkeypatch.setattr(ciutils.utils, "report_connectedk8s_diagnostic", diagnostic)

    report_container_insights_configmap_failure(
        Exception("boom"),
        errors.CONFIGMAP_WRITE_FAILED,
        "update",
        raise_on_failure=False,
    )

    assert diagnostic.call_args.args[1] is errors.CONFIGMAP_WRITE_FAILED
    assert diagnostic.call_args.kwargs["operation"] == "update"


def test_report_failure_raises_by_default(monkeypatch):
    reporter = MagicMock(return_value=ValidationError("handled"))
    monkeypatch.setattr(ciutils.utils, "report_connectedk8s_error", reporter)

    with pytest.raises(ValidationError):
        report_container_insights_configmap_failure(
            Exception("boom"), errors.CONFIGMAP_WRITE_FAILED, "update"
        )

    assert reporter.call_args.args[1] is errors.CONFIGMAP_WRITE_FAILED
    assert reporter.call_args.kwargs["user_fault"] is True


def test_report_failure_names_the_permission_that_is_missing(monkeypatch):
    warnings: list[str] = []
    monkeypatch.setattr(
        ciutils.utils,
        "report_connectedk8s_error",
        MagicMock(return_value=ValidationError("handled")),
    )
    monkeypatch.setattr(
        ciutils.logger, "warning", lambda msg, *a, **k: warnings.append(msg)
    )

    with pytest.raises(ValidationError):
        report_container_insights_configmap_failure(
            ApiException(status=403), errors.CONFIGMAP_WRITE_FAILED, "update"
        )

    assert consts.CI_ConfigMap_Unauthorized_Message in warnings
