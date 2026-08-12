# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Standardized customer-facing and telemetry error definitions."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from azure.cli.core.azclierror import (
    ArgumentUsageError,
    CLIInternalError,
    FileOperationError,
    InvalidArgumentValueError,
    MutuallyExclusiveArgumentError,
    RequiredArgumentMissingError,
    ValidationError,
)

import azext_connectedk8s._constants as consts

if TYPE_CHECKING:
    from azure.cli.core.azclierror import AzCLIError


@dataclass(frozen=True)
class ArcError:
    """A stable error definition shared by console output and telemetry.

    ``fault_type`` is the string value emitted to Azure CLI telemetry. Definitions
    should always reference a ``consts.*_Fault_Type`` constant instead of copying
    the string literal. ``fault_type_aliases`` supports legacy call sites that
    currently emit more than one fault type for the same standardized error.
    """

    code: str
    name: str
    message: str
    fault_type: str
    tsg_link: str = ""
    az_error_cls: type[AzCLIError] | None = field(default=CLIInternalError)
    fault_type_aliases: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.code:
            raise ValueError("ArcError.code is required")
        if not self.name:
            raise ValueError(f"ArcError.name is required (code={self.code})")
        if not self.message:
            raise ValueError(f"ArcError.message is required (code={self.code})")
        if not self.fault_type:
            raise ValueError(f"ArcError.fault_type is required (code={self.code})")
        if len(self.code) != 9 or not self.code.startswith("AZK8S"):
            raise ValueError(
                f"ArcError.code must use the AZK8Snnnn format: {self.code}"
            )
        if not self.code[5:].isdigit():
            raise ValueError(
                f"ArcError.code must use the AZK8Snnnn format: {self.code}"
            )

    @property
    def all_fault_types(self) -> tuple[str, ...]:
        """Return the canonical fault type followed by any legacy aliases."""
        return (self.fault_type, *self.fault_type_aliases)

    def format(self, **context: object) -> str:
        """Render the stable customer-facing error message."""
        safe_context: defaultdict[str, object] = defaultdict(str, context)
        message = self.message.format_map(safe_context).rstrip()
        lines = [f"[{self.code}] {self.name}: {message}"]
        if self.tsg_link:
            lines.append(f"Troubleshooting: {self.tsg_link}")
        return "\n".join(lines)

    def as_error(self, **context: object) -> AzCLIError:
        """Build, but do not raise, the configured Azure CLI exception."""
        if self.az_error_cls is None:
            raise ValueError(f"{self.code} is a non-raising diagnostic error")
        return self.az_error_cls(self.format(**context))


def _define(
    *,
    code: str,
    name: str,
    description: str,
    fault_type: str,
    az_error_cls: type[AzCLIError] | None = CLIInternalError,
    fault_type_aliases: tuple[str, ...] = (),
    tsg_link: str = "",
) -> ArcError:
    return ArcError(
        code=code,
        name=name,
        message=f"{description} {{details}}",
        fault_type=fault_type,
        az_error_cls=az_error_cls,
        fault_type_aliases=fault_type_aliases,
        tsg_link=tsg_link,
    )


# General / Internal (AZK8S0001-AZK8S0099)
UNEXPECTED_ERROR = _define(
    code="AZK8S0001",
    name="UnexpectedError",
    description="An unexpected internal error occurred while running {operation}.",
    fault_type=consts.Catch_All_Fault_Type,
)
UNSUPPORTED_OPERATING_SYSTEM = _define(
    code="AZK8S0002",
    name="UnsupportedOperatingSystem",
    description="The current operating system is not supported.",
    fault_type=consts.Unsupported_OS_Fault_Type,
)
UNSUPPORTED_PROVISIONED_CLUSTER_OPERATION = _define(
    code="AZK8S0003",
    name="UnsupportedProvisionedClusterOperation",
    description="This operation is not supported on provisioned clusters.",
    fault_type=consts.Unsupported_Operation_Provisioned_Cluster_Fault_Type,
    az_error_cls=InvalidArgumentValueError,
)

# Configuration & Input (AZK8S0100-AZK8S0199)
INVALID_ARGUMENT_VALUE = _define(
    code="AZK8S0100",
    name="InvalidArgumentValue",
    description="An argument value is invalid.",
    fault_type=consts.Invalid_Argument_Fault_Type,
    az_error_cls=InvalidArgumentValueError,
)
UPDATE_NO_PARAMETERS = _define(
    code="AZK8S0101",
    name="UpdateNoParameters",
    description="No parameters were supplied to change the connected cluster.",
    fault_type=consts.Update_No_Params_Fault_Type,
    az_error_cls=RequiredArgumentMissingError,
)
UPDATE_PROXY_PARAMETER_CONFLICT = _define(
    code="AZK8S0102",
    name="UpdateProxyParameterConflict",
    description="The supplied proxy parameters conflict with each other.",
    fault_type=consts.Update_Proxy_Conflict_Fault_Type,
    az_error_cls=MutuallyExclusiveArgumentError,
)
PROXY_CERT_PATH_NOT_FOUND = _define(
    code="AZK8S0103",
    name="ProxyCertificatePathNotFound",
    description="The supplied proxy certificate path does not exist.",
    fault_type=consts.Proxy_Cert_Path_Does_Not_Exist_Fault_Type,
    az_error_cls=InvalidArgumentValueError,
)
INVALID_LOCATION = _define(
    code="AZK8S0104",
    name="InvalidLocation",
    description="The supplied Azure location is invalid or unsupported.",
    fault_type=consts.Invalid_Location_Fault_Type,
    az_error_cls=InvalidArgumentValueError,
)
PRIVATE_LINK_SCOPE_LOCATION_MISMATCH = _define(
    code="AZK8S0105",
    name="PrivateLinkScopeLocationMismatch",
    description="The Private Link Scope and connected cluster locations do not match.",
    fault_type=consts.Pls_Location_Mismatch_Fault_Type,
    az_error_cls=ArgumentUsageError,
)
INVALID_GATEWAY_ARM_ID = _define(
    code="AZK8S0106",
    name="InvalidGatewayArmId",
    description="The supplied Gateway ARM resource ID is invalid.",
    fault_type=consts.Gateway_ArmId_Is_Invalid_Fault_Type,
    az_error_cls=InvalidArgumentValueError,
)

# Kubeconfig & Cluster Access (AZK8S0200-AZK8S0299)
KUBECONFIG_LOAD_FAILED = _define(
    code="AZK8S0200",
    name="KubeconfigLoadFailed",
    description="Failed to load the kubeconfig.",
    fault_type=consts.Load_Kubeconfig_Fault_Type,
    az_error_cls=FileOperationError,
)
CONFIGMAP_READ_FAILED = _define(
    code="AZK8S0201",
    name="ConfigMapReadFailed",
    description="Failed to read the Azure Arc ConfigMap.",
    fault_type=consts.Read_ConfigMap_Fault_Type,
)
KUBERNETES_CONNECTIVITY_FAILED = _define(
    code="AZK8S0202",
    name="KubernetesConnectivityFailed",
    description="Unable to connect to the Kubernetes cluster.",
    fault_type=consts.Kubernetes_Connectivity_FaultType,
)
DEFAULT_NAMESPACE_NOT_FOUND = _define(
    code="AZK8S0203",
    name="DefaultNamespaceNotFound",
    description="The default namespace does not exist on the Kubernetes cluster.",
    fault_type=consts.Default_Namespace_Does_Not_Exist_Fault_Type,
    az_error_cls=ValidationError,
)
KUBERNETES_DISTRIBUTION_DETECTION_FAILED = _define(
    code="AZK8S0204",
    name="KubernetesDistributionDetectionFailed",
    description="Failed to detect the Kubernetes distribution.",
    fault_type=consts.Get_Kubernetes_Distro_Fault_Type,
)
KUBERNETES_NAMESPACE_GET_FAILED = _define(
    code="AZK8S0205",
    name="KubernetesNamespaceGetFailed",
    description="Failed to determine the Kubernetes namespace.",
    fault_type=consts.Get_Kubernetes_Namespace_Fault_Type,
)
LINUX_NODE_NOT_FOUND = _define(
    code="AZK8S0206",
    name="LinuxNodeNotFound",
    description="No Linux node is available for scheduling Azure Arc agents.",
    fault_type=consts.Linux_Node_Not_Exists_Fault_Type,
)
CLUSTER_ROLE_BINDING_CREATE_FORBIDDEN = _define(
    code="AZK8S0207",
    name="ClusterRoleBindingCreateForbidden",
    description="The current identity cannot create Kubernetes ClusterRoleBindings.",
    fault_type=consts.Cannot_Create_ClusterRoleBindings_Fault_Type,
)
KUBERNETES_CONFIGURATION_LOAD_FAILED = _define(
    code="AZK8S0208",
    name="KubernetesConfigurationLoadFailed",
    description="Failed to load the Kubernetes client configuration.",
    fault_type=consts.Failed_To_Load_K8s_Configuration_Fault_Type,
)

# Network & Connectivity (AZK8S0300-AZK8S0399)
DATA_PLANE_HEALTH_CHECK_FAILED = _define(
    code="AZK8S0300",
    name="DataPlaneHealthCheckFailed",
    description="The Azure Arc data-plane health check failed.",
    fault_type=consts.DP_Health_Check_Fault_Type,
)
DNS_NXDOMAIN = _define(
    code="AZK8S0301",
    name="DnsNxDomain",
    description="DNS resolution failed because the domain does not exist (NXDOMAIN).",
    fault_type=consts.DNS_NXDomain_Fault_Type,
    az_error_cls=None,
)
DNS_TIMEOUT = _define(
    code="AZK8S0302",
    name="DnsTimeout",
    description="DNS resolution timed out.",
    fault_type=consts.DNS_Timeout_Fault_Type,
    az_error_cls=None,
)
DNS_SERVFAIL = _define(
    code="AZK8S0303",
    name="DnsServerFailure",
    description="The DNS server returned SERVFAIL.",
    fault_type=consts.DNS_ServFail_Fault_Type,
    az_error_cls=None,
)
DNS_NO_SERVERS_REACHABLE = _define(
    code="AZK8S0304",
    name="DnsNoServersReachable",
    description="DNS resolution failed because no DNS servers could be reached.",
    fault_type=consts.DNS_No_Servers_Reachable_Fault_Type,
    az_error_cls=None,
)
DNS_COMMUNICATIONS_ERROR = _define(
    code="AZK8S0305",
    name="DnsCommunicationsError",
    description="A network communication error occurred while contacting the DNS server.",
    fault_type=consts.DNS_Communications_Error_Fault_Type,
    az_error_cls=None,
)
ONBOARDING_OUTBOUND_CONNECTIVITY_FAILED = _define(
    code="AZK8S0306",
    name="OnboardingOutboundConnectivityFailed",
    description="Outbound connectivity to an onboarding endpoint failed.",
    fault_type=consts.Outbound_Connectivity_Check_Failed_For_Onboarding_Fault_Type,
    az_error_cls=None,
)
CLUSTER_CONNECT_OUTBOUND_CONNECTIVITY_FAILED = _define(
    code="AZK8S0307",
    name="ClusterConnectOutboundConnectivityFailed",
    description="Outbound connectivity to a cluster-connect endpoint failed.",
    fault_type=consts.Outbound_Connectivity_Check_Failed_For_Cluster_Connect_Fault_Type,
    az_error_cls=None,
)
OUTBOUND_ENDPOINT_NON2XX = _define(
    code="AZK8S0308",
    name="OutboundEndpointNonSuccessResponse",
    description="An outbound endpoint returned a non-success HTTP response.",
    fault_type=consts.Prediagnostics_Outbound_Non2xx_Response_Fault_Type,
    az_error_cls=None,
)
CERT_PULLDOWN_FAILED = _define(
    code="AZK8S0309",
    name="CertificatePulldownFailed",
    description=(
        "Azure Arc agent identity or certificate synchronization did not finish "
        "before the Helm timeout. If this persists, delete the connected cluster "
        "resource and re-onboard."
    ),
    fault_type=consts.Helm_Timeout_ClusterIdentity_Fault_Type,
)

# Azure Resource Operations (AZK8S0400-AZK8S0499)
CONNECTED_CLUSTER_CREATE_FAILED = _define(
    code="AZK8S0400",
    name="ConnectedClusterCreateFailed",
    description="Failed to create the connected cluster Azure resource.",
    fault_type=consts.Create_ConnectedCluster_Fault_Type,
)
CONNECTED_CLUSTER_UPDATE_FAILED = _define(
    code="AZK8S0401",
    name="ConnectedClusterUpdateFailed",
    description="Failed to update the connected cluster Azure resource.",
    fault_type=consts.Update_ConnectedCluster_Fault_Type,
)
CONNECTED_CLUSTER_DELETE_FAILED = _define(
    code="AZK8S0402",
    name="ConnectedClusterDeleteFailed",
    description="Failed to delete the connected cluster Azure resource.",
    fault_type=consts.Delete_ConnectedCluster_Fault_Type,
)
CLUSTER_ALREADY_ONBOARDED = _define(
    code="AZK8S0403",
    name="ClusterAlreadyOnboarded",
    description="The Kubernetes cluster is already onboarded to Azure Arc.",
    fault_type=consts.Cluster_Already_Onboarded_Fault_Type,
    az_error_cls=ArgumentUsageError,
)
RESOURCE_ALREADY_EXISTS = _define(
    code="AZK8S0404",
    name="ConnectedClusterResourceAlreadyExists",
    description="A connected cluster resource with the same name already exists.",
    fault_type=consts.Resource_Already_Exists_Fault_Type,
    az_error_cls=ArgumentUsageError,
)
RESOURCE_NOT_FOUND = _define(
    code="AZK8S0405",
    name="ConnectedClusterResourceNotFound",
    description="The connected cluster Azure resource does not exist.",
    fault_type=consts.Resource_Does_Not_Exist_Fault_Type,
    az_error_cls=ArgumentUsageError,
)
INVALID_DELETE_REQUEST = _define(
    code="AZK8S0406",
    name="InvalidDeleteRequest",
    description="The connected cluster delete request is invalid.",
    fault_type=consts.Bad_DeleteRequest_Fault_Type,
    az_error_cls=ValidationError,
)
RESOURCE_PROVIDER_FETCH_FAILED = _define(
    code="AZK8S0407",
    name="ResourceProviderFetchFailed",
    description="Failed to fetch Azure resource-provider information.",
    fault_type=consts.Get_ResourceProvider_Fault_Type,
)
CONNECTED_CLUSTER_PROVIDER_NOT_REGISTERED = _define(
    code="AZK8S0408",
    name="ConnectedClusterProviderNotRegistered",
    description="The Microsoft.Kubernetes resource provider is not registered.",
    fault_type=consts.CC_Provider_Namespace_Not_Registered_Fault_Type,
    az_error_cls=ValidationError,
)
CONNECTED_CLUSTER_RESOURCE_ID_MISSING = _define(
    code="AZK8S0409",
    name="ConnectedClusterResourceIdMissing",
    description="The connected cluster Azure resource ID is missing.",
    fault_type=consts.Connected_Cluster_Resource_Id_None_Fault_Type,
)

# Helm & Agent Lifecycle (AZK8S0500-AZK8S0599)
HELM_RELEASE_INSTALL_FAILED = _define(
    code="AZK8S0500",
    name="HelmReleaseInstallFailed",
    description=(
        "The Azure Arc agent Helm release {operation} failed. Run "
        "'kubectl get pods -n azure-arc' and inspect pod logs for more information."
    ),
    fault_type=consts.Install_HelmRelease_Fault_Type,
)
HELM_RELEASE_DELETE_FAILED = _define(
    code="AZK8S0501",
    name="HelmReleaseDeleteFailed",
    description="Failed to delete the Azure Arc agent Helm release.",
    fault_type=consts.Delete_HelmRelease_Fault_Type,
)
HELM_CHART_PULL_FAILED = _define(
    code="AZK8S0502",
    name="HelmChartPullFailed",
    description="Failed to pull the Azure Arc Helm chart.",
    fault_type=consts.Pull_HelmChart_Fault_Type,
)
HELM_CHART_EXPORT_FAILED = _define(
    code="AZK8S0503",
    name="HelmChartExportFailed",
    description="Failed to export the Azure Arc Helm chart.",
    fault_type=consts.Export_HelmChart_Fault_Type,
)
HELM_REPO_ADD_FAILED = _define(
    code="AZK8S0504",
    name="HelmRepositoryAddFailed",
    description="Failed to add the Helm repository.",
    fault_type=consts.Add_HelmRepo_Fault_Type,
)
HELM_RELEASE_LIST_FAILED = _define(
    code="AZK8S0505",
    name="HelmReleaseListFailed",
    description="Failed to list Helm releases.",
    fault_type=consts.List_HelmRelease_Fault_Type,
)
AGENT_STATE_TIMEOUT = _define(
    code="AZK8S0506",
    name="AgentStateTimeout",
    description="Timed out waiting for the Azure Arc agent state during {operation}.",
    fault_type=consts.Agent_State_Timeout_Fault_Type,
)
KEY_PAIR_GENERATION_FAILED = _define(
    code="AZK8S0507",
    name="KeyPairGenerationFailed",
    description="Failed to generate the RSA key pair.",
    fault_type=consts.KeyPair_Generate_Fault_Type,
)
RELEASE_NAMESPACE_NOT_FOUND = _define(
    code="AZK8S0508",
    name="ReleaseNamespaceNotFound",
    description="The azure-arc Helm release namespace was not found.",
    fault_type=consts.Release_Namespace_Not_Found_Fault_Type,
)
HELM_VALUES_GET_FAILED = _define(
    code="AZK8S0509",
    name="HelmValuesGetFailed",
    description="Failed to get the Azure Arc Helm values.",
    fault_type=consts.Get_Helm_Values_Failed_Fault_Type,
)
HELM_NOT_INSTALLED = _define(
    code="AZK8S0510",
    name="HelmNotInstalled",
    description="Helm is not installed.",
    fault_type=consts.Helm_Installation_Fault_Type,
)
HELM_VERSION_TOO_OLD = _define(
    code="AZK8S0511",
    name="HelmVersionTooOld",
    description="The installed Helm version is too old.",
    fault_type=consts.Helm_Version_Fault_Type,
)
HELM_TIMEOUT_PENDING_OR_UNSCHEDULABLE = _define(
    code="AZK8S0512",
    name="HelmTimeoutPendingOrUnschedulable",
    description=(
        "Azure Arc agent pods are pending or unschedulable. Check node capacity, "
        "taints, node selectors, and affinity rules."
    ),
    fault_type=consts.Helm_Timeout_PendingOrUnschedulable_Fault_Type,
)
HELM_TIMEOUT_IMAGE_PULL_FAILED = _define(
    code="AZK8S0513",
    name="HelmTimeoutImagePullFailed",
    description=(
        "Azure Arc agent pods could not pull their container images. Verify the "
        "cluster nodes can reach mcr.microsoft.com, check registry or proxy settings, "
        "and confirm nodes have free disk space."
    ),
    fault_type=consts.Helm_Timeout_ImagePull_Fault_Type,
)
HELM_TIMEOUT_GENERIC = _define(
    code="AZK8S0514",
    name="HelmTimeout",
    description=(
        "Azure Arc agent installation did not finish before the Helm timeout. Retry "
        "onboarding or inspect the 'azure-arc' namespace for pods that are not ready."
    ),
    fault_type=consts.Helm_Timeout_Generic_Fault_Type,
)

# Pre-onboarding Diagnostics (AZK8S0600-AZK8S0699)
PREDIAGNOSTICS_FAILED = _define(
    code="AZK8S0600",
    name="PrediagnosticsFailed",
    description="The pre-onboarding diagnostic checks failed.",
    fault_type=consts.Install_Prediagnostics_Fault_Type,
)
PREDIAGNOSTICS_JOB_EXECUTION_FAILED = _define(
    code="AZK8S0601",
    name="PrediagnosticsJobExecutionFailed",
    description="The pre-onboarding diagnostic job failed to execute.",
    fault_type=consts.Install_Prediagnostics_Job_Execution_Error_Fault_Type,
)
POST_DIAGNOSTIC_PRECHECK_FAILED = _define(
    code="AZK8S0602",
    name="PostDiagnosticPrecheckFailed",
    description="A required post-diagnostic precheck failed.",
    fault_type=consts.Post_Diagnostic_Precheck_Fault_Type,
    az_error_cls=ValidationError,
)
PREDIAGNOSTICS_INCOMPLETE = _define(
    code="AZK8S0603",
    name="PrediagnosticsIncomplete",
    description="The pre-onboarding checks completed without a conclusive result.",
    fault_type=consts.Cluster_Diagnostic_Prechecks_Incomplete_Fault_Type,
    az_error_cls=ValidationError,
)
PREDIAGNOSTICS_JOB_NOT_SCHEDULED = _define(
    code="AZK8S0604",
    name="PrediagnosticsJobNotScheduled",
    description="The pre-onboarding diagnostic job could not be scheduled.",
    fault_type=consts.Cluster_Diagnostic_Checks_Job_Not_Scheduled_Fault_Type,
)
PREDIAGNOSTICS_JOB_NOT_COMPLETE = _define(
    code="AZK8S0605",
    name="PrediagnosticsJobNotComplete",
    description="The pre-onboarding diagnostic job did not complete within the timeout.",
    fault_type=consts.Cluster_Diagnostic_Checks_Job_Not_Complete_Fault_Type,
)
PREDIAGNOSTICS_LOG_SAVE_FAILED = _define(
    code="AZK8S0606",
    name="PrediagnosticsLogSaveFailed",
    description="Failed to save the pre-onboarding diagnostic job logs.",
    fault_type=consts.Cluster_Diagnostic_Checks_Job_Log_Save_Failed_Fault_Type,
    az_error_cls=None,
)
PREDIAGNOSTICS_HELM_INSTALL_FAILED = _define(
    code="AZK8S0607",
    name="PrediagnosticsHelmInstallFailed",
    description="Failed to install the pre-onboarding diagnostic Helm release.",
    fault_type=consts.Cluster_Diagnostic_Checks_Helm_Install_Failed_Fault_Type,
)

# Features (AZK8S0700-AZK8S0799)
CUSTOM_LOCATIONS_ENABLE_FAILED = _define(
    code="AZK8S0700",
    name="CustomLocationsEnableFailed",
    description="Failed to enable the custom locations feature.",
    fault_type=consts.Custom_Locations_Enable_Failed_Fault_Type,
)
CUSTOM_LOCATIONS_OID_FETCH_FAILED = _define(
    code="AZK8S0701",
    name="CustomLocationsOidFetchFailed",
    description="Failed to fetch the custom locations application object ID.",
    fault_type=consts.Custom_Locations_OID_Fetch_Fault_Type_Exception,
    fault_type_aliases=(consts.Custom_Locations_OID_Fetch_Fault_Type_CLOid_None,),
)
CUSTOM_LOCATIONS_REGISTRATION_CHECK_FAILED = _define(
    code="AZK8S0702",
    name="CustomLocationsRegistrationCheckFailed",
    description="The custom locations provider registration check failed.",
    fault_type=consts.Custom_Locations_Registration_Check_Fault_Type,
)

# Client Proxy (AZK8S0800-AZK8S0899)
CLIENT_PROXY_DOWNLOAD_FAILED = _define(
    code="AZK8S0800",
    name="ClientProxyDownloadFailed",
    description="Failed to download the client proxy binary.",
    fault_type=consts.Download_Exe_Fault_Type,
)
CLIENT_PROXY_PORT_IN_USE = _define(
    code="AZK8S0801",
    name="ClientProxyPortInUse",
    description="The client proxy port is already in use.",
    fault_type=consts.Client_Proxy_Port_Fault_Type,
)
CLIENT_PROXY_START_FAILED = _define(
    code="AZK8S0802",
    name="ClientProxyStartFailed",
    description="Failed to start the client proxy process.",
    fault_type=consts.Run_Clientproxy_Fault_Type,
)
CLIENT_PROXY_CONFIG_CREATE_FAILED = _define(
    code="AZK8S0803",
    name="ClientProxyConfigCreateFailed",
    description="Failed to create the client proxy configuration file.",
    fault_type=consts.Create_Config_Fault_Type,
    az_error_cls=FileOperationError,
)
CLIENT_PROXY_CLOSED = _define(
    code="AZK8S0804",
    name="ClientProxyClosed",
    description="The client proxy process was closed externally.",
    fault_type=consts.Proxy_Closed_Externally_Fault_Type,
)
CLUSTER_CREDENTIALS_GET_FAILED = _define(
    code="AZK8S0805",
    name="ClusterCredentialsGetFailed",
    description="Failed to get cluster credentials.",
    fault_type=consts.Get_Credentials_Failed_Fault_Type,
)


# Backward-compatible aliases for the initially wired call sites.
HELM_RELEASE_OPERATION_FAILED = HELM_RELEASE_INSTALL_FAILED
HELM_TIMEOUT_CLUSTER_IDENTITY = CERT_PULLDOWN_FAILED

HELM_TIMEOUT_ERRORS: dict[str, ArcError] = {
    "ImagePullFailure": HELM_TIMEOUT_IMAGE_PULL_FAILED,
    "PendingOrUnschedulable": HELM_TIMEOUT_PENDING_OR_UNSCHEDULABLE,
    "ClusterIdentityFailure": CERT_PULLDOWN_FAILED,
    "GenericHelmTimeout": HELM_TIMEOUT_GENERIC,
}

ALL_ERRORS: tuple[ArcError, ...] = (
    UNEXPECTED_ERROR,
    UNSUPPORTED_OPERATING_SYSTEM,
    UNSUPPORTED_PROVISIONED_CLUSTER_OPERATION,
    INVALID_ARGUMENT_VALUE,
    UPDATE_NO_PARAMETERS,
    UPDATE_PROXY_PARAMETER_CONFLICT,
    PROXY_CERT_PATH_NOT_FOUND,
    INVALID_LOCATION,
    PRIVATE_LINK_SCOPE_LOCATION_MISMATCH,
    INVALID_GATEWAY_ARM_ID,
    KUBECONFIG_LOAD_FAILED,
    CONFIGMAP_READ_FAILED,
    KUBERNETES_CONNECTIVITY_FAILED,
    DEFAULT_NAMESPACE_NOT_FOUND,
    KUBERNETES_DISTRIBUTION_DETECTION_FAILED,
    KUBERNETES_NAMESPACE_GET_FAILED,
    LINUX_NODE_NOT_FOUND,
    CLUSTER_ROLE_BINDING_CREATE_FORBIDDEN,
    KUBERNETES_CONFIGURATION_LOAD_FAILED,
    DATA_PLANE_HEALTH_CHECK_FAILED,
    DNS_NXDOMAIN,
    DNS_TIMEOUT,
    DNS_SERVFAIL,
    DNS_NO_SERVERS_REACHABLE,
    DNS_COMMUNICATIONS_ERROR,
    ONBOARDING_OUTBOUND_CONNECTIVITY_FAILED,
    CLUSTER_CONNECT_OUTBOUND_CONNECTIVITY_FAILED,
    OUTBOUND_ENDPOINT_NON2XX,
    CERT_PULLDOWN_FAILED,
    CONNECTED_CLUSTER_CREATE_FAILED,
    CONNECTED_CLUSTER_UPDATE_FAILED,
    CONNECTED_CLUSTER_DELETE_FAILED,
    CLUSTER_ALREADY_ONBOARDED,
    RESOURCE_ALREADY_EXISTS,
    RESOURCE_NOT_FOUND,
    INVALID_DELETE_REQUEST,
    RESOURCE_PROVIDER_FETCH_FAILED,
    CONNECTED_CLUSTER_PROVIDER_NOT_REGISTERED,
    CONNECTED_CLUSTER_RESOURCE_ID_MISSING,
    HELM_RELEASE_INSTALL_FAILED,
    HELM_RELEASE_DELETE_FAILED,
    HELM_CHART_PULL_FAILED,
    HELM_CHART_EXPORT_FAILED,
    HELM_REPO_ADD_FAILED,
    HELM_RELEASE_LIST_FAILED,
    AGENT_STATE_TIMEOUT,
    KEY_PAIR_GENERATION_FAILED,
    RELEASE_NAMESPACE_NOT_FOUND,
    HELM_VALUES_GET_FAILED,
    HELM_NOT_INSTALLED,
    HELM_VERSION_TOO_OLD,
    HELM_TIMEOUT_PENDING_OR_UNSCHEDULABLE,
    HELM_TIMEOUT_IMAGE_PULL_FAILED,
    HELM_TIMEOUT_GENERIC,
    PREDIAGNOSTICS_FAILED,
    PREDIAGNOSTICS_JOB_EXECUTION_FAILED,
    POST_DIAGNOSTIC_PRECHECK_FAILED,
    PREDIAGNOSTICS_INCOMPLETE,
    PREDIAGNOSTICS_JOB_NOT_SCHEDULED,
    PREDIAGNOSTICS_JOB_NOT_COMPLETE,
    PREDIAGNOSTICS_LOG_SAVE_FAILED,
    PREDIAGNOSTICS_HELM_INSTALL_FAILED,
    CUSTOM_LOCATIONS_ENABLE_FAILED,
    CUSTOM_LOCATIONS_OID_FETCH_FAILED,
    CUSTOM_LOCATIONS_REGISTRATION_CHECK_FAILED,
    CLIENT_PROXY_DOWNLOAD_FAILED,
    CLIENT_PROXY_PORT_IN_USE,
    CLIENT_PROXY_START_FAILED,
    CLIENT_PROXY_CONFIG_CREATE_FAILED,
    CLIENT_PROXY_CLOSED,
    CLUSTER_CREDENTIALS_GET_FAILED,
)

ERROR_CATALOG: dict[str, ArcError] = {error.code: error for error in ALL_ERRORS}
FAULT_TYPE_CATALOG: dict[str, ArcError] = {
    fault_type: error for error in ALL_ERRORS for fault_type in error.all_fault_types
}

if len(ERROR_CATALOG) != len(ALL_ERRORS):
    raise ValueError("Duplicate standardized connectedk8s error code")
if len({error.name for error in ALL_ERRORS}) != len(ALL_ERRORS):
    raise ValueError("Duplicate standardized connectedk8s error name")
if len(FAULT_TYPE_CATALOG) != sum(len(error.all_fault_types) for error in ALL_ERRORS):
    raise ValueError("Duplicate standardized connectedk8s fault type")


def get_error(code: str) -> ArcError | None:
    """Return a standardized error by AZK8S code."""
    return ERROR_CATALOG.get(code)


def get_error_by_fault_type(fault_type: str) -> ArcError | None:
    """Return a standardized error by canonical or legacy telemetry fault type."""
    return FAULT_TYPE_CATALOG.get(fault_type)


def get_helm_timeout_error(classification: str) -> ArcError:
    """Return the standardized error for a Helm timeout classification."""
    return HELM_TIMEOUT_ERRORS.get(classification, HELM_TIMEOUT_GENERIC)
