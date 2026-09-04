# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import types
import unittest
from unittest import mock

from azure.cli.core.azclierror import MutuallyExclusiveArgumentError

from azext_aro_hcp.custom import ClusterCreate, GetVersions, RequestCredential


class _Arg:
    def __init__(self, value):
        self.value = value

    def to_serialized_data(self):
        return self.value


class ClusterCreateTest(unittest.TestCase):

    def test_content_adds_identity(self):
        operation_type = ClusterCreate.HcpOpenShiftClustersCreateOrUpdate
        base_type = operation_type.__mro__[1]
        operation = object.__new__(operation_type)

        with mock.patch.object(
                base_type, "content", new_callable=mock.PropertyMock,
                return_value={"properties": {}}):
            self.assertEqual(
                {"properties": {}, "identity": {"type": "UserAssigned"}},
                operation.content,
            )

    def test_content_replaces_identity_type(self):
        operation_type = ClusterCreate.HcpOpenShiftClustersCreateOrUpdate
        base_type = operation_type.__mro__[1]
        operation = object.__new__(operation_type)
        content = {"identity": {"type": "SystemAssigned", "userAssignedIdentities": {}}}

        with mock.patch.object(
                base_type, "content", new_callable=mock.PropertyMock,
                return_value=content):
            self.assertEqual("UserAssigned", operation.content["identity"]["type"])
            self.assertEqual({}, operation.content["identity"]["userAssignedIdentities"])


class GetVersionsTest(unittest.TestCase):

    def _command(self, control_plane=False, node_pools=False):
        command = object.__new__(GetVersions)
        command.ctx = types.SimpleNamespace(args=types.SimpleNamespace(
            control_plane=_Arg(control_plane),
            node_pools=_Arg(node_pools),
        ))
        return command

    @mock.patch("azext_aro_hcp.custom.has_value", return_value=True)
    @mock.patch.object(GetVersions.__mro__[1], "_output")
    def test_default_output_filters_and_sorts_full_versions(self, base_output, _):
        base_output.return_value = ([
            {"name": "4.20.1", "properties": {"enabled": True, "channelGroup": "candidate"}},
            {"name": "4.19.3", "properties": {"enabled": False}},
            {"name": "4.19.2", "properties": {"channelGroup": "stable"}},
        ], "next")

        result, next_link = self._command()._output()

        self.assertEqual(["4.19.2", "4.20.1"], [row["Name"] for row in result])
        self.assertEqual("next", next_link)

    @mock.patch("azext_aro_hcp.custom.has_value", return_value=True)
    @mock.patch.object(GetVersions.__mro__[1], "_output")
    def test_control_plane_output_deduplicates_major_minor(self, base_output, _):
        base_output.return_value = ([
            {"name": "4.20.2", "properties": {"channelGroup": "stable"}},
            {"name": "4.19.3", "properties": {"channelGroup": "stable"}},
            {"name": "4.20.1", "properties": {"channelGroup": "candidate"}},
            {"name": "invalid", "properties": {}},
        ], None)

        result, _ = self._command(control_plane=True)._output()

        self.assertEqual(["4.19", "4.20"], [row["Name"] for row in result])
        self.assertEqual(["stable", "candidate"], [row["ChannelGroup"] for row in result])

    @mock.patch("azext_aro_hcp.custom.has_value", return_value=True)
    @mock.patch.object(GetVersions.__mro__[1], "_output", return_value=([], None))
    def test_flags_are_mutually_exclusive(self, _, __):
        with self.assertRaises(MutuallyExclusiveArgumentError):
            self._command(control_plane=True, node_pools=True)._output()


class RequestCredentialTest(unittest.TestCase):

    def test_handler_without_admin_does_not_call_service(self):
        command = object.__new__(RequestCredential)
        with mock.patch.object(RequestCredential.__mro__[1], "_handler") as base_handler:
            self.assertIsNone(command._handler({"admin": False}))
        base_handler.assert_not_called()

    @mock.patch(
        "azext_aro_hcp._kubeconfig._generate_admin_credential_request",
        return_value=(b"private-key", "csr"),
    )
    @mock.patch.object(RequestCredential.__mro__[1], "_handler", return_value="poller")
    def test_handler_populates_internal_csr(self, base_handler, _):
        command = object.__new__(RequestCredential)
        command_args = {"admin": True}

        self.assertEqual("poller", command._handler(command_args))

        self.assertEqual("csr", command_args["certificate_signing_request"])
        self.assertEqual(b"private-key", command._private_key_pem)
        base_handler.assert_called_once_with(command_args)

    @mock.patch(
        "azext_aro_hcp._kubeconfig._generate_admin_credential_request",
        return_value=(b"private-key", "csr"),
    )
    @mock.patch.object(RequestCredential.__mro__[1], "_handler", side_effect=RuntimeError("failed"))
    def test_handler_clears_key_when_poller_creation_fails(self, _, __):
        command = object.__new__(RequestCredential)
        with self.assertRaisesRegex(RuntimeError, "failed"):
            command._handler({"admin": True})
        self.assertFalse(hasattr(command, "_private_key_pem"))

    @mock.patch("azext_aro_hcp._kubeconfig.print_or_merge_credentials")
    @mock.patch("azext_aro_hcp._kubeconfig._embed_private_key", return_value="embedded")
    @mock.patch.object(RequestCredential, "deserialize_output", return_value={"kubeconfig": "config\\n"})
    @mock.patch("azext_aro_hcp.custom.has_value", return_value=False)
    def test_output_embeds_key_and_uses_default_context(
            self, _, __, embed_private_key, print_or_merge):
        command = object.__new__(RequestCredential)
        command._private_key_pem = b"private-key"
        command.ctx = types.SimpleNamespace(
            vars=types.SimpleNamespace(instance=object()),
            args=types.SimpleNamespace(
                file=_Arg("/tmp/config"),
                context_name=_Arg(None),
                name=_Arg("cluster-one"),
                overwrite_existing=_Arg(False),
            ),
        )

        self.assertIsNone(command._output())

        self.assertFalse(hasattr(command, "_private_key_pem"))
        embed_private_key.assert_called_once_with("config\n", b"private-key")
        print_or_merge.assert_called_once_with(
            "/tmp/config", "embedded", False, "cluster-one-admin"
        )

    def test_hidden_csr_is_added_to_request_content(self):
        operation_type = RequestCredential.HcpOpenShiftClustersRequestAdminCredential
        base_type = operation_type.__mro__[1]
        operation = object.__new__(operation_type)
        operation.ctx = types.SimpleNamespace(
            args=types.SimpleNamespace(certificate_signing_request=_Arg("pem-csr"))
        )

        with mock.patch.object(
                base_type, "content", new_callable=mock.PropertyMock, return_value={}):
            self.assertEqual(
                {"certificateSigningRequest": "pem-csr"},
                operation.content,
            )


if __name__ == "__main__":
    unittest.main()