from azext_load.data_plane import custom_argtypes


def load_arguments(self, _):
    with self.argument_context('load test show') as c:
        c.argument('test_id', custom_argtypes.test_id)

    with self.argument_context('load test create') as c:
        c.argument('env', custom_argtypes.env_type)
        c.argument('secrets', custom_argtypes.secret_type)
        c.argument('certificate', custom_argtypes.certificate_type)

    with self.argument_context('load test update') as c:
        c.argument('test_id', custom_argtypes.test_id)
        c.argument('env', custom_argtypes.env_type)
        c.argument('secrets', custom_argtypes.secret_type)
        c.argument('certificate', custom_argtypes.certificate_type)