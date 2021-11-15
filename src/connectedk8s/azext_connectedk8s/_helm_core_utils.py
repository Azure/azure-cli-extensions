# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
from enum import Enum
from subprocess import Popen, PIPE
import yaml

from knack.log import get_logger
from azure.cli.core import telemetry
from azure.cli.core.azclierror import CLIInternalError, ValidationError
import azext_connectedk8s._constants as consts

logger = get_logger(__name__)


class Command(Enum):
    HELM_VERSION = 1
    HELM_GET_VALUES = 2
    HELM_GET_RELEASE = 3


class HelmCoreUtils:

    def __init__(self, kube_config=None, kube_context=None):
        os.environ['HELM_EXPERIMENTAL_OCI'] = '1'
        self.set_kube_configuration(kube_config, kube_context)

    def set_kube_configuration(self, kube_config=None, kube_context=None):
        self.__kube_config = kube_config
        self.__kube_context = kube_context

    def __set_param(self, cmd_helm):
        if self.__kube_config:
            cmd_helm.extend(["--kubeconfig", self.__kube_config])
        if self.__kube_context:
            cmd_helm.extend(["--kube-context", self.__kube_context])
        return cmd_helm

    def pull_helm_chart(self, registry_path, helm_client_location):
        cmd_helm_chart_pull = [helm_client_location, "chart", "pull", registry_path]

        cmd_helm_chart_pull = self.__set_param(cmd_helm_chart_pull)

        self.__execute_helm_command(cmd_helm_chart_pull, consts.Pull_HelmChart_Fault_Type,
                                    'Unable to pull helm chart from the registry',
                                    "Unable to pull helm chart from the registry '{}': "
                                    .format(registry_path))

    def export_helm_chart(self, registry_path, chart_export_path, helm_client_location):
        cmd_helm_chart_export = [helm_client_location, "chart", "export", registry_path,
                                 "--destination", chart_export_path]

        cmd_helm_chart_export = self.__set_param(cmd_helm_chart_export)

        self.__execute_helm_command(cmd_helm_chart_export, consts.Export_HelmChart_Fault_Type,
                                    'Unable to export helm chart from the registry',
                                    "Unable to export helm chart from the registry '{}': "
                                    .format(registry_path))

    def add_helm_repo(self, repo_name, repo_url, helm_client_location):
        cmd_helm_repo = [helm_client_location, "repo", "add", repo_name, repo_url]

        cmd_helm_repo = self.__set_param(cmd_helm_repo)

        self.__execute_helm_command(cmd_helm_repo, consts.Add_HelmRepo_Fault_Type,
                                    'Failed to add helm repository',
                                    "Unable to add repository {} to helm: ".format(repo_url))

    def check_helm_version(self):
        cmd_helm_version = ["helm", "version", "--short", "--client"]

        cmd_helm_version = self.__set_param(cmd_helm_version)

        return self.__execute_helm_command(cmd_helm_version, consts.Check_HelmVersion_Fault_Type,
                                           'Unable to determine helm version',
                                           "Unable to determine helm version: ",
                                           Command.HELM_VERSION)

    def get_release_namespace(self, helm_client_location):
        cmd_helm_release = [helm_client_location, "list", "-a", "--all-namespaces", "--output", "json"]

        cmd_helm_release = self.__set_param(cmd_helm_release)

        output_helm_release = self.__execute_helm_command(cmd_helm_release, consts.List_HelmRelease_Fault_Type,
                                                          'Unable to list helm release',
                                                          "Helm list release failed: ",
                                                          Command.HELM_GET_RELEASE)
        try:
            output_helm_release = json.loads(output_helm_release)
        except json.decoder.JSONDecodeError:
            return None
        for release in output_helm_release:
            if release['name'] == 'azure-arc':
                return release['namespace']
        return None

    def get_all_helm_values(self, release_namespace, helm_client_location):
        cmd_helm_values = [helm_client_location, "get", "values", "--all", "azure-arc", "--namespace",
                           release_namespace]

        cmd_helm_values = self.__set_param(cmd_helm_values)

        output_helm_values = self.__execute_helm_command(cmd_helm_values,
                                                         consts.Get_Helm_Values_Failed,
                                                         'Error while doing helm get values azure-arc',
                                                         "Error while getting the helm values in the"
                                                         " azure-arc namespace: ",
                                                         Command.HELM_GET_VALUES)
        try:
            existing_values = yaml.safe_load(output_helm_values)
            return existing_values
        except Exception as e:
            telemetry.set_exception(exception=e,
                                    fault_type=consts.Helm_Existing_User_Supplied_Value_Get_Fault,
                                    summary='Problem loading the helm existing values')
            raise CLIInternalError("Problem loading the helm existing values: " + str(e))

    def __execute_helm_command(self, helm_cmd, fault_type=None, error_summary=None,
                               error_string=None, cmd_type=None):
        response_helm = Popen(helm_cmd, stdout=PIPE, stderr=PIPE)
        output, error_helm = response_helm.communicate()
        if response_helm.returncode != 0:
            if cmd_type is not None and cmd_type in [Command.HELM_GET_VALUES, Command.HELM_GET_RELEASE] and \
            'forbidden' in error_helm.decode("ascii"):
                telemetry.set_user_fault()
            telemetry.set_exception(exception=error_helm.decode("ascii"),
                                    fault_type=fault_type, summary=error_summary)
            raise CLIInternalError(error_string + error_helm.decode("ascii"))

        if cmd_type is not None and cmd_type is Command.HELM_VERSION and "v2" in output.decode("ascii"):
            telemetry.set_exception(exception='Helm 3 not found', fault_type=consts.Helm_Version_Fault_Type,
                                    summary='Helm3 not found on the machine')
            raise ValidationError("Helm version 3+ is required.",
                                  recommendation="Ensure that you have installed the latest version of Helm. "
                                  "Learn more at https://aka.ms/arc/k8s/onboarding-helm-install")

        return output.decode('ascii')
