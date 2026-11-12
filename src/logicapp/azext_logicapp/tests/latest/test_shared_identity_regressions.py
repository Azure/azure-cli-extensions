# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Offline deletion regressions; runnable with unittest and Azure CLI's Python."""

from azext_logicapp import _connection, _managed_connection as managed
from azure.cli.core.azclierror import ClientRequestError, InvalidArgumentValueError, ResourceNotFoundError, ValidationError
import copy
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import quote, unquote

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))


CONNECTION_ID = "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Web/connections/shared"
UAMI_ID = "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/shared"
SYSTEM_AUTH = {"type": "ManagedServiceIdentity"}
UAMI_AUTH = {"type": "ManagedServiceIdentity", "identity": UAMI_ID}
UNSAFE_POLICY_NAMES = (
    ".", "..", "foo/bar", "foo\\bar", "foo?api-version=bad", "foo#fragment",
    "foo%2fbar", "foo%2Fbar", "foo%5cbar", "foo%5Cbar", "foo%252fbar", "%64up",
    "foo\u2028bar", "foo\u200bbar",
) + tuple("foo" + chr(value) + "bar" for value in (0, 1, 10, 13, 31, 127, 128, 159))


def _entry(authentication):
    result = {"connection": {"id": CONNECTION_ID}}
    if authentication is not None:
        result["authentication"] = copy.deepcopy(authentication)
    return result


def _policy(name, principal):
    return {
        "name": name,
        "properties": {
            "principal": {
                "type": "ActiveDirectory",
                "identity": {"objectId": principal, "tenantId": "tenant"},
            }
        },
    }


def _site_identity(system=True):
    return {
        "type": "SystemAssigned, UserAssigned" if system else "UserAssigned",
        "principalId": "system-a" if system else None,
        "tenantId": "tenant",
        "userAssignedIdentities": {UAMI_ID: {"principalId": "shared-uami"}},
    }


class _MemoryVfs:
    def __init__(self, authentication, alias=None):
        self.payload = {"managedApiConnections": {"selected": _entry(authentication)}}
        if alias is not None:
            self.payload["managedApiConnections"]["alias"] = _entry(alias)
        self.writes = []
        self.fail_write = False

    def get(self, path):
        assert path == "connections.json"
        return copy.deepcopy(self.payload)

    def get_raw(self, path):
        return {"content": json.dumps(self.get(path)).encode("utf-8"), "headers": {"ETag": '"memory"'},
                "statusCode": 200}

    def put_raw(self, path, content, if_match=None):
        assert path == "connections.json"
        assert if_match == '"memory"'
        if self.fail_write:
            raise OSError("VFS write failed")
        self.writes.append(content)
        self.payload = json.loads(content.decode("utf-8"))
        return {"statusCode": 200, "payload": None, "headers": {}}


class _MemoryArm:
    def __init__(self, identity, policies):
        self.identity = identity
        self.policies = copy.deepcopy(policies)
        self.exists = True
        self.calls = []
        self.identity_error = None
        self.policy_listing = None
        self.identity_raw = None
        self.policy_raw = None

    def send(self, _ctx, method, url, **_kwargs):
        resource_id = url.split("?")[0]
        self.calls.append((method, resource_id))
        if "/providers/Microsoft.Web/sites/" in resource_id:
            if self.identity_error:
                raise self.identity_error
            if self.identity_raw is not None:
                return SimpleNamespace(content=self.identity_raw)
            payload = {"identity": copy.deepcopy(self.identity)}
        elif method == "GET" and resource_id == CONNECTION_ID + "/accessPolicies":
            if self.policy_raw is not None:
                return SimpleNamespace(content=self.policy_raw)
            payload = (copy.deepcopy(self.policy_listing) if self.policy_listing is not None
                       else {"value": copy.deepcopy(self.policies)})
        elif method == "DELETE" and resource_id.startswith(CONNECTION_ID + "/accessPolicies/"):
            name = unquote(resource_id.rsplit("/", 1)[-1])
            self.policies = [item for item in self.policies if item["name"] != name]
            payload = {}
        elif method == "DELETE" and resource_id == CONNECTION_ID:
            self.exists = False
            payload = {}
        else:
            raise AssertionError("Unexpected ARM request: {} {}".format(method, resource_id))
        return SimpleNamespace(content=json.dumps(payload).encode("utf-8"))

    @property
    def deletes(self):
        return [resource for method, resource in self.calls if method == "DELETE"]


class SharedIdentityDeletionTests(unittest.TestCase):
    def _delete(self, vfs, arm, keep_resource=False):
        cmd = SimpleNamespace(cli_ctx=object())
        with patch("azure.cli.core.commands.client_factory.get_subscription_id", return_value="sub"):
            result = _connection.connection_delete(
                cmd, "rg", "app-a", "selected", keep_resource=keep_resource,
                client=vfs, sender=arm.send)
        self.assertNotIn("selected", vfs.payload["managedApiConnections"])
        self.assertEqual(1, len(vfs.writes))
        return result

    def test_managed_id_refuses_unsafe_or_cross_scope_before_arm_and_unlink(self):
        invalid = (
            None, "", False, True, 1, [], {},
            "https://management.azure.com" + CONNECTION_ID,
            "https://untrusted.invalid" + CONNECTION_ID,
            "//untrusted.invalid" + CONNECTION_ID,
            CONNECTION_ID + "/", CONNECTION_ID + "/accessPolicies/child",
            CONNECTION_ID + "?api-version=bad", CONNECTION_ID + "#fragment",
            CONNECTION_ID.replace("/sub/", "/other-sub/"),
            CONNECTION_ID.replace("/rg/", "/other-group/"),
            CONNECTION_ID.replace("Microsoft.Web", "Microsoft.Other"),
            CONNECTION_ID.replace("/connections/", "/sites/"),
            CONNECTION_ID.replace("/sub/", "/%73ub/"),
            CONNECTION_ID.replace("/rg/", "/rg%2fother/"),
            CONNECTION_ID.replace("/shared", "/.."),
            CONNECTION_ID.replace("/shared", "/foo\\bar"),
            CONNECTION_ID + "\n", CONNECTION_ID.replace("/rg/", "/r\x01g/"),
        )
        cmd = SimpleNamespace(cli_ctx=object())
        for value in invalid:
            for keep in (False, True):
                with self.subTest(value=value, keep_resource=keep):
                    vfs = _MemoryVfs(SYSTEM_AUTH)
                    vfs.payload["managedApiConnections"]["selected"]["connection"]["id"] = value
                    before = copy.deepcopy(vfs.payload)
                    arm = _MemoryArm(_site_identity(), [_policy("own", "system-a")])
                    with patch("azure.cli.core.commands.client_factory.get_subscription_id", return_value="sub"):
                        with self.assertRaises(ValidationError):
                            _connection.connection_delete(
                                cmd, "rg", "app-a", "selected", keep_resource=keep,
                                client=vfs, sender=arm.send)
                    self.assertEqual([], arm.calls)
                    self.assertEqual([], vfs.writes)
                    self.assertEqual(before, vfs.payload)

    def test_managed_id_scope_is_case_insensitive_without_rewriting_identity(self):
        value = CONNECTION_ID.upper()
        cmd = SimpleNamespace(cli_ctx=object())
        with patch("azure.cli.core.commands.client_factory.get_subscription_id", return_value="SuB"):
            self.assertEqual(value, _connection._managed_cleanup_id(cmd, "rG", value))

    def test_managed_inspection_validates_routes_without_inventing_cleanup_scope(self):
        cmd = SimpleNamespace(cli_ctx=object())
        for value in ("https://untrusted.invalid/" + CONNECTION_ID, CONNECTION_ID + "?other=1",
                      "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Web/sites/other"):
            with self.subTest(value=value):
                arm = _MemoryArm(_site_identity(), [])
                with self.assertRaises(ValidationError):
                    _connection._get_arm_connection(cmd, value, sender=arm.send)
                self.assertEqual([], arm.calls)
        foreign = CONNECTION_ID.replace("/rg/", "/other-group/")
        sender = unittest.mock.Mock(return_value=SimpleNamespace(content=b"{}"))
        _connection._get_arm_connection(cmd, foreign, sender=sender)
        self.assertIn(foreign, sender.call_args.args[2])

    def test_shared_uami_two_apps_preserve_acl_and_resource_including_keep_resource(self):
        for keep_resource in (False, True):
            with self.subTest(keep_resource=keep_resource):
                app_a = _MemoryVfs(UAMI_AUTH)
                app_b = _MemoryVfs(UAMI_AUTH)
                app_b_before = copy.deepcopy(app_b.payload)
                policy = _policy("app-b-shared-uami", "shared-uami")
                arm = _MemoryArm(_site_identity(system=False), [policy])
                result = self._delete(app_a, arm, keep_resource)
                self.assertTrue(arm.exists)
                self.assertEqual([policy], arm.policies)
                self.assertEqual([], arm.deletes)
                self.assertEqual(app_b_before, app_b.payload)
                self.assertEqual([], result["accessPolicies"]["removed"])
                self.assertEqual(["app-b-shared-uami"], result["accessPolicies"]["retained"])
                self.assertIn("user-assigned", result["resource"]["reason"])
                self.assertIn("shared", result["resource"]["reason"])
                if keep_resource:
                    self.assertIn("--keep-resource", result["resource"]["reason"])

    def test_assigned_but_unused_uami_policy_is_not_owned_by_system_connection(self):
        for keep_resource in (False, True):
            with self.subTest(keep_resource=keep_resource):
                arm = _MemoryArm(_site_identity(), [
                    _policy("system-policy", "system-a"),
                    _policy("unused-uami-policy", "shared-uami"),
                ])
                result = self._delete(_MemoryVfs(SYSTEM_AUTH), arm, keep_resource)
                self.assertTrue(arm.exists)
                self.assertEqual([_policy("unused-uami-policy", "shared-uami")], arm.policies)
                self.assertEqual([CONNECTION_ID + "/accessPolicies/system-policy"], arm.deletes)
                self.assertEqual(["system-policy"], result["accessPolicies"]["removed"])
                self.assertEqual(["unused-uami-policy"], result["accessPolicies"]["retained"])

    def test_unused_uami_alone_cannot_establish_system_connection_ownership(self):
        arm = _MemoryArm(_site_identity(), [_policy("unused-uami-policy", "shared-uami")])
        result = self._delete(_MemoryVfs(SYSTEM_AUTH), arm)
        self.assertTrue(arm.exists)
        self.assertEqual([], arm.deletes)
        self.assertEqual(["unused-uami-policy"], result["accessPolicies"]["retained"])
        self.assertIn("shared", result["resource"]["reason"])

    def test_selected_uami_does_not_revoke_unused_system_policy(self):
        arm = _MemoryArm(_site_identity(), [
            _policy("unused-system-policy", "system-a"),
            _policy("shared-uami-policy", "shared-uami"),
        ])
        result = self._delete(_MemoryVfs(UAMI_AUTH), arm)
        self.assertEqual([], arm.deletes)
        self.assertEqual(["unused-system-policy", "shared-uami-policy"],
                         result["accessPolicies"]["retained"])

    def test_exclusive_system_identity_deletes_own_acl_and_resource(self):
        arm = _MemoryArm(_site_identity(), [_policy("system-policy", "SYSTEM-A")])
        result = self._delete(_MemoryVfs(SYSTEM_AUTH), arm)
        self.assertFalse(arm.exists)
        self.assertEqual([CONNECTION_ID + "/accessPolicies/system-policy", CONNECTION_ID], arm.deletes)
        self.assertTrue(result["resource"]["removed"])
        self.assertIsNone(result["resource"]["reason"])
        self.assertEqual(["system-policy"], result["accessPolicies"]["removed"])

    def test_missing_or_malformed_policy_tenant_never_authorizes_deletion(self):
        samples = (None, "", " ", "\t\n", False, True, 0, 1, 1.0, [], {}, "other-tenant")
        for tenant in samples:
            for keep_resource in (False, True):
                with self.subTest(tenant=tenant, keep_resource=keep_resource):
                    policy = _policy("unverified-policy", "system-a")
                    policy["properties"]["principal"]["identity"]["tenantId"] = tenant
                    arm = _MemoryArm(_site_identity(), [policy])
                    result = self._delete(_MemoryVfs(SYSTEM_AUTH), arm, keep_resource=keep_resource)
                    self.assertEqual([], arm.deletes)
                    self.assertEqual([policy], arm.policies)
                    self.assertTrue(arm.exists)
                    self.assertTrue(result["resource"]["retained"])
                    self.assertEqual(["unverified-policy"], result["accessPolicies"]["retained"])
        policy = _policy("missing-tenant-policy", "system-a")
        policy["properties"]["principal"]["identity"].pop("tenantId")
        arm = _MemoryArm(_site_identity(), [policy])
        result = self._delete(_MemoryVfs(SYSTEM_AUTH), arm)
        self.assertEqual([], arm.deletes)
        self.assertEqual(["missing-tenant-policy"], result["accessPolicies"]["retained"])

    def test_incomplete_site_principal_or_tenant_never_borrows_profile_evidence(self):
        samples = (None, "", " ", "\t\n", False, True, 0, 1, 1.0, [], {}, " tenant", "tenant ")
        for field in ("principalId", "tenantId"):
            for value in samples:
                with self.subTest(field=field, value=value):
                    identity = _site_identity()
                    identity[field] = value
                    policy = _policy("system-policy", "system-a")
                    arm = _MemoryArm(identity, [policy])
                    with patch("azext_logicapp._managed_connection._tenant_id",
                               side_effect=AssertionError("Do not infer the site's tenant from CLI login")):
                        result = self._delete(_MemoryVfs(SYSTEM_AUTH), arm)
                    self.assertEqual([], arm.deletes)
                    self.assertEqual([policy], arm.policies)
                    self.assertTrue(arm.exists)
                    self.assertTrue(result["resource"]["retained"])
                    self.assertEqual(["system-policy"], result["accessPolicies"]["retained"])

    def test_case_insensitive_complete_principal_and_tenant_match_authorizes_cleanup(self):
        identity = _site_identity()
        identity["principalId"] = "SYSTEM-A"
        identity["tenantId"] = "TeNaNt"
        policy = _policy("system-policy", "system-a")
        policy["properties"]["principal"]["type"] = "aCtIvEdIrEcToRy"
        policy["properties"]["principal"]["identity"]["tenantId"] = "TENANT"
        arm = _MemoryArm(identity, [policy])
        result = self._delete(_MemoryVfs(SYSTEM_AUTH), arm)
        self.assertEqual([CONNECTION_ID + "/accessPolicies/system-policy", CONNECTION_ID], arm.deletes)
        self.assertTrue(result["resource"]["removed"])

    def test_same_object_id_in_other_tenant_retains_that_policy_and_resource(self):
        own = _policy("system-policy", "system-a")
        other = _policy("cross-tenant-policy", "system-a")
        other["properties"]["principal"]["identity"]["tenantId"] = "other-tenant"
        arm = _MemoryArm(_site_identity(), [own, other])
        result = self._delete(_MemoryVfs(SYSTEM_AUTH), arm)
        self.assertEqual([CONNECTION_ID + "/accessPolicies/system-policy"], arm.deletes)
        self.assertEqual([other], arm.policies)
        self.assertTrue(arm.exists)
        self.assertEqual(["cross-tenant-policy"], result["accessPolicies"]["retained"])

    def test_tenant_evidence_is_refreshed_after_unlink_before_any_arm_delete(self):
        for stage in ("site", "policy"):
            with self.subTest(stage=stage):
                vfs = _MemoryVfs(SYSTEM_AUTH)
                arm = _MemoryArm(_site_identity(), [_policy("system-policy", "system-a")])
                original_put = vfs.put_raw

                def change_tenant(*args, **kwargs):
                    receipt = original_put(*args, **kwargs)
                    if stage == "site":
                        arm.identity["tenantId"] = "other-tenant"
                    else:
                        arm.policies[0]["properties"]["principal"]["identity"]["tenantId"] = "other-tenant"
                    return receipt

                vfs.put_raw = change_tenant
                result = self._delete(vfs, arm)
                self.assertEqual([], arm.deletes)
                self.assertTrue(arm.exists)
                self.assertEqual(["system-policy"], result["accessPolicies"]["retained"])

    def test_keep_resource_still_revokes_exclusive_system_acl(self):
        arm = _MemoryArm(_site_identity(), [_policy("system-policy", "system-a")])
        result = self._delete(_MemoryVfs(SYSTEM_AUTH), arm, keep_resource=True)
        self.assertTrue(arm.exists)
        self.assertEqual([CONNECTION_ID + "/accessPolicies/system-policy"], arm.deletes)
        self.assertIn("--keep-resource", result["resource"]["reason"])

    def test_duplicate_policy_names_never_authorize_acl_or_resource_deletion(self):
        for duplicate_name in ("system-policy", "SYSTEM-POLICY"):
            for principals in (("system-a", "system-b"), ("system-b", "system-a"),
                               ("system-a", "system-a"), ("system-b", "system-b")):
                for keep_resource in (False, True):
                    with self.subTest(name=duplicate_name, principals=principals,
                                      keep_resource=keep_resource):
                        policies = [_policy("system-policy", principals[0]),
                                    _policy(duplicate_name, principals[1])]
                        arm = _MemoryArm(_site_identity(), policies)
                        result = self._delete(_MemoryVfs(SYSTEM_AUTH), arm, keep_resource)
                        self.assertEqual([], arm.deletes)
                        self.assertEqual(policies, arm.policies)
                        self.assertTrue(arm.exists)
                        self.assertEqual([], result["accessPolicies"]["removed"])
                        self.assertEqual(["system-policy", duplicate_name],
                                         result["accessPolicies"]["retained"])
                        self.assertIn("Duplicate access policy names", result["resource"]["reason"])

    def test_duplicate_policy_names_preserve_verified_unique_acl_cleanup(self):
        for duplicate_name in ("ambiguous-policy", "AMBIGUOUS-POLICY"):
            with self.subTest(name=duplicate_name):
                duplicate = [_policy("ambiguous-policy", "system-a"),
                             _policy(duplicate_name, "system-b")]
                arm = _MemoryArm(_site_identity(), [_policy("unique-policy", "system-a")] + duplicate)
                result = self._delete(_MemoryVfs(SYSTEM_AUTH), arm)
                self.assertEqual([CONNECTION_ID + "/accessPolicies/unique-policy"], arm.deletes)
                self.assertEqual(duplicate, arm.policies)
                self.assertTrue(arm.exists)
                self.assertEqual(["unique-policy"], result["accessPolicies"]["removed"])
                self.assertEqual(["ambiguous-policy", duplicate_name], result["accessPolicies"]["retained"])

    def test_duplicate_policy_names_are_rechecked_after_unlink(self):
        for duplicate_name in ("system-policy", "SYSTEM-POLICY"):
            for keep_resource in (False, True):
                with self.subTest(name=duplicate_name, keep_resource=keep_resource):
                    vfs = _MemoryVfs(SYSTEM_AUTH)
                    arm = _MemoryArm(_site_identity(), [_policy("system-policy", "system-a")])
                    original_put = vfs.put_raw

                    def add_duplicate(*args, **kwargs):
                        receipt = original_put(*args, **kwargs)
                        arm.policies.append(_policy(duplicate_name, "system-b"))
                        return receipt

                    vfs.put_raw = add_duplicate
                    result = self._delete(vfs, arm, keep_resource)
                    self.assertEqual([], arm.deletes)
                    self.assertTrue(arm.exists)
                    self.assertEqual(["system-policy", duplicate_name], result["accessPolicies"]["retained"])

    def test_invalid_policy_names_never_establish_ownership(self):
        for name in (None, "", " ", "\t\n", False, True, 0, 1, 1.0, [], {}, " policy", "policy ") + UNSAFE_POLICY_NAMES:
            with self.subTest(name=name):
                policy = _policy(name, "system-a")
                arm = _MemoryArm(_site_identity(), [policy])
                result = self._delete(_MemoryVfs(SYSTEM_AUTH), arm)
                self.assertEqual([], arm.deletes)
                self.assertEqual([policy], arm.policies)
                self.assertTrue(arm.exists)
                self.assertIn("complete access policy list", result["resource"]["reason"])

    def test_unsafe_policy_evidence_blocks_other_acl_cleanup_before_and_after_unlink(self):
        for unsafe in UNSAFE_POLICY_NAMES:
            for late in (False, True):
                with self.subTest(name=unsafe, late=late):
                    vfs = _MemoryVfs(SYSTEM_AUTH)
                    own = _policy("dup", "system-a")
                    foreign = _policy("foo", "system-b")
                    ambiguous = _policy(unsafe, "system-b")
                    policies = [own, foreign] if late else [own, foreign, ambiguous]
                    arm = _MemoryArm(_site_identity(), policies)
                    if late:
                        original_put = vfs.put_raw

                        def add_unsafe(*args, **kwargs):
                            receipt = original_put(*args, **kwargs)
                            arm.policies.append(ambiguous)
                            return receipt

                        vfs.put_raw = add_unsafe
                    result = self._delete(vfs, arm)
                    self.assertEqual([], arm.deletes)
                    self.assertEqual([own, foreign, ambiguous], arm.policies)
                    self.assertTrue(arm.exists)
                    self.assertEqual(["dup", "foo"], result["accessPolicies"]["retained"])

    def test_safe_policy_names_are_quoted_as_single_child_segments(self):
        for name in ("policy-name_1.2", "policy name", "caf\u00e9", "policy:plus+at@"):
            with self.subTest(name=name):
                arm = _MemoryArm(_site_identity(), [_policy(name, "system-a")])
                result = self._delete(_MemoryVfs(SYSTEM_AUTH), arm)
                self.assertEqual([CONNECTION_ID + "/accessPolicies/" + quote(name, safe=""),
                                  CONNECTION_ID], arm.deletes)
                self.assertEqual([name], result["accessPolicies"]["removed"])
                self.assertEqual([], arm.policies)

    def test_explicit_acl_routes_reject_unsafe_names_before_arm_io(self):
        cmd = SimpleNamespace(cli_ctx=object())
        for name in UNSAFE_POLICY_NAMES:
            for operation in (managed.acl_show, managed.acl_add, managed.acl_remove):
                with self.subTest(name=name, operation=operation.__name__):
                    arm = _MemoryArm(_site_identity(), [])
                    kwargs = {"policy": name, "sender": arm.send}
                    if operation is managed.acl_add:
                        kwargs["object_id"] = "system-a"
                    with patch.object(managed, "_connection_id", return_value=CONNECTION_ID):
                        with self.assertRaises(InvalidArgumentValueError):
                            operation(cmd, "rg", "shared", **kwargs)
                    self.assertEqual([], arm.calls)

    def test_system_identity_only_revokes_own_acl_on_shared_resource(self):
        arm = _MemoryArm(_site_identity(), [
            _policy("system-policy", "system-a"), _policy("app-b-policy", "system-b"),
        ])
        result = self._delete(_MemoryVfs(SYSTEM_AUTH), arm)
        self.assertTrue(arm.exists)
        self.assertEqual([_policy("app-b-policy", "system-b")], arm.policies)
        self.assertEqual([CONNECTION_ID + "/accessPolicies/system-policy"], arm.deletes)
        self.assertIn("shared", result["resource"]["reason"])

    def test_no_acl_does_not_prove_exclusive_resource_ownership(self):
        arm = _MemoryArm(_site_identity(), [])
        result = self._delete(_MemoryVfs(SYSTEM_AUTH), arm)
        self.assertEqual([], arm.deletes)
        self.assertTrue(result["resource"]["retained"])
        self.assertIn("ownership", result["resource"]["reason"])

    def test_missing_or_unverifiable_system_identity_preserves_policies(self):
        for identity in (None, _site_identity(system=False), {"type": "None", "principalId": "system-a"}):
            with self.subTest(identity=identity):
                arm = _MemoryArm(identity, [_policy("system-policy", "system-a")])
                result = self._delete(_MemoryVfs(SYSTEM_AUTH), arm)
                self.assertEqual([], arm.deletes)
                self.assertEqual(["system-policy"], result["accessPolicies"]["retained"])
                self.assertIn("verified", result["resource"]["reason"])

    def test_identity_lookup_failure_preserves_acl_and_resource(self):
        for error_type in (ResourceNotFoundError, ValidationError):
            with self.subTest(error_type=error_type):
                arm = _MemoryArm(_site_identity(), [_policy("system-policy", "system-a")])
                arm.identity_error = error_type("identity unavailable")
                result = self._delete(_MemoryVfs(SYSTEM_AUTH), arm)
                self.assertEqual([], arm.deletes)
                self.assertIn("verified", result["resource"]["reason"])

    def test_ambiguous_or_nonfinite_access_policy_json_never_authorizes_cleanup(self):
        own = _policy("system-policy", "system-a")
        shared = _policy("shared-policy", "other-app")
        selected = json.dumps([own])
        samples = [
            ('{"value":' + json.dumps([shared, own]) + ',"value":' + selected + '}').encode(),
            ('{"value":' + selected.replace('"objectId":',
             '"objectId":"other-app","objectId":', 1) + '}').encode(),
            b"not-json", b"\xff",
        ]
        samples.extend(('{"value":' + selected + ',"ignored":' + value + '}').encode()
                       for value in ("NaN", "Infinity", "-Infinity", "1e999"))
        for raw in samples:
            with self.subTest(raw=raw):
                vfs = _MemoryVfs(SYSTEM_AUTH)
                arm = _MemoryArm(_site_identity(), [own, shared])
                arm.policy_raw = raw
                with self.assertRaises(ClientRequestError):
                    self._delete(vfs, arm)
                self.assertIn("selected", vfs.payload["managedApiConnections"])
                self.assertEqual([], vfs.writes)
                self.assertEqual([], arm.deletes)
                self.assertTrue(arm.exists)
                self.assertEqual([own, shared], arm.policies)

    def test_ambiguous_or_nonfinite_site_identity_json_never_establishes_exclusivity(self):
        identity = json.dumps(_site_identity())
        samples = [
            ('{"identity":{"type":"None"},"identity":' + identity + '}').encode(),
            ('{"identity":' + identity.replace('"principalId": "system-a"',
             '"principalId":"other-app","principalId":"system-a"', 1) + '}').encode(),
            b"not-json", b"\xff", b"[]",
        ]
        samples.extend(('{"identity":' + identity + ',"ignored":' + value + '}').encode()
                       for value in ("NaN", "Infinity", "-Infinity", "1e999"))
        for raw in samples:
            with self.subTest(raw=raw):
                policy = _policy("system-policy", "system-a")
                vfs = _MemoryVfs(SYSTEM_AUTH)
                arm = _MemoryArm(_site_identity(), [policy])
                arm.identity_raw = raw
                with self.assertRaises(ClientRequestError):
                    self._delete(vfs, arm)
                self.assertIn("selected", vfs.payload["managedApiConnections"])
                self.assertEqual([], vfs.writes)
                self.assertEqual([], arm.deletes)
                self.assertTrue(arm.exists)
                self.assertEqual([policy], arm.policies)

    def test_missing_or_other_authentication_never_infers_assigned_identity_ownership(self):
        for authentication in (None, {}, {"type": "Raw"}, {"type": "ManagedServiceIdentity", "identity": ""}):
            with self.subTest(authentication=authentication):
                arm = _MemoryArm(_site_identity(), [_policy("system-policy", "system-a")])
                result = self._delete(_MemoryVfs(authentication), arm)
                self.assertEqual([], arm.deletes)
                self.assertTrue(result["resource"]["retained"])
                self.assertEqual(["system-policy"], result["accessPolicies"]["retained"])
                self.assertIsNotNone(result["resource"]["reason"])

    def test_another_entry_in_same_app_preserves_system_acl_and_resource(self):
        for keep_resource in (False, True):
            for alias_id in (CONNECTION_ID, CONNECTION_ID.upper() + "/"):
                with self.subTest(keep_resource=keep_resource, alias_id=alias_id):
                    vfs = _MemoryVfs(SYSTEM_AUTH, alias=SYSTEM_AUTH)
                    vfs.payload["managedApiConnections"]["alias"]["connection"]["id"] = alias_id
                    arm = _MemoryArm(_site_identity(), [_policy("system-policy", "system-a")])
                    result = self._delete(vfs, arm, keep_resource)
                    self.assertIn("alias", vfs.payload["managedApiConnections"])
                    self.assertEqual([], arm.deletes)
                    self.assertIn("another", result["resource"]["reason"].lower())

    def test_another_connection_resource_does_not_block_exclusive_system_delete(self):
        vfs = _MemoryVfs(SYSTEM_AUTH, alias=SYSTEM_AUTH)
        vfs.payload["managedApiConnections"]["alias"]["connection"]["id"] = CONNECTION_ID + "-other"
        arm = _MemoryArm(_site_identity(), [_policy("system-policy", "system-a")])
        result = self._delete(vfs, arm)
        self.assertTrue(result["resource"]["removed"])
        self.assertIn("alias", vfs.payload["managedApiConnections"])

    def test_failed_connections_write_never_revokes_access_or_deletes_resource(self):
        vfs = _MemoryVfs(SYSTEM_AUTH)
        vfs.fail_write = True
        arm = _MemoryArm(_site_identity(), [_policy("system-policy", "system-a")])
        with self.assertRaises(ClientRequestError):
            self._delete(vfs, arm)
        self.assertIn("selected", vfs.payload["managedApiConnections"])
        self.assertEqual([], arm.deletes)

    def test_explicit_null_identity_uses_system_identity(self):
        authentication = {"type": "managedserviceidentity", "identity": None}
        arm = _MemoryArm(_site_identity(), [_policy("system-policy", "system-a")])
        result = self._delete(_MemoryVfs(authentication), arm)
        self.assertTrue(result["resource"]["removed"])

    def test_untyped_app_identity_is_not_considered_exclusive(self):
        arm = _MemoryArm({"principalId": "system-a"}, [_policy("system-policy", "system-a")])
        result = self._delete(_MemoryVfs(SYSTEM_AUTH), arm)
        self.assertEqual([], arm.deletes)
        self.assertIn("verified", result["resource"]["reason"])

    def test_incomplete_or_malformed_policy_listing_cannot_prove_resource_ownership(self):
        own_policy = _policy("system-policy", "system-a")
        listings = (
            {"value": [own_policy], "nextLink": "https://management.azure.com/more"},
            {"value": [own_policy, {}]},
            {"value": "invalid"},
            [own_policy],
        )
        for listing in listings:
            with self.subTest(listing=listing):
                arm = _MemoryArm(_site_identity(), [own_policy])
                arm.policy_listing = listing
                result = self._delete(_MemoryVfs(SYSTEM_AUTH), arm)
                self.assertTrue(arm.exists)
                self.assertNotIn(CONNECTION_ID, arm.deletes)
                self.assertIn("complete access policy list", result["resource"]["reason"])

    def test_malformed_principal_type_is_not_exclusive_acl_ownership(self):
        policy = _policy("unknown-policy", "system-a")
        policy["properties"]["principal"].pop("type")
        arm = _MemoryArm(_site_identity(), [policy])
        result = self._delete(_MemoryVfs(SYSTEM_AUTH), arm)
        self.assertEqual([], arm.deletes)
        self.assertEqual(["unknown-policy"], result["accessPolicies"]["retained"])

    def test_false_valued_policy_continuations_retain_all_acls_before_and_after_unlink(self):
        policies = [_policy("system-policy", "system-a"), _policy("second-policy", "system-a")]
        for continuation in (False, 0, 0.0, [], {}):
            for keep_resource in (False, True):
                for after_unlink in (False, True):
                    with self.subTest(continuation=continuation, keep_resource=keep_resource,
                                      after_unlink=after_unlink):
                        vfs = _MemoryVfs(SYSTEM_AUTH)
                        arm = _MemoryArm(_site_identity(), policies)
                        incomplete = {"value": policies, "nextLink": continuation}
                        if after_unlink:
                            write = vfs.put_raw

                            def change_listing(*args, **kwargs):
                                receipt = write(*args, **kwargs)
                                arm.policy_listing = incomplete
                                return receipt

                            vfs.put_raw = change_listing
                        else:
                            arm.policy_listing = incomplete
                        result = self._delete(vfs, arm, keep_resource=keep_resource)
                        self.assertTrue(arm.exists)
                        self.assertEqual(policies, arm.policies)
                        self.assertEqual([], arm.deletes)
                        self.assertEqual([], result["accessPolicies"]["removed"])
                        self.assertEqual(["system-policy", "second-policy"],
                                         result["accessPolicies"]["retained"])
                        self.assertNotIn("selected", vfs.payload["managedApiConnections"])
                        self.assertFalse(result["resource"]["removed"])

    def test_only_absent_null_or_empty_string_policy_continuations_prove_completeness(self):
        policy = _policy("system-policy", "system-a")
        for listing in ({"value": [policy]}, {"value": [policy], "nextLink": None},
                        {"value": [policy], "nextLink": ""}):
            with self.subTest(listing=listing):
                arm = _MemoryArm(_site_identity(), [policy])
                arm.policy_listing = listing
                result = self._delete(_MemoryVfs(SYSTEM_AUTH), arm)
                self.assertEqual([CONNECTION_ID + "/accessPolicies/system-policy", CONNECTION_ID], arm.deletes)
                self.assertTrue(result["resource"]["removed"])

    def test_connections_entry_is_persisted_before_any_arm_delete(self):
        vfs = _MemoryVfs(SYSTEM_AUTH)
        arm = _MemoryArm(_site_identity(), [_policy("system-policy", "system-a")])
        original_send = arm.send

        def send(ctx, method, url, **kwargs):
            if method == "DELETE":
                self.assertNotIn("selected", vfs.payload["managedApiConnections"])
                self.assertEqual(1, len(vfs.writes))
            return original_send(ctx, method, url, **kwargs)

        arm.send = send
        self._delete(vfs, arm)
        self.assertFalse(arm.exists)

    def test_initial_arm_read_failures_preserve_the_entire_file_and_resources(self):
        for stage in ("identity", "policies"):
            for error_type in (OSError, ClientRequestError):
                with self.subTest(stage=stage, error_type=error_type):
                    vfs = _MemoryVfs(SYSTEM_AUTH)
                    before = copy.deepcopy(vfs.payload)
                    policy = _policy("system-policy", "system-a")
                    arm = _MemoryArm(_site_identity(), [policy])
                    original_send = arm.send

                    def unavailable(ctx, method, url, **kwargs):
                        match = ("/providers/Microsoft.Web/sites/" in url if stage == "identity"
                                 else "/accessPolicies?" in url)
                        if method == "GET" and match:
                            self.assertEqual([], vfs.writes)
                            raise error_type("ownership preflight unavailable")
                        return original_send(ctx, method, url, **kwargs)

                    arm.send = unavailable
                    with self.assertRaises(error_type):
                        self._delete(vfs, arm)
                    self.assertEqual(before, vfs.payload)
                    self.assertEqual([], vfs.writes)
                    self.assertEqual([], arm.deletes)
                    self.assertEqual([policy], arm.policies)
                    self.assertTrue(arm.exists)

    def test_ownership_evidence_is_refreshed_after_unlink_before_arm_mutation(self):
        vfs = _MemoryVfs(SYSTEM_AUTH)
        own = _policy("system-policy", "system-a")
        shared = _policy("new-shared-policy", "other-app")
        arm = _MemoryArm(_site_identity(), [own])
        original_put = vfs.put_raw

        def add_shared_policy(*args, **kwargs):
            receipt = original_put(*args, **kwargs)
            arm.policies.append(shared)
            return receipt

        vfs.put_raw = add_shared_policy
        result = self._delete(vfs, arm)
        self.assertTrue(arm.exists)
        self.assertEqual([shared], arm.policies)
        self.assertEqual([CONNECTION_ID + "/accessPolicies/system-policy"], arm.deletes)
        self.assertEqual(["new-shared-policy"], result["accessPolicies"]["retained"])
        self.assertIn("shared", result["resource"]["reason"])

    def test_late_invalid_ownership_evidence_retains_arm_without_unsafe_file_replay(self):
        vfs = _MemoryVfs(SYSTEM_AUTH)
        policy = _policy("system-policy", "system-a")
        arm = _MemoryArm(_site_identity(), [policy])
        original_put = vfs.put_raw

        def invalidate_after_unlink(*args, **kwargs):
            receipt = original_put(*args, **kwargs)
            arm.policy_raw = b'{"value":[],"value":[]}'
            return receipt

        vfs.put_raw = invalidate_after_unlink
        with self.assertRaises(ClientRequestError):
            self._delete(vfs, arm)
        self.assertNotIn("selected", vfs.payload["managedApiConnections"])
        self.assertEqual(1, len(vfs.writes))
        self.assertEqual([], arm.deletes)
        self.assertEqual([policy], arm.policies)
        self.assertTrue(arm.exists)

    def test_already_removed_system_acl_does_not_abort_resource_delete(self):
        vfs = _MemoryVfs(SYSTEM_AUTH)
        arm = _MemoryArm(_site_identity(), [_policy("system-policy", "system-a")])
        original_send = arm.send

        def send(ctx, method, url, **kwargs):
            if method == "DELETE" and "/accessPolicies/" in url:
                raise ResourceNotFoundError("already removed")
            return original_send(ctx, method, url, **kwargs)

        arm.send = send
        result = self._delete(vfs, arm)
        self.assertTrue(result["resource"]["removed"])
        self.assertEqual([], result["accessPolicies"]["removed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
