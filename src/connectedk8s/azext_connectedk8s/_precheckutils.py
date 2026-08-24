# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Pre-onboarding diagnostic checks for az connectedk8s connect.

This module runs a short-lived Kubernetes Job ("cluster-diagnostic-checks-job") on the target
cluster BEFORE the actual Arc agent installation. The job validates:
  - DNS resolution (can the cluster resolve required hostnames?)
  - Outbound connectivity (can the cluster reach MCR and ARM endpoints?)
  - Entra (Azure AD) authentication endpoint reachability
  - CRD ownership (are required CRDs free from conflicting Helm releases?)

Results are parsed from the job's container logs and reported via CLI telemetry so we can
track onboarding failure root causes in ADX. If any check fails, the user is warned and
onboarding may be blocked depending on severity.

Flow:
  1. custom.py calls fetch_diagnostic_checks_results()
  2. That function calls executing_cluster_diagnostic_checks_job() to deploy & wait for the Job
  3. Container logs are parsed to determine pass/fail for each check
  4. Telemetry is sent summarizing results (success or failure details)
  5. custom.py decides whether to proceed with agent installation based on the result
"""

from __future__ import annotations

import json
import os
import shutil
from subprocess import PIPE, Popen
from typing import TYPE_CHECKING, Any

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
# pylint: disable=too-many-positional-arguments, consider-using-with
# Precheck flow orchestrates many steps and captures rich diagnostics, so complexity is currently centralized.
# Keep these suppressions local to this module until the precheck workflow is split into smaller units.

# ---------------------------------------------------------------------------
# Module-level state
# These globals track the diagnostic job lifecycle and individual check results.
# They are reset at the start of each fetch_diagnostic_checks_results() call.
# ---------------------------------------------------------------------------
diagnoser_output: list[
    str
] = []  # Collects human-readable log lines for display to the user
prediagnostic_job_execution_status = consts.Job_Status_Not_Started
prediagnostic_dns_check = consts.Diagnostic_Check_Starting
prediagnostic_outbound_check = consts.Diagnostic_Check_Starting
prediagnostic_entra_check = consts.Diagnostic_Check_Starting
prediagnostic_crd_check = consts.Diagnostic_Check_Starting


# ---------------------------------------------------------------------------
# Log parsing helpers
# These parse specific sections of the diagnostic job's container logs.
# ---------------------------------------------------------------------------


def _parse_entra_check_result(entra_check_log: str) -> str:
    """Parse the Entra connectivity check log line and return the check result status.

    The diagnostic container outputs a line like:
      "Entra Authentication Endpoint Connectivity Check Result : https://login.microsoftonline.com : 200"
    A 200 or 404 response means the endpoint is reachable. 404 is expected because the
    diagnostic container curls the base login.microsoftonline.com path without a valid
    tenant/resource URL suffix (e.g. /{tenant-id}/oauth2/v2.0/token), so the server
    returns 404 — but receiving any HTTP response confirms network reachability.
    Any other response code indicates a connectivity failure.
    """
    if not entra_check_log:
        # Entra check not present in logs — older helm chart version, not applicable
        return consts.Diagnostic_Check_Not_Applicable

    # Format: "Entra Authentication Endpoint Connectivity Check Result : <endpoint> : <response_code>"
    parts = entra_check_log.strip().split(" : ")
    if len(parts) >= 3:
        entra_response_code = parts[-1].strip()
        if entra_response_code in ("200", "404"):
            return consts.Diagnostic_Check_Passed
        diagnoser_output.append(
            f"Error: Entra authentication endpoint connectivity check failed. "
            f"Response code: {entra_response_code}. "
            "Please ensure outbound connectivity to the Entra (Azure AD) authentication endpoint.\n"
        )
        return consts.Diagnostic_Check_Failed
    return consts.Diagnostic_Check_Incomplete


def _parse_crd_check_result(crd_check_log: str) -> str:
    """Parse the CRD ownership check log and return the check result status.

    If the diagnostic container detected CRDs owned by a conflicting Helm release,
    it outputs lines containing the CRD_Ownership_Check_Failed_String marker.
    Any such output means CRDs must be cleaned up before onboarding can proceed.
    """
    if crd_check_log:
        diagnoser_output.append(
            f"Error: CRD ownership validation failed.\n{crd_check_log.strip()}"
        )
        return consts.Diagnostic_Check_Failed
    return consts.Diagnostic_Check_Passed


# ---------------------------------------------------------------------------
# Telemetry helpers
# These emit fault events to ADX via the Azure CLI telemetry pipeline.
# Key data is encoded in the fault_type string (whitelisted field) rather than
# in custom properties or long descriptions, which are dropped/rejected.
# ---------------------------------------------------------------------------


def _send_onboarding_telemetry_event(fault_type: str, summary: str) -> None:
    """Send a fault telemetry event with a short summary.

    The fault_type should encode any structured data (check results, component
    names) since it maps to the whitelisted context.default.azurecli.faulttype
    field in ADX. The summary must be short and free of raw JSON to avoid
    pipeline content-validation rejections.
    """
    logger.debug(
        "[Telemetry] faultType=%s summary=%s",
        fault_type,
        summary,
    )
    try:
        raise RuntimeError(summary)
    except RuntimeError as e:
        telemetry.set_exception(
            exception=e,
            fault_type=fault_type,
            summary=summary,
        )


# ---------------------------------------------------------------------------
# Public telemetry functions (called from fetch_diagnostic_checks_results and custom.py)
# ---------------------------------------------------------------------------


def _attach_error_details(components: list[dict[str, Any]]) -> None:
    """Extract error details from diagnoser_output and attach to failed components.

    For each failed component, searches diagnoser_output for lines containing the
    component keyword. Prefers lines also containing 'error' or 'failed', but falls
    back to any matching line. Skips the "Precheck summary:" line (it's metadata,
    not an actionable error detail).
    """
    keyword_map = {
        "dns": "dns",
        "outboundConnectivity": "outbound",
        "entra": "entra",
        "crd": "crd",
    }

    for component in components:
        if component["checkResult"] != consts.Diagnostic_Check_Failed:
            continue
        keyword = keyword_map.get(component["componentName"], "")
        error_lines: list[str] = []
        fallback_lines: list[str] = []
        for line in diagnoser_output:
            # Skip the summary line — it's metadata already encoded in fault_type
            if line.startswith("Precheck summary:"):
                continue
            if keyword.lower() not in line.lower():
                continue
            first_line = line.split("\n")[0].strip()
            if "error" in line.lower() or "failed" in line.lower():
                error_lines.append(first_line)
            else:
                fallback_lines.append(first_line)

        # Use error lines preferentially, fall back to any matching lines
        chosen = (error_lines or fallback_lines)[:3]
        if chosen:
            component["error"] = " ; ".join(chosen)


def send_prediagnostic_job_execution_error_telemetry(reason: str = "") -> None:
    """Send telemetry when prediagnostic job execution fails.

    Encodes the job status into the fault_type so ADX queries can distinguish
    between not-scheduled, not-completed, cleanup-failed, etc. without relying
    on add_extension_event properties (which get stripped by GDPR pipeline).
    """
    # Build structured message for add_extension_event (best-effort, may be stripped)
    msg: dict[str, Any] = {"jobExecutionStatus": prediagnostic_job_execution_status}
    if reason:
        msg["reason"] = reason

    props = {
        consts.Telemetry_Onboarding_Error_Type_Key: consts.Install_Prediagnostics_Job_Execution_Error_Fault_Type,
        consts.Telemetry_Onboarding_Error_Message_Key: json.dumps(msg).replace("'", ""),
    }
    telemetry.add_extension_event("connectedk8s", props)

    # Encode job status into fault_type for ADX visibility
    status_slug = prediagnostic_job_execution_status.replace(" ", "-").lower()
    fault_type = f"prediagnostics-job-{status_slug}"

    # Build a descriptive summary that survives into reserved.datamodel.fault.description
    short_reason = reason[:200] if reason else "no additional details"
    summary = (
        f"Prediagnostic job failed | status={prediagnostic_job_execution_status} | "
        f"reason={short_reason}"
    )
    _send_onboarding_telemetry_event(fault_type, summary)


def send_prediagnostic_check_failure_telemetry(
    dns_check: str, outbound_connectivity_check: str
) -> None:
    """Send telemetry when prediagnostic checks fail (job completed but checks did not pass).

    Emits detailed, per-check error information in the summary field (which survives
    to reserved.datamodel.fault.description in ADX). The fault_type encodes a
    structured pass/fail/na per check for easy KQL filtering.
    """
    # Build generic component list
    components: list[dict[str, Any]] = [
        {"componentName": "dns", "checkResult": dns_check},
        {
            "componentName": "outboundConnectivity",
            "checkResult": outbound_connectivity_check,
        },
        {"componentName": "entra", "checkResult": prediagnostic_entra_check},
        {"componentName": "crd", "checkResult": prediagnostic_crd_check},
    ]

    # Attach structured error details from diagnoser_output
    _attach_error_details(components)

    props = {
        consts.Telemetry_Onboarding_Error_Type_Key: consts.Install_Prediagnostics_Fault_Type,
        consts.Telemetry_Onboarding_Error_Message_Key: json.dumps(components).replace(
            "'", ""
        ),
    }
    telemetry.add_extension_event("connectedk8s", props)

    # Build the encoded fault_type (survives to context.default.azurecli.faulttype)
    def _short(result: str) -> str:
        return {"Passed": "pass", "Failed": "fail", "NotApplicable": "na"}.get(
            result, "incomplete"
        )

    fault_type = (
        f"prediagnostics"
        f"-dns-{_short(dns_check)}"
        f"-outbound-{_short(outbound_connectivity_check)}"
        f"-entra-{_short(prediagnostic_entra_check)}"
        f"-crd-{_short(prediagnostic_crd_check)}"
    )

    # Build a rich summary with per-check errors (survives to reserved.datamodel.fault.description)
    failed_details: list[str] = []
    for comp in components:
        if comp["checkResult"] == consts.Diagnostic_Check_Failed:
            error_msg = comp.get("error", "no error details captured")
            failed_details.append(f"{comp['componentName']}={error_msg}")

    if failed_details:
        # Truncate to 500 chars to stay under any pipeline limits
        details_str = " | ".join(failed_details)[:500]
        summary = f"Prediagnostic check failures: {details_str}"
    else:
        summary = (
            f"Prediagnostic checks failed | "
            f"dns={dns_check} outbound={outbound_connectivity_check} "
            f"entra={prediagnostic_entra_check} crd={prediagnostic_crd_check}"
        )

    _send_onboarding_telemetry_event(fault_type, summary)


def send_post_diagnostic_precheck_failure_telemetry(
    check_name: str, reason: str
) -> None:
    """Send telemetry for individual precheck failures that occur after the diagnostic job."""
    # Build structured message for add_extension_event
    msg = {"checkName": check_name, "reason": reason}

    props = {
        consts.Telemetry_Onboarding_Error_Type_Key: consts.Post_Diagnostic_Precheck_Fault_Type,
        consts.Telemetry_Onboarding_Error_Message_Key: json.dumps(msg).replace("'", ""),
    }
    telemetry.add_extension_event("connectedk8s", props)

    # Also send via set_exception for ADX fault_type encoding
    fault_type = f"{consts.Post_Diagnostic_Precheck_Fault_Type}-{check_name}"
    short_reason = reason[:80] if reason else "unknown"
    _send_onboarding_telemetry_event(
        fault_type,
        f"Post-diagnostic precheck failed: {short_reason}",
    )


def get_precheck_failure_summary() -> str:
    for output in reversed(diagnoser_output):
        if output.startswith("Precheck summary:"):
            return output
    return ""


# ---------------------------------------------------------------------------
# Main entry point — called from custom.py during `az connectedk8s connect`
# ---------------------------------------------------------------------------


def fetch_diagnostic_checks_results(  # pylint: disable=too-many-return-statements
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
    """Run the pre-onboarding diagnostic job and return an aggregate result.

    Returns:
        (result, storage_space_available) where result is one of:
          - Diagnostic_Check_Passed: all checks passed, safe to proceed with onboarding
          - Diagnostic_Check_Failed: at least one check failed, onboarding may be blocked
          - Diagnostic_Check_Incomplete: job didn't run or checks couldn't be determined
    """
    global prediagnostic_job_execution_status, prediagnostic_dns_check, prediagnostic_outbound_check, prediagnostic_entra_check, prediagnostic_crd_check  # pylint: disable=global-statement
    try:
        diagnoser_output.clear()
        prediagnostic_job_execution_status = consts.Job_Status_Not_Started
        prediagnostic_dns_check = consts.Diagnostic_Check_Starting
        prediagnostic_outbound_check = consts.Diagnostic_Check_Starting
        prediagnostic_entra_check = consts.Diagnostic_Check_Starting
        prediagnostic_crd_check = consts.Diagnostic_Check_Starting
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
        if cluster_diagnostic_checks_container_log is None:
            diagnoser_output.append(
                "Precheck summary: "
                f"jobExecutionStatus={prediagnostic_job_execution_status}; "
                f"dnsCheck={prediagnostic_dns_check}; outboundConnectivityCheck={prediagnostic_outbound_check}; "
                f"entraCheck={prediagnostic_entra_check}; crdCheck={prediagnostic_crd_check}"
            )
            send_prediagnostic_job_execution_error_telemetry()
            return consts.Diagnostic_Check_Incomplete, storage_space_available

        if cluster_diagnostic_checks_container_log != "":
            cluster_diagnostic_checks_container_log_list = (
                cluster_diagnostic_checks_container_log.split("\n")
            )
            cluster_diagnostic_checks_container_log_list.pop(-1)
            dns_check_log = ""
            outbound_connectivity_check_log = ""
            entra_check_log = ""
            crd_check_log = ""
            counter_container_logs = 1
            # For retrieving only cluster_diagnostic_checks logs from the output
            for outputs in cluster_diagnostic_checks_container_log_list:
                if consts.Outbound_Connectivity_Check_Result_String in outputs:
                    counter_container_logs = 1
                    if outbound_connectivity_check_log == "":
                        outbound_connectivity_check_log += outputs
                    else:
                        outbound_connectivity_check_log += "  " + outputs
                elif consts.Entra_Connectivity_Check_Result_String in outputs:
                    entra_check_log = outputs
                    counter_container_logs = 1
                elif consts.CRD_Ownership_Check_Failed_String in outputs:
                    crd_check_log += outputs + "\n"
                    counter_container_logs = 1
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
            prediagnostic_dns_check = dns_check
            outbound_connectivity_check, storage_space_available = (
                azext_utils.check_cluster_outbound_connectivity(
                    outbound_connectivity_check_log,
                    filepath_with_timestamp,
                    storage_space_available,
                    diagnoser_output,
                )
            )
            prediagnostic_outbound_check = outbound_connectivity_check

            prediagnostic_entra_check = _parse_entra_check_result(entra_check_log)
            prediagnostic_crd_check = _parse_crd_check_result(crd_check_log)
        else:
            # Empty log — if job didn't complete (e.g., pod never scheduled), treat as Incomplete not Passed
            if prediagnostic_job_execution_status == consts.Job_Status_Not_Completed:
                # Mark all individual checks as NotApplicable since the pod never produced output
                prediagnostic_dns_check = consts.Diagnostic_Check_Not_Applicable
                prediagnostic_outbound_check = consts.Diagnostic_Check_Not_Applicable
                prediagnostic_entra_check = consts.Diagnostic_Check_Not_Applicable
                prediagnostic_crd_check = consts.Diagnostic_Check_Not_Applicable
                diagnoser_output.append(
                    "Precheck summary: "
                    f"jobExecutionStatus={prediagnostic_job_execution_status}; "
                    f"dnsCheck={prediagnostic_dns_check}; outboundConnectivityCheck={prediagnostic_outbound_check}; "
                    f"entraCheck={prediagnostic_entra_check}; crdCheck={prediagnostic_crd_check}"
                )
                send_prediagnostic_job_execution_error_telemetry()
                return consts.Diagnostic_Check_Incomplete, storage_space_available
            return consts.Diagnostic_Check_Passed, storage_space_available

        # If any of the check remain Incomplete than we will return Incomplete
        if consts.Diagnostic_Check_Incomplete in (
            dns_check,
            outbound_connectivity_check,
        ):
            diagnoser_output.append(
                "Precheck summary: "
                f"jobExecutionStatus={prediagnostic_job_execution_status}; "
                f"dnsCheck={dns_check}; outboundConnectivityCheck={outbound_connectivity_check}"
            )
            return consts.Diagnostic_Check_Incomplete, storage_space_available

        diagnoser_output.append(
            "Precheck summary: "
            f"jobExecutionStatus={prediagnostic_job_execution_status}; "
            f"dnsCheck={dns_check}; outboundConnectivityCheck={outbound_connectivity_check}; "
            f"entraCheck={prediagnostic_entra_check}; crdCheck={prediagnostic_crd_check}"
        )

        # Return Incomplete if any mandatory check couldn't be determined
        if (
            dns_check == consts.Diagnostic_Check_Incomplete
            or outbound_connectivity_check == consts.Diagnostic_Check_Incomplete
            or prediagnostic_entra_check == consts.Diagnostic_Check_Incomplete
        ):
            return consts.Diagnostic_Check_Incomplete, storage_space_available

        # Return Failed only if at least one check actually failed
        if (
            dns_check == consts.Diagnostic_Check_Failed
            or outbound_connectivity_check == consts.Diagnostic_Check_Failed
            or prediagnostic_entra_check == consts.Diagnostic_Check_Failed
            or prediagnostic_crd_check == consts.Diagnostic_Check_Failed
        ):
            send_prediagnostic_check_failure_telemetry(
                dns_check, outbound_connectivity_check
            )
            return consts.Diagnostic_Check_Failed, storage_space_available

        # If the job did not complete, partial results cannot be trusted -- treat as Incomplete.
        # The container may have exited early, causing some checks to appear
        # Passed/NotApplicable while later checks never actually executed.
        if prediagnostic_job_execution_status == consts.Job_Status_Not_Completed:
            send_prediagnostic_job_execution_error_telemetry()
            return consts.Diagnostic_Check_Incomplete, storage_space_available

        # All checks passed or not applicable
        return consts.Diagnostic_Check_Passed, storage_space_available

    # To handle any exception that may occur during the execution
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.exception(
            "An exception has occured while trying to execute cluster diagnostic checks "
            "container on the cluster."
        )
        send_prediagnostic_job_execution_error_telemetry(reason=str(e))
        telemetry.set_exception(
            exception=e,
            fault_type=consts.Cluster_Diagnostic_Checks_Execution_Failed_Fault_Type,
            summary="Error occured while executing the cluster diagnostic checks container",
        )

    return consts.Diagnostic_Check_Incomplete, storage_space_available


# ---------------------------------------------------------------------------
# Job execution — deploys the diagnostic helm chart, watches the Job, fetches logs
# ---------------------------------------------------------------------------


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
    """Deploy the diagnostic checks helm chart, wait for the Job to complete, and return logs.

    Returns:
        - Container log string if the job ran (may be empty if pod produced no output)
        - None if the job could not be scheduled or cleanup of a stale release failed
    """
    global prediagnostic_job_execution_status  # pylint: disable=global-statement
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
        prediagnostic_job_execution_status = consts.Job_Status_Running
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
                    prediagnostic_job_execution_status = (
                        consts.Job_Status_Cleanup_Failed
                    )
                    logger.warning(
                        "Cleanup of previous diagnostic checks helm release failed and hence couldn't "
                        'install the new helm release. Please cleanup older release using "helm delete '
                        'cluster-diagnostic-checks -n azure-arc-release" and try onboarding again'
                    )
                    telemetry.set_exception(
                        exception=Exception(error_kubectl_delete_helm.decode("ascii")),
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

        logger.debug(
            "Step: %s: Chart path for Cluster Diagnostic Checks Job: %s",
            azext_utils.get_utctimestring(),
            chart_path,
        )
        logger.debug(
            "Step: %s: Creating Cluster Diagnostic Checks job",
            azext_utils.get_utctimestring(),
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
            mcr_url,
        )

        # Watch the Job for up to 60s waiting for it to reach Complete or Failed (3 retries) state
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
            except (KeyError, AttributeError, TypeError):
                logger.debug(
                    "Caught Exception, executing Cluster Diagnostic Checks job: ",
                    exc_info=True,
                )
                continue

        # --- Post-watch: handle the three possible outcomes ---
        # 1. Job not completed → save pod description for debugging
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

        # 2. Job never scheduled (pod couldn't be created) → cleanup and return None
        if is_job_scheduled is False:
            prediagnostic_job_execution_status = consts.Job_Status_Not_Scheduled
            telemetry.set_exception(
                exception="Could not schedule Cluster Diagnostic Checks Job in the cluster",
                fault_type=consts.Cluster_Diagnostic_Checks_Job_Not_Scheduled,
                summary="Could not schedule Cluster Diagnostic Checks Job in the cluster",
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

        # 3. Job was scheduled but didn't complete (e.g. OOMKilled, timeout) → fetch partial logs
        if is_job_complete is False:
            prediagnostic_job_execution_status = consts.Job_Status_Not_Completed
            # Job was scheduled successfully, but didn't complete. We will fetch the logs and delete helm release.
            logger.debug(
                "Cluster Diagnostic Checks Job Failed.  Fetch results and delete Helm release in the cluster"
            )

            # Fetching the cluster diagnostic checks Container logs
            all_pods = corev1_api_instance.list_namespaced_pod("azure-arc-release")
            # Pick the pod with the latest creation time to avoid reading stale logs from old pods
            matching_pods = [
                p for p in all_pods.items if p.metadata.name.startswith(job_name)
            ]
            matching_pods.sort(
                key=lambda p: p.metadata.creation_timestamp, reverse=True
            )
            if matching_pods:
                each_pod = matching_pods[0]
                # Fetching the current Pod name and creating a folder with that name inside the timestamp folder
                pod_name = each_pod.metadata.name

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
                        with open(dns_check_path, "w+", encoding="utf-8") as f:
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
                except (ValueError, TypeError) as e:
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
                exception="Could not complete Cluster Diagnostic Checks Job after scheduling in the cluster",
                fault_type=consts.Cluster_Diagnostic_Checks_Job_Not_Complete,
                summary="Could not complete Cluster Diagnostic Checks Job after scheduling in the cluster",
            )
            logger.warning(
                "Cluster diagnostics job didn't reach completed state in the kubernetes cluster. The "
                "possible reasons can be resource constraints on the cluster.\n"
            )

        # 4. Job completed successfully → fetch logs for result parsing
        if is_job_complete:
            all_pods = corev1_api_instance.list_namespaced_pod("azure-arc-release")
            # Pick the pod with the latest creation time to avoid reading stale logs from old pods
            matching_pods = [
                p for p in all_pods.items if p.metadata.name.startswith(job_name)
            ]
            matching_pods.sort(
                key=lambda p: p.metadata.creation_timestamp, reverse=True
            )
            if matching_pods:
                each_pod = matching_pods[0]
                pod_name = each_pod.metadata.name
                try:
                    cluster_diagnostic_checks_container_log = (
                        corev1_api_instance.read_namespaced_pod_log(
                            name=pod_name,
                            container="cluster-diagnostic-checks-container",
                            namespace="azure-arc-release",
                        )
                    )
                    if storage_space_available:
                        log_path = os.path.join(
                            filepath_with_timestamp,
                            "cluster_diagnostic_checks_job_log.txt",
                        )
                        with open(log_path, "w+") as f:
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
                except Exception:  # pylint: disable=broad-exception-caught
                    logger.exception(
                        "An exception has occured while saving the Cluster "
                        "Diagnostic Checks Job logs in the local machine."
                    )

        # Clearing all the resources after fetching the cluster diagnostic checks container logs
        Popen(cmd_helm_delete, stdout=PIPE, stderr=PIPE)

    # To handle any exception that may occur during the execution
    except Exception as e:  # pylint: disable=broad-exception-caught
        prediagnostic_job_execution_status = consts.Job_Status_Execution_Failed
        Popen(cmd_helm_delete, stdout=PIPE, stderr=PIPE)
        raise CLIInternalError(
            f"Failed to execute Cluster Diagnostic Checks Job: {e}"
        ) from e
    if is_job_complete:
        prediagnostic_job_execution_status = consts.Job_Status_Completed
    logger.debug(cluster_diagnostic_checks_container_log)
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
    mcr_url: str,
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
    cmd_helm_install.extend(["--set", f"global.mcrRepository={mcr_url}"])
    cmd_helm_install.extend(["--set", f"global.image.registry={mcr_url}"])
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
        error = azext_utils.process_helm_error_detail(error)
        if "forbidden" in error or "timed out waiting for the condition" in error:
            telemetry.set_user_fault()

        telemetry.set_exception(
            exception=Exception(error),
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
                with open(
                    cli_output_logger_path, "w+", encoding="utf-8"
                ) as cli_output_writer:
                    for output in diagnoser_output:
                        cli_output_writer.write(output + "\n")
                    # If flag is 0 that means that process was terminated using the Keyboard Interrupt so adding that
                    # also to the text file
                    if flag == 0:
                        cli_output_writer.write("Process terminated externally.\n")

            # If no issues was found during the whole troubleshoot execution
            elif flag:
                with open(
                    cli_output_logger_path, "w+", encoding="utf-8"
                ) as cli_output_writer:
                    cli_output_writer.write(
                        "The diagnoser didn't find any issues on the cluster.\n"
                    )
            # If process was terminated by user
            else:
                with open(
                    cli_output_logger_path, "w+", encoding="utf-8"
                ) as cli_output_writer:
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
    except (ValueError, TypeError) as e:
        logger.exception(
            "An exception has occured while trying to store the diagnoser results."
        )
        telemetry.set_exception(
            exception=e,
            fault_type=consts.Diagnoser_Result_Fault_Type,
            summary="Error while storing the diagnoser results",
        )

    return consts.Diagnostic_Check_Failed
