# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-locals

import os

from azext_load.data_plane.utils.utils import (
    convert_yaml_to_test,
    create_or_update_test_with_config,
    create_or_update_test_without_config,
    download_file,
    get_admin_data_plane_client,
    load_yaml,
    upload_file_to_test,
    upload_files_helper,
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
    test_plan=None,
    resource_group_name=None,
    load_test_config_file=None,
    test_description=None,
    engine_instances=None,
    env=None,
    secrets=None,
    certificate=None,
    key_vault_reference_identity=None,
    subnet_id=None,
    split_csv=None,
    custom_no_wait=False,
):
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    logger.info("Create test has started for test ID : %s", test_id)
    body = None
    try:
        body = client.get_test(test_id)
    except ResourceNotFoundError:
        pass
    if body is not None:
        msg = f"Test with given test ID : {test_id} already exist."
        logger.debug(msg)
        raise InvalidArgumentValueError(msg)
    body = {}
    yaml, yaml_test_body = None, None
    if split_csv is None:
        split_csv = False
    if load_test_config_file is None:
        body = create_or_update_test_without_config(
            test_id,
            body,
            display_name=display_name,
            test_description=test_description,
            engine_instances=engine_instances,
            env=env,
            secrets=secrets,
            certificate=certificate,
            key_vault_reference_identity=key_vault_reference_identity,
            subnet_id=subnet_id,
            split_csv=split_csv,
        )
    else:
        yaml = load_yaml(load_test_config_file)
        yaml_test_body = convert_yaml_to_test(yaml)
        body = create_or_update_test_with_config(
            test_id,
            body,
            yaml_test_body,
            display_name=display_name,
            test_description=test_description,
            engine_instances=engine_instances,
            env=env,
            secrets=secrets,
            certificate=certificate,
            key_vault_reference_identity=key_vault_reference_identity,
            subnet_id=subnet_id,
            split_csv=split_csv,
        )
    logger.debug("Creating test with test ID: %s and body : %s", test_id, body)
    response = client.create_or_update_test(test_id=test_id, body=body)
    logger.debug(
        "Created test with test ID: %s and response obj is %s", test_id, response
    )
    logger.info("Uploading files to test %s", test_id)
    upload_files_helper(
        client, test_id, yaml, test_plan, load_test_config_file, not custom_no_wait
    )
    response = client.get_test(test_id)
    logger.info("Upload files to test %s has completed", test_id)
    logger.info("Test %s has been created successfully", test_id)
    return response


def update_test(
    cmd,
    test_id,
    load_test_resource,
    display_name=None,
    test_plan=None,
    resource_group_name=None,
    load_test_config_file=None,
    test_description=None,
    engine_instances=None,
    env=None,
    secrets=None,
    certificate=None,
    key_vault_reference_identity=None,
    subnet_id=None,
    split_csv=None,
    custom_no_wait=False,
):
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    logger.info("Update test has started for test ID : %s", test_id)
    try:
        body = client.get_test(test_id)
    except ResourceNotFoundError as e:
        msg = f"Test with given test ID : {test_id} does not exist."
        logger.debug(msg)
        raise InvalidArgumentValueError(msg) from e
    logger.debug("Retrieved test with test ID: %s and body : %s", test_id, body)

    yaml, yaml_test_body = None, None
    if load_test_config_file is not None:
        yaml = load_yaml(load_test_config_file)
        yaml_test_body = convert_yaml_to_test(yaml)
        body = create_or_update_test_with_config(
            test_id,
            body,
            yaml_test_body,
            display_name=display_name,
            test_description=test_description,
            engine_instances=engine_instances,
            env=env,
            secrets=secrets,
            certificate=certificate,
            key_vault_reference_identity=key_vault_reference_identity,
            subnet_id=subnet_id,
            split_csv=split_csv,
        )
    else:
        body = create_or_update_test_without_config(
            test_id,
            body,
            display_name=display_name,
            test_description=test_description,
            engine_instances=engine_instances,
            env=env,
            secrets=secrets,
            certificate=certificate,
            key_vault_reference_identity=key_vault_reference_identity,
            subnet_id=subnet_id,
            split_csv=split_csv,
        )
    logger.info("Updating test with test ID: %s", test_id)
    response = client.create_or_update_test(test_id=test_id, body=body)
    logger.debug(
        "Updated test with test ID: %s and response obj is %s", test_id, response
    )
    logger.info("Uploading files to test %s", test_id)
    upload_files_helper(
        client, test_id, yaml, test_plan, load_test_config_file, not custom_no_wait
    )
    response = client.get_test(test_id)
    logger.info("Upload files to test %s has completed", test_id)
    logger.info("Test %s has been updated successfully", test_id)
    return response


def list_tests(
    cmd,
    load_test_resource,
    resource_group_name=None,
):
    logger.info("Listing tests for load test resource: %s", load_test_resource)
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    response = client.list_tests()
    logger.debug("Retrieved tests: %s", response)
    return response


def get_test(
    cmd,
    load_test_resource,
    test_id,
    resource_group_name=None,
):
    logger.debug("Retrieving test with test ID: %s", test_id)
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    response = client.get_test(test_id)
    logger.debug("Retrieved test: %s", response)
    return response


def download_test_files(
    cmd,
    load_test_resource,
    test_id,
    path,
    resource_group_name=None,
    force=False,  # pylint: disable=unused-argument
):
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    logger.info("Downloading test files with test ID: %s", test_id)
    list_of_file_details = client.list_test_files(test_id)
    if list_of_file_details:
        for file_detail in list_of_file_details:
            file_path = os.path.join(path, file_detail["fileName"])
            download_file(file_detail["url"], file_path)
            logger.debug(
                "Downloaded '%s' file for test with test ID: %s at %s",
                file_detail["url"],
                test_id,
                file_path,
            )
        logger.warning(
            "Downloaded files for test ID: %s at  directory %s", test_id, path
        )
    else:
        logger.warning("No files found for test with test ID: %s", test_id)


def delete_test(
    cmd,
    load_test_resource,
    test_id,
    resource_group_name=None,
):
    logger.info("Deleting test with test ID: %s", test_id)
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    client.delete_test(test_id)
    logger.info("Deleted test with test ID: %s", test_id)


def add_test_app_component(
    cmd,
    load_test_resource,
    test_id,
    app_component_id,
    app_component_name,
    app_component_type,
    app_component_kind=None,
    resource_group_name=None,
):
    logger.info("Add test app component started for test: %s", test_id)
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
    response = client.create_or_update_app_components(test_id=test_id, body=body)
    logger.info("Add test app component completed for test: %s", test_id)
    logger.debug("Add test app component response: %s", response)
    return response


def list_test_app_component(
    cmd,
    load_test_resource,
    test_id,
    resource_group_name=None,
):
    logger.info("Listing app components")
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    response = client.get_app_components(test_id=test_id)
    logger.debug("Retrieved app components: %s", response)
    logger.info("Listing app components completed")
    return response


def remove_test_app_component(
    cmd,
    load_test_resource,
    test_id,
    app_component_id,
    resource_group_name=None,
):
    logger.info("Removing app components")
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    body = {"testId": test_id, "components": {app_component_id: None}}
    logger.debug("Removing following app component from the test: %s", body)
    response = client.create_or_update_app_components(test_id=test_id, body=body)
    logger.debug("Removed app component: %s", response)
    logger.info("Removing app components completed")
    return response


def add_test_server_metric(
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
    logger.info("Add test server metric started")
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
    response = client.create_or_update_server_metrics_config(test_id=test_id, body=body)
    logger.debug("Add test server metric response: %s", response)
    logger.info("Add test server metric completed")
    return response


def list_test_server_metric(
    cmd,
    load_test_resource,
    test_id,
    resource_group_name=None,
):
    logger.info("Listing server metrics")
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    response = client.get_server_metrics_config(test_id=test_id)
    logger.debug("Retrieved server metrics: %s", response)
    logger.info("Listing server metrics completed")
    return response


def remove_test_server_metric(
    cmd,
    load_test_resource,
    test_id,
    metric_id,
    resource_group_name=None,
):
    logger.info("Removing server metrics")
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    body = {"testId": test_id, "metrics": {metric_id: None}}
    logger.debug("Removing server metrics from the test: %s", body)
    response = client.create_or_update_server_metrics_config(test_id=test_id, body=body)
    logger.debug("Removed server metrics: %s", response)
    logger.info("Removing server metrics completed")
    return response


def upload_test_file(
    cmd,
    load_test_resource,
    test_id,
    path,
    file_type=None,
    resource_group_name=None,
    no_wait=False,
):
    logger.info("Upload test file started")
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    logger.info("Uploading file for the test")
    response = upload_file_to_test(
        client, test_id, path, file_type=file_type, wait=not no_wait
    )
    logger.debug("Upload test file response: %s", response)
    logger.info("Upload test file completed")
    return response


def list_test_file(
    cmd,
    load_test_resource,
    test_id,
    resource_group_name=None,
):
    logger.info("Listing files for the test")
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    response = client.list_test_files(test_id)
    logger.debug("Retrieved files: %s", response)
    logger.info("Listing files for the test completed")
    return response


def download_test_file(
    cmd,
    load_test_resource,
    test_id,
    file_name,
    path,
    resource_group_name=None,
    force=False,  # pylint: disable=unused-argument
):
    logger.info("Downloading file for the test")
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    file = client.get_test_file(test_id, file_name)
    logger.debug("File details: %s", file)
    file_path = os.path.join(path, file_name)
    download_file(file.get("url"), file_path)
    logger.debug(
        "Downloaded '%s' file for test with test ID: %s at %s",
        file.get("url"),
        test_id,
        file_path,
    )
    logger.warning("Downloaded files for test ID: %s at directory %s", test_id, path)


def delete_test_file(
    cmd,
    load_test_resource,
    test_id,
    file_name,
    resource_group_name=None,
):
    logger.info(
        "Deleting file with file name : %s for the test : %s", file_name, test_id
    )
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    response = client.delete_test_file(test_id, file_name)
    logger.debug("Deleted file: %s", response)
    logger.info("Deleting file completed")
    return response
