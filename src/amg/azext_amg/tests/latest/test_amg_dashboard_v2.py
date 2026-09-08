# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import unittest
from unittest import mock

from azure.cli.core.azclierror import ArgumentUsageError

from azext_amg import dashboard_v2 as dv2


def _resp(status_code, body=None):
    r = mock.Mock()
    r.status_code = status_code
    r.content = json.dumps(body if body is not None else {}).encode()
    return r


def _v2_resource(uid="abc", title="T", ds_uid=None, folder=None, extra_annotations=None):
    query = {"kind": "DataQuery", "group": "prometheus", "version": "v0", "spec": {"expr": "up"}}
    if ds_uid:
        query["datasource"] = {"name": ds_uid}
    annotations = dict(extra_annotations or {})
    if folder:
        annotations["grafana.app/folder"] = folder
    return {
        "apiVersion": "dashboard.grafana.app/v2", "kind": "Dashboard",
        "metadata": {"name": uid, "annotations": annotations},
        "spec": {"title": title, "elements": {"panel-1": {"kind": "Panel", "spec": {
            "data": {"kind": "QueryGroup", "spec": {"queries": [{"kind": "PanelQuery", "spec": {
                "refId": "A", "query": query}}]}}}}}},
    }


class DashboardV2DetectionTests(unittest.TestCase):
    def test_is_v2_dashboard_definition(self):
        self.assertTrue(dv2.is_v2_dashboard_definition(_v2_resource()))
        self.assertTrue(dv2.is_v2_dashboard_definition({"apiVersion": "dashboard.grafana.app/v2beta1"}))
        self.assertTrue(dv2.is_v2_dashboard_definition({"elements": {}}))  # bare v2 spec
        self.assertFalse(dv2.is_v2_dashboard_definition({"title": "c", "panels": []}))  # classic
        self.assertFalse(dv2.is_v2_dashboard_definition({"meta": {}, "dashboard": {"panels": []}}))
        self.assertFalse(dv2.is_v2_dashboard_definition("not-a-dict"))

    def test_is_v2_stored_version(self):
        for v in ("v2alpha1", "v2beta1", "v2"):
            self.assertTrue(dv2.is_v2_stored_version(v))
        for v in ("v0alpha1", "v1", "v1beta1", None):
            self.assertFalse(dv2.is_v2_stored_version(v))

    def test_dashboard_identity_and_folder(self):
        self.assertEqual(dv2.dashboard_identity(_v2_resource(uid="u1", title="Ti")), ("u1", "Ti"))
        self.assertEqual(dv2.dashboard_folder_uid(_v2_resource(folder="f1")), "f1")
        classic = {"meta": {"folderUid": "cf"}, "dashboard": {"uid": "cu", "title": "ct"}}
        self.assertEqual(dv2.dashboard_identity(classic), ("cu", "ct"))
        self.assertEqual(dv2.dashboard_folder_uid(classic), "cf")

    def test_is_dashboard_provisioned(self):
        managed = _v2_resource(extra_annotations={"grafana.app/managedBy": "repo"})
        self.assertTrue(dv2.is_dashboard_provisioned(managed))
        self.assertFalse(dv2.is_dashboard_provisioned(_v2_resource(
            extra_annotations={"grafana.app/createdBy": "user:x"})))
        self.assertTrue(dv2.is_dashboard_provisioned({"meta": {"provisioned": True}, "dashboard": {}}))
        self.assertFalse(dv2.is_dashboard_provisioned({"meta": {"provisioned": False}, "dashboard": {}}))

    def test_get_v2_library_panel_uids(self):
        spec = {"elements": {
            "a": {"kind": "LibraryPanel", "spec": {"libraryPanel": {"uid": "lp1", "name": "n"}}},
            "b": {"kind": "Panel", "spec": {}},
            "c": {"kind": "LibraryPanel", "spec": {"libraryPanel": {"uid": "lp2"}}}}}
        self.assertEqual(sorted(dv2.get_v2_library_panel_uids(spec)), ["lp1", "lp2"])
        self.assertEqual(dv2.get_v2_library_panel_uids({"elements": {}}), [])

    def test_remap_v2_datasource_uids(self):
        res = _v2_resource(ds_uid="SRC")
        dv2.remap_v2_datasource_uids(res["spec"], {"SRC": "DST"})
        ds = res["spec"]["elements"]["panel-1"]["spec"]["data"]["spec"]["queries"][0]["spec"]["query"]["datasource"]
        self.assertEqual(ds["name"], "DST")
        # unmapped uid untouched; built-in refs ignored
        res2 = _v2_resource(ds_uid="OTHER")
        dv2.remap_v2_datasource_uids(res2["spec"], {"SRC": "DST"})
        ds2 = res2["spec"]["elements"]["panel-1"]["spec"]["data"]["spec"]["queries"][0]["spec"]["query"]["datasource"]
        self.assertEqual(ds2["name"], "OTHER")


_DISCO = "dashboard.grafana.app"


class DashboardV2VersionTests(unittest.TestCase):
    @staticmethod
    def _group(preferred, versions):
        return {"preferredVersion": {"version": preferred},
                "versions": [{"version": v} for v in versions]}

    def test_resolve_prefers_server_preferred(self):
        with mock.patch.object(dv2, "_request",
                               return_value=_resp(200, self._group("v2", ["v2", "v2beta1", "v1"]))):
            self.assertEqual(dv2.resolve_dashboard_v2_api_version("u", {}), "v2")

    def test_resolve_v2beta1_when_preferred(self):
        with mock.patch.object(dv2, "_request",
                               return_value=_resp(200, self._group("v1beta1", ["v2beta1", "v1beta1"]))):
            self.assertEqual(dv2.resolve_dashboard_v2_api_version("u", {}), "v2beta1")

    def test_resolve_none_when_v2_absent(self):
        with mock.patch.object(dv2, "_request",
                               return_value=_resp(200, self._group("v1beta1", ["v1beta1", "v0alpha1"]))):
            self.assertIsNone(dv2.resolve_dashboard_v2_api_version("u", {}))

    def test_resolve_none_on_discovery_failure(self):
        with mock.patch.object(dv2, "_request", return_value=_resp(404)):
            self.assertIsNone(dv2.resolve_dashboard_v2_api_version("u", {}))

    def test_require_raises_when_unavailable(self):
        with mock.patch.object(dv2, "_request", return_value=_resp(404)):
            with self.assertRaises(ArgumentUsageError):
                dv2.require_dashboard_v2_api_version("u", {})


class DashboardV2ReadWriteTests(unittest.TestCase):
    def test_read_v2_dashboard_returns_v2_stored(self):
        disco = _resp(200, {"preferredVersion": {"version": "v2"}, "versions": [{"version": "v2"}]})
        v2_body = _resp(200, {"apiVersion": "dashboard.grafana.app/v2", "spec": {"elements": {}}})
        with mock.patch.object(dv2, "_request", side_effect=[disco, v2_body]):
            out = dv2.read_v2_dashboard("u", {}, "uid1")
        self.assertIsNotNone(out)
        self.assertIn("elements", out["spec"])

    def test_read_v2_dashboard_none_for_classic_stored(self):
        disco = _resp(200, {"preferredVersion": {"version": "v2"}, "versions": [{"version": "v2"}]})
        upconv = _resp(200, {"apiVersion": "dashboard.grafana.app/v2",
                             "status": {"conversion": {"storedVersion": "v0alpha1"}}, "spec": {"elements": {}}})
        with mock.patch.object(dv2, "_request", side_effect=[disco, upconv]):
            self.assertIsNone(dv2.read_v2_dashboard("u", {}, "uid1"))

    def test_read_v2_dashboard_none_on_404(self):
        disco = _resp(200, {"preferredVersion": {"version": "v2"}, "versions": [{"version": "v2"}]})
        with mock.patch.object(dv2, "_request", side_effect=[disco, _resp(404)]):
            self.assertIsNone(dv2.read_v2_dashboard("u", {}, "uid1"))

    def test_read_v2_dashboard_with_version_skips_discovery(self):
        # When the caller passes a pre-resolved version (backup), no discovery request is made:
        # a single _request (the dashboard GET) is issued.
        v2_body = _resp(200, {"apiVersion": "dashboard.grafana.app/v2", "spec": {"elements": {}}})
        with mock.patch.object(dv2, "_request", return_value=v2_body) as req:
            out = dv2.read_v2_dashboard("u", {}, "uid1", version="v2")
        self.assertIsNotNone(out)
        self.assertEqual(req.call_count, 1)
        self.assertEqual(req.call_args[0][3], "/apis/dashboard.grafana.app/v2/namespaces/default/dashboards/uid1")

    def test_read_dashboard_uses_pre_resolved_v2_version(self):
        v2_body = _resp(200, {"apiVersion": "dashboard.grafana.app/v2", "spec": {"elements": {}}})
        with mock.patch.object(dv2, "_request", return_value=v2_body) as req:
            out = dv2.read_dashboard("u", {}, "uid1", "v2")
        self.assertIn("elements", out["spec"])
        self.assertEqual(req.call_count, 1)

    def test_read_dashboard_skips_v2_when_version_unavailable(self):
        classic = _resp(200, {"dashboard": {"uid": "uid1"}})
        with mock.patch.object(dv2, "_request", return_value=classic) as req:
            out = dv2.read_dashboard("u", {}, "uid1", None)
        self.assertEqual(out["dashboard"]["uid"], "uid1")
        self.assertEqual(req.call_count, 1)
        self.assertEqual(req.call_args[0][3], "/api/dashboards/uid/uid1")

    def test_read_dashboard_falls_back_for_classic_stored_dashboard(self):
        upconverted = _resp(200, {"status": {"conversion": {"storedVersion": "v0alpha1"}}})
        classic = _resp(200, {"dashboard": {"uid": "uid1"}})
        with mock.patch.object(dv2, "_request", side_effect=[upconverted, classic]) as req:
            out = dv2.read_dashboard("u", {}, "uid1", "v2")
        self.assertEqual(out["dashboard"]["uid"], "uid1")
        self.assertEqual(req.call_count, 2)
        self.assertEqual(req.call_args_list[1][0][3], "/api/dashboards/uid/uid1")

    def test_create_dashboard_v2_create_path_builds_resource(self):
        calls = []

        def fake(grafana_url, headers, method, path, body=None, raise_for_error_status=True):
            calls.append((method, path, body))
            if method == "get":
                return _resp(404)  # does not exist -> create (POST)
            return _resp(200, {"metadata": {"name": "abc"}})

        with mock.patch.object(dv2, "_request", side_effect=fake):
            dv2.create_dashboard_v2("u", {}, {"elements": {"e": {}}}, "v2",
                                    title="Ti", folder_uid="fold", overwrite=False)
        post = [c for c in calls if c[0] == "post"][0]
        body = post[2]
        self.assertEqual(body["apiVersion"], "dashboard.grafana.app/v2")
        self.assertEqual(body["kind"], "Dashboard")
        self.assertEqual(body["spec"]["title"], "Ti")
        self.assertEqual(body["metadata"]["annotations"]["grafana.app/folder"], "fold")
        self.assertEqual(body["metadata"]["annotations"]["grafana.app/grantPermissions"], "default")
        self.assertEqual(body["metadata"]["namespace"], "default")

    def test_create_dashboard_v2_strips_server_metadata_and_updates(self):
        calls = []

        def fake(grafana_url, headers, method, path, body=None, raise_for_error_status=True):
            calls.append((method, path, body))
            if method == "get":
                return _resp(200, {})  # exists -> update (PUT) when overwrite
            return _resp(200, {"metadata": {"name": "abc"}})

        resource = _v2_resource(uid="abc")
        resource["metadata"].update({"resourceVersion": "9", "creationTimestamp": "t",
                                     "generation": 3, "uid": "k8s-uid"})
        with mock.patch.object(dv2, "_request", side_effect=fake):
            dv2.create_dashboard_v2("u", {}, resource, "v2", overwrite=True)
        put = [c for c in calls if c[0] == "put"][0]
        meta = put[2]["metadata"]
        for stripped in ("resourceVersion", "creationTimestamp", "generation", "uid"):
            self.assertNotIn(stripped, meta)

    def test_create_dashboard_v2_conflict_without_overwrite(self):
        with mock.patch.object(dv2, "_request", return_value=_resp(200, {})):  # exists
            with self.assertRaises(ArgumentUsageError):
                dv2.create_dashboard_v2("u", {}, _v2_resource(uid="abc"), "v2", overwrite=False)


if __name__ == '__main__':
    unittest.main()
