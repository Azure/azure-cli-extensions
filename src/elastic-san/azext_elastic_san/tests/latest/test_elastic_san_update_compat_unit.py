# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------

import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from azure.cli.core.aaz._arg_action import AAZAnyTypeArgAction

from azext_elastic_san.custom import (
    ElasticSanCreate,
    ElasticSanUpdate,
    VolumeCreate,
    VolumeGroupCreate,
    VolumeGroupList,
    VolumeGroupUpdate,
    VolumeList,
    VolumeUpdate,
    _add_legacy_managed_by_output,
    _normalize_managed_by_argument,
)


class ElasticSanUpdateCompatTest(unittest.TestCase):
    def _create_body(self, args_data):
        schema = ElasticSanCreate._build_arguments_schema()
        command = object.__new__(ElasticSanCreate)
        command.callbacks = {}
        command.ctx = SimpleNamespace(
            args=schema._ValueCls(schema, schema.process_data(args_data)),
            get_http_client=Mock(),
        )
        command.pre_operations()
        return command.ElasticSansCreate(ctx=command.ctx).content

    def test_v2_create_sends_only_minimum_properties(self):
        body = self._create_body({
            "location": "eastus2euap",
            "sku": {"name": "ElasticSAN_LRS"},
            "version": "V2",
            "total_iops": 100000,
            "total_mbps": 1000,
            "total_size_tib": 25,
            "auto_scale_policy_enforcement": "Enabled",
            "capacity_unit_scale_up_limit_tib": 30,
            "increase_capacity_unit_by_tib": 4,
            "unused_size_tib": 14,
        })
        self.assertEqual(body, {
            "location": "eastus2euap",
            "properties": {
                "sku": {"name": "ElasticSAN_LRS"},
                "version": "V2",
                "totalIops": 100000,
                "totalMBps": 1000,
                "totalSizeTiB": 25,
                "autoScaleProperties": {
                    "scaleUpProperties": {
                        "autoScalePolicyEnforcement": "Enabled",
                        "capacityUnitScaleUpLimitTiB": 30,
                        "increaseCapacityUnitByTiB": 4,
                        "unusedSizeTiB": 14,
                    },
                },
            },
        })

    def test_v1_create_preserves_capacity_defaults(self):
        for version in ({}, {"version": "V1"}):
            with self.subTest(version=version):
                body = self._create_body({"sku": {"name": "Premium_LRS"}, **version})
                self.assertEqual(body["properties"]["baseSizeTiB"], 20)
                self.assertEqual(body["properties"]["extendedCapacitySizeTiB"], 0)

    def test_create_preserves_explicit_capacities(self):
        for version in ("V1", "V2"):
            with self.subTest(version=version):
                body = self._create_body({
                    "version": version,
                    "sku": {"name": "Premium_LRS" if version == "V1" else "ElasticSAN_LRS"},
                    "base_size_tib": 23,
                    "extended_capacity_size_tib": 14,
                })
                self.assertEqual(body["properties"]["baseSizeTiB"], 23)
                self.assertEqual(body["properties"]["extendedCapacitySizeTiB"], 14)

    def test_regenerated_extension_loads_custom_commands(self):
        from azure.cli.core.mock import DummyCli
        from azext_elastic_san import ElasticSanCommandsLoader

        command_table = ElasticSanCommandsLoader(cli_ctx=DummyCli()).load_command_table(None)
        self.assertIsInstance(command_table["elastic-san update"], ElasticSanUpdate)
        self.assertIsInstance(command_table["elastic-san volume-group update"], VolumeGroupUpdate)
        self.assertIn("elastic-san create", command_table)

    def _execute_update(self, command_type, args_data, resource, actions, force_string=False):
        schema = command_type._build_arguments_schema()
        args = schema._ValueCls(schema, schema.process_data(args_data))
        command = object.__new__(command_type)
        command.callbacks = {}
        command.ctx = SimpleNamespace(
            args=args,
            vars=SimpleNamespace(),
            generic_update_args={"actions": actions, "force_string": force_string},
            get_http_client=Mock(),
        )
        is_san = command_type is ElasticSanUpdate
        get_type = command.ElasticSansGet if is_san else command.VolumeGroupsGet
        update_type = command.ElasticSansUpdate if is_san else command.VolumeGroupsUpdate
        if is_san and ("sku" in args_data or "availability_zones" in args_data):
            update_type = command.ElasticSanReplace
        events = []
        bodies = []

        def get_instance(operation):
            events.append("GET")
            instance_schema = operation._build_schema_on_200()
            operation.ctx.vars.instance = instance_schema._ValueCls(
                instance_schema, instance_schema.process_data(resource)
            )

        def send_update(operation):
            events.append(operation.method)
            bodies.append(operation.content)

        command.post_operations = Mock()
        with patch.object(get_type, "__call__", get_instance), \
                patch.object(update_type, "__call__", send_update):
            list(command._execute_operations())
        command.post_operations.assert_called_once()
        return events, bodies[0]

    def test_san_patch_merges_explicit_and_generic_updates(self):
        events, body = self._execute_update(
            ElasticSanUpdate,
            {"base_size_tib": 25},
            {
                "location": "eastus2euap",
                "tags": {"remove": "old", "keep": "original"},
                "properties": {
                    "sku": {"name": "Premium_LRS"},
                    "availabilityZones": ["1"],
                    "version": "V1",
                    "baseSizeTiB": 23,
                    "extendedCapacitySizeTiB": 14,
                    "provisioningState": "Succeeded",
                },
            },
            [("set", ["tags.keep=123", "baseSizeTiB=26"]), ("remove", ["tags.remove"])],
            force_string=True,
        )
        self.assertEqual(events, ["GET", "PATCH"])
        self.assertEqual(body["tags"], {"keep": "123"})
        self.assertEqual(body["properties"]["baseSizeTiB"], 26)
        self.assertEqual(body["properties"]["extendedCapacitySizeTiB"], 14)
        self.assertNotIn("location", body)
        for key in ("sku", "availabilityZones", "version", "provisioningState"):
            self.assertNotIn(key, body["properties"])

    def test_san_legacy_options_select_put_and_keep_explicit_updates(self):
        events, body = self._execute_update(
            ElasticSanUpdate,
            {"sku": {"name": "Premium_ZRS"}, "base_size_tib": 25},
            {
                "location": "eastus2euap",
                "tags": {"keep": "original"},
                "properties": {"sku": {"name": "Premium_LRS"}, "baseSizeTiB": 23},
            },
            [("set", ["tags.added=value"])],
        )
        self.assertEqual(events, ["GET", "PUT"])
        self.assertEqual(body["location"], "eastus2euap")
        self.assertEqual(body["properties"]["sku"]["name"], "Premium_ZRS")
        self.assertEqual(body["properties"]["baseSizeTiB"], 25)
        self.assertEqual(body["tags"], {"keep": "original", "added": "value"})

    def test_volume_group_patch_supports_add_set_and_remove(self):
        events, body = self._execute_update(
            VolumeGroupUpdate,
            {"reserved_iops": 1000},
            {"properties": {
                "protocolType": "iSCSI",
                "reservedIops": 500,
                "networkAcls": {"virtualNetworkRules": [
                    {"id": "/subnets/old", "action": "Allow"},
                ]},
                "qualityOfService": "PerformanceCritical",
                "encryptionInTransit": True,
                "provisioningState": "Succeeded",
            }},
            [
                ("add", ["networkAcls.virtualNetworkRules", "id=/subnets/new", "action=Allow"]),
                ("remove", ["networkAcls.virtualNetworkRules", "0"]),
                ("set", ["reservedMBps=100"]),
            ],
        )
        self.assertEqual(events, ["GET", "PATCH"])
        self.assertEqual(body["properties"]["reservedIops"], 1000)
        self.assertEqual(body["properties"]["reservedMBps"], 100)
        self.assertEqual(body["properties"]["networkAcls"]["virtualNetworkRules"],
                         [{"id": "/subnets/new", "action": "Allow"}])
        for key in ("qualityOfService", "encryptionInTransit", "provisioningState"):
            self.assertNotIn(key, body["properties"])

    def test_volume_group_legacy_identity_none_clears_identity(self):
        events, body = self._execute_update(
            VolumeGroupUpdate,
            {"identity": {"type": "None"}},
            {
                "identity": {
                    "type": "SystemAssigned, UserAssigned",
                    "principalId": "principal",
                    "userAssignedIdentities": {"/identities/old": {"clientId": "client"}},
                },
                "properties": {"protocolType": "iSCSI"},
            },
            [],
        )
        self.assertEqual(events, ["GET", "PATCH"])
        self.assertEqual(body["identity"]["type"], "None")
        self.assertEqual(body["identity"]["userAssignedIdentities"], {})

    def test_volume_group_disabling_system_identity_keeps_user_identity(self):
        _, body = self._execute_update(
            VolumeGroupUpdate,
            {"mi_system_assigned": "False"},
            {
                "identity": {
                    "type": "SystemAssigned, UserAssigned",
                    "userAssignedIdentities": {"/identities/keep": {"clientId": "client"}},
                },
                "properties": {"protocolType": "iSCSI"},
            },
            [],
        )
        self.assertEqual(body["identity"]["type"], "UserAssigned")
        self.assertEqual(body["identity"]["userAssignedIdentities"], {"/identities/keep": {}})

    def test_update_commands_register_generic_update_arguments(self):
        for command in (ElasticSanUpdate, VolumeGroupUpdate):
            with self.subTest(command=command.__name__):
                args_schema = command._build_arguments_schema()

                self.assertTrue(command.AZ_SUPPORT_GENERIC_UPDATE)
                self.assertTrue(hasattr(args_schema, "generic_update_add"))
                self.assertTrue(hasattr(args_schema, "generic_update_set"))
                self.assertTrue(hasattr(args_schema, "generic_update_remove"))
                self.assertTrue(hasattr(args_schema, "generic_update_force_string"))

    def test_long_options_have_short_aliases(self):
        for command in (VolumeList, VolumeGroupList):
            with self.subTest(command=command.__name__):
                arg = command._build_arguments_schema()._fields["x_ms_access_soft_deleted_resources"]
                self.assertIn("-a", arg._options)

        for command in (VolumeGroupCreate, VolumeGroupUpdate):
            with self.subTest(command=command.__name__):
                arg = command._build_arguments_schema()._fields["delete_retention_policy"]
                self.assertIn("-d", arg._options)

    def test_legacy_sku_and_zones_use_full_put_body(self):
        args_schema = ElasticSanUpdate._build_arguments_schema()
        args = args_schema._ValueCls(
            args_schema,
            args_schema.process_data({
                "elastic_san_name": "test-san",
                "resource_group": "test-rg",
                "sku": {"name": "ElasticSAN_LRS"},
                "availability_zones": ["2"],
            }),
        )
        instance_schema = ElasticSanUpdate.ElasticSansGet._build_schema_on_200()
        instance = instance_schema._ValueCls(
            instance_schema,
            instance_schema.process_data({
                "id": "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.ElasticSan/elasticSans/test-san",
                "name": "test-san",
                "location": "eastus2",
                "type": "Microsoft.ElasticSan/elasticSans",
                "tags": {"keep": "tag"},
                "properties": {
                    "sku": {"name": "Premium_LRS", "tier": "Premium"},
                    "availabilityZones": ["1"],
                    "baseSizeTiB": 23,
                    "extendedCapacitySizeTiB": 14,
                    "publicNetworkAccess": "Enabled",
                    "version": "V1",
                },
            }),
        )
        operation = object.__new__(ElasticSanUpdate.ElasticSanReplace)
        operation.ctx = SimpleNamespace(args=args, vars=SimpleNamespace(instance=instance))

        body = operation.content

        self.assertEqual(operation.method, "PUT")
        self.assertEqual(body["location"], "eastus2")
        self.assertEqual(body["tags"], {"keep": "tag"})
        self.assertEqual(body["properties"]["sku"]["name"], "ElasticSAN_LRS")
        self.assertEqual(body["properties"]["availabilityZones"], ["2"])
        self.assertEqual(body["properties"]["baseSizeTiB"], 23)
        self.assertEqual(body["properties"]["extendedCapacitySizeTiB"], 14)

    def test_legacy_sku_enum_includes_elastic_san_sku(self):
        args_schema = ElasticSanUpdate._build_arguments_schema()

        self.assertIn("ElasticSAN_LRS", args_schema.sku.name.enum.to_choices())


class VolumeManagedByCompatTest(unittest.TestCase):
    def test_legacy_managed_by_object_converts_to_single_resource_array(self):
        legacy_managed_by = AAZAnyTypeArgAction.decode_str(
            "{resource-id:/subscriptions/sub/resourceGroups/rg/providers/test/type/name}"
        )
        for command in (VolumeCreate, VolumeUpdate):
            with self.subTest(command=command.__name__):
                args_schema = command._build_arguments_schema()
                args_data = args_schema.process_data({
                    "managed_by": legacy_managed_by
                })
                args = args_schema._ValueCls(args_schema, args_data)

                _normalize_managed_by_argument(args)

                self.assertEqual(
                    args.managed_by.to_serialized_data(),
                    [{"resource_ids": ["/subscriptions/sub/resourceGroups/rg/providers/test/type/name"]}],
                )

    def test_legacy_managed_by_object_serializes_as_current_wire_array(self):
        args_schema = VolumeCreate._build_arguments_schema()
        args = args_schema._ValueCls(
            args_schema,
            args_schema.process_data({
                "elastic_san_name": "test-san",
                "resource_group": "test-rg",
                "volume_group_name": "test-group",
                "volume_name": "test-volume",
                "size_gib": 1,
                "managed_by": {"resource-id": "/resource/legacy"},
            }),
        )
        _normalize_managed_by_argument(args)
        operation = object.__new__(VolumeCreate.VolumesCreate)
        operation.ctx = SimpleNamespace(args=args)

        body = operation.content

        self.assertEqual(
            body["properties"]["managedBy"],
            [{"resourceIds": ["/resource/legacy"]}],
        )

    def test_current_managed_by_array_remains_unchanged(self):
        args_schema = VolumeCreate._build_arguments_schema()
        args_data = args_schema.process_data({
            "managed_by": [{"client_id": "client", "resource_ids": ["/subscriptions/sub/resourceGroups/rg/providers/test/type/name"]}]
        })
        args = args_schema._ValueCls(args_schema, args_data)

        _normalize_managed_by_argument(args)

        self.assertEqual(
            args.managed_by.to_serialized_data(),
            [{"client_id": "client", "resource_ids": ["/subscriptions/sub/resourceGroups/rg/providers/test/type/name"]}],
        )

    def test_output_keeps_new_shape_and_adds_first_resource_alias(self):
        output = {
            "properties": {
                "managedBy": [
                    {"resourceIds": ["/resource/first", "/resource/second"]},
                    {"resourceIds": ["/resource/third"]},
                ]
            }
        }

        result = _add_legacy_managed_by_output(output)

        self.assertEqual(result["properties"]["managedBy"], output["properties"]["managedBy"])
        self.assertEqual(result["properties"]["managedByResourceId"], "/resource/first")


if __name__ == "__main__":
    unittest.main()
