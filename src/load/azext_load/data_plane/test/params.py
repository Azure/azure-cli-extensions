def load_test_arguments(self, _):
    with self.argument_context('load test list') as c:
        c.argument('--load-test-resource', type=str, help='The name of load test resource.' )
        c.argument('--resource-group', type=str, help='The resource group name where the load test resource is present')