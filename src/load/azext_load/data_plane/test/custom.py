import yaml
from yaml.loader import SafeLoader

from azext_load.data_plane.util import get_load_test_resource_endpoint, get_login_credentials


def create_or_update_test(
    cmd,
    test_name,
    load_test_resource=None,
    resource_group=None,
    load_test_config_file=None,
    test_description=None,
    test_plan=None,
    config_file=None,
    engine_instances=None,
    env=None,
    secrets=None,
    kevault_id=None,
):
    from azext_load.data_plane.client_factory import admin_data_plane_client

    client = admin_data_plane_client(cmd.cli_ctx)
    if load_test_config_file is not None:
        # exception handling for incorrect filepath or name
        file = open(load_test_config_file)
        data = yaml.load(file, SafeLoader)
        return client.create_or_update_test(test_name, data)
    else:
        return client.create_or_update_test(
            test_name,
            {
                "displayName": test_name,
                "testPlan": test_plan,
                "description": test_description,
                "engineInstances": engine_instances,
                "testId": test_name,
                "env": env,
            },
        )


def list_tests(
    cmd,
    load_test_resource=None,
    resource_group=None,
):
    from azext_load.data_plane.client_factory import admin_data_plane_client

    credential, subscription_id, _ = get_login_credentials(cmd.cli_ctx)
    endpoint = get_load_test_resource_endpoint(credential, load_test_resource, resource_group=resource_group, subscription_id=subscription_id)
    client = admin_data_plane_client(cmd.cli_ctx, subscription=subscription_id, endpoint=endpoint)

    return client.list_tests()
