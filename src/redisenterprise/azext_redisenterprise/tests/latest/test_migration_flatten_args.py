# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Offline (no Azure) assertions for the ``migration start`` flatten override.

These tests verify that the extension-layer subclass ``MigrationStart`` flattens the
polymorphic ``azureCacheForRedis`` object argument into individual top-level options and
that the generated request body still receives the mapped values. They run entirely
offline (no recordings, no live subscription) and therefore always execute in CI.
"""

import unittest

from azext_redisenterprise.custom import MigrationStart


class MigrationStartFlattenArgsTest(unittest.TestCase):

    def test_flat_args_registered_and_object_hidden(self):
        schema = MigrationStart._build_arguments_schema()

        # The four source properties are exposed as individual top-level arguments.
        for name in ("source_resource_id", "skip_data_migration", "switch_dns", "force_migrate"):
            arg = getattr(schema, name, None)
            self.assertIsNotNone(arg, "expected flat argument '{}' to be registered".format(name))
            self.assertTrue(arg._registered, "flat argument '{}' should be registered".format(name))

        # The three properties that are always applicable stay required at the CLI layer.
        for name in ("source_resource_id", "skip_data_migration", "switch_dns"):
            self.assertTrue(getattr(schema, name)._required,
                            "flat argument '{}' should be required".format(name))
        self.assertFalse(schema.force_migrate._required,
                         "force_migrate should be optional")

        # The original object wrapper is no longer surfaced on the command line.
        self.assertFalse(schema.azure_cache_for_redis._registered,
                         "--azure-cache-for-redis should be hidden after flattening")
        self.assertFalse(schema.azure_cache_for_redis._required,
                         "hidden --azure-cache-for-redis should not be required")

    def test_flat_options_have_expected_names(self):
        schema = MigrationStart._build_arguments_schema()
        expected = {
            "source_resource_id": "--source-resource-id",
            "skip_data_migration": "--skip-data-migration",
            "switch_dns": "--switch-dns",
            "force_migrate": "--force-migrate",
        }
        for name, option in expected.items():
            self.assertIn(option, getattr(schema, name)._options,
                          "argument '{}' should expose option '{}'".format(name, option))


if __name__ == "__main__":
    unittest.main()
