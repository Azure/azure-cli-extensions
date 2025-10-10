# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------
import base64
import codecs
import contextlib
import os
import pathlib
import re
import shlex
import shutil
import sys
import tarfile
import tempfile
import time
import traceback
from http import HTTPStatus
from subprocess import STDOUT, CalledProcessError, call, check_output
from typing import Tuple

from azext_arcdata.core.constants import (
    ARC_INSTANCE_LABEL,
    ARC_NAMESPACE_LABEL,
    ARC_RESOURCE_KIND_LABEL,
)
from azext_arcdata.core.exceptions import ClusterLogError
from azext_arcdata.core.util import (
    display,
    is_windows,
    retry,
    with_timeout,
)
from azext_arcdata.kubernetes_sdk.models.custom_resource_definition import (
    CustomResourceDefinition,
)
from humanfriendly.terminal.spinners import AutomaticSpinner
from knack.log import get_logger
from kubernetes import client as k8sClient
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream
from urllib3.exceptions import MaxRetryError, NewConnectionError

logger = get_logger(__name__)

# Container names and the log file locations for each container. Even if a container is not in this list, the
# STDOUT logs will be copied for that container. /var/log is always copied.
LOG_PATTERNS = {
    "arc-sqlmi": ["/var/opt/mssql/log"],
    "mssql-test": ["/tests/junit"],
    "controller": ["/var/opt/controller/log"],
}

# System and Connectedk8 namespaces.
#
CONNECTEDK8S_NAMESPACE = "azure-arc"
SYSTEM_NAMESPACE = "kube-system"

# ControlDB System login name.
#
CONTROLDB_CONTAINER_NAME = "mssql-server"
CONTROLDB_DATA_PATH = "/var/opt/mssql/data"
CONTROLDB_LABEL = "app=controldb"
CONTROLDB_SYSTEM_SECRET = "controller-system-secret"

# ControlDB CDC controlled tables - empirically determined tables that
# are useful to have CDC enabled on for state transition history
#
# Guidelines:
#
#  - Table must have Primary Key to be included.
#
#  - Include tables that contain debuggable information
#    where we wish we could have had a breadcrumb trail of
#   "what happened to the system to finally get here" - CDC
#    will capture all of the state changes as a row.
#
CONTROLDB_CDC_TABLES = [
    # Controller
    "Settings",
    # FSM plugin
    "ArcDaemonSetFsm",
    "ArcReplicaSetFsm",
    "ArcStatefulSetFsm",
    "ClusterManagementFsm",
    "CustomResourceFsm",
    "CustomResourceProviderFsm",
    "UpgradeVersionStatusFsm",
    # FSM framework
    "fsm_active_finite_state_machines",
    "fsm_active_workflows",
    "fsm_timer_events",
    "fsm_workflow_errors",
    # Monitoring
    "LogsRetentionFsm",
    # Postgres - Tasks
    "PostgreSqlRestoreTaskFsm",
    # SQL MI - HA
    "HadrAgFsm",
    "HadrCreateDatabaseFsm",
    "HadrDbmEndpointFsm",
    "HadrDropDatabaseFsm",
    "HadrReprovisionDbmEndpointFsm",
    # SQL MI - DR
    "DistributedAGFsm",
    # SQL MI - PITR
    "RestoreManagedDatabaseFsm",
    # SQL MI - Tasks
    "SqlManagedInstanceReprovisionReplicaTaskFsm",
    "SqlManagedInstanceRestoreTaskFsm",
    # Usage
    "Resources",
]

# Default logs folder for each container.
#
DEFAULT_LOG_FOLDER = "/var/log"

# Byte limit for console.
#
CONSOLE_OUT_LIMIT_BYTES = 100 * 1000 * 1000

CONNECTION_RETRY_ATTEMPTS = 10
CONNECTION_RETRY_INTERVAL_SECONDS = 10


@contextlib.contextmanager
def pushd(new_dir: str) -> None:
    """
    A thin wrapper to allow file copies from windows filesystems, since 'kubectl cp'
    throws on "C:":

        https://github.com/kubernetes/kubernetes/issues/77310#issuecomment-600571650

    :param new_dir: The directory to push and pop.
    """
    previous_dir = os.getcwd()
    logger.debug("Pushing directory from '%s' to '%s'", previous_dir, new_dir)
    os.chdir(new_dir)
    try:
        yield
    finally:
        logger.debug(
            "Popping directory from '%s' to '%s'", new_dir, previous_dir
        )
        os.chdir(previous_dir)


def validate_namespace(namespace):
    """
    Verifies the given name space is valid and is a SQL cluster or is system cluster
    Exits the command if namespace is not valid
    :param namespace:
    :return:
    """
    logger.debug("Validating the cluster name ...")
    if not namespace:
        logger.error("Please specify valid namespace")
    if namespace == SYSTEM_NAMESPACE:
        return
    else:
        try:
            # Verify the given namespace is a SQL cluster
            #
            namespace_response = k8sClient.CoreV1Api().read_namespace(namespace)
            if (
                namespace_response.metadata.labels is None
                or ARC_NAMESPACE_LABEL not in namespace_response.metadata.labels
            ):
                logger.debug(
                    'Namespace "%s" was not created by the Azure Arc deployment workflow and does not have the "%s" label.',
                    namespace,
                    ARC_NAMESPACE_LABEL,
                )
        except k8sClient.rest.ApiException as e:
            # If 404 Notfound is returned by K8s
            #
            if e.status == HTTPStatus.NOT_FOUND:
                logger.error("Cluster does not exist.")
                sys.exit(1)
            else:
                logger.error(e.body)
                exit(e.status)


def run_command_within_container(cluster_name, pod_name, container_name, cmd):
    """
    Running command within specific container
    :param cluster_name:
    :param pod_name:
    :param container_name:
    :param cmd:
    :return:
    """
    try:
        display(
            "Starting to run '%s' command in '%s' container of '%s' pod"
            % (cmd, container_name, pod_name)
        )

        response = stream(
            k8sClient.CoreV1Api().connect_get_namespaced_pod_exec,
            name=pod_name,
            namespace=cluster_name,
            command=cmd,
            container=container_name,
            stderr=True,
            stdin=False,
            stdout=True,
            tty=False,
        )

        display("Command ran successfully with the output:\n %s" % (response))
        return response
    except ApiException as e:
        logger.error(e.body)
        raise e
    except Exception as e:
        traceback.print_exc()
        raise e


def copy_container_log_folder(
    namespace, target, pod_name, container_name, log_path
):
    """
    Copies the files inside a log folder from the given container to the target location.
    Returns true if copy command completes successfully.
    :param namespace: cluster name
    :param target: target folder
    :param pod_name: pod name
    :param container_name: container name
    :param log_path: the log folder path in the container
    :return:
    """
    try:
        command = "kubectl "
        if "KUBECTL_CONTEXT" in os.environ:
            command += "--context %s " % (os.environ["KUBECTL_CONTEXT"])
        command += "cp -n %s -c %s %s ." % (
            namespace,
            container_name,
            pod_name + ":" + log_path,
        )
        parts = shlex.split(command)
        logger.debug(
            "Collecting logs from pod: %s container: %s path: %s to: %s"
            % (pod_name, container_name, log_path, target)
        )
        check_output(parts, stderr=STDOUT, cwd=target)
        return True

    except CalledProcessError as e:
        return False


def copy_container_logs(
    namespace, target, pod_name, container_name, containers
):
    """
    Copies the container logs, bases on the log patterns configured for each
    container, to the target location
    :param namespace: cluster name
    :param target: target folder
    :param pod_name: pod name
    :param container_name: container name
    :param containers:
    :return:
    """

    if container_name in LOG_PATTERNS:
        # Get the log patterns for the container
        #
        container_log_patterns = LOG_PATTERNS[container_name]
    else:
        container_log_patterns = []

    # Add default log location
    #
    if DEFAULT_LOG_FOLDER not in container_log_patterns:
        container_log_patterns.append(DEFAULT_LOG_FOLDER)

    for logPath in container_log_patterns:
        # Copy the logs to the target folder
        #
        files_copied = copy_container_log_folder(
            namespace, target, pod_name, container_name, logPath
        )
        if containers and not files_copied:
            logger.debug(
                "Couldn't copy the folder '%s' from container '%s'. Trying other containers"
                % (logPath, container_name)
            )
            for otherContainer in containers:
                # ignore the container already processed
                #
                if otherContainer.name == container_name:
                    continue

                # Try copy the directory from another container in the same pod
                #
                files_copied = copy_container_log_folder(
                    namespace, target, pod_name, otherContainer.name, logPath
                )

                if files_copied:
                    logger.debug(
                        "Found the folder '%s' in container '%s'"
                        % (logPath, otherContainer.name)
                    )
                    break
        if not files_copied:
            logger.debug(
                "Couldn't find the folder '%s' in any container" % (logPath)
            )


def copy_consoleout_log(namespace, target, pod_name, container_name, previous):
    """
    Copies the STDOUT logs for each container to the target location
    Getting the kubernete "previous" logs If previous is True
    :param namespace: cluster name
    :param target: target folder
    :param pod_name: pod name
    :param container_name: container name
    :return:
    """
    stdout_log = os.path.join(
        target, pod_name + "-" + container_name + "-stdout.log"
    )
    if previous:
        stdout_log = os.path.join(
            target, pod_name + "-" + container_name + "-previous-stdout.log"
        )
    log = k8sClient.CoreV1Api().read_namespaced_pod_log(
        name=pod_name,
        namespace=namespace,
        container=container_name,
        previous=previous,
        limit_bytes=CONSOLE_OUT_LIMIT_BYTES,
    )
    with codecs.open(stdout_log, "w", encoding="utf-8") as logFile:
        log = log + "\n[truncated]\n"
        logFile.write(log)


def copy_kubernetes_logs(namespace, target, pod_name, container_name):
    """
    Copies the STDOUT logs for each container to the target location
    :param namespace: cluster name
    :param target: target folder
    :param pod_name: pod name
    :param container_name: container name
    :return:
    """
    # Create the STDOUT log file in the target folder
    #
    logger.debug("Collecting STDOUT logs to: " + target)

    try:
        copy_consoleout_log(namespace, target, pod_name, container_name, False)
        copy_consoleout_log(namespace, target, pod_name, container_name, True)
    except k8sClient.rest.ApiException as e:
        if e.status == 400:
            # Getting previous logs for container can fail if the container doesn't have
            # previous termination. The error can be ignored in this case
            #
            if "previous terminated container" not in e.body:
                logger.debug(e.body)
        else:
            logger.warn(
                "Failed to copy STDOUT logs for pod: %s container: %s error: %s"
                % (pod_name, container_name, e.body)
            )


def copy_file_to_from_container(
    namespace: str,
    pod_name: str,
    container_name: str,
    local_file: str,
    container_file: str,
    direction: str,
) -> str:
    """
    Copy file "to" or "from" the local folder to the container.

    :param namespace: kubernetes namespace
    :param pod_name: exact pod name
    :param container_name: arc data services container name
    :param local_file: full path of local file
    :param container_folder: full path of container file
    :param direction: copy direction, either "to" or "from"
    :return: output of the kubectl command
    """
    try:
        k8s_path = f"{namespace}/{pod_name}:{container_file}"
        kubectl_cmd = ["kubectl", "cp"]

        if "KUBECTL_CONTEXT" in os.environ:
            kubectl_cmd.extend(["--context", os.environ["KUBECTL_CONTEXT"]])

        if direction == "to":
            display(
                f"Starting to copy local file from: {local_file} to container: {k8s_path}."
            )
            kubectl_cmd.extend([local_file, k8s_path])
        else:
            display(
                f"Starting to copy file from container: {k8s_path} to local: {local_file}."
            )
            kubectl_cmd.extend([k8s_path, local_file])

        kubectl_cmd.extend(
            [
                "-c",
                container_name,
            ]
        )
        rt = check_output(kubectl_cmd, stderr=STDOUT).decode()
        return rt

    except CalledProcessError as e:
        logger.debug(
            "Command failed with the error:\n %s" % (e.output.decode())
        )
        raise e
    except Exception as e:
        traceback.print_exc()
        raise e


def create_package(output_file_name, source_folder_name):
    """
    Create an folder from the collected logs
    :param output_file_name: the name of the folder to create
    :param source_folder_name: the path to the folder to move the files from
    :return:
    """
    display("Copying logs to %s." % (output_file_name))
    shutil.move(source_folder_name, output_file_name)
    display("Log files are copied to %s." % (os.path.abspath(output_file_name)))


def create_archive(output_file_name, source_folder_name, root_folder):
    """
    Create an archive from the collected logs
    :param output_file_name: the name of the archive to create
    :param source_folder_name: the path to the folder to create archive from
    :param root_folder: name of the root folder to put in the archive
    :return:
    """
    display("Creating an archive from %s." % (source_folder_name))
    with tarfile.open(output_file_name, "w:gz", compresslevel=1) as tar:
        tar.add(source_folder_name, root_folder)
    display(
        "Log files are archived in %s." % (os.path.abspath(output_file_name))
    )


def move_dumps(target_log_folder, dumps_target_log_folder):
    """
    Moves the dump files from log folders to a new folder for dumps only.
    Keeps the folder structure of the file in the target folder
    :param target_log_folder: folder that include all the logs
    :param dumps_target_log_folder: folder to move the dumps to
    """
    if not os.path.exists(dumps_target_log_folder):
        os.makedirs(dumps_target_log_folder)

    for root, dirs, files in os.walk(target_log_folder):
        dump_current_path = pathlib.Path(root)

        # Get the folder structure of the dump file to create the same in target. Removing the first folder name which is the temp folder for logs
        #
        dump_target_folder = os.path.join(
            dumps_target_log_folder,
            str(dump_current_path.relative_to(*dump_current_path.parts[:1])),
        )

        for file in files:
            dump_source_file = os.path.join(root, file)
            if (
                file.endswith(".dmp")
                or file.endswith(".mdmp")
                or file.endswith(".gdmp")
                or "core.sqlservr" in dump_source_file
                or "core.controller" in dump_source_file
                or "core.manual.controller" in dump_source_file
                or "SQLD" in dump_source_file
            ):

                # Move the dump from logs folders to dump folders
                #
                dump_target_file = os.path.join(dump_target_folder, file)
                os.makedirs(dump_target_folder, exist_ok=True)
                shutil.move(dump_source_file, dump_target_file)


def copy_logs_and_package(
    target_folder,
    root_folder,
    package_name_prefix,
    method_to_collect_logs,
    namespace,
    skip_compress=False,
    exclude_dumps=False,
    collect_cluster_logs=False,
):
    """
    Calls the given method (method_to_collect_logs) to collect logs in the target folder and creates a package from
    the result.
    :param target_folder: target folder
    :param root_folder: Root folder to collect logs in and create package from
    :param package_name_prefix: The prefix to use for the package file name
    :param method_to_collect_logs: The method to call to collect logs
    :param namespace: cluster name
    :param skip_compress: skips compressing the result if set to True
    :param exclude_dumps: exclude dumps if set to True
    :param collect_cluster_logs: if method_to_collect_logs is about collecting cluster logs
    :return:
    """
    temp_dir_path = tempfile.mkdtemp()

    try:
        target_log_folder = os.path.join(temp_dir_path, root_folder)
        target_dump_folder = os.path.join(temp_dir_path, "dumps")
        if not os.path.exists(target_log_folder):
            os.makedirs(target_log_folder)

        retry(
            method_to_collect_logs,
            target_log_folder,
            retry_count=CONNECTION_RETRY_ATTEMPTS,
            retry_delay=CONNECTION_RETRY_INTERVAL_SECONDS,
            retry_method="collect cluster logs",
            retry_on_exceptions=(NewConnectionError, MaxRetryError),
        )
        timestr = time.strftime("%Y%m%d-%H%M%S")
        file_name_prefix = package_name_prefix + "-" + timestr
    except Exception as e:
        raise ClusterLogError(
            "An error occurred while collecting the logs: {0}".format(e)
        )

    try:
        # Copy dumps to a separate folder
        # There can only be dump files for user's cluster when collecting log files.
        # Otherwise, skip dump moving steps.
        #
        if namespace != SYSTEM_NAMESPACE and collect_cluster_logs:
            move_dumps(target_log_folder, target_dump_folder)
        else:
            exclude_dumps = True
    except Exception as e:
        raise ClusterLogError(
            "An error occurred while moving dump files: {0}".format(e)
        )

    # Create an archive if skip_ compress is set to True, copy the logs to a folder.
    #
    if skip_compress:
        try:
            create_package(
                os.path.join(target_folder, file_name_prefix), target_log_folder
            )
            if not exclude_dumps:
                create_package(
                    os.path.join(target_folder, file_name_prefix + "-dumps"),
                    target_dump_folder,
                )
        except Exception as e:
            raise ClusterLogError(
                "An error occurred while copying the logs to a folder: {0}".format(
                    e
                )
            )

    # Otherwise, create an archive.
    #
    else:
        try:
            create_archive(
                os.path.join(target_folder, file_name_prefix + ".tar.gz"),
                target_log_folder,
                root_folder,
            )
            if not exclude_dumps:
                create_archive(
                    os.path.join(
                        target_folder, file_name_prefix + "-dumps" + ".tar.gz"
                    ),
                    target_dump_folder,
                    root_folder,
                )
        except Exception as e:
            raise ClusterLogError(
                "An error occurred while creating the archive: {0}".format(e)
            )

    try:
        if os.path.exists(temp_dir_path):
            shutil.rmtree(temp_dir_path)
    except Exception as e:
        raise ClusterLogError(
            "An error occurred while removing the temporary logs directory `{0}`: {1}".format(
                temp_dir_path, e
            )
        )


def _get_crd_by_kind(kind: str):
    """
    Returns the corresponding Arc CRD for the given resource kind.
    :param kind: resource kind
    :return:
    """

    api = k8sClient.ApiextensionsV1Api()
    crds = api.list_custom_resource_definition()
    for crd in crds.items:
        if crd.spec.names.kind == kind:
            return crd


def collect_cluster_logs(
    namespace,
    target_log_folder,
    pod_filter=None,
    container_filter=None,
    resource_kind=None,
    resource_name=None,
):
    """
    Collects cluster logs and copies to the target folder
    :param namespace: cluster name
    :param target_log_folder: target folder
    :param pod_filter: name to use to filter the pods
    :param container_filter: name to use to filter containers
    :param resource_kind: resource kind
    :param resource_name: resource name (used in conjunction with resource_kind) for selecting related k8s resources
    :return:
    """
    api = k8sClient.CustomObjectsApi()
    cr, label_selector, stateful_sets = None, None, None
    if resource_kind and resource_name:
        crd = CustomResourceDefinition(
            _get_crd_by_kind(resource_kind).to_dict()
        )
        cr = api.get_namespaced_custom_object(
            name=resource_name,
            namespace=namespace,
            group=crd.group,
            version=crd.stored_version,
            plural=crd.plural,
        )
        label_selector = "%s=%s,%s=%s" % (
            ARC_INSTANCE_LABEL,
            resource_name,
            ARC_RESOURCE_KIND_LABEL,
            resource_kind,
        )

    if cr:
        with open(
            os.path.join(
                target_log_folder, "%s-%s.json" % (resource_kind, resource_name)
            ),
            "w",
        ) as log_file:
            log_file.write(str(cr))

    # Get all the pods for given namespace
    #
    if label_selector:
        stateful_sets = (
            k8sClient.AppsV1Api()
            .list_namespaced_stateful_set(
                namespace=namespace, label_selector=label_selector
            )
            .items
        )
        pods = (
            k8sClient.CoreV1Api()
            .list_namespaced_pod(
                namespace=namespace, label_selector=label_selector
            )
            .items
        )
    else:
        pods = (
            k8sClient.CoreV1Api().list_namespaced_pod(namespace=namespace).items
        )

    if stateful_sets and len(stateful_sets) > 0:
        with open(
            os.path.join(
                target_log_folder,
                "%s-%s-statefulsets.json" % (resource_kind, resource_name),
            ),
            "w",
        ) as log_file:
            log_file.write(str(stateful_sets))

    if pods and len(pods) > 0:
        display("Collecting logs for containers...")

        for pod in pods:
            pod_name = pod.metadata.name

            # Filter the pod if podFilter is specified
            #
            if pod_filter is not None and pod_filter not in pod_name:
                continue

            # Filter AKS omsagent
            #
            if "omsagent" in pod_name:
                continue

            pod_log_folder = os.path.join(target_log_folder, pod_name)
            if not os.path.exists(pod_log_folder):
                os.makedirs(pod_log_folder)

            with open(
                os.path.join(pod_log_folder, "pod.json"), "w"
            ) as log_file:
                log_file.write(str(pod))

            events = (
                k8sClient.CoreV1Api()
                .list_namespaced_event(
                    namespace=namespace,
                    field_selector="involvedObject.kind=Pod,involvedObject.uid=%s,involvedObject.namespace=%s"
                    % (pod.metadata.uid, pod.metadata.namespace),
                    pretty="true",
                )
                .items
            )
            if events and len(events) > 0:
                with open(
                    os.path.join(pod_log_folder, "events.json"), "w"
                ) as log_file:
                    log_file.write(str(events))

            # Get the containers for the pod
            #
            spec = pod.spec
            for container in spec.containers:

                # Filter the container if containerFilter is specified
                #
                container_name = container.name
                if (
                    container_filter is not None
                    and container_filter not in container_name
                ):
                    continue

                # Create the target folder
                #
                target = os.path.join(
                    target_log_folder, pod_name, container_name
                )
                if not os.path.exists(target):
                    os.makedirs(target)

                logger.debug(
                    "\x1b[0;32;40m"
                    + pod_name
                    + "/"
                    + container_name
                    + "\x1b[0m"
                )

                # Copy logs
                #
                copy_kubernetes_logs(
                    namespace, target, pod_name, container_name
                )
                copy_container_logs(
                    namespace, target, pod_name, container_name, spec.containers
                )
    else:
        logger.warn("No pod found in the given namespace.")


def get_controldb_pod(namespace: str) -> str:
    """
    Returns the name of the ControlDB pod
    :param namespace: arc data service namespace
    :return: pod name
    """
    try:
        items = (
            k8sClient.CoreV1Api()
            .list_namespaced_pod(
                namespace=namespace, label_selector=CONTROLDB_LABEL
            )
            .items
        )
        return items[0].metadata.name
    except k8sClient.rest.ApiException as e:
        logger.error(e.body)
        raise e


def get_controldb_system_login(namespace: str) -> Tuple[str, str]:
    """
    Gets the system login for ControlDB
    :param namespace: arc data service namespace
    :return: Tuple of username and password
    """
    logger.debug(
        f"Obtaining ControlDB system login from secret in namespace {namespace}"
    )

    try:
        secret = k8sClient.CoreV1Api().read_namespaced_secret(
            CONTROLDB_SYSTEM_SECRET, namespace
        )

        for field in secret.data:
            secret.data[field] = base64.b64decode(secret.data[field]).decode(
                "utf-8"
            )

        return secret.data["username"], secret.data["password"]

    except k8sClient.rest.ApiException as e:
        logger.error(e.body)
        raise e


def parse_os_target_filepath(filepath: str) -> Tuple[str, str]:
    """
    Parses the target filepath based on the caller's OS.
    :param filepath: full filepath
    :return: Tuple of folder and file
    """
    if is_windows():
        delim = "\\"
    else:
        delim = "/"

    folder = delim.join(filepath.split(delim)[:-1])
    file = filepath.split(delim)[-1]

    logger.debug(f"Parsed file path: {folder}")
    logger.debug(f"Parsed backup file: {file}")

    return folder, file


def execute_controldb_query(namespace: str, database: str, query: str) -> None:
    """
    Executes a transact SQL query against ControlDB as system login.

    :param namespace: arc data service namespace :param query: Transact SQL query
    :return:
    """
    username, password = get_controldb_system_login(namespace)

    cmd = [
        "/opt/mssql-tools/bin/sqlcmd",
        "-S",
        "localhost,1433",
        "-U",
        username,
        "-P",
        password,
        "-d",
        database,
        "-Q",
        query,
    ]
    response = run_command_within_container(
        namespace, get_controldb_pod(namespace), CONTROLDB_CONTAINER_NAME, cmd
    )
    logger.debug(response)


def controldb_cdc(namespace: str, enable: str, retention_hours: int) -> None:
    """
    Enables or disables Change Data Capture on ControlDB supported system tables.
    :param namespace: arc data service namespace
    :param enable: True to enable, False to disable
    :return:
    """
    queries_to_execute = []

    is_enabled = str(enable).lower() == "true"
    if is_enabled:

        retention_mins = retention_hours * 60
        display(
            f"Enabling ControlDB Change Data Capture for {retention_hours} hours..."
        )

        # ControlDB has large payloads, maximum text replication size must be
        # set to max: bit.ly/cdc-text-repl-size
        #
        queries_to_execute.append(
            f"""EXEC sp_configure 'show advanced options', 1 ;
                    RECONFIGURE ;
                    EXEC sp_configure 'max text repl size', -1 ;
                    RECONFIGURE;
                 """
        )

        # Database
        #
        queries_to_execute.append("EXEC sys.sp_cdc_enable_db")

        # Tables
        #
        for table in CONTROLDB_CDC_TABLES:
            queries_to_execute.append(
                f"""EXEC sys.sp_cdc_enable_table 
                    @source_schema = 'dbo', 
                    @source_name = '{table}', 
                    @role_name = NULL, 
                    @supports_net_changes = 1;
                """
            )

        # Retention
        #
        queries_to_execute.append(
            f"EXEC sys.sp_cdc_change_job @job_type='cleanup', @retention={retention_mins}"
        )

    else:
        display("Disabling ControlDB Change Data Capture...")
        queries_to_execute.append("EXEC sys.sp_cdc_disable_db")

    for query in queries_to_execute:
        logger.debug("Executing query:")
        logger.debug(query)
        execute_controldb_query(
            namespace=namespace, database="controller", query=query
        )


def restore_unique_controldb_from_backup(
    namespace: str, backup_file_path: str
) -> None:
    """
    Restores a Controldb COPY ONLY backup into a target ControlDB pod.
    :param namespace: arc data service namespace
    :param backup_file_path: path to the .bak file, must be valid
    :return:
    """
    display("Restoring controldb backup under unique database name...")

    # Input validation
    #
    if not backup_file_path:
        raise ValueError("Backup file path must be specified.")

    if not os.path.exists(backup_file_path):
        raise ValueError(f"Backup file {backup_file_path} does not exist.")

    backup_folder, backup_file = parse_os_target_filepath(backup_file_path)

    if not backup_file.endswith(".bak"):
        raise ValueError("Valid backup file must end with .bak")

    try:
        # Define related variables
        #
        timestamp = int(time.time())
        backup_dir = f"/tmp/controldb-{timestamp}"
        restored_db_name = f"controller-{timestamp}"

        mdf_path = f"{CONTROLDB_DATA_PATH}/{restored_db_name}.mdf"
        ldf_path = f"{CONTROLDB_DATA_PATH}/{restored_db_name}_log.ldf"

        # Create temporary directory for backup
        #
        cmd = ["mkdir", "-p", backup_dir]
        response = run_command_within_container(
            namespace,
            get_controldb_pod(namespace),
            CONTROLDB_CONTAINER_NAME,
            cmd,
        )
        logger.debug(response)

        # Copy .bak from local TO container
        #
        with pushd(backup_folder):
            response = copy_file_to_from_container(
                namespace=namespace,
                pod_name=get_controldb_pod(namespace),
                container_name=CONTROLDB_CONTAINER_NAME,
                local_file=backup_file,
                container_file=f"{backup_dir}/{backup_file}",
                direction="to",
            )
            logger.debug(response)

        # Restore backup, with CDC data intact - if exists
        #
        query = (
            f"RESTORE DATABASE [{restored_db_name}] FROM DISK = '{backup_dir}/{backup_file}'"
            f"WITH MOVE 'controller' TO '{mdf_path}', MOVE 'controller_log' TO '{ldf_path}', "
            f"KEEP_CDC"
        )
        execute_controldb_query(
            namespace=namespace, database="master", query=query
        )

        # Clean up folder
        #
        cmd = ["rm", "-rf", backup_dir]
        response = run_command_within_container(
            namespace,
            get_controldb_pod(namespace),
            CONTROLDB_CONTAINER_NAME,
            cmd,
        )
        logger.debug(response)

        display(
            f"Successfully restored controller database {restored_db_name} from backup {backup_file}."
        )

    except k8sClient.rest.ApiException as e:
        logger.error(e.body)
        raise e


def collect_controldb_backup(namespace: str, target_backup_folder: str) -> None:
    """
    Copies a Controldb COPY ONLY backup to the target folder
    :param namespace: arc data service namespace
    :param target_backup_folder: target folder for backup
    :return:
    """
    display("Collecting controldb backup...")

    try:
        # Define related variables
        #
        timestamp = int(time.time())
        backup_dir = f"/tmp/controldb-{timestamp}"
        backup_file = f"controller-{timestamp}.bak"

        # Create temporary directory for backup
        #
        cmd = ["mkdir", "-p", backup_dir]
        response = run_command_within_container(
            namespace,
            get_controldb_pod(namespace),
            CONTROLDB_CONTAINER_NAME,
            cmd,
        )
        logger.debug(response)

        # Create backup
        #
        query = f"BACKUP DATABASE controller TO DISK = '{backup_dir}/{backup_file}' WITH COPY_ONLY"
        execute_controldb_query(
            namespace=namespace, database="master", query=query
        )

        # Copy .bak FROM container to local
        #
        with pushd(target_backup_folder):
            response = copy_file_to_from_container(
                namespace=namespace,
                pod_name=get_controldb_pod(namespace),
                container_name=CONTROLDB_CONTAINER_NAME,
                local_file=backup_file,
                container_file=f"{backup_dir}/{backup_file}",
                direction="from",
            )
            logger.debug(response)

        # Clean up
        #
        cmd = ["rm", "-rf", backup_dir]
        response = run_command_within_container(
            namespace,
            get_controldb_pod(namespace),
            CONTROLDB_CONTAINER_NAME,
            cmd,
        )
        logger.debug(response)

    except k8sClient.rest.ApiException as e:
        logger.error(e.body)
        raise e


def collect_cluster_info(
    namespace, target_log_folder, pod_filter=None, container_filter=None
):
    """
    Collects cluster info and copies to the target folder
    :param namespace: cluster name
    :param target_log_folder: target folder
    :param pod_filter: name to use to filter the pods
    :param container_filter: name to use to filter containers
    :return:
    """
    display("Collecting cluster info...")

    try:
        events = k8sClient.CoreV1Api().list_namespaced_event(
            namespace=namespace, pretty="true"
        )
        with open(
            os.path.join(target_log_folder, "events.json"), "w"
        ) as logFile:
            logFile.write(str(events))

        stateful_sets = k8sClient.AppsV1Api().list_namespaced_stateful_set(
            namespace=namespace, pretty="true"
        )
        with open(os.path.join(target_log_folder, "ss.json"), "w") as logFile:
            logFile.write(str(stateful_sets))

        replica_sets = k8sClient.AppsV1Api().list_namespaced_replica_set(
            namespace=namespace, pretty="true"
        )
        with open(os.path.join(target_log_folder, "rs.json"), "w") as logFile:
            logFile.write(str(replica_sets))

        deployments = k8sClient.AppsV1Api().list_namespaced_replica_set(
            namespace=namespace, pretty="true"
        )
        with open(os.path.join(target_log_folder, "dpl.json"), "w") as logFile:
            logFile.write(str(deployments))

        daemon_sets = k8sClient.AppsV1Api().list_namespaced_daemon_set(
            namespace=namespace, pretty="true"
        )
        with open(os.path.join(target_log_folder, "ds.json"), "w") as logFile:
            logFile.write(str(daemon_sets))

        services = k8sClient.CoreV1Api().list_namespaced_service(
            namespace=namespace, pretty="true"
        )
        with open(os.path.join(target_log_folder, "svc.json"), "w") as logFile:
            logFile.write(str(services))

        pods = k8sClient.CoreV1Api().list_namespaced_pod(
            namespace=namespace, pretty="true"
        )
        with open(os.path.join(target_log_folder, "pods.json"), "w") as logFile:
            logFile.write(str(pods))

        pv = k8sClient.CoreV1Api().list_persistent_volume(pretty="true")
        with open(os.path.join(target_log_folder, "pv.json"), "w") as logFile:
            logFile.write(str(pv))

        pvc = k8sClient.CoreV1Api().list_namespaced_persistent_volume_claim(
            namespace=namespace, pretty="true"
        )
        with open(os.path.join(target_log_folder, "pvc.json"), "w") as logFile:
            logFile.write(str(pvc))
    except k8sClient.rest.ApiException as e:
        logger.error(e.body)
        raise e


def is_in_dev_mode():
    """
    Returns true if running in dev mode, otherwise returns false
    :return:
    """
    if "AZDATA_DEV_MODE" not in os.environ:
        return False
    dev_mode = os.environ["AZDATA_DEV_MODE"]
    return dev_mode in ["True", "true", "1", "yes"]


def copy_controldb_backup(
    namespace,
    target_folder,
    skip_compress=False,
):
    """
    Generates and copies the controller database backup to the target location
    :param namespace: arc data services namespace
    :param target_folder: target folder
    :param skip_compress: skips compressing the result if set to True
    """

    copy_logs_and_package(
        target_folder,
        namespace,
        "backups-" + namespace,
        lambda target_log_folder: collect_controldb_backup(
            namespace, target_log_folder
        ),
        namespace,
        skip_compress,
        exclude_dumps=True,
        collect_cluster_logs=False,
    )


def copy_logs(
    namespace,
    target_folder,
    pod_filter=None,
    container_filter=None,
    resource_kind=None,
    resource_name=None,
    skip_compress=False,
    exclude_dumps=False,
    exclude_cluster_info=False,
):
    """
    Copies the log files for each container to the target location
    Filters the pods by the given pod filter if specified.
    Filters the containers by given container filer if specified.
    :param namespace: cluster name
    :param target_folder: target folder
    :param pod_filter: name to use to filter the pods
    :param container_filter: name to use to filter containers
    :param resource_kind: resource kind
    :param resource_name: resource name (used in conjunction with resource_kind) for selecting related k8s resources
    :param skip_compress: skips compressing the result if set to True
    :param exclude_dumps: exclude dumps if set to True
    :param exclude_cluster_info: exclude kubernetes resource snapshots if set to True
    :return:
    """
    display("Collecting the logs for cluster '%s'." % namespace)
    retry(
        validate_namespace,
        namespace,
        retry_count=CONNECTION_RETRY_ATTEMPTS,
        retry_delay=CONNECTION_RETRY_INTERVAL_SECONDS,
        retry_method="validate namespace",
        retry_on_exceptions=(NewConnectionError, MaxRetryError),
    )

    # Copy and package logs
    #
    copy_logs_and_package(
        target_folder,
        namespace,
        "debuglogs-" + namespace,
        lambda target_log_folder: collect_cluster_logs(
            namespace,
            target_log_folder,
            pod_filter,
            container_filter,
            resource_kind,
            resource_name,
        ),
        namespace,
        skip_compress,
        exclude_dumps,
        collect_cluster_logs=True,
    )

    # Copy and package cluster info
    #
    if not exclude_cluster_info:
        copy_logs_and_package(
            target_folder,
            namespace,
            "clusterinfo-" + namespace,
            lambda target_log_folder: collect_cluster_info(
                namespace, target_log_folder, pod_filter, container_filter
            ),
            namespace,
            skip_compress,
            exclude_dumps,
            collect_cluster_logs=False,
        )


def copy_cluster_and_system_logs(
    name,
    target_folder=None,
    pod_filter=None,
    container_filter=None,
    resource_kind=None,
    resource_name=None,
    timeout=None,
    # -- opt in to full visibility unless otherwise instructed --
    skip_compress=False,
    exclude_dumps=False,
    exclude_arcdata_logs=False,
    exclude_system_logs=False,
    exclude_controldb=False,
    exclude_cluster_info=False,
):
    """
    Copy Logs for the given cluster and system cluster
    :param name:
    :param target_folder:
    :param pod_filter:
    :param container_filter:
    :param timeout:
    :param skip_compress: skips compressing the result if set to True
    :param exclude_dumps: exclude dumps if set to True
    :param exclude_arcdata_logs: exclude arc data services logs if set to True
    :param exclude_system_logs: exclude system logs if set to True
    :param exclude_controldb: exclude controller database backup if set to True
    :param exclude_cluster_info: exclude kubernetes resource snapshots if set to True
    :return:
    """
    if target_folder is None:
        default_debug_directory = "logs"
        target_folder = default_debug_directory

    os.makedirs(target_folder, exist_ok=True)

    try:
        # Copy logs for the given cluster.
        #
        if not exclude_arcdata_logs:

            display(f"Collecting logs from namespace '{name}'...")

            copy_logs(
                namespace=name,
                target_folder=target_folder,
                pod_filter=pod_filter,
                container_filter=container_filter,
                resource_kind=resource_kind,
                resource_name=resource_name,
                skip_compress=skip_compress,
                exclude_dumps=exclude_dumps,
                exclude_cluster_info=exclude_cluster_info,
            )

        # Generate and copy controldb backup.
        #
        if not exclude_controldb:
            copy_controldb_backup(
                namespace=name,
                target_folder=target_folder,
                skip_compress=skip_compress,
            )

        # Copy logs for the system cluster if requested. Not filtering any system pod or system container.
        #
        if not exclude_system_logs:
            for system_namespace in [SYSTEM_NAMESPACE, CONNECTEDK8S_NAMESPACE]:
                if name != system_namespace:
                    try:
                        n = k8sClient.CoreV1Api().read_namespace(
                            system_namespace
                        )

                    except k8sClient.rest.ApiException as e:
                        if e.status == HTTPStatus.FORBIDDEN:
                            display(
                                f"Attempt to copy Kubernetes logs from {system_namespace} failed due to insufficient permissions."
                            )
                        if e.status == HTTPStatus.NOT_FOUND:
                            display(
                                f"Attempt to copy Kubernetes logs is skipped due to the namespace {system_namespace} not found."
                            )
                        logger.debug(e)
                        continue

                    display(
                        f"Collecting logs from namespace '{system_namespace}'..."
                    )
                    copy_logs(
                        namespace=system_namespace,
                        target_folder=target_folder,
                        pod_filter=None,
                        container_filter=None,
                        skip_compress=skip_compress,
                        exclude_dumps=exclude_dumps,
                        exclude_cluster_info=exclude_cluster_info,
                    )

    except ClusterLogError as e:
        logger.error(e)
    except TimeoutError:
        logger.error(
            "Couldn't finish collecting logs after %s seconds" % timeout
        )
    except Exception:
        logger.error("Failed to copy cluster logs", exc_info=True)


def copy_debug_logs(
    name,
    target_folder=None,
    pod_filter=None,
    container_filter=None,
    resource_kind=None,
    resource_name=None,
    timeout=None,
    skip_compress=False,
    exclude_dumps=False,
    exclude_arcdata_logs=False,
    exclude_system_logs=False,
    exclude_controldb=False,
    exclude_cluster_info=False,
):
    """
    Wrapper to collect cluster and system logs with timeout as an optional parameter
    :param name:
    :param target_folder:
    :param pod_filter:
    :param container_filter:
    :param timeout:
    :param skip_compress: skips compressing the result if set to True
    :param exclude_dumps: exclude dumps if set to True
    :param exclude_arcdata_logs: exclude arc data services logs if set to True
    :param exclude_system_logs: exclude system logs if set to True
    :param exclude_controldb: exclude controller database backup if set to True
    :param exclude_cluster_info: exclude kubernetes resource snapshots if set to True
    :return:
    """
    if timeout and timeout > 0:
        with_timeout(
            timeout,
            copy_cluster_and_system_logs,
            name,
            target_folder,
            pod_filter,
            container_filter,
            resource_kind,
            resource_name,
            timeout,
            skip_compress,
            exclude_dumps,
            exclude_arcdata_logs,
            exclude_system_logs,
            exclude_controldb,
            exclude_cluster_info,
        )
    else:
        copy_cluster_and_system_logs(
            name,
            target_folder,
            pod_filter,
            container_filter,
            resource_kind,
            resource_name,
            timeout,
            skip_compress,
            exclude_dumps,
            exclude_arcdata_logs,
            exclude_system_logs,
            exclude_controldb,
            exclude_cluster_info,
        )


def take_controller_dump(cluster_name, target_folder):
    """
    Trigger dump for controller
    :param cluster_name:
    :param target_folder:
    :return:
    """
    # define related variables
    #
    log_dir = "/var/opt/controller/log/"
    dump_format = "core.manual.controller.*\.d"
    trigger_dump_script = [
        "/opt/controller/bin/trigger-dump.sh",
        "--program",
        "controller",
    ]
    app_label = "app=controller"
    container_name = "controller"

    # trigger dump
    #
    items = (
        k8sClient.CoreV1Api()
        .list_namespaced_pod(namespace=cluster_name, label_selector=app_label)
        .items
    )
    pod_name = items[0].metadata.name
    response = run_command_within_container(
        cluster_name, pod_name, container_name, trigger_dump_script
    )

    # copy dump into target folder
    #
    m = re.search(log_dir + dump_format, response)
    dump_dir = m.group(0)
    response = copy_file_to_from_container(
        namespace=cluster_name,
        pod_name=pod_name,
        container_name=container_name,
        local_file=target_folder,
        container_file=dump_dir,
        direction="from",
    )
    logger.debug(response)


def take_dump(cluster_name, container_name, target_folder):
    """
    Trigger dump for the given name
    :param cluster_name:
    :param container_name:
    :param target_folder:
    :return:
    """
    retry(
        validate_namespace,
        cluster_name,
        retry_count=CONNECTION_RETRY_ATTEMPTS,
        retry_delay=CONNECTION_RETRY_INTERVAL_SECONDS,
        retry_method="validate namespace",
        retry_on_exceptions=(NewConnectionError, MaxRetryError),
    )

    if container_name == "controller":
        retry(
            take_controller_dump,
            cluster_name,
            target_folder,
            retry_count=CONNECTION_RETRY_ATTEMPTS,
            retry_delay=CONNECTION_RETRY_INTERVAL_SECONDS,
            retry_method="collect dump from controller",
            retry_on_exceptions=(NewConnectionError, MaxRetryError),
        )
    else:
        raise AttributeError(
            "Unknown container name: {name}", name=container_name
        )
