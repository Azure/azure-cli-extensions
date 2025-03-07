# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_load.data_plane.utils.utils import (
    create_or_update_test_run_body,
    download_from_storage_container,
    get_file_info_and_download,
    get_testrun_data_plane_client,
)
from azext_load.data_plane.utils.constants import HighScaleThreshold
from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.core.exceptions import ResourceNotFoundError
from urllib.parse import urlparse

from knack.log import get_logger

logger = get_logger(__name__)


def create_test_run(
    cmd,
    load_test_resource,
    test_run_id,
    test_id,
    display_name=None,
    existing_test_run_id=None,
    description=None,
    env=None,
    secrets=None,
    certificate=None,
    resource_group_name=None,
    no_wait=False,
    debug_mode=False,
):
    logger.info("Create test run started")
    client = get_testrun_data_plane_client(cmd, load_test_resource, resource_group_name)
    test_run_body = None
    try:
        test_run_body = client.get_test_run(test_run_id=test_run_id)
    except ResourceNotFoundError:
        pass
    if test_run_body:
        msg = f"Test run with given test run ID : {test_run_id} already exist."
        logger.debug(msg)
        raise InvalidArgumentValueError(msg)

    test_run_body = create_or_update_test_run_body(
        test_id,
        display_name=display_name,
        description=description,
        env=env,
        secrets=secrets,
        certificate=certificate,
        debug_mode=debug_mode,
    )
    logger.debug("Creating test run with following request %s", test_run_body)
    poller = client.begin_test_run(
        test_run_id=test_run_id,
        body=test_run_body,
        old_test_run_id=existing_test_run_id,
    )
    response = poller.polling_method().resource()
    if not no_wait:
        response = poller.result()
    logger.info("Test run created with following response %s", response)
    return response.as_dict()


def get_test_run(cmd, load_test_resource, test_run_id, resource_group_name=None):
    logger.info("Getting test run %s", test_run_id)
    client = get_testrun_data_plane_client(cmd, load_test_resource, resource_group_name)
    response = client.get_test_run(test_run_id=test_run_id)
    logger.debug("Test run %s", response)
    logger.info("Getting test run completed")
    return response.as_dict()


def update_test_run(
    cmd,
    test_run_id,
    load_test_resource,
    description=None,
    display_name=None,
    resource_group_name=None,
):
    logger.info("Update test run started")
    client = get_testrun_data_plane_client(cmd, load_test_resource, resource_group_name)
    try:
        test_run_body = client.get_test_run(test_run_id=test_run_id)
    except ResourceNotFoundError as e:
        msg = f"Test run with given test run ID : {test_run_id} does not exist."
        logger.debug(msg)
        raise InvalidArgumentValueError(msg) from e
    if description:
        if description.casefold() in ["null", ""]:
            description = None
        else:
            description = description or test_run_body.get("description")
    display_name = display_name or test_run_body.get("displayName")
    test_run_body = create_or_update_test_run_body(
        test_run_body.get("testId"), description=description, display_name=display_name
    )
    logger.info("Updating test run %s", test_run_id)
    # pylint: disable-next=protected-access
    response = client.begin_test_run(test_run_id=test_run_id, body=test_run_body).result()
    logger.debug("Test run updated with following response %s", response)
    logger.info("Update test run completed")
    return response.as_dict()


def delete_test_run(cmd, load_test_resource, test_run_id, resource_group_name=None):
    client = get_testrun_data_plane_client(cmd, load_test_resource, resource_group_name)
    logger.info("Deleting test run %s", test_run_id)
    response = client.delete_test_run(test_run_id=test_run_id)
    logger.debug("Test run deleted with following response %s", response)
    logger.info("Delete test run completed")
    return response


def list_test_runs(cmd, test_id, load_test_resource, resource_group_name=None):
    client = get_testrun_data_plane_client(cmd, load_test_resource, resource_group_name)
    logger.info("Listing test runs for test %s", test_id)
    response = client.list_test_runs(test_id=test_id)
    logger.debug("Test runs listed with following response %s", response)
    logger.info("List test runs completed")
    return [test_run.as_dict() for test_run in response]


def stop_test_run(cmd, load_test_resource, test_run_id, resource_group_name=None):
    client = get_testrun_data_plane_client(cmd, load_test_resource, resource_group_name)
    logger.info("Stopping test run %s", test_run_id)
    response = client.stop_test_run(test_run_id=test_run_id)
    logger.debug("Test run stopped with following response %s", response)
    logger.info("Stop test run completed")
    return response


def copy_test_run_artifacts_url(cmd, load_test_resource, test_run_id, resource_group_name=None):
    client = get_testrun_data_plane_client(cmd, load_test_resource, resource_group_name)
    logger.info("Fetching test run copy artifacts SAS URL for test run %s", test_run_id)
    logger.warning("You can use the SAS URL with Azure Storage Explorer or AzCopy to access the storage resource.")
    test_run_data = client.get_test_run(test_run_id=test_run_id)
    artifacts_container = test_run_data.get(
        "testArtifacts", {}).get(
        "outputArtifacts", {}).get(
        "artifactsContainerInfo")
    if artifacts_container is None or artifacts_container.get("url") is None:
        logger.warning("No test artifacts container found for test run %s", test_run_id)
    else:
        logger.info("Fetched test run copy artifacts SAS URL %s", artifacts_container)
        return artifacts_container.get("url")


def _download_results_file(test_run_output_artifacts, test_run_id, path):
    logger.info("Downloading results file for test run %s", test_run_id)
    if test_run_output_artifacts is not None:
        result_file_info = test_run_output_artifacts.get("resultFileInfo")
        if result_file_info is not None and result_file_info.get("url") is not None:
            file_path = get_file_info_and_download(result_file_info, path)
            logger.warning("Results file downloaded to %s", file_path)
        else:
            logger.info("No results file found for test run %s", test_run_id)
    else:
        logger.warning(
            "No results file found for test run %s",
            test_run_id,
        )


def _download_reports_file(test_run_output_artifacts, test_run_id, path):
    logger.info("Downloading report file for test run %s", test_run_id)
    if test_run_output_artifacts is not None:
        report_file_info = test_run_output_artifacts.get("reportFileInfo")
        if report_file_info is not None and report_file_info.get("url") is not None:
            file_path = get_file_info_and_download(report_file_info, path)
            logger.warning("Report file downloaded to %s", file_path)
        else:
            logger.info("No report file found for test run %s", test_run_id)
    else:
        logger.warning(
            "No report file found for test run %s",
            test_run_id,
        )


def _download_logs_file(test_run_output_artifacts, test_run_id, path):
    logger.info("Downloading log file for test run %s", test_run_id)
    if test_run_output_artifacts is not None:
        logs_file_info = test_run_output_artifacts.get("logsFileInfo")
        if logs_file_info is not None and logs_file_info.get("url") is not None:
            file_path = get_file_info_and_download(logs_file_info, path)
            logger.warning("Log file downloaded to %s", file_path)
        else:
            logger.info("No log file found for test run %s", test_run_id)
    else:
        logger.warning(
            "No logs file and output artifacts found for test run %s",
            test_run_id,
        )


def _download_input_file(test_run_input_artifacts, test_run_id, path):
    logger.info("Downloading input artifacts for test run %s", test_run_id)
    if test_run_input_artifacts is not None:
        files_to_download = []
        for item in test_run_input_artifacts.values():
            if isinstance(item, list):
                files_to_download.extend(item)
            else:
                files_to_download.append(item)
        for artifact_data in files_to_download:
            if artifact_data.get("url") is not None:
                get_file_info_and_download(artifact_data, path)
        logger.warning("Input artifacts downloaded to %s", path)
    else:
        logger.warning("No input artifacts found for test run %s", test_run_id)


def _is_high_scale_test_run(test_run_data):
    engines = test_run_data.get("loadTestConfiguration", {}).get("engineInstances")
    duration = test_run_data.get("duration")
    if (
        (engines is not None and engines > HighScaleThreshold.MAX_ENGINE_INSTANCES_PER_TEST_RUN)
        or (duration is not None and duration > HighScaleThreshold.MAX_DURATION_HOURS_PER_TEST_RUN * 60 * 60 * 1000)
    ):
        return True
    return False


def _download_from_artifacts_container(artifacts_container, path, logs=False, results=False):
    logger.info(
        "Downloading %s from artifacts container for high scale test run",
        {"logs" if logs else "results" if results else "files"}
    )
    if artifacts_container is not None and artifacts_container.get("url") is not None:
        artifacts_container_url = artifacts_container.get("url")
        artifacts_container_url = _update_artifacts_container_path(artifacts_container_url, logs, results)
        download_from_storage_container(artifacts_container_url, path)
        logger.info(
            "%s from artifacts container downloaded to %s",
            {"Logs" if logs else "Results" if results else "Files"},
            path
        )
    else:
        logger.warning("No artifacts container found")


def _update_artifacts_container_path(artifacts_container_url, logs, results):
    artifacts_container_path = urlparse(artifacts_container_url).path
    artifacts_container_path_updated = (
        artifacts_container_path
        + f"{'' if artifacts_container_path.endswith('/') else '/'}"
        + f"{'logs' if logs else 'results' if results else ''}"
    )
    return artifacts_container_url.replace(
        artifacts_container_path, artifacts_container_path_updated,
    )


def download_test_run_files(
    cmd,
    load_test_resource,
    test_run_id,
    path,
    test_run_input=False,
    test_run_log=False,
    test_run_results=False,
    test_run_report=False,
    resource_group_name=None,
    force=False,  # pylint: disable=unused-argument
):
    logger.info("Downloading test run files for test run %s", test_run_id)
    client = get_testrun_data_plane_client(cmd, load_test_resource, resource_group_name)
    test_run_data = client.get_test_run(test_run_id=test_run_id)
    if test_run_data.get("testArtifacts") is None:
        logger.warning("No test artifacts found for test run %s", test_run_id)

    test_run_input_artifacts = test_run_data.get("testArtifacts", {}).get("inputArtifacts")
    test_run_output_artifacts = test_run_data.get("testArtifacts", {}).get("outputArtifacts")
    if test_run_input:
        _download_input_file(test_run_input_artifacts, test_run_id, path)

    is_high_scale_test_run = _is_high_scale_test_run(test_run_data)
    artifacts_container = (
        test_run_output_artifacts.get("artifactsContainerInfo")
        if test_run_output_artifacts
        else None
    )
    if test_run_log:
        if is_high_scale_test_run:
            _download_from_artifacts_container(artifacts_container, path, logs=True)
        else:
            _download_logs_file(test_run_output_artifacts, test_run_id, path)

    if test_run_results:
        if is_high_scale_test_run:
            _download_from_artifacts_container(artifacts_container, path, results=True)
        else:
            _download_results_file(test_run_output_artifacts, test_run_id, path)

    if test_run_report:
        _download_reports_file(test_run_output_artifacts, test_run_id, path)


# app components
def add_test_run_app_component(
    cmd,
    load_test_resource,
    test_run_id,
    app_component_id,
    app_component_name,
    app_component_type,
    app_component_kind=None,
    resource_group_name=None,
):
    logger.info("Adding app component to test run %s", test_run_id)
    client = get_testrun_data_plane_client(cmd, load_test_resource, resource_group_name)
    body = {
        "testRunId": test_run_id,
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
    logger.debug("Adding app component to the test run: %s", body)
    response = client.create_or_update_app_components(
        test_run_id=test_run_id, body=body
    )
    logger.debug("App component added with following response %s", response)
    logger.info("App component completed")
    return response.as_dict()


def list_test_run_app_component(
    cmd,
    load_test_resource,
    test_run_id,
    resource_group_name=None,
):
    client = get_testrun_data_plane_client(cmd, load_test_resource, resource_group_name)
    logger.info("Listing app components for the given test run")
    response = client.get_app_components(test_run_id=test_run_id)
    logger.debug(
        "List of app components completed with following response %s", response
    )
    logger.info("App components completed")
    return response.as_dict()


def remove_test_run_app_component(
    cmd,
    load_test_resource,
    test_run_id,
    app_component_id,
    resource_group_name=None,
):
    client = get_testrun_data_plane_client(cmd, load_test_resource, resource_group_name)
    body = {"testRunId": test_run_id, "components": {app_component_id: None}}
    logger.info("Removing app component from the test run: %s", body)
    response = client.create_or_update_app_components(
        test_run_id=test_run_id, body=body
    )
    logger.debug("App component removed completed with following response %s", response)
    logger.info("App component completed")
    return response.as_dict()


# server metrics


def add_test_run_server_metric(
    cmd,
    load_test_resource,
    test_run_id,
    metric_id,
    metric_name,
    metric_namespace,
    aggregation,
    app_component_id,
    app_component_type,
    resource_group_name=None,
):
    logger.info("Adding server metrics to test run %s", test_run_id)
    client = get_testrun_data_plane_client(cmd, load_test_resource, resource_group_name)
    body = {
        "testRunId": test_run_id,
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
    logger.debug("Adding server metrics to the test run: %s", body)
    response = client.create_or_update_server_metrics_config(
        test_run_id=test_run_id, body=body
    )
    logger.debug(
        "Server metrics added completed with following response %s", test_run_id
    )
    logger.info("Server metrics completed")
    return response.as_dict()


def list_test_run_server_metric(
    cmd,
    load_test_resource,
    test_run_id,
    resource_group_name=None,
):
    client = get_testrun_data_plane_client(cmd, load_test_resource, resource_group_name)
    logger.info("Listing server metrics")
    response = client.get_server_metrics_config(test_run_id=test_run_id)
    logger.debug(
        "List of server metrics completed with following response %s", response
    )
    logger.info("Server metrics completed")
    return response.as_dict()


def remove_test_run_server_metric(
    cmd,
    load_test_resource,
    test_run_id,
    metric_id,
    resource_group_name=None,
):
    client = get_testrun_data_plane_client(cmd, load_test_resource, resource_group_name)
    body = {"testRunId": test_run_id, "metrics": {metric_id: None}}
    logger.info("Removing server metrics from the test run: %s", body)
    response = client.create_or_update_server_metrics_config(
        test_run_id=test_run_id, body=body
    )
    logger.debug(
        "Server metrics removed completed with following response %s", response
    )
    logger.info("Server metrics completed")
    return response.as_dict()


def get_test_run_metric_namespaces(
    cmd, load_test_resource, test_run_id, resource_group_name=None
):
    client = get_testrun_data_plane_client(cmd, load_test_resource, resource_group_name)
    logger.info("Getting client metrics namespaces")
    response = client.get_metric_namespaces(test_run_id)
    logger.debug(
        "Getting client metrics namespaces completed with following response %s",
        response,
    )
    logger.info("Getting client metrics namespaces completed")
    return response.as_dict()


def list_test_run_metrics(
    cmd,
    load_test_resource,
    test_run_id,
    metric_namespace,
    metric_name=None,
    start_time=None,
    end_time=None,
    interval=None,
    aggregation=None,
    dimension_filters=None,
    resource_group_name=None,
):
    client = get_testrun_data_plane_client(cmd, load_test_resource, resource_group_name)
    logger.info(
        "Getting test run metric dimensions for test run %s for metric %s in namespace %s",
        test_run_id,
        metric_name,
        metric_namespace,
    )

    if start_time is None or end_time is None:
        test_run_response = client.get_test_run(test_run_id)
        if start_time is None:
            start_time = test_run_response["startDateTime"]
        if end_time is None:
            end_time = test_run_response["endDateTime"]

    time_interval = f"{start_time}/{end_time}"
    logger.debug("Time interval: %s", time_interval)

    if metric_name is not None:
        if dimension_filters is None:
            dimension_filters = []
        elif any(
            dimension_filter.get("name") == "*"
            for dimension_filter in dimension_filters
        ):
            # Add all values for all dimensions if '*' present in dimension names
            metric_definitions = client.get_metric_definitions(
                test_run_id, metric_namespace=metric_namespace
            )
            for metric_definition in metric_definitions.get("value", []):
                if metric_definition.get("name") == metric_name:
                    dimension_filters = [
                        {"name": metric_dimension.get("name"), "values": "*"}
                        for metric_dimension in metric_definition.get("dimensions", [])
                    ]
                    break
        logger.debug("Dimension filters: %s", dimension_filters)
        for dimension_filter in dimension_filters:
            # Add all values for given dimensions if '*' present in dimension values
            if "*" in dimension_filter.get("values", []):
                metric_dimensions = client.list_metric_dimension_values(
                    test_run_id,
                    name=dimension_filter["name"],
                    metric_name=metric_name,
                    metric_namespace=metric_namespace,
                    interval=interval,
                    time_interval=time_interval,
                )
                dimension_filter["values"] = list(metric_dimensions)

        metrics = client.list_metrics(
            test_run_id,
            metric_name=metric_name,
            metric_namespace=metric_namespace,
            time_interval=time_interval,
            aggregation=aggregation,
            interval=interval,
            body={
                "filters": dimension_filters,
            },
        )
        response = [metric.as_dict() for metric in metrics]
        logger.debug("All metrics: %s", response)
        logger.info("List metrics completed")
        return response

    # metric_name is None, so list metrics for all metric names
    metric_definitions = client.get_metric_definitions(
        test_run_id, metric_namespace=metric_namespace
    )
    aggregated_metrics = {}
    for metric_definition in metric_definitions.get("value", []):
        metric_name = metric_definition.get("name")
        if metric_name is None:
            pass
        metrics = client.list_metrics(
            test_run_id,
            metric_name=metric_name,
            metric_namespace=metric_namespace,
            time_interval=time_interval,
            aggregation=aggregation,
            interval=interval,
        )
        response = [metric.as_dict() for metric in metrics]
        aggregated_metrics[metric_name] = response
    logger.debug("Aggregated metrics: %s", aggregated_metrics)
    logger.info("List metrics completed")
    return aggregated_metrics


def get_test_run_metric_definitions(
    cmd, load_test_resource, test_run_id, metric_namespace, resource_group_name=None
):
    client = get_testrun_data_plane_client(cmd, load_test_resource, resource_group_name)
    logger.info(
        "Getting test run metric definitions for namespace %s", metric_namespace
    )
    metric_definitions = client.get_metric_definitions(
        test_run_id, metric_namespace=metric_namespace
    )
    logger.debug(
        "Getting test run metric definitions completed with following response %s",
        metric_definitions,
    )
    logger.info("Getting test run metric definitions completed")
    return metric_definitions.as_dict()


def get_test_run_metric_dimensions(
    cmd,
    load_test_resource,
    test_run_id,
    metric_name,
    metric_namespace,
    dimension_name,
    start_time=None,
    end_time=None,
    interval=None,
    resource_group_name=None,
):
    client = get_testrun_data_plane_client(cmd, load_test_resource, resource_group_name)
    logger.info(
        "Getting test run metric dimensions for test run %s for metric %s in namespace %s",
        test_run_id,
        metric_name,
        metric_namespace,
    )

    if start_time is None or end_time is None:
        test_run_response = client.get_test_run(test_run_id)
        if start_time is None:
            start_time = test_run_response["startDateTime"]
        if end_time is None:
            end_time = test_run_response["endDateTime"]

    dimensions = client.list_metric_dimension_values(
        test_run_id,
        dimension_name,
        metric_name=metric_name,
        metric_namespace=metric_namespace,
        time_interval=f"{start_time}/{end_time}",
        interval=interval,
    )
    response = list(dimensions)
    logger.debug("Dimensions: %s", response)
    logger.info("List dimensions completed")
    return response
