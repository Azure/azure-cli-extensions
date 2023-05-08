from .utils import argtypes

def load_arguments(self, _):
    with self.argument_context('load test') as c:
        c.argument('load_test_resource', argtypes.load_test_resource)
        c.argument('resource_group_name', argtypes.resource_group)
