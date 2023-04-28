def load_dataplane_arguments(self, _):
    with self.argument_context('load test') as c:
        c.argument('load_test_resource', options_list=['--name'],type=str, help='The name of load test resource.' )
        c.argument('resource_group', type=str, help='The resource group name where the load test resource is present')