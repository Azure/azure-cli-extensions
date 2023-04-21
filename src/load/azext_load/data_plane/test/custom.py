import yaml
from yaml.loader import SafeLoader


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
