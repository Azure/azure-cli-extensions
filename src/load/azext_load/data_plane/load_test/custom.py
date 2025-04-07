# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-locals

import os

from azext_load.data_plane.utils.constants import LoadTestConfigKeys
from azext_load.data_plane.utils.utils import (
    convert_yaml_to_test,
    create_autostop_criteria_from_args,
    create_or_update_test_with_config,
    create_or_update_test_without_config,
    download_file,
    generate_trends_row,
    get_admin_data_plane_client,
    get_testrun_data_plane_client,
    infer_test_type_from_test_plan,
    load_yaml,
    upload_file_to_test,
    upload_files_helper,
    merge_existing_app_components,
    merge_existing_server_metrics,
    parse_app_comps_and_server_metrics,
    is_not_empty_dictionary,
)
from azext_load.data_plane.utils.models import (
    AllowedTestTypes,
    AllowedTrendsResponseTimeAggregations,
)
from azure.cli.core.azclierror import InvalidArgumentValueError, FileOperationError
from azure.core.exceptions import ResourceNotFoundError
from knack.log import get_logger

logger = get_logger(__name__)


def create_test(
    cmd,
    load_test_resource,
    test_id,
    display_name=None,
    test_plan=None,
    test_type=None,
    resource_group_name=None,
    load_test_config_file=None,
    test_description=None,
    engine_instances=None,
    env=None,
    secrets=None,
    certificate=None,
    key_vault_reference_identity=None,
    metrics_reference_identity=None,
    subnet_id=None,
    split_csv=None,
    disable_public_ip=None,
    custom_no_wait=False,
    autostop=None,
    autostop_error_rate=None,
    autostop_error_rate_time_window=None,
    regionwise_engines=None,
    engine_ref_id_type=None,
    engine_ref_ids=None,
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
    app_components, add_defaults_to_app_components, server_metrics = None, None, None
    autostop_criteria = create_autostop_criteria_from_args(
        autostop=autostop, error_rate=autostop_error_rate, time_window=autostop_error_rate_time_window)
    if load_test_config_file is None:
        test_type = test_type or infer_test_type_from_test_plan(test_plan)
        logger.debug("Inferred test type: %s", test_type)
        body = create_or_update_test_without_config(
            test_id,
            body,
            display_name=display_name,
            test_description=test_description,
            test_type=test_type,
            engine_instances=engine_instances,
            env=env,
            secrets=secrets,
            certificate=certificate,
            key_vault_reference_identity=key_vault_reference_identity,
            metrics_reference_identity=metrics_reference_identity,
            subnet_id=subnet_id,
            split_csv=split_csv,
            disable_public_ip=disable_public_ip,
            autostop_criteria=autostop_criteria,
            regionwise_engines=regionwise_engines,
            engine_ref_id_type=engine_ref_id_type,
            engine_ref_ids=engine_ref_ids,
        )
    else:
        yaml = load_yaml(load_test_config_file)
        yaml_test_body = convert_yaml_to_test(cmd, yaml)
        app_components, add_defaults_to_app_components, server_metrics = parse_app_comps_and_server_metrics(data=yaml)
        test_type = (
            test_type or
            yaml.get(LoadTestConfigKeys.TEST_TYPE) or
            infer_test_type_from_test_plan(test_plan) or
            infer_test_type_from_test_plan(yaml.get(LoadTestConfigKeys.TEST_PLAN))
        )
        logger.debug("Inferred test type: %s", test_type)
        body = create_or_update_test_with_config(
            test_id,
            body,
            yaml_test_body,
            display_name=display_name,
            test_type=test_type,
            test_description=test_description,
            engine_instances=engine_instances,
            env=env,
            secrets=secrets,
            certificate=certificate,
            key_vault_reference_identity=key_vault_reference_identity,
            metrics_reference_identity=metrics_reference_identity,
            subnet_id=subnet_id,
            split_csv=split_csv,
            disable_public_ip=disable_public_ip,
            autostop_criteria=autostop_criteria,
            regionwise_engines=regionwise_engines,
            engine_ref_id_type=engine_ref_id_type,
            engine_ref_ids=engine_ref_ids,
        )
    logger.debug("Creating test with test ID: %s and body : %s", test_id, body)
    response = client.create_or_update_test(test_id=test_id, body=body)
    logger.debug(
        "Created test with test ID: %s and response obj is %s", test_id, response
    )
    logger.info("Uploading files to test %s", test_id)
    evaluated_test_type = test_type or yaml_test_body.get("kind") if yaml_test_body else response.get("kind")
    upload_files_helper(
        client, test_id, yaml, test_plan, load_test_config_file, not custom_no_wait, evaluated_test_type
    )
    logger.info("Upload files to test %s has completed", test_id)
    if is_not_empty_dictionary(app_components):
        # only get and patch the app components if its present in the yaml.
        app_component_response = client.create_or_update_app_components(
            test_id=test_id, body={"testId": test_id, "components": app_components}
        )
        logger.warning(
            "Added app components for test ID: %s and response is %s", test_id, app_component_response
        )
    if is_not_empty_dictionary(server_metrics):
        # only get and patch the app components if its present in the yaml.
        server_metrics_existing = None
        try:
            server_metrics_existing = client.get_server_metrics_config(test_id)
        except ResourceNotFoundError:
            server_metrics_existing = {"metrics": {}}
        server_metrics_merged = merge_existing_server_metrics(
            add_defaults_to_app_components, server_metrics, server_metrics_existing.get("metrics", {})
        )
        server_metric_response = client.create_or_update_server_metrics_config(
            test_id=test_id, body={"testId": test_id, "metrics": server_metrics_merged}
        )
        logger.warning(
            "Added server metrics for test ID: %s and response is %s", test_id, server_metric_response
        )
    response = client.get_test(test_id)
    logger.info("Test %s has been created successfully", test_id)
    return response.as_dict()


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
    metrics_reference_identity=None,
    subnet_id=None,
    split_csv=None,
    disable_public_ip=None,
    custom_no_wait=False,
    autostop=None,
    autostop_error_rate=None,
    autostop_error_rate_time_window=None,
    regionwise_engines=None,
    engine_ref_id_type=None,
    engine_ref_ids=None,
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
    app_components, server_metrics, add_defaults_to_app_components = None, None, None
    autostop_criteria = create_autostop_criteria_from_args(
        autostop=autostop, error_rate=autostop_error_rate, time_window=autostop_error_rate_time_window)
    if load_test_config_file is not None:
        yaml = load_yaml(load_test_config_file)
        yaml_test_body = convert_yaml_to_test(cmd, yaml)
        app_components, add_defaults_to_app_components, server_metrics = parse_app_comps_and_server_metrics(data=yaml)
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
            metrics_reference_identity=metrics_reference_identity,
            subnet_id=subnet_id,
            split_csv=split_csv,
            disable_public_ip=disable_public_ip,
            autostop_criteria=autostop_criteria,
            regionwise_engines=regionwise_engines,
            engine_ref_id_type=engine_ref_id_type,
            engine_ref_ids=engine_ref_ids,
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
            metrics_reference_identity=metrics_reference_identity,
            subnet_id=subnet_id,
            split_csv=split_csv,
            disable_public_ip=disable_public_ip,
            autostop_criteria=autostop_criteria,
            regionwise_engines=regionwise_engines,
            engine_ref_id_type=engine_ref_id_type,
            engine_ref_ids=engine_ref_ids
        )
    logger.info("Updating test with test ID: %s", test_id)
    response = client.create_or_update_test(test_id=test_id, body=body)
    logger.debug(
        "Updated test with test ID: %s and response obj is %s", test_id, response
    )
    logger.info("Uploading files to test %s", test_id)
    upload_files_helper(
        client, test_id, yaml, test_plan, load_test_config_file, not custom_no_wait, body.get("kind")
    )

    if is_not_empty_dictionary(app_components):
        # only get and patch the app components if its present in the yaml.
        try:
            app_components_existing = client.get_app_components(test_id)
        except ResourceNotFoundError:
            app_components_existing = {"components": {}}
        app_components_merged = merge_existing_app_components(
            app_components, app_components_existing.get("components", {})
        )
        app_component_response = client.create_or_update_app_components(
            test_id=test_id, body={"testId": test_id, "components": app_components_merged}
        )
        logger.warning(
            "Added app components for test ID: %s and response is %s", test_id, app_component_response
        )
    if is_not_empty_dictionary(server_metrics):
        # only get and patch the app components if its present in the yaml.
        try:
            server_metrics_existing = client.get_server_metrics_config(test_id)
        except ResourceNotFoundError:
            server_metrics_existing = {"metrics": {}}
        server_metrics_merged = merge_existing_server_metrics(
            add_defaults_to_app_components, server_metrics_existing.get("metrics", {}), server_metrics
        )
        server_metric_response = client.create_or_update_server_metrics_config(
            test_id=test_id, body={"testId": test_id, "metrics": server_metrics_merged}
        )
        logger.warning(
            "Added server metrics for test ID: %s and response is %s", test_id, server_metric_response
        )
    response = client.get_test(test_id)
    logger.info("Upload files to test %s has completed", test_id)
    logger.info("Test %s has been updated successfully", test_id)
    return response.as_dict()


def list_tests(
    cmd,
    load_test_resource,
    resource_group_name=None,
):
    logger.info("Listing tests for load test resource: %s", load_test_resource)
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    response_list = client.list_tests()
    logger.debug("Retrieved tests: %s", response_list)
    return [response.as_dict() for response in response_list]


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
    return response.as_dict()


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


def convert_to_jmx(
    cmd,
    load_test_resource,
    test_id,
    resource_group_name=None,
):
    logger.info("Converting test with test ID: %s to JMX", test_id)
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    existing_test = client.get_test(test_id)
    if (
        existing_test is not None
        and existing_test.get("kind") != AllowedTestTypes.URL.value
    ):
        raise InvalidArgumentValueError(
            f"Test with test ID: {test_id} is not of type URL. "
            "Only URL type tests can be converted to JMX."
        )
    body = create_or_update_test_without_config(
        test_id=test_id,
        body=existing_test,
        test_type=AllowedTestTypes.JMX.value,
    )
    response = client.create_or_update_test(test_id=test_id, body=body)
    logger.debug("Converted test with test ID: %s to JMX", test_id)
    return response.as_dict()


def set_baseline(
    cmd,
    load_test_resource,
    test_id,
    test_run_id,
    resource_group_name=None,
):
    logger.info("Setting baseline for test with test ID: %s", test_id)
    test_client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    test_run_client = get_testrun_data_plane_client(cmd, load_test_resource, resource_group_name)
    existing_test = test_client.get_test(test_id)
    existing_test_run = test_run_client.get_test_run(test_run_id)
    if existing_test_run.get("testId") != test_id:
        raise InvalidArgumentValueError(
            f"Test run with ID: {test_run_id} is not associated with test ID: {test_id}"
        )
    if existing_test_run.get("status") not in ["CANCELLED", "DONE"]:
        raise InvalidArgumentValueError(
            f"Test run with ID: {test_run_id} does not have a valid "
            f"test run status {existing_test_run.get('status')}. "
            "Valid test run status are: CANCELLED, DONE"
        )
    if existing_test_run.get("testRunStatistics", {}).get("Total") is None:
        raise InvalidArgumentValueError(
            f"Sampler statistics are not yet available for test run ID {test_run_id}. "
            "Please try again later."
        )
    body = create_or_update_test_without_config(
        test_id=test_id,
        body=existing_test,
        baseline_test_run_id=test_run_id,
    )
    response = test_client.create_or_update_test(test_id=test_id, body=body)
    logger.debug("Set test run %s as baseline for test: %s", test_run_id, test_id)
    return response.as_dict()


def compare_to_baseline(
    cmd,
    load_test_resource,
    test_id,
    resource_group_name=None,
    response_time_aggregate=AllowedTrendsResponseTimeAggregations.MEAN.value,
):
    logger.info("Showing test trends for test with test ID: %s", test_id)
    test_client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    test_run_client = get_testrun_data_plane_client(cmd, load_test_resource, resource_group_name)
    test = test_client.get_test(test_id)
    if test.get("baselineTestRunId") is None:
        raise InvalidArgumentValueError(
            f"Test with ID: {test_id} does not have a baseline test run associated with it."
        )
    baseline_test_run_id = test.get("baselineTestRunId")
    baseline_test_run = test_run_client.get_test_run(baseline_test_run_id)
    all_test_runs = test_run_client.list_test_runs(
        orderby="executedDateTime desc",
        test_id=test_id,
        status="CANCELLED,DONE",
        maxpagesize=20,
    )
    all_test_runs = [run.as_dict() for run in all_test_runs]
    logger.debug("Total number of test runs: %s", len(all_test_runs))
    count = 0
    recent_test_runs = []
    for run in all_test_runs:
        if (
            run.get("testRunId") != baseline_test_run_id
            and count < 10  # Show only 10 most recent test runs
        ):
            recent_test_runs.append(run)
            count += 1

    logger.debug("Number of recent test runs: %s", len(recent_test_runs))
    rows = [
        generate_trends_row(baseline_test_run, response_time_aggregate=response_time_aggregate)
    ]
    for run in recent_test_runs:
        rows.append(
            generate_trends_row(run, response_time_aggregate=response_time_aggregate)
        )
    logger.debug("Retrieved test trends: %s", rows)
    return rows


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
    return response.as_dict()


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
    return response.as_dict()


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
    return response.as_dict()


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
    return response.as_dict()


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
    return response.as_dict()


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
    return response.as_dict()


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
    if not no_wait and response is not None and response.get("validationStatus") == "VALIDATION_FAILURE":
        raise FileOperationError(
            f"File upload failed due to validation failure: {response.get('validationFailureDetails')}"
        )
    logger.debug("Upload test file response: %s", response)
    logger.info("Upload test file completed")
    return response.as_dict()


def list_test_file(
    cmd,
    load_test_resource,
    test_id,
    resource_group_name=None,
):
    logger.info("Listing files for the test")
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    response_list = client.list_test_files(test_id)
    logger.debug("Retrieved files: %s", response_list)
    logger.info("Listing files for the test completed")
    return [response.as_dict() for response in response_list]


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
