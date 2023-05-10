from azext_load.data_plane.utils import argtypes


def load_arguments(self, _):
    # Load Test Run
    with self.argument_context("load test-run create") as c:
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

    with self.argument_context("load test-run download-files") as c:
        c.argument("path", argtypes.path)
        c.argument("test_run_input", argtypes.test_run_input)
        c.argument("test_run_log", argtypes.test_run_log)
        c.argument("test_run_results", argtypes.test_run_results)
    #

    # Load Test App Components
    with self.argument_context("load test-run app-components") as c:
        c.argument("app_component_id", argtypes.app_component_id)

    with self.argument_context("load test-run app-components create") as c:
        c.argument("app_component_type", argtypes.app_component_type)
        c.argument("app_component_name", argtypes.app_component_name)
        c.argument("app_component_type", argtypes.app_component_type)
    #

    # Load Test Server Metrics
    with self.argument_context("load test-run server-metrics") as c:
        c.argument("metric_id", argtypes.metric_id)

    with self.argument_context("load test-run server-metrics add") as c:
        c.argument("metric_name", argtypes.metric_name)
        c.argument("metric_namespace", argtypes.metric_namespace)
        c.argument("aggregation", argtypes.aggregation)
        c.argument("app_component_id", argtypes.app_component_id)
        c.argument("app_component_type", argtypes.app_component_type)
    #
