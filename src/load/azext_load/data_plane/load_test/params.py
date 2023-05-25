# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_load.data_plane.utils import argtypes


def load_arguments(self, _):
    # Load Test
    with self.argument_context("load test create") as c:
        c.argument("test_id", argtypes.test_id_no_completer)
        c.argument("test_plan", argtypes.test_plan)
        c.argument("display_name", argtypes.test_display_name)
        c.argument("test_description", argtypes.test_description)
        c.argument("env", argtypes.env)
        c.argument("secrets", argtypes.secret)
        c.argument("certificate", argtypes.certificate)
        c.argument("subnet_id", argtypes.subnet_id)
        c.argument("split_csv", argtypes.split_csv)
        c.argument("load_test_config_file", argtypes.load_test_config_file)
        c.argument(
            "key_vault_reference_identity", argtypes.key_vault_reference_identity
        )
        c.argument("engine_instances", argtypes.engine_instances)
        c.argument("wait", argtypes.wait)

    with self.argument_context("load test update") as c:
        c.argument("load_test_config_file", argtypes.load_test_config_file)
        c.argument("test_plan", argtypes.test_plan)
        c.argument("display_name", argtypes.test_display_name)
        c.argument("test_description", argtypes.test_description)
        c.argument("env", argtypes.env)
        c.argument("secrets", argtypes.secret)
        c.argument("certificate", argtypes.certificate)
        c.argument(
            "key_vault_reference_identity", argtypes.key_vault_reference_identity
        )
        c.argument("engine_instances", argtypes.engine_instances)
        c.argument("subnet_id", argtypes.subnet_id)
        c.argument("split_csv", argtypes.split_csv)
        c.argument("wait", argtypes.wait)

    with self.argument_context("load test download-files") as c:
        c.argument("path", argtypes.dir_path)
        c.argument("force", argtypes.force)

    # Load Test File
    with self.argument_context("load test file download") as c:
        c.argument("file_name", argtypes.file_name)
        c.argument("path", argtypes.dir_path)
        c.argument("force", argtypes.force)

    with self.argument_context("load test file upload") as c:
        c.argument("path", argtypes.file_path)
        c.argument("file_type", argtypes.file_type)
        c.argument("wait", argtypes.wait)

    # Load Test App Components
    with self.argument_context("load test app-components") as c:
        c.argument("app_component_id", argtypes.app_component_id)

    with self.argument_context("load test app-components create") as c:
        c.argument("app_component_type", argtypes.app_component_type)
        c.argument("app_component_name", argtypes.app_component_name)
        c.argument("app_component_type", argtypes.app_component_type)

    # Load Test Server Metrics
    with self.argument_context("load test server-metrics") as c:
        c.argument("metric_id", argtypes.server_metric_id)

    with self.argument_context("load test server-metrics add") as c:
        c.argument("metric_name", argtypes.server_metric_name)
        c.argument("metric_namespace", argtypes.server_metric_namespace)
        c.argument("aggregation", argtypes.server_metric_aggregation)
        c.argument("app_component_id", argtypes.app_component_id)
        c.argument("app_component_type", argtypes.app_component_type)
