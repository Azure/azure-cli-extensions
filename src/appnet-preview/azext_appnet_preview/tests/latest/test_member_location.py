# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from types import SimpleNamespace
from unittest import mock

from azure.cli.core.azclierror import RequiredArgumentMissingError
from azure.core.exceptions import HttpResponseError, ServiceRequestError

from azext_appnet_preview.custom import MemberJoin


class _FakeArg:
    """Minimal stand-in for an AAZ arg value used by the resolution logic."""

    def __init__(self, value, has=True):
        self._value = value
        self._has = has

    def to_serialized_data(self):
        return self._value


def _has_value(arg):
    return isinstance(arg, _FakeArg) and arg._has


def _make_member(location_arg, resource_id_arg):
    # Build a MemberJoin without running the full AAZCommand __init__; the
    # resolution helpers only rely on self.cli_ctx and self.ctx.args.
    member = object.__new__(MemberJoin)
    member.cli_ctx = mock.MagicMock()
    args = SimpleNamespace(member_location=location_arg, member_resource_id=resource_id_arg)
    member.ctx = SimpleNamespace(args=args)
    return member, args


VALID_ID = (
    "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg/"
    "providers/Microsoft.ContainerService/managedClusters/cluster1"
)


class MemberLocationResolutionTest(unittest.TestCase):

    @mock.patch("azext_appnet_preview.custom.has_value", side_effect=_has_value)
    @mock.patch("azext_appnet_preview.custom.is_valid_resource_id", return_value=True)
    @mock.patch("azext_appnet_preview.custom.get_mgmt_service_client")
    def test_location_defaults_to_cluster_location(self, mock_client_factory, _mock_valid, _mock_has):
        mock_client_factory.return_value.resources.get_by_id.return_value = SimpleNamespace(location="eastus2")
        member, args = _make_member(
            location_arg=_FakeArg(None, has=False),
            resource_id_arg=_FakeArg(VALID_ID),
        )

        member._resolve_member_location(args)

        self.assertEqual(args.member_location, "eastus2")

    @mock.patch("azext_appnet_preview.custom.has_value", side_effect=_has_value)
    def test_missing_location_and_cluster_raises(self, _mock_has):
        member, args = _make_member(
            location_arg=_FakeArg(None, has=False),
            resource_id_arg=_FakeArg(None, has=False),
        )

        with self.assertRaises(RequiredArgumentMissingError):
            member._resolve_member_location(args)

    @mock.patch("azext_appnet_preview.custom.logger")
    @mock.patch("azext_appnet_preview.custom.has_value", side_effect=_has_value)
    @mock.patch("azext_appnet_preview.custom.is_valid_resource_id", return_value=True)
    @mock.patch("azext_appnet_preview.custom.get_mgmt_service_client")
    def test_explicit_location_matching_cluster_no_warning(
            self, mock_client_factory, _mock_valid, _mock_has, mock_logger):
        mock_client_factory.return_value.resources.get_by_id.return_value = SimpleNamespace(location="eastus2")
        member, args = _make_member(
            location_arg=_FakeArg("EastUS2"),
            resource_id_arg=_FakeArg(VALID_ID),
        )

        member._resolve_member_location(args)

        self.assertEqual(args.member_location.to_serialized_data(), "EastUS2")
        mock_logger.warning.assert_not_called()

    @mock.patch("azext_appnet_preview.custom.logger")
    @mock.patch("azext_appnet_preview.custom.has_value", side_effect=_has_value)
    @mock.patch("azext_appnet_preview.custom.is_valid_resource_id", return_value=True)
    @mock.patch("azext_appnet_preview.custom.get_mgmt_service_client")
    def test_explicit_location_mismatch_warns(
            self, mock_client_factory, _mock_valid, _mock_has, mock_logger):
        mock_client_factory.return_value.resources.get_by_id.return_value = SimpleNamespace(location="eastus2")
        member, args = _make_member(
            location_arg=_FakeArg("westus2"),
            resource_id_arg=_FakeArg(VALID_ID),
        )

        member._resolve_member_location(args)

        self.assertEqual(args.member_location.to_serialized_data(), "westus2")
        mock_logger.warning.assert_called_once()

    @mock.patch("azext_appnet_preview.custom.has_value", side_effect=_has_value)
    @mock.patch("azext_appnet_preview.custom.is_valid_resource_id", return_value=False)
    def test_invalid_resource_id_returns_none(self, _mock_valid, _mock_has):
        member, args = _make_member(
            location_arg=_FakeArg(None, has=False),
            resource_id_arg=_FakeArg("not-a-resource-id"),
        )

        self.assertIsNone(member._get_member_cluster_location(args))

    def test_member_location_schema_is_optional_and_not_configured_defaulted(self):
        schema = MemberJoin._build_arguments_schema()
        ml = schema.member_location
        self.assertFalse(ml._required)
        # The resource-group location auto-fill and the 'location' configured default must
        # both be cleared, otherwise an omitted --member-location would silently resolve to
        # the RG location or `az configure --defaults location=...` and skip auto-detect.
        self.assertIsNone(getattr(ml._fmt, "_resource_group_arg", None))
        self.assertIsNone(ml._configured_default)

    @mock.patch("azext_appnet_preview.custom.has_value", side_effect=_has_value)
    @mock.patch("azext_appnet_preview.custom.is_valid_resource_id", return_value=True)
    @mock.patch("azext_appnet_preview.custom.get_mgmt_service_client")
    def test_arm_read_failure_returns_none(self, mock_client_factory, _mock_valid, _mock_has):
        mock_client_factory.return_value.resources.get_by_id.side_effect = HttpResponseError(message="not found")
        member, args = _make_member(
            location_arg=_FakeArg(None, has=False),
            resource_id_arg=_FakeArg(VALID_ID),
        )

        self.assertIsNone(member._get_member_cluster_location(args))

    @mock.patch("azext_appnet_preview.custom.has_value", side_effect=_has_value)
    @mock.patch("azext_appnet_preview.custom.is_valid_resource_id", return_value=True)
    @mock.patch("azext_appnet_preview.custom.get_mgmt_service_client")
    def test_arm_transport_failure_returns_none(self, mock_client_factory, _mock_valid, _mock_has):
        # ServiceRequestError subclasses AzureError but NOT HttpResponseError; connection
        # and timeout failures must also be treated as location-unavailable.
        mock_client_factory.return_value.resources.get_by_id.side_effect = ServiceRequestError(message="conn reset")
        member, args = _make_member(
            location_arg=_FakeArg(None, has=False),
            resource_id_arg=_FakeArg(VALID_ID),
        )

        self.assertIsNone(member._get_member_cluster_location(args))

    @mock.patch("azext_appnet_preview.custom.has_value", side_effect=_has_value)
    @mock.patch("azext_appnet_preview.custom.is_valid_resource_id", return_value=True)
    @mock.patch("azext_appnet_preview.custom.get_mgmt_service_client")
    def test_explicit_location_honored_when_cluster_unreadable(
            self, mock_client_factory, _mock_valid, _mock_has):
        # ARM read fails, but the user supplied --member-location explicitly: it must be
        # honored without raising and without a spurious mismatch warning.
        mock_client_factory.return_value.resources.get_by_id.side_effect = HttpResponseError(message="forbidden")
        member, args = _make_member(
            location_arg=_FakeArg("westus2"),
            resource_id_arg=_FakeArg(VALID_ID),
        )

        member._resolve_member_location(args)

        self.assertEqual(args.member_location.to_serialized_data(), "westus2")


if __name__ == "__main__":
    unittest.main()
