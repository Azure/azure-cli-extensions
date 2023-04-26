def load_test_arguments(self):
    with self.argument_context('load test') as c:
        c.argument('--test-name', type=str, help='The name of test to be create.' )
        c.argument('--test-description', type=str, help='Description of test.')