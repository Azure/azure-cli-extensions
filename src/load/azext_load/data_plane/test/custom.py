from knack.log import get_logger
import yaml, json, errno
from yaml.loader import SafeLoader

from azext_load.data_plane.util import (
    get_load_test_resource_endpoint,
    get_login_credentials,
    create_or_update_body
)

logger = get_logger(__name__)


def create_test(
    cmd,
    load_test_resource,
    display_name=None,
    resource_group_name=None,
    load_test_config_file=None,
    test_description=None,
    test_plan=None,
    config_file=None,
    engine_instances=None,
    env=None,
    secrets=None,
    certificate=None,
    key_vault_reference_identity=None,
    subnet_id=None,
):
    from azext_load.data_plane.client_factory import admin_data_plane_client
    from azext_load.data_plane.util import generate_test_id

    credential, subscription_id, _ = get_login_credentials(cmd.cli_ctx)
    endpoint = get_load_test_resource_endpoint(
        credential,
        load_test_resource,
        resource_group=resource_group_name,
        subscription_id=subscription_id,
    )
    client = admin_data_plane_client(
        cmd.cli_ctx,
        subscription=subscription_id,
        endpoint=endpoint,
        credential=credential,
    )
    body = {}
    body = create_or_update_body(body= body, load_test_config_file=load_test_config_file, display_name=display_name, test_description=test_description, config_file=config_file, engine_instances=engine_instances, env=env, secrets=secrets, certificate=certificate, key_vault_reference_identity=key_vault_reference_identity, subnet_id=subnet_id )
    test_id = generate_test_id(body["displayName"])
    response_obj = client.create_or_update_test(test_id=test_id, body=body)
    if test_plan is not None:
        client.begin_upload_test_file(
            test_id,
            file_name=test_id + "TestPlan.jmx",
            body=open(test_plan, "r"),
        )
    return response_obj


def update_test(
    cmd,
    test_id,
    load_test_resource,
    display_name=None,
    resource_group_name=None,
    load_test_config_file=None,
    test_description=None,
    test_plan=None,
    config_file=None,
    engine_instances=None,
    env=None,
    secrets=None,
    certificate=None,
    key_vault_reference_identity=None,
    subnet_id=None,
):
    from azext_load.data_plane.client_factory import admin_data_plane_client
    from azext_load.data_plane.util import generate_test_id

    credential, subscription_id, _ = get_login_credentials(cmd.cli_ctx)
    endpoint = get_load_test_resource_endpoint(
        credential,
        load_test_resource,
        resource_group=resource_group_name,
        subscription_id=subscription_id,
    )
    client = admin_data_plane_client(
        cmd.cli_ctx,
        subscription=subscription_id,
        endpoint=endpoint,
        credential=credential,
    )
    body = client.get_test(test_id)
    body = create_or_update_body(body= body, load_test_config_file=load_test_config_file, display_name=display_name, test_description=test_description, config_file=config_file, engine_instances=engine_instances, env=env, secrets=secrets, certificate=certificate, key_vault_reference_identity=key_vault_reference_identity, subnet_id=subnet_id )
    response_obj = client.create_or_update_test(test_id=test_id, body=body)
    logger.warning("body: %s", body)
    response_obj = client.create_or_update_test(
        test_id=generate_test_id(body["displayName"]), body=body
    )
    if test_plan is not None:
        client.begin_upload_test_file(
            response_obj["testId"],
            file_name=response_obj["displayName"] + "TestPlan.jmx",
            body=open(test_plan, "r"),
        )
    return response_obj


def list_tests(
    cmd,
    load_test_resource,
    resource_group_name=None,
):
    from azext_load.data_plane.client_factory import admin_data_plane_client

    credential, subscription_id, _ = get_login_credentials(cmd.cli_ctx)
    endpoint = get_load_test_resource_endpoint(
        credential,
        load_test_resource,
        resource_group=resource_group_name,
        subscription_id=subscription_id,
    )
    client = admin_data_plane_client(
        cmd.cli_ctx,
        subscription=subscription_id,
        endpoint=endpoint,
        credential=credential,
    )

    return client.list_tests()


def get_test(
    cmd,
    load_test_resource,
    test_id,
    resource_group_name=None,
):
    from azext_load.data_plane.client_factory import admin_data_plane_client

    credential, subscription_id, _ = get_login_credentials(cmd.cli_ctx)
    endpoint = get_load_test_resource_endpoint(
        credential,
        load_test_resource,
        resource_group=resource_group_name,
        subscription_id=subscription_id,
    )
    client = admin_data_plane_client(
        cmd.cli_ctx,
        subscription=subscription_id,
        endpoint=endpoint,
        credential=credential,
    )
    client.create_or_update_app_components
    return client.get_test(test_id)


def download_test_files(
    cmd,
    load_test_resource,
    test_id,
    path,
    resource_group_name=None,
):
    from azext_load.data_plane.client_factory import admin_data_plane_client
    import requests
    import os

    credential, subscription_id, _ = get_login_credentials(cmd.cli_ctx)
    endpoint = get_load_test_resource_endpoint(
        credential,
        load_test_resource,
        resource_group=resource_group_name,
        subscription_id=subscription_id,
    )
    client = admin_data_plane_client(
        cmd.cli_ctx,
        subscription=subscription_id,
        endpoint=endpoint,
        credential=credential,
    )
    list_of_file_details = client.list_test_files(test_id)
    if list_of_file_details:
        if not os.path.exists(path):
            os.mkdir(path)
        for file_detail in list_of_file_details:
            with requests.get(file_detail["url"]) as current_file:
                with open(path + "\\" + file_detail["fileName"], "w+") as f:
                    f.write(current_file.text)
    return (
        "Files belonging to test "
        + test_id
        + " are downloaded in "
        + path
        + " location."
    )

def delete_test(
    cmd,
    load_test_resource,
    test_id,
    resource_group_name=None,
):
    from azext_load.data_plane.client_factory import admin_data_plane_client

    credential, subscription_id, _ = get_login_credentials(cmd.cli_ctx)
    endpoint = get_load_test_resource_endpoint(
        credential,
        load_test_resource,
        resource_group=resource_group_name,
        subscription_id=subscription_id,
    )
    client = admin_data_plane_client(
        cmd.cli_ctx,
        subscription=subscription_id,
        endpoint=endpoint,
        credential=credential,
    )
    return client.delete_test(test_id)