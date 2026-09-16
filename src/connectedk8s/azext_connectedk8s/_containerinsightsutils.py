# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Container Insights proxy bypass for az connectedk8s connect/update/delete.

The Container Insights agent (ama-logs) does not read the proxy settings held by the Arc
agents. It is configured through the "container-azm-ms-agentconfig" ConfigMap in the
"kube-system" namespace, where "ignore_proxy_settings" under [agent_settings.proxy_config]
tells it to bypass the proxy.

The bypass is therefore cluster state, not an agent proxy setting, and is driven by its own
parameters rather than by --proxy-skip-range. Nothing here reads or writes no_proxy.

Flow:
  1. --add-proxy-bypass <extension type> on connect/update requests the bypass;
     --clear-proxy-bypass on update withdraws it
  2. sync_container_insights_proxy_bypass_configmap() dispatches on that answer, so connect
     and update cannot drift apart:
       - requested     -> ensure_container_insights_proxy_bypass_configmap() writes the
                          setting, creating the ConfigMap only if it does not already exist
       - not requested -> remove_container_insights_proxy_bypass_configmap() undoes a setting
                          added by an earlier run, identified by the annotation this CLI stamps
  3. delete calls remove_container_insights_proxy_bypass_configmap() directly, as does
     connect when it clears a stale bypass left by an earlier onboarding
  4. Every call runs before the step it protects, so a failure stops the command instead of
     leaving the agents and the ConfigMap out of step

Only the "ignore_proxy_settings" line is ever written, and the bypass is withdrawn by setting it
to "false". That happens only where the annotation shows this CLI added it, so settings the
customer owns are left alone.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from knack.log import get_logger
from kubernetes import client as kube_client
from kubernetes.client.rest import ApiException

import azext_connectedk8s._constants as consts
import azext_connectedk8s._errors as errors
import azext_connectedk8s._utils as utils

if TYPE_CHECKING:
    from knack.commands import CLICommand

logger = get_logger(__name__)


def find_active_proxy_bypass_setting(lines: list[str]) -> tuple[int | None, int | None]:
    # Find the active ignore_proxy_settings line inside [agent_settings.proxy_config]. The
    # setting is scoped to that section, so a match anywhere else is not a proxy bypass.
    # Returns its header and index, or the first proxy_config header when the setting is absent.
    first_header: int | None = None
    current_header: int | None = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        # Track which section the following settings belong to.
        if stripped.startswith("["):
            in_section = "".join(stripped.split()).startswith(
                consts.CI_ConfigMap_Proxy_Config_Section
            )
            current_header = i if in_section else None
            if in_section and first_header is None:
                first_header = i
            continue
        if current_header is not None and stripped.startswith(
            consts.CI_ConfigMap_Proxy_Bypass_Setting
        ):
            return current_header, i

    return first_header, None


def merge_proxy_bypass_into_agent_settings(agent_settings: str) -> str:
    # Set ignore_proxy_settings to "true" in place, leaving the agent's other settings intact.
    lines = agent_settings.splitlines()
    header, setting = find_active_proxy_bypass_setting(lines)

    # An existing active setting is forced to "true".
    if setting is not None:
        line = lines[setting]
        enabled = consts.CI_ConfigMap_Proxy_Bypass_Enabled.replace(" ", "")
        if line.strip().replace(" ", "").startswith(enabled):
            return agent_settings
        indent = line[: len(line) - len(line.lstrip())]
        lines[setting] = f"{indent}{consts.CI_ConfigMap_Proxy_Bypass_Enabled}"
        return "\n".join(lines)

    # No active setting: add it under an existing active proxy_config header if present.
    if header is not None:
        lines.insert(header + 1, f"    {consts.CI_ConfigMap_Proxy_Bypass_Enabled}")
        return "\n".join(lines)

    # Otherwise append a fresh proxy_config section.
    block = consts.CI_ConfigMap_Proxy_Bypass_Block
    if not agent_settings.strip():
        return block
    return agent_settings.rstrip("\n") + "\n" + block


def remove_proxy_bypass_from_agent_settings(agent_settings: str) -> str:
    # Withdraw the bypass by setting ignore_proxy_settings to "false", leaving the agent's other
    # settings intact.
    lines = agent_settings.splitlines()
    _, setting = find_active_proxy_bypass_setting(lines)

    # Nothing to undo unless proxy_config holds an active setting.
    if setting is None:
        return agent_settings

    line = lines[setting]
    indent = line[: len(line) - len(line.lstrip())]
    lines[setting] = f"{indent}{consts.CI_ConfigMap_Proxy_Bypass_Disabled}"
    return "\n".join(lines)


def report_container_insights_configmap_failure(
    e: Exception,
    error: errors.ArcError,
    operation: str,
    raise_on_failure: bool = True,
    error_message: str = consts.CI_ConfigMap_Error_Message,
    warning_message: str = consts.CI_ConfigMap_Removal_Failed_Warning,
    cmd: CLICommand | None = None,
) -> None:
    # True raises so the command stops here; False logs a warning and returns.
    if not raise_on_failure:
        logger.warning(warning_message)
        logger.debug("Kubernetes Exception: ", exc_info=True)
        utils.report_connectedk8s_diagnostic(
            cmd, error, exception=e, operation=operation, details=str(e)
        )
        return

    # Mirrors kubernetes_exception_handler, so the likely cause is still named before failing.
    if isinstance(e, ApiException):
        if e.status == 403:
            logger.warning(consts.CI_ConfigMap_Unauthorized_Message)
        elif e.status == 404:
            logger.warning(consts.CI_ConfigMap_Not_Found_Message)
        else:
            logger.debug("Kubernetes Exception: ", exc_info=True)
        details = f"{error_message}\nError Response: {e.body}"
    else:
        details = f"{error_message}\nError: {e}"

    raise utils.report_connectedk8s_error(
        cmd,
        error,
        exception=e,
        user_fault=True,
        operation=operation,
        details=details,
    ) from e


def ensure_container_insights_proxy_bypass_configmap(
    api_instance: kube_client.CoreV1Api,
    cmd: CLICommand | None = None,
) -> None:
    # Create the ConfigMap when absent, otherwise merge the bypass into the existing one.
    # Runs before the cluster resource and the helm upgrade, so a failure stops the command.
    print(
        f"Step: {utils.get_utctimestring()}: Ensuring '{consts.CI_ConfigMap_Name}' ConfigMap "
        f"in '{consts.CI_ConfigMap_Namespace}' namespace bypasses the proxy for Container Insights"
    )

    try:
        existing = api_instance.read_namespaced_config_map(
            name=consts.CI_ConfigMap_Name,
            namespace=consts.CI_ConfigMap_Namespace,
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        # An absent ConfigMap is not a failure; it is created with just the bypass setting.
        if getattr(e, "status", None) == 404:
            create_container_insights_proxy_bypass_configmap(api_instance, cmd=cmd)
            return
        report_container_insights_configmap_failure(
            e,
            errors.CONFIGMAP_READ_FAILED,
            "read",
            cmd=cmd,
        )
        return

    # Merge the bypass into the existing agent-settings, keeping all other settings.
    data = existing.data or {}
    current = data.get(consts.CI_ConfigMap_Agent_Settings_Key, "")
    merged = merge_proxy_bypass_into_agent_settings(current)
    if merged == current:
        print(
            f"Step: {utils.get_utctimestring()}: '{consts.CI_ConfigMap_Name}' ConfigMap already "
            f"bypasses the proxy for Container Insights; no change needed. "
            f"{consts.Proxy_Bypass_ContainerInsights_Clear}"
        )
        return

    data[consts.CI_ConfigMap_Agent_Settings_Key] = merged
    existing.data = data
    # Only reached when this CLI changed the setting, so stamp it for removal by a later run.
    if existing.metadata is None:
        existing.metadata = kube_client.V1ObjectMeta(
            name=consts.CI_ConfigMap_Name,
            namespace=consts.CI_ConfigMap_Namespace,
        )
    annotations = existing.metadata.annotations or {}
    annotations[consts.CI_ConfigMap_Proxy_Bypass_Annotation] = "azure-cli"
    existing.metadata.annotations = annotations
    try:
        api_instance.replace_namespaced_config_map(
            name=consts.CI_ConfigMap_Name,
            namespace=consts.CI_ConfigMap_Namespace,
            body=existing,
        )
        print(
            f"Step: {utils.get_utctimestring()}: Updated existing '{consts.CI_ConfigMap_Name}' "
            f"ConfigMap to bypass the proxy for Container Insights. "
            f"{consts.Proxy_Bypass_ContainerInsights_Clear}"
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        report_container_insights_configmap_failure(
            e,
            errors.CONFIGMAP_WRITE_FAILED,
            "update",
            cmd=cmd,
        )


def create_container_insights_proxy_bypass_configmap(
    api_instance: kube_client.CoreV1Api,
    cmd: CLICommand | None = None,
) -> None:
    # Seed only the proxy-bypass setting; the Container Insights solution fills in the rest.
    configmap = kube_client.V1ConfigMap(
        metadata=kube_client.V1ObjectMeta(
            name=consts.CI_ConfigMap_Name,
            namespace=consts.CI_ConfigMap_Namespace,
            # Stamp the ConfigMap so a later run can remove the setting added here.
            annotations={consts.CI_ConfigMap_Proxy_Bypass_Annotation: "azure-cli"},
        ),
        data={
            "schema-version": "v1",
            "config-version": "ver1",
            consts.CI_ConfigMap_Agent_Settings_Key: consts.CI_ConfigMap_Proxy_Bypass_Block,
        },
    )

    try:
        api_instance.create_namespaced_config_map(
            namespace=consts.CI_ConfigMap_Namespace,
            body=configmap,
        )
        print(
            f"Step: {utils.get_utctimestring()}: Created '{consts.CI_ConfigMap_Name}' ConfigMap "
            f"in '{consts.CI_ConfigMap_Namespace}' namespace for Container Insights proxy bypass. "
            f"{consts.Proxy_Bypass_ContainerInsights_Clear}"
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        if getattr(e, "status", None) == 409:
            # ConfigMap appeared between the read and this create; merge into it instead.
            logger.warning(
                "ConfigMap '%s' appeared concurrently in '%s' namespace; merging the "
                "proxy-bypass setting into it.",
                consts.CI_ConfigMap_Name,
                consts.CI_ConfigMap_Namespace,
            )
            ensure_container_insights_proxy_bypass_configmap(api_instance, cmd=cmd)
            return
        report_container_insights_configmap_failure(
            e,
            errors.CONFIGMAP_WRITE_FAILED,
            "create",
            cmd=cmd,
        )


def remove_container_insights_proxy_bypass_configmap(
    api_instance: kube_client.CoreV1Api,
    raise_on_failure: bool = True,
    announce_skip: bool = False,
    cmd: CLICommand | None = None,
) -> None:
    # Undo the bypass only where the annotation shows this CLI added it. A setting without that
    # annotation is customer-configured and is left untouched.
    # announce_skip is on only for an explicit clear.
    try:
        existing = api_instance.read_namespaced_config_map(
            name=consts.CI_ConfigMap_Name,
            namespace=consts.CI_ConfigMap_Namespace,
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        # No ConfigMap means there is no setting to undo; never create one here.
        if getattr(e, "status", None) == 404:
            if announce_skip:
                logger.warning(consts.CI_ConfigMap_Nothing_To_Clear_Warning)
            return
        report_container_insights_configmap_failure(
            e,
            errors.CONFIGMAP_READ_FAILED,
            "read",
            raise_on_failure,
            error_message=consts.CI_ConfigMap_Removal_Error_Message,
            cmd=cmd,
        )
        return

    # Without metadata there is no annotation, so the setting was not added by this CLI.
    metadata = existing.metadata
    annotations = (metadata.annotations or {}) if metadata else {}
    if consts.CI_ConfigMap_Proxy_Bypass_Annotation not in annotations:
        if announce_skip:
            logger.warning(consts.CI_ConfigMap_Not_Managed_Warning)
        return

    data = existing.data or {}
    current = data.get(consts.CI_ConfigMap_Agent_Settings_Key, "")
    data[consts.CI_ConfigMap_Agent_Settings_Key] = (
        remove_proxy_bypass_from_agent_settings(current)
    )
    existing.data = data

    # Drop the annotation too, so the disabled setting left behind is not treated as CLI-owned.
    del annotations[consts.CI_ConfigMap_Proxy_Bypass_Annotation]
    metadata.annotations = annotations

    try:
        api_instance.replace_namespaced_config_map(
            name=consts.CI_ConfigMap_Name,
            namespace=consts.CI_ConfigMap_Namespace,
            body=existing,
        )
        print(
            f"Step: {utils.get_utctimestring()}: Disabled the Container Insights "
            f"proxy bypass in '{consts.CI_ConfigMap_Name}' ConfigMap in "
            f"'{consts.CI_ConfigMap_Namespace}' namespace"
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        report_container_insights_configmap_failure(
            e,
            errors.CONFIGMAP_WRITE_FAILED,
            "remove the bypass from",
            raise_on_failure,
            error_message=consts.CI_ConfigMap_Removal_Error_Message,
            cmd=cmd,
        )


def sync_container_insights_proxy_bypass_configmap(
    api_instance: kube_client.CoreV1Api,
    requested: bool,
    cmd: CLICommand | None = None,
) -> None:
    # Single entry point for connect and update, so the two cannot drift apart. Callers only reach
    # here when --add-proxy-bypass or --clear-proxy-bypass was passed, so a failure is always fatal.
    # Apply the bypass when requested, otherwise remove it.
    if requested:
        ensure_container_insights_proxy_bypass_configmap(api_instance, cmd=cmd)
    else:
        remove_container_insights_proxy_bypass_configmap(
            api_instance, announce_skip=True, cmd=cmd
        )
