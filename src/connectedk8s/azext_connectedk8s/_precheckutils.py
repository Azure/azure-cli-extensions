# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import annotations

import os
import shutil
from subprocess import PIPE, Popen
from typing import TYPE_CHECKING

from azure.cli.core import telemetry
from azure.cli.core.azclierror import (
    CLIInternalError,
)
from knack.log import get_logger
from kubernetes import config, watch

import azext_connectedk8s._constants as consts
import azext_connectedk8s._utils as azext_utils

if TYPE_CHECKING:
    from knack.commands import CLICommand
    from kubernetes.client import BatchV1Api, CoreV1Api

logger = get_logger(__name__)
# pylint: disable=unused-argument, too-many-locals, too-many-branches, too-many-statements, line-too-long
# pylint: disable

diagnoser_output: list[str] = []


def fetch_diagnostic_checks_results(
    cmd: CLICommand,
    corev1_api_instance: CoreV1Api,
    batchv1_api_instance: BatchV1Api,
    helm_client_location: str,
    kubectl_client_location: str,
    kube_config: str | None,
    kube_context: str | None,
    location: str | None,
    http_proxy: str,
    https_proxy: str,
    no_proxy: str,
    proxy_cert: str,
    azure_cloud: str,
    filepath_with_timestamp: str,
    storage_space_available: bool,
) -> tuple[str, bool]:
    try:
        # Setting DNS and Outbound Check as working
        dns_check = "Starting"
        outbound_connectivity_check = "Starting"
        # Executing the cluster_diagnostic_checks job and fetching the logs obtained
        cluster_diagnostic_checks_container_log = (
            executing_cluster_diagnostic_checks_job(
                cmd,
                corev1_api_instance,
                batchv1_api_instance,
                helm_client_location,
                kubectl_client_location,
                kube_config,
                kube_context,
                location,
                http_proxy,
                https_proxy,
                no_proxy,
                proxy_cert,
                azure_cloud,
                filepath_with_timestamp,
                storage_space_available,
            )
        )
        # If cluster_diagnostic_checks_container_log is not empty there were errors.  Try to read the logs.
        if (
            cluster_diagnostic_checks_container_log is not None
            and cluster_diagnostic_checks_container_log != ""
        ):
            cluster_diagnostic_checks_container_log_list = (
                cluster_diagnostic_checks_container_log.split("\n")
            )
            cluster_diagnostic_checks_container_log_list.pop(-1)
            dns_check_log = ""
            outbound_connectivity_check_log = ""
            counter_container_logs = 1
            # For retrieving only cluster_diagnostic_checks logs from the output
            for outputs in cluster_diagnostic_checks_container_log_list:
                if consts.Outbound_Connectivity_Check_Result_String in outputs:
                    counter_container_logs = 1
                    if outbound_connectivity_check_log == "":
                        outbound_connectivity_check_log += outputs
                    else:
                        outbound_connectivity_check_log += "  " + outputs
                elif consts.DNS_Check_Result_String in outputs:
                    dns_check_log += outputs
                    counter_container_logs = 0
                elif counter_container_logs == 0:
                    dns_check_log += "  " + outputs
            dns_check, storage_space_available = azext_utils.check_cluster_DNS(
                dns_check_log,
                filepath_with_timestamp,
                storage_space_available,
                diagnoser_output,
            )
            outbound_connectivity_check, storage_space_available = (
                azext_utils.check_cluster_outbound_connectivity(
                    outbound_connectivity_check_log,
                    filepath_with_timestamp,
                    storage_space_available,
                    diagnoser_output,
                )
            )
        else:
            return consts.Diagnostic_Check_Passed, storage_space_available

        # If any of the check remain Incomplete than we will return Incomplete
        if (
            dns_check == consts.Diagnostic_Check_Incomplete
            or outbound_connectivity_check == consts.Diagnostic_Check_Incomplete
        ):
            return consts.Diagnostic_Check_Incomplete, storage_space_available

        return consts.Diagnostic_Check_Failed, storage_space_available

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.exception(
            "An exception has occured while trying to execute cluster diagnostic checks "
            "container on the cluster."
        )
        telemetry.set_exception(
            exception=e,
            fault_type=consts.Cluster_Diagnostic_Checks_Execution_Failed_Fault_Type,
            summary="Error occured while executing the cluster diagnostic checks container",
        )

    return consts.Diagnostic_Check_Incomplete, storage_space_available


def executing_cluster_diagnostic_checks_job(
    cmd: CLICommand,
    corev1_api_instance: CoreV1Api,
    batchv1_api_instance: BatchV1Api,
    helm_client_location: str,
    kubectl_client_location: str,
    kube_config: str | None,
    kube_context: str | None,
    location: str | None,
    http_proxy: str,
    https_proxy: str,
    no_proxy: str,
    proxy_cert: str,
    azure_cloud: str,
    filepath_with_timestamp: str,
    storage_space_available: bool,
) -> str | None:
    job_name = "cluster-diagnostic-checks-job"
    # Setting the log output as Empty
    cluster_diagnostic_checks_container_log = ""
    release_namespace = azext_utils.get_release_namespace(
        kube_config, kube_context, helm_client_location, "cluster-diagnostic-checks"
    )
    cmd_helm_delete = [
        helm_client_location,
        "delete",
        "cluster-diagnostic-checks",
        "-n",
        "azure-arc-release",
    ]
    if kube_config:
        cmd_helm_delete.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_delete.extend(["--kube-context", kube_context])

    # To handle the user keyboard Interrupt
    try:
        # Executing the Cluster Diagnostic Checks Job yaml
        config.load_kube_config(kube_config, kube_context)
        # checking existence of the release and if present we delete the stale release
        if release_namespace is not None:
            # Attempting deletion of cluster diagnostic checks resources to handle the scenario if any stale
            # resources are present
            response_kubectl_delete_helm = Popen(
                cmd_helm_delete, stdout=PIPE, stderr=PIPE
            )
            _, error_kubectl_delete_helm = response_kubectl_delete_helm.communicate()
            # If any error occured while execution of delete command
            if response_kubectl_delete_helm.returncode != 0:
                # Converting the string of multiple errors to list
                error_msg_list = error_kubectl_delete_helm.decode("ascii").split("\n")
                error_msg_list.pop(-1)
                valid_exception_list = []
                # Checking if any exception occured or not
                exception_occured_counter = 0
                for ind_errors in error_msg_list:
                    if "not found" in ind_errors or "deleted" in ind_errors:
                        pass
                    else:
                        valid_exception_list.append(ind_errors)
                        exception_occured_counter = 1
                # If any exception occured we will print the exception and return
                if exception_occured_counter == 1:
                    logger.warning(
                        "Cleanup of previous diagnostic checks helm release failed and hence couldn't "
                        'install the new helm release. Please cleanup older release using "helm delete '
                        'cluster-diagnostic-checks -n azure-arc-release" and try onboarding again'
                    )
                    telemetry.set_exception(
                        exception=error_kubectl_delete_helm.decode("ascii"),
                        fault_type=consts.Cluster_Diagnostic_Checks_Release_Cleanup_Failed,
                        summary="Error while executing Cluster Diagnostic Checks Job",
                    )
                    return None

        mcr_url = azext_utils.get_mcr_path(cmd.cli_ctx.cloud.endpoints.active_directory)

        chart_path = azext_utils.get_chart_path(
            f"{mcr_url}/{consts.Cluster_Diagnostic_Checks_Job_Registry_Path}",
            kube_config,
            kube_context,
            helm_client_location,
            consts.Pre_Onboarding_Helm_Charts_Folder_Name,
            consts.Pre_Onboarding_Helm_Charts_Release_Name,
            False,
        )

        print(
            f"Step: {azext_utils.get_utctimestring()}: Chart path for Cluster Diagnostic Checks Job: {chart_path}"
        )
        print(
            f"Step: {azext_utils.get_utctimestring()}: Creating Cluster Diagnostic Checks job"
        )
        helm_install_release_cluster_diagnostic_checks(
            chart_path,
            location,
            http_proxy,
            https_proxy,
            no_proxy,
            proxy_cert,
            azure_cloud,
            kube_config,
            kube_context,
            helm_client_location,
        )

        # Watching for cluster diagnostic checks container to reach in completed stage
        w = watch.Watch()
        is_job_complete = False
        is_job_scheduled = False
        # To watch for changes in pods' states till it reach completed state or exit if it takes more than 180 seconds
        for job in w.stream(
            batchv1_api_instance.list_namespaced_job,
            namespace="azure-arc-release",
            label_selector="",
            timeout_seconds=60,
        ):
            logger.debug(
                "Watching Cluster Diagnostic Checks Job to reach completed state"
            )
            try:
                # Checking if job get scheduled or not
                if job["object"].metadata.name == "cluster-diagnostic-checks-job":
                    is_job_scheduled = True

                    if (
                        job["object"].status.failed is not None
                        and job["object"].status.failed >= 3
                    ):
                        logger.debug("Cluster Diagnostic Checks job Failed")
                        w.stop()
                        break

                    if job["object"].status.conditions is None:
                        continue

                    is_complete = any(
                        condition.type == "Complete"
                        for condition in job["object"].status.conditions
                    )
                    if is_complete:
                        is_job_complete = True
                        logger.debug(
                            "Cluster Diagnostic Checks Job reached completed state"
                        )
                        w.stop()
            except Exception:
                logger.debug(
                    "Caught Exception, executing Cluster Diagnostic Checks job: ",
                    exc_info=True,
                )
                continue

        # If job is not completed then we will save the pod description for debugging
        if is_job_complete is False:
            logger.debug(
                "Saving Pod Description of Cluster Diagnostic Checks Job at: %s",
                filepath_with_timestamp,
            )
            azext_utils.save_cluster_diagnostic_checks_pod_description(
                corev1_api_instance,
                kubectl_client_location,
                kube_config,
                kube_context,
                filepath_with_timestamp,
                storage_space_available,
            )

        # If job is not scheduled then we will delete the helm release
        if is_job_scheduled is False:
            telemetry.set_exception(
                exception="Couldn't schedule Cluster Diagnostic Checks Job in the cluster",
                fault_type=consts.Cluster_Diagnostic_Checks_Job_Not_Scheduled,
                summary="Couldn't schedule Cluster Diagnostic Checks Job in the cluster",
            )
            logger.warning(
                "Unable to schedule the Cluster Diagnostic Checks Job in the kubernetes cluster. The "
                "possible reasons can be presence of a security policy or security context constraint "
                "(SCC) or it may happen becuase of lack of ResourceQuota.\n"
            )
            logger.debug(
                "Cluster diagnostic Job couldn't be scheduled.  Deleting the helm release in the cluster"
            )
            Popen(cmd_helm_delete, stdout=PIPE, stderr=PIPE)
            return None

        if is_job_complete is False:
            # Job was scheduled successfully, but didn't complete. We will fetch the logs and delete helm release.
            logger.debug(
                "Cluster Diagnostic Checks Job Failed.  Fetch results and delete Helm release in the cluster"
            )

            # Fetching the cluster diagnostic checks Container logs
            all_pods = corev1_api_instance.list_namespaced_pod("azure-arc-release")
            # Traversing through all agents
            for each_pod in all_pods.items:
                # Fetching the current Pod name and creating a folder with that name inside the timestamp folder
                pod_name = each_pod.metadata.name
                if not pod_name.startswith(job_name):
                    continue

                # Creating a text file with the name of the container and adding that containers logs in it
                cluster_diagnostic_checks_container_log = (
                    corev1_api_instance.read_namespaced_pod_log(
                        name=pod_name,
                        container="cluster-diagnostic-checks-container",
                        namespace="azure-arc-release",
                    )
                )
                try:
                    if storage_space_available:
                        dns_check_path = os.path.join(
                            filepath_with_timestamp,
                            "cluster_diagnostic_checks_job_log.txt",
                        )
                        with open(dns_check_path, "w+") as f:
                            f.write(cluster_diagnostic_checks_container_log)
                except OSError as e:
                    if "[Errno 28]" in str(e):
                        storage_space_available = False
                        telemetry.set_exception(
                            exception=e,
                            fault_type=consts.No_Storage_Space_Available_Fault_Type,
                            summary="No space left on device",
                        )
                        shutil.rmtree(filepath_with_timestamp, ignore_errors=False)
                    else:
                        logger.exception(
                            "An exception has occured while saving the Cluster "
                            "Diagnostic Checks Job logs in the local machine."
                        )
                        telemetry.set_exception(
                            exception=e,
                            fault_type=consts.Cluster_Diagnostic_Checks_Job_Log_Save_Failed,
                            summary="Error occured while saving the cluster diagnostic "
                            "checks job logs in the local machine",
                        )

                # To handle any exception that may occur during the execution
                except Exception as e:
                    logger.exception(
                        "An exception has occured while saving the Cluster "
                        "Diagnostic Checks Job logs in the local machine."
                    )
                    telemetry.set_exception(
                        exception=e,
                        fault_type=consts.Cluster_Diagnostic_Checks_Job_Log_Save_Failed,
                        summary="Error occured while saving the cluster diagnostic checks "
                        "job logs in the local machine",
                    )

            telemetry.set_exception(
                exception="Couldn't complete Cluster Diagnostic Checks Job after scheduling in the cluster",
                fault_type=consts.Cluster_Diagnostic_Checks_Job_Not_Complete,
                summary="Couldn't complete Cluster Diagnostic Checks Job after scheduling in the cluster",
            )
            logger.warning(
                "Cluster diagnostics job didn't reach completed state in the kubernetes cluster. The "
                "possible reasons can be resource constraints on the cluster.\n"
            )

        # Clearing all the resources after fetching the cluster diagnostic checks container logs
        Popen(cmd_helm_delete, stdout=PIPE, stderr=PIPE)

    # To handle any exception that may occur during the execution
    except Exception as e:
        Popen(cmd_helm_delete, stdout=PIPE, stderr=PIPE)
        raise CLIInternalError(f"Failed to execute Cluster Diagnostic Checks Job: {e}")

    return cluster_diagnostic_checks_container_log


def helm_install_release_cluster_diagnostic_checks(
    chart_path: str,
    location: str | None,
    http_proxy: str,
    https_proxy: str,
    no_proxy: str,
    proxy_cert: str,
    azure_cloud: str,
    kube_config: str | None,
    kube_context: str | None,
    helm_client_location: str,
    onboarding_timeout: str = "60",
) -> None:
    cmd_helm_install = [
        helm_client_location,
        "upgrade",
        "--install",
        "cluster-diagnostic-checks",
        chart_path,
        "--namespace",
        f"{consts.Release_Install_Namespace}",
        "--create-namespace",
        "--output",
        "json",
    ]
    # To set some other helm parameters through file
    cmd_helm_install.extend(["--set", f"global.location={location}"])
    cmd_helm_install.extend(["--set", f"global.azureCloud={azure_cloud}"])
    if https_proxy:
        cmd_helm_install.extend(["--set", f"global.httpsProxy={https_proxy}"])
    if http_proxy:
        cmd_helm_install.extend(["--set", f"global.httpProxy={http_proxy}"])
    if no_proxy:
        cmd_helm_install.extend(["--set", f"global.noProxy={no_proxy}"])
    if proxy_cert:
        cmd_helm_install.extend(["--set-file", f"global.proxyCert={proxy_cert}"])

    if kube_config:
        cmd_helm_install.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_install.extend(["--kube-context", kube_context])

    # Change --timeout format for helm client to understand
    onboarding_timeout = onboarding_timeout + "s"
    cmd_helm_install.extend(["--wait", "--timeout", f"{onboarding_timeout}"])

    response_helm_install = Popen(cmd_helm_install, stdout=PIPE, stderr=PIPE)
    _, error_helm_install = response_helm_install.communicate()
    if response_helm_install.returncode != 0:
        error = error_helm_install.decode("ascii")
        if "forbidden" in error or "timed out waiting for the condition" in error:
            telemetry.set_user_fault()

        telemetry.set_exception(
            exception=error,
            fault_type=consts.Cluster_Diagnostic_Checks_Helm_Install_Failed_Fault_Type,
            summary="Unable to install cluster diagnostic checks helm release",
        )
        raise CLIInternalError(
            f"Unable to install cluster diagnostic checks helm release: {error}"
        )


def fetching_cli_output_logs(
    filepath_with_timestamp: str, storage_space_available: bool, flag: int
) -> str:
    # This function is used to store the output that is obtained throughout the Diagnoser process

    try:
        # If storage space is available then only we store the output
        if storage_space_available:
            # Path to store the diagnoser results
            cli_output_logger_path = os.path.join(
                filepath_with_timestamp, consts.Diagnoser_Results
            )
            # If any results are obtained during the process than we will add it to the text file.
            if len(diagnoser_output) > 0:
                with open(cli_output_logger_path, "w+") as cli_output_writer:
                    for output in diagnoser_output:
                        cli_output_writer.write(output + "\n")
                    # If flag is 0 that means that process was terminated using the Keyboard Interrupt so adding that
                    # also to the text file
                    if flag == 0:
                        cli_output_writer.write("Process terminated externally.\n")

            # If no issues was found during the whole troubleshoot execution
            elif flag:
                with open(cli_output_logger_path, "w+") as cli_output_writer:
                    cli_output_writer.write(
                        "The diagnoser didn't find any issues on the cluster.\n"
                    )
            # If process was terminated by user
            else:
                with open(cli_output_logger_path, "w+") as cli_output_writer:
                    cli_output_writer.write("Process terminated externally.\n")

        return consts.Diagnostic_Check_Passed

    # For handling storage or OS exception that may occur during the execution
    except OSError as e:
        if "[Errno 28]" in str(e):
            storage_space_available = False
            telemetry.set_exception(
                exception=e,
                fault_type=consts.No_Storage_Space_Available_Fault_Type,
                summary="No space left on device",
            )
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False)

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.exception(
            "An exception has occured while trying to store the diagnoser results."
        )
        telemetry.set_exception(
            exception=e,
            fault_type=consts.Diagnoser_Result_Fault_Type,
            summary="Error while storing the diagnoser results",
        )

    return consts.Diagnostic_Check_Failed
