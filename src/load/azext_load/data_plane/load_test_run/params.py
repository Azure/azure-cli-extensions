# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from azext_load.data_plane.utils import argtypes


def load_arguments(self, _):
    # Load Test Run
    with self.argument_context("load test-run create") as c:
        c.argument("test_run_id", argtypes.test_run_id_no_completer)
        c.argument("existing_test_run_id", argtypes.existing_test_run_id)
        c.argument("test_id", argtypes.test_id)
        c.argument("display_name", argtypes.test_run_display_name)
        c.argument("description", argtypes.test_run_description)
        c.argument("env", argtypes.env)
        c.argument("secrets", argtypes.secret)
        c.argument("certificate", argtypes.certificate)

    with self.argument_context("load test-run update") as c:
        c.argument("test_id", argtypes.test_id)
        c.argument("description", argtypes.test_run_description)
        c.argument("display_name", argtypes.test_run_display_name)

    with self.argument_context("load test-run download-files") as c:
        c.argument("path", argtypes.dir_path)
        c.argument("test_run_input", argtypes.test_run_input)
        c.argument("test_run_log", argtypes.test_run_log)
        c.argument("test_run_results", argtypes.test_run_results)
        c.argument("force", argtypes.force)

    with self.argument_context("load test-run list") as c:
        c.argument("test_id", argtypes.test_id)

    # Load Test Run App Components
    with self.argument_context("load test-run app-component") as c:
        c.argument("app_component_id", argtypes.app_component_id)

    with self.argument_context("load test-run app-component add") as c:
        c.argument("app_component_name", argtypes.app_component_name)
        c.argument("app_component_type", argtypes.app_component_type)
        c.argument("app_component_kind", argtypes.app_component_kind)

    # Load Test Run Server Metrics
    with self.argument_context("load test-run server-metric") as c:
        c.argument("metric_id", argtypes.server_metric_id)

    with self.argument_context("load test-run server-metric add") as c:
        c.argument("metric_name", argtypes.server_metric_name)
        c.argument("metric_namespace", argtypes.server_metric_namespace)
        c.argument("aggregation", argtypes.server_metric_aggregation)
        c.argument("app_component_id", argtypes.app_component_id)
        c.argument("app_component_type", argtypes.app_component_type)

    # Load Test Run Metrics
    with self.argument_context("load test-run metrics") as c:
        c.argument("test_run_id", argtypes.test_run_id)

    with self.argument_context("load test-run metrics list") as c:
        c.argument("metric_namespace", argtypes.metric_namespace)
        c.argument("metric_name", argtypes.metric_name)
        c.argument("start_time", argtypes.start_iso_time)
        c.argument("end_time", argtypes.end_iso_time)
        c.argument("aggregation", argtypes.aggregation)
        c.argument("interval", argtypes.interval)
        c.argument("dimension_filters", argtypes.dimension_filters)

    with self.argument_context("load test-run metrics get-definitions") as c:
        c.argument("metric_namespace", argtypes.metric_namespace)

    with self.argument_context("load test-run metrics get-dimensions") as c:
        c.argument("metric_name", argtypes.metric_name)
        c.argument("dimension_name", argtypes.metric_dimension)
        c.argument("metric_namespace", argtypes.metric_namespace)
        c.argument("start_time", argtypes.start_iso_time)
        c.argument("end_time", argtypes.end_iso_time)
        c.argument("interval", argtypes.interval)
