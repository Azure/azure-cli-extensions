# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azext_load.data_plane.utils.utils import (
    convert_yaml_to_test,
    create_or_update_body,
    download_file,
    get_admin_data_plane_client,
    load_yaml,
    upload_file_to_test,
)
from azext_load.data_plane.utils.validators import AllowedFileTypes
from azure.cli.core.azclierror import FileOperationError, InvalidArgumentValueError
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
    wait=False,
):
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    body = {}

    yaml, yaml_test_body = None, None
    if load_test_config_file is not None:
        yaml = load_yaml(load_test_config_file)
        yaml_test_body = convert_yaml_to_test(yaml)

    body = create_or_update_body(
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
    tests = client.list_tests()
    for test in tests:
        if test_id == test.get("testId"):
            logger.debug("Test with given test ID : %s already exists.", test_id)
            raise InvalidArgumentValueError(
                f"Test with given test ID : {test_id} already exists."
            )
    logger.info("Creating test with test ID: %s and body : %s", test_id, body)
    response = client.create_or_update_test(test_id=test_id, body=body)
    logger.info(
        "Created test with test ID: %s and response obj is %s", test_id, response
    )

    files = client.list_test_files(test_id)
    if yaml and yaml.get("userProperty") is not None:
        file_name = os.path.basename(yaml.get("userProperty"))
        file_response = upload_file_to_test(
            client,
            test_id,
            yaml["userProperty"],
            file_type=AllowedFileTypes.USER_PROPERTIES,
            wait=wait,
        )
        logger.info(
            "Uploaded file '%s' of type %s to test %s",
            file_name,
            AllowedFileTypes.USER_PROPERTIES,
            test_id,
        )

    if yaml and yaml.get("configurationFiles") is not None:
        for config_file in yaml["configurationFiles"]:
            file_name = os.path.basename(config_file)
            upload_file_to_test(
                client,
                test_id,
                config_file,
                file_type=AllowedFileTypes.ADDITIONAL_ARTIFACTS,
                wait=wait,
            )
            logger.info(
                "Uploaded file '%s' of type %s to test %s",
                file_name,
                AllowedFileTypes.ADDITIONAL_ARTIFACTS,
                test_id,
            )

    if (yaml and yaml.get("testPlan") is not None) or test_plan is not None:
        test_plan = test_plan if test_plan is not None else yaml["testPlan"]
        file_name = os.path.basename(test_plan)
        for file in files:
            if AllowedFileTypes.JMX_FILE.value == file["fileType"]:
                client.delete_test_file(test_id, file["fileName"])
                logger.info(
                    "File with name '%s' already exists in test %s. Deleting it!",
                    file_name,
                    test_id,
                )
                break
        file_response = upload_file_to_test(
            client, test_id, test_plan, file_type=AllowedFileTypes.JMX_FILE, wait=wait
        )
        if wait and file_response.get("validationStatus") != "VALIDATION_SUCCESS":
            raise FileOperationError(
                f"Test plan file {test_plan} is not valid. Please check the file and try again."
            )

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
    
    yaml, yaml_test_body = None, None
    if load_test_config_file is not None:
        yaml = load_yaml(load_test_config_file)
        yaml_test_body = convert_yaml_to_test(yaml)

    body = create_or_update_body(
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
    logger.info("Updating test with test ID: %s and body : %s", test_id, body)
    response = client.create_or_update_test(test_id=test_id, body=body)
    logger.info(
        "Updated test with test ID: %s and response obj is %s", test_id, response
    )

    files = client.list_test_files(test_id)
    if yaml and yaml.get("userProperty") is not None:
        file_name = os.path.basename(yaml["userProperty"])
        for file in files:
            if AllowedFileTypes.USER_PROPERTIES.value == file["fileType"]:
                client.delete_test_file(test_id, file["fileName"])
                logger.info(
                    "File of type '%s' already exists in test %s. Deleting it!",
                    AllowedFileTypes.USER_PROPERTIES,
                    test_id,
                )
                break
        file_response = upload_file_to_test(
            client,
            test_id,
            yaml["userProperty"],
            file_type=AllowedFileTypes.USER_PROPERTIES,
            wait=wait,
        )
        logger.info(
            "Uploaded file '%s' of type %s to test %s",
            file_name,
            AllowedFileTypes.USER_PROPERTIES,
            test_id,
        )

    if yaml and yaml.get("configurationFiles") is not None:
        for config_file in yaml["configurationFiles"]:
            file_name = os.path.basename(config_file)
            if file_name in [file["fileName"] for file in files]:
                client.delete_test_file(test_id, file_name)
                logger.info(
                    "File with name '%s' already exists in test %s. Deleting it!",
                    file_name,
                    test_id,
                )
            upload_file_to_test(
                client,
                test_id,
                config_file,
                file_type=AllowedFileTypes.ADDITIONAL_ARTIFACTS,
                wait=wait,
            )
            logger.info(
                "Uploaded file '%s' of type %s to test %s",
                file_name,
                AllowedFileTypes.ADDITIONAL_ARTIFACTS,
                test_id,
            )

    if yaml and yaml.get("testPlan") is not None or test_plan is not None:
        test_plan = test_plan if test_plan is not None else yaml["testPlan"]
        file_name = os.path.basename(test_plan)
        for file in files:
            if AllowedFileTypes.JMX_FILE.value == file["fileType"]:
                client.delete_test_file(test_id, file["fileName"])
                logger.info(
                    "File with name '%s' already exists in test %s. Deleting it!",
                    file_name,
                    test_id,
                )
                break
        file_response = upload_file_to_test(
            client, test_id, test_plan, file_type=AllowedFileTypes.JMX_FILE, wait=wait
        )
        if wait and file_response.get("validationStatus") != "VALIDATION_SUCCESS":
            raise FileOperationError(
                f"Test plan file {test_plan} is not valid. Please check the file and try again."
            )

    return response


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


def list_test_app_component(
    cmd,
    load_test_resource,
    test_id,
    resource_group_name=None,
):
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    logger.debug("Listing app components")
    return client.get_app_components(test_id=test_id)


def remove_test_app_component(
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


def list_test_server_metric(
    cmd,
    load_test_resource,
    test_id,
    resource_group_name=None,
):
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    logger.debug("Listing server metrics")
    return client.get_server_metrics_config(test_id=test_id)


def remove_test_server_metric(
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
    return upload_file_to_test(client, test_id, path, file_type=file_type, wait=wait)


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
