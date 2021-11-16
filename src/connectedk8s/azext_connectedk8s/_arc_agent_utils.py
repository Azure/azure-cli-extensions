# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from subprocess import Popen, PIPE

from knack.log import get_logger
from azure.cli.core import telemetry
from azure.cli.core.azclierror import CLIInternalError
import azext_connectedk8s._constants as consts
import azext_connectedk8s._kube_core_utils as kube_core_utils
import azext_connectedk8s._utils as utils

logger = get_logger(__name__)


def _execute_helm_command(cmd_helm, error=None):
    response_helm_cmd = Popen(cmd_helm, stdout=PIPE, stderr=PIPE)
    _, error_helm_cmd = response_helm_cmd.communicate()
    if response_helm_cmd.returncode != 0:
        if ('forbidden' in error_helm_cmd.decode("ascii") or
                'timed out waiting for the condition' in error_helm_cmd.decode("ascii")):
            telemetry.set_user_fault()
        telemetry.set_exception(exception=error_helm_cmd.decode("ascii"),
                                fault_type=consts.Install_HelmRelease_Fault_Type,
                                summary='Unable to install helm release')
        logger.warning("Please check if the azure-arc namespace was deployed and run" +
                       " 'kubectl get pods -n azure-arc' to check if all the pods are" +
                       " in running state. A possible cause for pods stuck in pending" +
                       " state could be insufficient resources on the kubernetes cluster" +
                       " to onboard to arc.")
        raise CLIInternalError(str.format(error, error_helm_cmd.decode("ascii")))


class ArcAgentUtils:

    __proxy_details = {}

    def __init__(self, kube_config=None, kube_context=None, values_file=None, proxy_details=None,
                 auto_upgrade=None):
        os.environ['HELM_EXPERIMENTAL_OCI'] = '1'
        self.set_kube_configuration(kube_config, kube_context)
        self.set_proxy_configuration(proxy_details)
        self.set_values_file(values_file)
        self.set_auto_upgrade(auto_upgrade)

    def set_kube_configuration(self, kube_config=None, kube_context=None):
        self.__kube_config = kube_config
        self.__kube_context = kube_context

    def set_proxy_configuration(self, proxy_details=None):
        self.__proxy_details = proxy_details

    def set_values_file(self, values_file=None):
        self.__values_file = values_file

    def set_auto_upgrade(self, auto_upgrade=None):
        self.__auto_upgrade = auto_upgrade

    def execute_arc_agent_install(self, chart_path, subscription_id, kubernetes_distro,
                                  kubernetes_infra, resource_group_name, cluster_name, location,
                                  onboarding_tenant_id, private_key_pem, no_wait, cloud_name,
                                  enable_custom_locations, custom_locations_oid, helm_client_location,
                                  onboarding_timeout="300"):

        cmd_helm_install = [helm_client_location, "upgrade", "--install", "azure-arc", chart_path,
                            "--set", "global.subscriptionId={}".format(subscription_id),
                            "--set", "global.kubernetesDistro={}".format(kubernetes_distro),
                            "--set", "global.kubernetesInfra={}".format(kubernetes_infra),
                            "--set", "global.resourceGroupName={}".format(resource_group_name),
                            "--set", "global.resourceName={}".format(cluster_name),
                            "--set", "global.location={}".format(location),
                            "--set", "global.tenantId={}".format(onboarding_tenant_id),
                            "--set", "global.onboardingPrivateKey={}".format(private_key_pem),
                            "--set", "systemDefaultValues.spnOnboarding=false",
                            "--set", "global.azureEnvironment={}".format(cloud_name),
                            "--set", "systemDefaultValues.clusterconnect-agent.enabled=true",
                            "--output", "json"]

        # Add custom-locations related params
        if enable_custom_locations:
            cmd_helm_install.extend(["--set", "systemDefaultValues.customLocations.enabled=true"])
            cmd_helm_install.extend(["--set", "systemDefaultValues.customLocations.oid={}"
                                     .format(custom_locations_oid)])

        cmd_helm_install = self.__set_params(cmd_helm_install)

        if not no_wait:
            # Change --timeout format for helm client to understand
            onboarding_timeout = onboarding_timeout + "s"
            cmd_helm_install.extend(["--wait", "--timeout", "{}".format(onboarding_timeout)])

        _execute_helm_command(cmd_helm_install, "Unable to install helm release: ")

    def execute_arc_agent_update(self, chart_path, release_namespace, helm_client_location):

        cmd_helm_upgrade = [helm_client_location, "upgrade", "azure-arc", chart_path, "--namespace",
                            release_namespace, "--reuse-values", "--wait", "--output", "json"]

        cmd_helm_upgrade = self.__set_params(cmd_helm_upgrade)

        _execute_helm_command(cmd_helm_upgrade, consts.Update_Agent_Failure)

    def execute_arc_agent_upgrade(self, chart_path, release_namespace, upgrade_timeout, existing_user_values,
                                  helm_client_location):

        cmd_helm_upgrade = [helm_client_location, "upgrade", "azure-arc", chart_path, "--namespace",
                            release_namespace, "--output", "json", "--atomic", "--wait", "--timeout",
                            "{}".format(upgrade_timeout)]

        proxy_enabled_param_added = False
        infra_added = False
        for key, value in utils.flatten(existing_user_values).items():
            if value is not None:
                if key == "global.isProxyEnabled":
                    proxy_enabled_param_added = True
                if (key == "global.httpProxy" or key == "global.httpsProxy" or key == "global.noProxy"):
                    if value and not proxy_enabled_param_added:
                        cmd_helm_upgrade.extend(["--set", "global.isProxyEnabled={}".format(True)])
                        proxy_enabled_param_added = True
                if key == "global.kubernetesDistro" and value == "default":
                    value = "generic"
                if key == "global.kubernetesInfra":
                    infra_added = True
                cmd_helm_upgrade.extend(["--set", "{}={}".format(key, value)])

        if not proxy_enabled_param_added:
            cmd_helm_upgrade.extend(["--set", "global.isProxyEnabled={}".format(False)])

        if not infra_added:
            cmd_helm_upgrade.extend(["--set", "global.kubernetesInfra={}".format("generic")])

        cmd_helm_upgrade = self.__set_params(cmd_helm_upgrade)

        _execute_helm_command(cmd_helm_upgrade, consts.Upgrade_Agent_Failure)

    def execute_arc_agent_enable_features(self, chart_path, release_namespace, enable_azure_rbac,
                                          enable_cluster_connect, enable_cl, custom_locations_oid,
                                          helm_client_location, azrbac_client_id=None,
                                          azrbac_client_secret=None, azrbac_skip_authz_check=None):
        cmd_helm_upgrade = [helm_client_location, "upgrade", "azure-arc", chart_path, "--namespace",
                            release_namespace, "--reuse-values", "--wait", "--output", "json"]

        cmd_helm_upgrade = self.__set_params(cmd_helm_upgrade)

        if enable_azure_rbac:
            cmd_helm_upgrade.extend(["--set", "systemDefaultValues.guard.enabled=true"])
            cmd_helm_upgrade.extend(["--set", "systemDefaultValues.guard.clientId={}"
                                     .format(azrbac_client_id)])
            cmd_helm_upgrade.extend(["--set", "systemDefaultValues.guard.clientSecret={}"
                                     .format(azrbac_client_secret)])
            cmd_helm_upgrade.extend(["--set", "systemDefaultValues.guard.skipAuthzCheck={}"
                                     .format(azrbac_skip_authz_check)])
        if enable_cluster_connect:
            cmd_helm_upgrade.extend(["--set", "systemDefaultValues.clusterconnect-agent.enabled=true"])
        if enable_cl:
            cmd_helm_upgrade.extend(["--set", "systemDefaultValues.customLocations.enabled=true"])
            cmd_helm_upgrade.extend(["--set", "systemDefaultValues.customLocations.oid={}"
                                     .format(custom_locations_oid)])

        _execute_helm_command(cmd_helm_upgrade, consts.Error_enabling_Features)

    def execute_arc_agent_disable_features(self, chart_path, release_namespace, disable_azure_rbac,
                                           disable_cluster_connect, disable_cl, helm_client_location):
        cmd_helm_upgrade = [helm_client_location, "upgrade", "azure-arc", chart_path, "--namespace", release_namespace,
                            "--reuse-values",
                            "--wait", "--output", "json"]

        cmd_helm_upgrade = self.__set_params(cmd_helm_upgrade)

        if disable_azure_rbac:
            cmd_helm_upgrade.extend(["--set", "systemDefaultValues.guard.enabled=false"])
        if disable_cluster_connect:
            cmd_helm_upgrade.extend(["--set", "systemDefaultValues.clusterconnect-agent.enabled=false"])
        if disable_cl:
            cmd_helm_upgrade.extend(["--set", "systemDefaultValues.customLocations.enabled=false"])
            cmd_helm_upgrade.extend(["--set", "systemDefaultValues.customLocations.oid={}".format("")])

        _execute_helm_command(cmd_helm_upgrade, consts.Error_disabling_Features)

    def execute_delete_arc_agents(self, release_namespace, configuration, helm_client_location):
        cmd_helm_delete = [helm_client_location, "delete", "azure-arc", "--namespace", release_namespace]

        cmd_helm_delete = self.__set_params(cmd_helm_delete)

        _execute_helm_command(cmd_helm_delete, "Error occured while cleaning up arc agents. " +
                              "Helm release deletion failed: ")

        kube_core_utils.ensure_namespace_cleanup(configuration)

    def __set_params(self, cmd_helm):

        # To set some other helm parameters through file
        if self.__values_file is not None:
            cmd_helm.extend(["-f", self.__values_file])
        if self.__auto_upgrade:
            cmd_helm.extend(["--set", "systemDefaultValues.azureArcAgents.autoUpdate={}"
                            .format(self.__auto_upgrade)])
        if self.__proxy_details and self.__proxy_details.get('https_proxy'):
            cmd_helm.extend(["--set", "global.httpsProxy={}"
                            .format(self.__proxy_details.get('https_proxy'))])
        if self.__proxy_details and self.__proxy_details.get('http_proxy'):
            cmd_helm.extend(["--set", "global.httpProxy={}"
                            .format(self.__proxy_details.get('http_proxy'))])
        if self.__proxy_details and self.__proxy_details.get('no_proxy'):
            cmd_helm.extend(["--set", "global.noProxy={}"
                            .format(self.__proxy_details.get('no_proxy'))])
        if self.__proxy_details and self.__proxy_details.get('proxy_cert'):
            cmd_helm.extend(["--set-file", "global.proxyCert={}"
                            .format(self.__proxy_details.get('proxy_cert'))])
        if (self.__proxy_details and (self.__proxy_details.get('https_proxy') or
            self.__proxy_details.get('http_proxy') or self.__proxy_details.get('no_proxy'))):
            cmd_helm.extend(["--set", "global.isProxyEnabled={}".format(True)])
        if self.__proxy_details and self.__proxy_details.get('disable_proxy'):
            cmd_helm.extend(["--set", "global.isProxyEnabled={}".format(False)])
        if self.__kube_config:
            cmd_helm.extend(["--kubeconfig", self.__kube_config])
        if self.__kube_context:
            cmd_helm.extend(["--kube-context", self.__kube_context])

        return cmd_helm
