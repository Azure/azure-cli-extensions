# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=line-too-long

from azext_load.data_plane.utils import argtypes


def load_arguments(self, _):
    # Load Test
    with self.argument_context("load test create") as c:
        c.argument("test_id", argtypes.test_id_no_completer)
        c.argument("test_plan", argtypes.test_plan)
        c.argument("display_name", argtypes.test_display_name)
        c.argument("test_description", argtypes.test_description)
        c.argument("env", argtypes.env, help="space-separated environment variables: key[=value] [key[=value] ...].")
        c.argument("secrets", argtypes.secret, help="space-separated secrets: key[=value] [key[=value] ...]. Secrets should be stored in Azure Key Vault, and the secret identifier should be provided as the value.")
        c.argument("certificate", argtypes.certificate, help="a single certificate in 'key[=value]' format. The certificate should be stored in Azure Key Vault in PFX format, and the certificate identifier should be provided as the value.")
        c.argument("subnet_id", argtypes.subnet_id)
        c.argument("split_csv", argtypes.split_csv)
        c.argument("load_test_config_file", argtypes.load_test_config_file)
        c.argument(
            "key_vault_reference_identity", argtypes.key_vault_reference_identity
        )
        c.argument("engine_instances", argtypes.engine_instances)
        c.argument("custom_no_wait", argtypes.custom_no_wait)

    with self.argument_context("load test update") as c:
        c.argument("load_test_config_file", argtypes.load_test_config_file)
        c.argument("test_plan", argtypes.test_plan)
        c.argument("display_name", argtypes.test_display_name)
        c.argument("test_description", argtypes.test_description)
        c.argument("env", argtypes.env)
        c.argument("secrets", argtypes.secret)
        c.argument("certificate", argtypes.certificate)
        c.argument(
            "key_vault_reference_identity", argtypes.key_vault_reference_identity, help="The identity that will be used to access the key vault. Provide `null` or `None` to use the system assigned identity of the load test resource."
        )
        c.argument("engine_instances", argtypes.engine_instances)
        c.argument("subnet_id", argtypes.subnet_id)
        c.argument("split_csv", argtypes.split_csv)
        c.argument("custom_no_wait", argtypes.custom_no_wait)

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

    with self.argument_context("load test file delete") as c:
        c.argument("file_name", argtypes.file_name)

    # Load Test App Components
    with self.argument_context("load test app-component") as c:
        c.argument("app_component_id", argtypes.app_component_id)

    with self.argument_context("load test app-component add") as c:
        c.argument("app_component_kind", argtypes.app_component_kind)
        c.argument("app_component_name", argtypes.app_component_name)
        c.argument("app_component_type", argtypes.app_component_type)

    # Load Test Server Metrics
    with self.argument_context("load test server-metric") as c:
        c.argument("metric_id", argtypes.server_metric_id)

    with self.argument_context("load test server-metric add") as c:
        c.argument("metric_name", argtypes.server_metric_name)
        c.argument("metric_namespace", argtypes.server_metric_namespace)
        c.argument("aggregation", argtypes.server_metric_aggregation)
        c.argument("app_component_id", argtypes.app_component_id)
        c.argument("app_component_type", argtypes.app_component_type)
