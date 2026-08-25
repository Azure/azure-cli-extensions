# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# Helpers for creating dashboards that use the Grafana v2 ("dynamic dashboards") schema through
# the dashboard apiserver (dashboard.grafana.app). Classic (v1) dashboards continue to use the
# legacy /api/dashboards/db endpoint in custom.py. See Grafana's own routing logic:
# https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/view-dashboard-json-model/

import copy
import json

import requests

from azure.cli.core.azclierror import ArgumentUsageError
from azure.cli.core.util import should_disable_connection_verify

DASHBOARD_APISERVER_GROUP = "dashboard.grafana.app"
# AMG runs single-org Grafana (org 1), whose apiserver namespace is "default". Grafana Cloud
# multi-tenant instances use "stacks-<id>". TODO: confirm/derive on a live AMG 13 instance.
DASHBOARD_APISERVER_NAMESPACE = "default"


def is_v2_dashboard_definition(definition):
    # Mirrors Grafana's own discriminator (isDashboardV2Spec: the spec has an "elements" map) and
    # also accepts a full v2 k8s resource envelope (apiVersion: dashboard.grafana.app/v2*).
    if not isinstance(definition, dict):
        return False
    api_version = definition.get("apiVersion")
    if isinstance(api_version, str) and api_version.startswith(DASHBOARD_APISERVER_GROUP + "/v2"):
        return True
    spec = definition.get("spec")
    if isinstance(spec, dict) and "elements" in spec:
        return True
    # a bare v2 spec (no k8s envelope) has "elements" and never the classic "panels" array
    return "elements" in definition and "panels" not in definition


def is_v2_stored_version(version):
    # Matches Grafana's isV2StoredVersion — the stored apiserver versions that carry the v2 model.
    return version in ("v2alpha1", "v2beta1", "v2")


def _request(grafana_url, http_headers, method, path, *, body=None, raise_for_error_status=True):
    resp = requests.request(method, url=grafana_url.rstrip("/") + path, headers=http_headers,
                            json=body, timeout=60, verify=not should_disable_connection_verify())
    if resp.status_code >= 400 and raise_for_error_status:
        resp.raise_for_status()
    return resp


def resolve_dashboard_v2_api_version(grafana_url, http_headers):
    # Discover which dashboard.grafana.app v2 version this instance serves, mirroring Grafana's
    # DashboardAPIVersionResolver (prefer the server's preferredVersion, else v2, else v2beta1).
    # Returns None when the v2 apiserver isn't served at all (e.g. a v1-only gateway) so the caller
    # can fail loudly instead of POSTing a v2 body to the legacy v1 endpoint.
    response = _request(grafana_url, http_headers, "get", "/apis/" + DASHBOARD_APISERVER_GROUP + "/",
                        raise_for_error_status=False)
    if response.status_code >= 400:
        return None
    group = json.loads(response.content)
    versions = {v.get("version") for v in group.get("versions", [])}
    preferred = (group.get("preferredVersion") or {}).get("version")
    if preferred in ("v2", "v2beta1"):
        return preferred
    if "v2" in versions:
        return "v2"
    if "v2beta1" in versions:
        return "v2beta1"
    return None


def require_dashboard_v2_api_version(grafana_url, http_headers):
    # As resolve_dashboard_v2_api_version, but raises when the instance doesn't serve the v2 API,
    # so a v2 definition is never silently sent to the legacy v1 endpoint.
    version = resolve_dashboard_v2_api_version(grafana_url, http_headers)
    if not version:
        raise ArgumentUsageError(
            "The dashboard uses the Grafana v2 (dynamic dashboards) schema, but this Grafana instance does "
            "not serve the 'dashboard.grafana.app' v2 API. Use a Grafana 13+ instance, or provide a classic "
            "(v1) dashboard JSON.")
    return version


def read_v2_dashboard(grafana_url, http_headers, uid, version=None):
    # Return the full v2 dashboard resource when the dashboard is stored as v2, else None.
    # The legacy /api/dashboards/uid endpoint down-converts v2 dashboards to classic (lossy), so
    # callers that need fidelity (show / backup / migrate) should try this first and only fall
    # back to the classic read when it returns None. Detection uses the apiserver's own
    # status.conversion.storedVersion: a v2-stored dashboard read at v2 has no conversion, whereas
    # a classic dashboard read at v2 reports a v0/v1 storedVersion (an up-conversion we must skip).
    # Callers reading many dashboards from one instance (backup) can resolve the version once and
    # pass it in to avoid a discovery request per dashboard.
    if version is None:
        version = resolve_dashboard_v2_api_version(grafana_url, http_headers)
    if not version:
        return None
    path = (f"/apis/{DASHBOARD_APISERVER_GROUP}/{version}"
            f"/namespaces/{DASHBOARD_APISERVER_NAMESPACE}/dashboards/{uid}")
    resp = _request(grafana_url, http_headers, "get", path, raise_for_error_status=False)
    if resp.status_code >= 400:
        return None
    body = json.loads(resp.content)
    stored = ((body.get("status") or {}).get("conversion") or {}).get("storedVersion")
    if stored is None or is_v2_stored_version(stored):
        return body
    return None


def create_dashboard_v2(grafana_url, http_headers, definition, version, *, title=None, folder_uid=None,
                        overwrite=None):
    # Normalise the input into a k8s Dashboard resource (apiVersion / kind / metadata / spec).
    if isinstance(definition.get("spec"), dict) and definition.get("kind") == "Dashboard":
        resource = copy.deepcopy(definition)
        metadata = resource.get("metadata") or {}
        spec = resource.get("spec") or {}
    else:  # a bare v2 spec, no k8s envelope
        spec = copy.deepcopy(definition)
        metadata = {}
        resource = {}

    if title:
        spec["title"] = title

    annotations = metadata.get("annotations") or {}
    if folder_uid:
        annotations["grafana.app/folder"] = folder_uid
    annotations["grafana.app/grantPermissions"] = "default"
    metadata["annotations"] = annotations
    metadata["namespace"] = DASHBOARD_APISERVER_NAMESPACE
    for server_field in ("resourceVersion", "creationTimestamp", "generation", "uid"):
        metadata.pop(server_field, None)  # server-managed; not valid on create / re-create

    resource["apiVersion"] = DASHBOARD_APISERVER_GROUP + "/" + version
    resource["kind"] = "Dashboard"
    resource["metadata"] = metadata
    resource["spec"] = spec
    resource.pop("status", None)

    base_path = (f"/apis/{DASHBOARD_APISERVER_GROUP}/{version}"
                 f"/namespaces/{DASHBOARD_APISERVER_NAMESPACE}/dashboards")
    name = metadata.get("name")

    if name:
        existing = _request(grafana_url, http_headers, "get", base_path + "/" + name,
                            raise_for_error_status=False)
        if existing.status_code == 200:
            if not overwrite:
                raise ArgumentUsageError(
                    f"A dashboard with uid '{name}' already exists. Use --overwrite to replace it.")
            response = _request(grafana_url, http_headers, "put", base_path + "/" + name, body=resource)
            return json.loads(response.content)

    # create: name (if any) is honoured by the apiserver; otherwise the backend generates one
    response = _request(grafana_url, http_headers, "post", base_path, body=resource)
    return json.loads(response.content)


def dashboard_identity(content):
    # Return (uid, title) for either a classic {meta, dashboard} object or a v2 resource.
    if is_v2_dashboard_definition(content):
        return content.get("metadata", {}).get("name"), content.get("spec", {}).get("title", "")
    dashboard = content.get("dashboard", content)
    return dashboard.get("uid"), dashboard.get("title", "")


def dashboard_folder_uid(content):
    # Return the folder uid for either a classic {meta, dashboard} object or a v2 resource.
    if is_v2_dashboard_definition(content):
        return content.get("metadata", {}).get("annotations", {}).get("grafana.app/folder", "")
    return content.get("meta", {}).get("folderUid", "")


def remap_v2_datasource_uids(node, uid_mapping):
    # Rewrite datasource UIDs inside a v2 dashboard spec. In the v2 schema a datasource reference is
    # {"datasource": {"name": "<uid>"}} (the uid is under "name"; the type lives in the sibling
    # DataQuery "group" field) — unlike the classic {"datasource": {"type", "uid"}}. The classic
    # remapper (utils.remap_datasource_uids) matches "uid" and so never reaches v2 refs; this walks
    # the spec and rewrites "name" (and defensively "uid") when it maps to a known source uid.
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "datasource" and isinstance(value, dict):
                for ref_key in ("name", "uid"):
                    if value.get(ref_key) in uid_mapping:
                        value[ref_key] = uid_mapping[value[ref_key]]
            else:
                remap_v2_datasource_uids(value, uid_mapping)
    elif isinstance(node, list):
        for item in node:
            remap_v2_datasource_uids(item, uid_mapping)


def is_dashboard_provisioned(content):
    # Whether a dashboard is externally managed (file provisioning, repo, terraform, kubectl, ...)
    # and therefore should not be synced/overwritten. Classic exposes this as meta.provisioned; v2
    # carries the grafana.app/managedBy annotation (absent on user-created dashboards).
    if is_v2_dashboard_definition(content):
        return bool(content.get("metadata", {}).get("annotations", {}).get("grafana.app/managedBy"))
    return bool(content.get("meta", {}).get("provisioned"))


def get_v2_library_panel_uids(spec):
    # Collect library-panel uids referenced by a v2 spec. Library panels are elements of kind
    # "LibraryPanel" whose spec.libraryPanel.uid holds the uid; spec.elements is a flat map, so this
    # also catches panels nested inside rows/tabs by the layout.
    uids = []
    for element in (spec.get("elements") or {}).values():
        if isinstance(element, dict) and element.get("kind") == "LibraryPanel":
            uid = (element.get("spec") or {}).get("libraryPanel", {}).get("uid")
            if uid:
                uids.append(uid)
    return uids
