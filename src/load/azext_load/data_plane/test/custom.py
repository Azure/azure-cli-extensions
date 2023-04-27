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

    credential, subscription_id, _ = get_login_credentials(cmd.cli_ctx)
    endpoint = get_load_test_resource_endpoint(credential, load_test_resource, resource_group=resource_group, subscription_id=subscription_id)
    client = admin_data_plane_client(cmd.cli_ctx, subscription=subscription_id, endpoint=endpoint, credential=credential)
    if load_test_config_file is not None:
        # exception handling for incorrect filepath or name
        file = open(load_test_config_file)
        data = yaml.load(file, SafeLoader)
        response_obj = client.create_or_update_test(test_name, data) 
    else:
        response_obj = client.create_or_update_test(
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
    if test_plan is not None:
        client.begin_upload_test_file(test_name, file_name=test_name+"TestPlan.jmx", body = open(test_plan, "r"))
    return response_obj


def list_tests(
    cmd,
    load_test_resource,
    resource_group=None,
):
    from azext_load.data_plane.client_factory import admin_data_plane_client

    credential, subscription_id, _ = get_login_credentials(cmd.cli_ctx)
    endpoint = get_load_test_resource_endpoint(credential, load_test_resource, resource_group=resource_group, subscription_id=subscription_id)
    client = admin_data_plane_client(cmd.cli_ctx, subscription=subscription_id, endpoint=endpoint, credential=credential)

    return client.list_tests()

def get_test(
    cmd,
    load_test_resource,
    test_id,
    resource_group=None,
):
    from azext_load.data_plane.client_factory import admin_data_plane_client

    credential, subscription_id, _ = get_login_credentials(cmd.cli_ctx)
    endpoint = get_load_test_resource_endpoint(credential, load_test_resource, resource_group=resource_group, subscription_id=subscription_id)
    client = admin_data_plane_client(cmd.cli_ctx, subscription=subscription_id, endpoint=endpoint, credential=credential)
    return client.get_test(test_id)


def download_test_files(
    cmd,
    load_test_resource,
    test_id,
    path,
    resource_group=None,
):
    from azext_load.data_plane.client_factory import admin_data_plane_client
    import requests, os
    credential, subscription_id, _ = get_login_credentials(cmd.cli_ctx)
    endpoint = get_load_test_resource_endpoint(credential, load_test_resource, resource_group=resource_group, subscription_id=subscription_id)
    client = admin_data_plane_client(cmd.cli_ctx, subscription=subscription_id, endpoint=endpoint, credential=credential)
    list_of_file_details = client.list_test_files(test_id)
    if list_of_file_details:
        if not os.path.exists(path):
            os.mkdir(path)
        for file_detail in list_of_file_details:
            with requests.get(file_detail["url"]) as current_file:
                with open(path+"\\"+file_detail["fileName"], 'w+') as f:
                    f.write(current_file.text) 
    return "Files belonging to test "+test_id+" are downloaded in "+path+" location."
