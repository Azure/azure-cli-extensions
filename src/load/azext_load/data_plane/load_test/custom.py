import os

from azext_load.data_plane.utils.utils import (
    create_or_update_body,
    download_file,
    get_admin_data_plane_client,
    upload_configuration_files,
    upload_test_plan,
)
from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.core.exceptions import ResourceNotFoundError
from knack.log import get_logger

logger = get_logger(__name__)


def create_test(
    cmd,
    load_test_resource,
    test_id,
    display_name=None,
    resource_group_name=None,
    load_test_config_file=None,
    test_description=None,
    test_plan=None,
    configuration_files=None,
    engine_instances=None,
    env=None,
    secrets=None,
    certificate=None,
    key_vault_reference_identity=None,
    subnet_id=None,
    wait=False,
):
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    body = {}
    body = create_or_update_body(
        test_id,
        body,
        load_test_config_file=load_test_config_file,
        display_name=display_name,
        test_description=test_description,
        engine_instances=engine_instances,
        env=env,
        secrets=secrets,
        certificate=certificate,
        key_vault_reference_identity=key_vault_reference_identity,
        subnet_id=subnet_id,
    )
    list_of_tests = client.list_tests()
    for test in list_of_tests:
        if test_id == test.get("testId"):
            logger.debug("Test with given test ID : %s already exists.", test_id)
            raise InvalidArgumentValueError(
                f"Test with given test ID : {test_id} already exists."
            )
    logger.info("Creating test with test ID: %s and body : %s", test_id, body)
    response_obj = client.create_or_update_test(test_id=test_id, body=body)
    logger.debug(
        "Response object for creating test with test ID: %s is %s",
        test_id,
        response_obj,
    )
    logger.info(
        "Created test with test ID: %s and response obj is %s", test_id, response_obj
    )

    if test_plan is not None:
        upload_test_plan(client, test_id, test_plan, wait)

    if configuration_files is not None:
        upload_configuration_files(client, test_id, configuration_files)

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
    configuration_files=None,
    engine_instances=None,
    env=None,
    secrets=None,
    certificate=None,
    key_vault_reference_identity=None,
    subnet_id=None,
    wait=False,
):
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    try:
        body = client.get_test(test_id)
    except ResourceNotFoundError:
        msg = f"Test with given test ID : {test_id} does not exist."
        logger.debug(msg)
        raise InvalidArgumentValueError(msg)
    logger.debug("Retrieved test with test ID: %s and body : %s", test_id, body)
    body = create_or_update_body(
        test_id,
        body,
        load_test_config_file=load_test_config_file,
        display_name=display_name,
        test_description=test_description,
        engine_instances=engine_instances,
        env=env,
        secrets=secrets,
        certificate=certificate,
        key_vault_reference_identity=key_vault_reference_identity,
        subnet_id=subnet_id,
    )
    logger.info("Updating test with test ID: %s and body : %s", test_id, body)
    response_obj = client.create_or_update_test(test_id=test_id, body=body)
    logger.debug(
        "Response object for updating test with test ID: %s is %s",
        test_id,
        response_obj,
    )
    logger.info(
        "Updated test with test ID: %s and response obj is %s", test_id, response_obj
    )
    if test_plan is not None:
        upload_test_plan(client, test_id, test_plan, wait)

    if configuration_files is not None:
        upload_configuration_files(client, test_id, configuration_files)
    return response_obj


def list_tests(
    cmd,
    load_test_resource,
    resource_group_name=None,
):
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    logger.info("Listing tests")
    return client.list_tests()


def get_test(
    cmd,
    load_test_resource,
    test_id,
    resource_group_name=None,
):
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    logger.debug("Retrieving test with test ID: %s", test_id)
    return client.get_test(test_id)


def download_test_files(
    cmd, load_test_resource, test_id, path, resource_group_name=None, force=False
):
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    logger.debug("Downloading test files with test ID: %s", test_id)
    list_of_file_details = client.list_test_files(test_id)
    if list_of_file_details:
        for file_detail in list_of_file_details:
            file_path = os.path.join(path, file_detail["fileName"])
            download_file(file_detail["url"], file_path)
            logger.info(
                "Downloaded '%s' file for test with test ID: %s at %s",
                file_detail["url"],
                test_id,
                file_path,
            )
        logger.warning(
            "Downloaded files for test with test ID: %s at %s", test_id, path
        )
    else:
        logger.warning("No files found for test with test ID: %s", test_id)


def delete_test(
    cmd,
    load_test_resource,
    test_id,
    resource_group_name=None,
):
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    logger.debug("Deleting test with test ID: %s", test_id)
    return client.delete_test(test_id)


def add_test_app_components(
    cmd,
    load_test_resource,
    test_id,
    app_component_id,
    app_component_name,
    app_component_type,
    app_component_kind=None,
    resource_group_name=None,
):
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    body = {
        "testId": test_id,
        "components": {
            app_component_id: {
                "resourceId": app_component_id,
                "resourceName": app_component_name,
                "resourceType": app_component_type,
            }
        },
    }
    if app_component_kind:
        body["components"][app_component_id]["kind"] = app_component_kind
    logger.debug("Adding app component to the test: %s", body)
    return client.create_or_update_app_components(test_id=test_id, body=body)


def list_test_app_components(
    cmd,
    load_test_resource,
    test_id,
    resource_group_name=None,
):
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    logger.debug("Listing app components")
    return client.get_app_components(test_id=test_id)


def remove_test_app_components(
    cmd,
    load_test_resource,
    test_id,
    app_component_id,
    resource_group_name=None,
):
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    body = {"testId": test_id, "components": {app_component_id: None}}
    logger.debug("Removing app component from the test: %s", body)
    return client.create_or_update_app_components(test_id=test_id, body=body)


def add_test_server_metrics(
    cmd,
    load_test_resource,
    test_id,
    metric_id,
    metric_name,
    metric_namespace,
    aggregation,
    app_component_id,
    app_component_type,
    resource_group_name=None,
):
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    body = {
        "testId": test_id,
        "metrics": {
            metric_id: {
                "name": metric_name,
                "metricNamespace": metric_namespace,
                "aggregation": aggregation,
                "resourceId": app_component_id,
                "resourceType": app_component_type,
            }
        },
    }
    logger.debug("Adding server metrics to the test: %s", body)
    return client.create_or_update_server_metrics_config(test_id=test_id, body=body)


def list_test_server_metrics(
    cmd,
    load_test_resource,
    test_id,
    resource_group_name=None,
):
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    logger.debug("Listing server metrics")
    return client.get_server_metrics_config(test_id=test_id)


def remove_test_server_metrics(
    cmd,
    load_test_resource,
    test_id,
    metric_id,
    resource_group_name=None,
):
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    body = {"testId": test_id, "metrics": {metric_id: None}}
    logger.debug("Removing server metrics from the test: %s", body)
    return client.create_or_update_server_metrics_config(test_id=test_id, body=body)


def upload_test_file(
    cmd,
    load_test_resource,
    test_id,
    path,
    file_type=None,
    resource_group_name=None,
    wait=False,
):
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    logger.info("Uploading file for the test")
    with open(path, "rb") as file:
        upload_poller = client.begin_upload_test_file(
            test_id,
            file_name=os.path.basename(file.name),
            file_type=file_type,
            body=file,
        )
        response = (
            upload_poller.result()
            if wait
            else upload_poller.polling_method().resource()
        )
        logger.debug(
            "Upload result for file with --wait%s passed: %s",
            "" if wait else " not",
            response,
        )
        return response


def list_test_file(
    cmd,
    load_test_resource,
    test_id,
    resource_group_name=None,
):
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    logger.debug("Listing files for the test")
    return client.list_test_files(test_id)


def download_test_file(
    cmd,
    load_test_resource,
    test_id,
    file_name,
    path,
    resource_group_name=None,
    force=False,
):
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    logger.debug("Downloading file for the test")
    file = client.get_test_file(test_id, file_name)
    logger.debug("File details: %s", file)

    file_path = os.path.join(path, file_name)
    download_file(file.get("url"), file_path)
    logger.info(
        "Downloaded '%s' file for test with test ID: %s at %s",
        file.get("url"),
        test_id,
        file_path,
    )
    logger.warning("Downloaded files for test with test ID: %s at %s", test_id, path)


def delete_test_file(
    cmd,
    load_test_resource,
    test_id,
    file_name,
    resource_group_name=None,
):
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    logger.debug("Deleting file for the test")
    return client.delete_test_file(test_id, file_name)
