from azext_load.data_plane.utils import argtypes


def load_arguments(self, _):
    # Load Test
    with self.argument_context("load test show") as c:
        c.argument("test_id", argtypes.test_id)

    with self.argument_context("load test create") as c:
        c.argument("test_id", argtypes.test_id)
        c.argument("env", argtypes.env)
        c.argument("secrets", argtypes.secret)
        c.argument("certificate", argtypes.certificate)

    with self.argument_context("load test update") as c:
        c.argument("test_id", argtypes.test_id)
        c.argument("env", argtypes.env)
        c.argument("secrets", argtypes.secret)
        c.argument("certificate", argtypes.certificate)
    #

    # Load Test App Components
    with self.argument_context("load test app-components") as c:
        c.argument("test_id", argtypes.test_id)

    with self.argument_context("load test app-components add") as c:
        c.argument("app_component_id", argtypes.app_component_id)

    with self.argument_context("load test app-components remove") as c:
        c.argument("app_component_id", argtypes.app_component_id)
    #

    # Load Test Server Metrics
    with self.argument_context("load test server-metrics") as c:
        c.argument("test_id", argtypes.test_id)

    with self.argument_context("load test server-metrics add") as c:
        c.argument("metric_id", argtypes.metric_id)

    with self.argument_context("load test server-metrics remove") as c:
        c.argument("metric_id", argtypes.metric_id)
    #
