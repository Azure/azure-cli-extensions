# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Grafana dashboard import for microsoft.kubernetesinventory.sync.

The extension's Helm chart ships Grafana dashboards under ``grafana-ui/``. When the caller passes
``importGrafana=true`` and ``grafanaResourceId=<Azure Managed Grafana ARM ID>`` in
``--configuration-settings``, the CLI downloads that version's chart from MCR and imports its
dashboards into the workspace with ``az grafana dashboard import``.
"""

import hashlib
import io
import os
import posixpath
import subprocess
import sys
import tarfile
import tempfile

import requests
from azure.cli.core.azclierror import (
    AzureResponseError,
    CLIInternalError,
    InvalidArgumentValueError,
    RequiredArgumentMissingError,
)
from azure.cli.core.util import send_raw_request
from azure.mgmt.core.tools import is_valid_resource_id, parse_resource_id
from knack.log import get_logger

from .._client_factory import cf_k8s_extension_types
from ..utils import get_mcr_path

logger = get_logger(__name__)

EXTENSION_TYPE = "microsoft.kubernetesinventory.sync"
CHART_REPOSITORY = "azurearck8s/applicationmonitoring/helmcharts/applicationmonitoring"
IMPORT_GRAFANA_SETTING = "importGrafana"
GRAFANA_RESOURCE_ID_SETTING = "grafanaResourceId"
REQUIRED_GRAFANA_PLUGIN = "marcusolsson-dynamictext-panel"
GRAFANA_API_VERSION = "2023-09-01"
CHART_LAYER_MEDIA_TYPE = "application/vnd.cncf.helm.chart.content.v1.tar+gzip"
MAX_CHART_BYTES = 50 * 1024 * 1024
DEFAULT_RELEASE_TRAIN = "stable"


def is_kubernetes_inventory_sync(extension_type):
    return (extension_type or "").lower() == EXTENSION_TYPE


def take_grafana_import_settings(configuration_settings):
    """Removes the CLI-only Grafana settings and returns the workspace ID, or None if not requested.

    The settings drive the CLI only, so they are not sent to the extension service or the chart.
    """
    if not configuration_settings:
        return None
    import_value = _pop_case_insensitive(configuration_settings, IMPORT_GRAFANA_SETTING)
    resource_id = _pop_case_insensitive(configuration_settings, GRAFANA_RESOURCE_ID_SETTING)
    if import_value is None:
        if resource_id is not None:
            raise RequiredArgumentMissingError(
                f"'{GRAFANA_RESOURCE_ID_SETTING}' requires '{IMPORT_GRAFANA_SETTING}=true'."
            )
        return None

    normalized = str(import_value).strip().lower()
    if normalized not in ("true", "false"):
        raise InvalidArgumentValueError(f"'{IMPORT_GRAFANA_SETTING}' must be 'true' or 'false'.")
    if normalized == "false":
        return None
    if not resource_id:
        raise RequiredArgumentMissingError(
            f"'{IMPORT_GRAFANA_SETTING}=true' requires '{GRAFANA_RESOURCE_ID_SETTING}' set to the "
            "Azure Managed Grafana resource ID."
        )
    return _validate_grafana_resource_id(str(resource_id).strip())


def latest_registered_version(cmd, resource_group_name, cluster_rp, cluster_type, cluster_name, release_train):
    versions = cf_k8s_extension_types(cmd.cli_ctx).cluster_list_versions(
        resource_group_name, cluster_rp, cluster_type, cluster_name, EXTENSION_TYPE,
        release_train=release_train or DEFAULT_RELEASE_TRAIN, show_latest=True,
    )
    for item in versions or []:
        value = getattr(getattr(item, "properties", None), "version", None)
        if value:
            return value
    raise InvalidArgumentValueError(
        f"No {EXTENSION_TYPE} version is registered for this cluster and release train, so there are "
        "no Grafana dashboards to import. Pass --version."
    )


def validate_create_request(extension):
    """Runs create's common argument validation, which custom.py otherwise runs after Create returns."""
    _custom_validator("__validate_version_and_auto_upgrade")(
        extension.version, extension.auto_upgrade_minor_version, extension.auto_upgrade_mode)
    _custom_validator("__validate_auto_upgrade_mode")(
        extension.auto_upgrade_minor_version, extension.auto_upgrade_mode)
    _custom_validator("__validate_scope_after_customization")(extension.scope)


def validate_update_request(patch):
    """Runs update's common argument validation, which custom.py otherwise runs after Update returns."""
    _custom_validator("__validate_auto_upgrade_mode")(patch.auto_upgrade_minor_version, patch.auto_upgrade_mode)


def _custom_validator(name):
    # custom.py imports the partner extensions, so it's imported lazily. The validators are looked up
    # by name so their double-underscore names aren't mangled and the rules stay defined once.
    from .. import custom
    return getattr(custom, name)


def import_grafana_dashboards(cmd, grafana_resource_id, version):
    """Imports the dashboards packaged in ``version`` of the chart into the Grafana workspace."""
    _require_amg_extension()
    workspace = _get_grafana_workspace(cmd, grafana_resource_id)
    plugins = (workspace.get("properties") or {}).get("grafanaPlugins") or {}
    if REQUIRED_GRAFANA_PLUGIN not in plugins:
        logger.warning(
            "Grafana workspace '%s' doesn't have the '%s' plugin, which the dashboards' panels use. "
            "Add it to the workspace for the dashboards to render.",
            workspace.get("name"), REQUIRED_GRAFANA_PLUGIN,
        )

    mcr_host = get_mcr_path(cmd.cli_ctx.cloud.endpoints.active_directory)
    dashboards = _chart_dashboards(_download_chart(mcr_host, version))
    if not dashboards:
        raise InvalidArgumentValueError(
            f"Version {version} of the {EXTENSION_TYPE} chart doesn't contain Grafana dashboards."
        )

    parsed = parse_resource_id(grafana_resource_id)
    with tempfile.TemporaryDirectory(prefix="k8s-extension-grafana-") as temp_dir:
        for file_name, content in dashboards:
            path = os.path.join(temp_dir, file_name)
            with open(path, "wb") as f:
                f.write(content)
            _run_az([
                "grafana", "dashboard", "import",
                "--name", parsed["name"],
                "--resource-group", parsed["resource_group"],
                "--subscription", parsed["subscription"],
                "--definition", path,
                "--overwrite", "true",
                "--only-show-errors", "--output", "none",
            ], f"import dashboard '{file_name}'")
            logger.warning("Imported Grafana dashboard '%s' into '%s'.", file_name, parsed["name"])


def _pop_case_insensitive(settings, key):
    for existing in list(settings):
        if existing.lower() == key.lower():
            return settings.pop(existing)
    return None


def _validate_grafana_resource_id(resource_id):
    if is_valid_resource_id(resource_id):
        parsed = parse_resource_id(resource_id)
        if (
            (parsed.get("namespace") or "").lower() == "microsoft.dashboard"
            and (parsed.get("type") or "").lower() == "grafana"
            and parsed.get("name")
            and not parsed.get("child_type_1")
        ):
            return resource_id
    raise InvalidArgumentValueError(
        f"'{GRAFANA_RESOURCE_ID_SETTING}' must be an Azure Managed Grafana resource ID: "
        "/subscriptions/<id>/resourceGroups/<group>/providers/Microsoft.Dashboard/grafana/<name>."
    )


def _require_amg_extension():
    from azure.cli.core.extension import ExtensionNotInstalledException, get_extension
    try:
        get_extension("amg")
    except ExtensionNotInstalledException as ex:
        raise RequiredArgumentMissingError(
            "Importing Grafana dashboards uses 'az grafana'. Install it with 'az extension add --name amg'."
        ) from ex


def _get_grafana_workspace(cmd, resource_id):
    url = f"{cmd.cli_ctx.cloud.endpoints.resource_manager.rstrip('/')}{resource_id}?api-version={GRAFANA_API_VERSION}"
    try:
        return send_raw_request(cmd.cli_ctx, "GET", url).json()
    except Exception as ex:
        raise AzureResponseError(f"Unable to read Grafana workspace '{resource_id}': {ex}") from ex


def _download_chart(mcr_host, version):
    base = f"https://{mcr_host}/v2/{CHART_REPOSITORY}"
    try:
        manifest = requests.get(
            f"{base}/manifests/{version}",
            headers={"Accept": "application/vnd.oci.image.manifest.v1+json"},
            timeout=60,
        )
        manifest.raise_for_status()
        layers = [layer for layer in manifest.json().get("layers", [])
                  if layer.get("mediaType") == CHART_LAYER_MEDIA_TYPE]
        if len(layers) != 1:
            raise CLIInternalError(f"Chart {CHART_REPOSITORY}:{version} has no single Helm chart layer.")
        digest, size = layers[0]["digest"], int(layers[0].get("size", 0))
        if size > MAX_CHART_BYTES:
            raise CLIInternalError(f"Chart {CHART_REPOSITORY}:{version} is larger than expected ({size} bytes).")
        blob = requests.get(f"{base}/blobs/{digest}", timeout=120)
        blob.raise_for_status()
    except requests.RequestException as ex:
        raise AzureResponseError(
            f"Unable to download chart {mcr_host}/{CHART_REPOSITORY}:{version}: {ex}"
        ) from ex

    algorithm, _, expected = digest.partition(":")
    if algorithm != "sha256" or hashlib.sha256(blob.content).hexdigest() != expected:
        raise CLIInternalError(f"Chart {CHART_REPOSITORY}:{version} failed digest verification.")
    return blob.content


def _chart_dashboards(chart_bytes):
    """Returns (file name, content) for each ``<chart>/grafana-ui/*.json`` regular file."""
    dashboards = []
    with tarfile.open(fileobj=io.BytesIO(chart_bytes), mode="r:gz") as archive:
        for member in archive.getmembers():
            parts = posixpath.normpath(member.name).split("/")
            if (
                member.isfile()
                and len(parts) == 3
                and parts[1] == "grafana-ui"
                and parts[2].endswith(".json")
                and not parts[2].startswith(".")
            ):
                dashboards.append((parts[2], archive.extractfile(member).read()))
    return sorted(dashboards)


def _run_az(args, description):
    result = subprocess.run(  # pylint: disable=subprocess-run-check
        [sys.executable, "-m", "azure.cli"] + args,
        capture_output=True, text=True, env=os.environ.copy(),
    )
    if result.returncode != 0:
        raise AzureResponseError(f"Failed to {description}: {(result.stderr or result.stdout).strip()}")
