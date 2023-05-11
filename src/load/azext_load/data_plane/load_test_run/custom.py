from azext_load.data_plane.utils.utils import (
    create_or_update_test_run_body,
    get_admin_data_plane_client,
    get_test_run_id,
    get_testrun_data_plane_client,
)
from azure.cli.core.azclierror import ValidationError
from knack.log import get_logger

logger = get_logger(__name__)


def create_test_run(
    cmd,
    load_test_resource,
    test_id,
    display_name=None,
    existing_test_id=None,
    description=None,
    env=None,
    secrets=None,
    certificate=None,
    resource_group_name=None,
    no_wait=False,
):
    client = get_testrun_data_plane_client(cmd, load_test_resource, resource_group_name)
    test_run_body = create_or_update_test_run_body(
        test_id,
        display_name=display_name,
        description=description,
        env=env,
        secrets=secrets,
        certificate=certificate,
    )

    poller = client.begin_test_run(
        test_run_id=get_test_run_id(),
        body=test_run_body,
        old_test_run_id=existing_test_id,
    )
    response = poller.polling_method()._initial_response
    if not no_wait:
        response = poller.result()
    return response


def get_test_run(cmd, load_test_resource, test_run_id, resource_group_name=None):
    client = get_testrun_data_plane_client(cmd, load_test_resource, resource_group_name)
    return client.get_test_run(test_run_id=test_run_id)


def update_test_run(
    cmd,
    test_run_id,
    description,
    load_test_resource,
    resource_group_name=None,
):
    client = get_testrun_data_plane_client(cmd, load_test_resource, resource_group_name)
    # validate if test run exists
    test_run_body = client.get_test_run(test_run_id=test_run_id)
    test_run_body = create_or_update_test_run_body(
        test_run_body.get("testId"), description=description
    )
    return client._test_run_initial(test_run_id=test_run_id, body=test_run_body)


def delete_test_run(cmd, load_test_resource, test_run_id, resource_group_name=None):
    client = get_testrun_data_plane_client(cmd, load_test_resource, resource_group_name)
    return client.delete_test_run(test_run_id=test_run_id)


def list_test_runs(cmd, test_id, load_test_resource, resource_group_name=None):
    client = get_testrun_data_plane_client(cmd, load_test_resource, resource_group_name)
    return client.list_test_runs(test_id=test_id)


def stop_test_run(cmd, load_test_resource, test_run_id, resource_group_name=None):
    client = get_testrun_data_plane_client(cmd, load_test_resource, resource_group_name)
    return client.stop_test_run(test_run_id=test_run_id)


def download_test_run_files(
    cmd,
    load_test_resource,
    test_run_id,
    path,
    test_run_input=False,
    test_run_log=False,
    test_run_results=False,
    resource_group_name=None,
):
    client = get_testrun_data_plane_client(cmd, load_test_resource, resource_group_name)
    test_run_data = client.get_test_run(test_run_id=test_run_id)
    if test_run_input:
        if test_run_data.get("inputArtifacts", {}).get("configFileInfo") is not None:
            pass
    if test_run_log:
        if test_run_data.get("inputArtifacts", {}).get("configFileInfo") is not None:
            pass
    if test_run_results:
        if test_run_data.get("inputArtifacts", {}).get("configFileInfo") is not None:
            pass


def get_client_metrics(cmd, load_test_resource, test_run_id, resource_group_name=None):
    client = get_testrun_data_plane_client(cmd, load_test_resource, resource_group_name)

    test_run_response = client.get_test_run(test_run_id)

    metric_namespaces = client.get_metric_namespaces(test_run_id)

    metric_definitions = client.get_metric_definitions(
        test_run_id, metric_namespace=metric_namespaces["value"][0]["name"]
    )

    metrics = client.list_metrics(
        test_run_id,
        metric_name=metric_definitions["value"][0]["name"],
        metric_namespace=metric_namespaces["value"][0]["name"],
        time_interval="{start}/{end}".format(
            start=test_run_response["startDateTime"],
            end=test_run_response["endDateTime"],
        ),
    )

    response = []
    for metric in metrics:
        response.append(metric)

    return response

# TODO: Add log statements everywhere
