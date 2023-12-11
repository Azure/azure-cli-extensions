# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
import json
import requests
import platform
import stat
from knack.util import CLIError
import azext_connectedk8s._constants as consts
import urllib.request
import shutil
import time
from knack.log import get_logger
from azure.cli.core import get_default_cli
import subprocess
from subprocess import Popen, PIPE, run, STDOUT, call, DEVNULL
from azure.cli.testsdk import (LiveScenarioTest, ResourceGroupPreparer, live_only)  # pylint: disable=import-error
from azure.cli.core.azclierror import RequiredArgumentMissingError

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))
logger = get_logger(__name__)

# Set up configuration file. If configuration file is not found, then auto-populate with fake values where allowed.
CONFIG = {} # dictionary of configurations
config_path = os.path.join(os.path.dirname(__file__), "config.json")
if not os.path.isfile(config_path):
    CONFIG["customLocationsOid"] = ""
    CONFIG["rbacAppId"] = "fakeRbacAppId"
    CONFIG["rbacAppSecret"] = "fakeRbacAppSecret"
    CONFIG["location"] = "eastus2euap"
else:
    with open(config_path, 'r') as f:
        CONFIG = json.load(f)
    for key in CONFIG:
        if not CONFIG[key]:
            raise RequiredArgumentMissingError(f"Missing required configuration in {config_path} file. Make sure all properties are populated.")

def _get_test_data_file(filename):
    # Don't output temporary test data to "**/azext_connectedk8s/tests/latest/data/" as that location
    # is for re-usable test data files by Azure CLI repositories convention.
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))))
    return os.path.join(root, "temp", filename).replace('\\', '\\\\')


def install_helm_client():

    # Fetch system related info
    operating_system = platform.system().lower()
    machine_type = platform.machine()

    # Set helm binary download & install locations
    if(operating_system == 'windows'):
        download_location_string = f'.azure\\helm\\{consts.HELM_VERSION}\\helm-{consts.HELM_VERSION}-{operating_system}-amd64.zip'
        install_location_string = f'.azure\\helm\\{consts.HELM_VERSION}\\{operating_system}-amd64\\helm.exe'
        requestUri = f'{consts.HELM_STORAGE_URL}/helm/helm-{consts.HELM_VERSION}-{operating_system}-amd64.zip'
    elif(operating_system == 'linux' or operating_system == 'darwin'):
        download_location_string = f'.azure/helm/{consts.HELM_VERSION}/helm-{consts.HELM_VERSION}-{operating_system}-amd64.tar.gz'
        install_location_string = f'.azure/helm/{consts.HELM_VERSION}/{operating_system}-amd64/helm'
        requestUri = f'{consts.HELM_STORAGE_URL}/helm/helm-{consts.HELM_VERSION}-{operating_system}-amd64.tar.gz'
    else:
        logger.warning(f'The {operating_system} platform is not currently supported for installing helm client.')
        return

    download_location = os.path.expanduser(os.path.join('~', download_location_string))
    download_dir = os.path.dirname(download_location)
    install_location = os.path.expanduser(os.path.join('~', install_location_string))

    # Download compressed helm binary if not already present
    if not os.path.isfile(download_location):
        # Creating the helm folder if it doesnt exist
        if not os.path.exists(download_dir):
            try:
                os.makedirs(download_dir)
            except Exception as e:
                logger.warning("Failed to create helm directory." + str(e))
                return

        # Downloading compressed helm client executable
        try:
            response = urllib.request.urlopen(requestUri)
        except Exception as e:
            logger.warning("Failed to download helm client.")
            return

        responseContent = response.read()
        response.close()

        # Creating the compressed helm binaries
        try:
            with open(download_location, 'wb') as f:
                f.write(responseContent)
        except Exception as e:
            logger.warning("Failed to extract helm executable" + str(e))
            return

    # Extract compressed helm binary
    if not os.path.isfile(install_location):
        try:
            shutil.unpack_archive(download_location, download_dir)
            os.chmod(install_location, os.stat(install_location).st_mode | stat.S_IXUSR)
        except Exception as e:
            logger.warning("Failed to extract helm executable" + str(e))
            return

    return install_location


def install_kubectl_client():
    # Return kubectl client path set by user
    try:

        # Fetching the current directory where the cli installs the kubectl executable
        home_dir = os.path.expanduser('~')
        kubectl_filepath = os.path.join(home_dir, '.azure', 'kubectl-client')

        try:
            os.mkdir(kubectl_filepath)
        except FileExistsError:
            pass

        operating_system = platform.system().lower()
        # Setting path depending on the OS being used
        if operating_system == 'windows':
            kubectl_path = os.path.join(kubectl_filepath, 'kubectl.exe')
        elif operating_system == 'linux' or operating_system == 'darwin':
            kubectl_path = os.path.join(kubectl_filepath, 'kubectl')
        else:
            logger.warning(f'The {operating_system} platform is not currently supported for installing kubectl client.')
            return

        if os.path.isfile(kubectl_path):
            return kubectl_path

        # Downloading kubectl executable if its not present in the machine
        get_default_cli().invoke(['aks', 'install-cli', '--install-location', kubectl_path])
        # Return the path of the kubectl executable
        return kubectl_path

    except Exception as e:
        logger.warning("Unable to install kubectl. Error: " + str(e))
        return


class Connectedk8sScenarioTest(LiveScenarioTest):

    @live_only()
    @ResourceGroupPreparer(name_prefix='conk8stest', location=CONFIG['location'], random_name_length=16)
    def test_connect(self,resource_group):
        # os.environ.setdefault('HELMREGISTRY', 'mcr.microsoft.com/azurearck8s/batch1/preview/azure-arc-k8sagents:1.1.59-preview')
        
        managed_cluster_name = self.create_random_name(prefix='test-connect', length=24)
        kubeconfig="%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml'))
        self.kwargs.update({
            'rg': resource_group,
            'name': self.create_random_name(prefix='cc-', length=12),
            'kubeconfig': kubeconfig,
            'managed_cluster_name': managed_cluster_name,
            'location': CONFIG['location']
        })

        self.cmd('aks create -g {rg} -n {managed_cluster_name} --generate-ssh-keys')
        self.cmd('aks get-credentials -g {rg} -n {managed_cluster_name} -f {kubeconfig} --admin')
        self.cmd('connectedk8s connect -g {rg} -n {name} -l {location} --tags foo=doo --kube-config {kubeconfig} --kube-context {managed_cluster_name}-admin', checks=[
            self.check('tags.foo', 'doo'),
            self.check('resourceGroup', '{rg}'),
            self.check('name', '{name}')
        ])

        self.cmd('connectedk8s delete -g {rg} -n {name} --kube-config {kubeconfig} --kube-context {managed_cluster_name}-admin -y')
        self.cmd('aks delete -g {rg} -n {managed_cluster_name} -y')

        # delete the kube config
        os.remove("%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml')))


    @live_only()
    @ResourceGroupPreparer(name_prefix='conk8stest', location=CONFIG['location'], random_name_length=16)
    def test_forcedelete(self,resource_group):
        managed_cluster_name = self.create_random_name(prefix='test-force-delete', length=24)
        kubeconfig="%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml'))
        self.kwargs.update({
            'rg': resource_group,
            'name': self.create_random_name(prefix='cc-', length=12),
            'kubeconfig': kubeconfig,
            'managed_cluster_name': managed_cluster_name,
            'location': CONFIG['location']
        })

        self.cmd('aks create -g {rg} -n {managed_cluster_name} --generate-ssh-keys')
        self.cmd('aks get-credentials -g {rg} -n {managed_cluster_name} -f {kubeconfig} --admin')
        self.cmd('connectedk8s connect -g {rg} -n {name} -l {location} --tags foo=doo --kube-config {kubeconfig} --kube-context {managed_cluster_name}-admin', checks=[
            self.check('tags.foo', 'doo'),
            self.check('name', '{name}')
        ])
        self.cmd('connectedk8s show -g {rg} -n {name}', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', '{rg}'),
            self.check('tags.foo', 'doo')
        ])

        # Simulating the condition in which the azure-arc namespace got deleted
        # connectedk8s delete command fails in this case
        kubectl_client_location = install_kubectl_client()
        subprocess.run([kubectl_client_location, "delete", "namespace", "azure-arc","--kube-config", kubeconfig])

        # Using the force delete command
        # -y to supress the prompts
        self.cmd('connectedk8s delete -g {rg} -n {name} --kube-config {kubeconfig} --kube-context {managed_cluster_name}-admin --force -y')
        self.cmd('aks delete -g {rg} -n {managed_cluster_name} -y')

        # delete the kube config
        os.remove("%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml')))


    @live_only()
    @ResourceGroupPreparer(name_prefix='conk8stest', location=CONFIG['location'], random_name_length=16)
    def test_enable_disable_features(self,resource_group):
        # os.environ.setdefault('HELMREGISTRY', 'mcr.microsoft.com/azurearck8s/batch1/preview/azure-arc-k8sagents:1.1.59-preview')

        managed_cluster_name = self.create_random_name(prefix='test-enable-disable', length=24)
        kubeconfig="%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml'))

        if CONFIG['customLocationsOid'] is None or CONFIG['customLocationsOid'] == "":
            cli = get_default_cli()
            cli.invoke(["ad", "sp", "list", "--filter", "displayName eq 'Custom Locations RP'"])
            if cli.result.exit_code != 0:
                raise cli.result.error
            CONFIG['customLocationsOid'] = cli.result.result[0]["id"]

        self.kwargs.update({
            'rg': resource_group,
            'name': self.create_random_name(prefix='cc-', length=12),
            'kubeconfig': kubeconfig,
            'managed_cluster_name': managed_cluster_name,
            'custom_locations_oid': CONFIG['customLocationsOid'],
            'rbac_app_id': CONFIG['rbacAppId'],
            'rbac_app_secret': CONFIG['rbacAppSecret'],
            'location': CONFIG['location']
        })

        self.cmd('aks create -g {rg} -n {managed_cluster_name} --generate-ssh-keys')
        self.cmd('aks get-credentials -g {rg} -n {managed_cluster_name} -f {kubeconfig} --admin')
        self.cmd('connectedk8s connect -g {rg} -n {name} -l {location} --tags foo=doo --kube-config {kubeconfig} --kube-context {managed_cluster_name}-admin', checks=[
            self.check('tags.foo', 'doo'),
            self.check('name', '{name}')
        ])
        self.cmd('connectedk8s show -g {rg} -n {name}', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', '{rg}'),
            self.check('tags.foo', 'doo')
        ])

        os.environ.setdefault('KUBECONFIG', kubeconfig)
        helm_client_location = install_helm_client()
        cmd = [helm_client_location, 'get', 'values', 'azure-arc', "--namespace", "azure-arc-release", "-ojson"]

        # scenario-1 : custom loc disabled and custom loc enabled (should be successfull as there is no dependency)
        self.cmd('connectedk8s disable-features -n {name} -g {rg} --features custom-locations --kube-config {kubeconfig} --kube-context {managed_cluster_name}-admin -y')
        cmd_output = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
        _, error_helm_delete = cmd_output.communicate()
        assert(cmd_output.returncode == 0)
        changed_cmd = json.loads(cmd_output.communicate()[0].strip())
        assert(changed_cmd["systemDefaultValues"]['customLocations']['enabled'] == bool(0))

        self.cmd('connectedk8s enable-features -n {name} -g {rg} --features custom-locations --kube-config {kubeconfig} --kube-context {managed_cluster_name}-admin --custom-locations-oid {custom_locations_oid}')
        cmd_output1 = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
        _, error_helm_delete = cmd_output1.communicate()
        assert(cmd_output1.returncode == 0)
        enabled_cmd1 = json.loads(cmd_output1.communicate()[0].strip())
        assert(enabled_cmd1["systemDefaultValues"]['customLocations']['enabled'] == bool(1))

        # scenario-2 : custom loc is enabled , check if disabling cluster connect results in an error
        with self.assertRaisesRegexp(CLIError, "Disabling 'cluster-connect' feature is not allowed when 'custom-locations' feature is enabled."):
            self.cmd('connectedk8s disable-features -n {name} -g {rg} --features cluster-connect --kube-config {kubeconfig} --kube-context {managed_cluster_name}-admin -y')

        # scenario-3 : disable custom location and cluster connect , then enable custom loc and check if cluster connect also gets on
        self.cmd('connectedk8s disable-features -n {name} -g {rg} --features custom-locations --kube-config {kubeconfig} --kube-context {managed_cluster_name}-admin -y')
        cmd_output1 = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
        _, error_helm_delete = cmd_output1.communicate()
        assert(cmd_output1.returncode == 0)
        disabled_cmd1 = json.loads(cmd_output1.communicate()[0].strip())
        assert(disabled_cmd1["systemDefaultValues"]['customLocations']['enabled'] == bool(0))

        self.cmd('connectedk8s disable-features -n {name} -g {rg} --features cluster-connect --kube-config {kubeconfig} --kube-context {managed_cluster_name}-admin -y')
        cmd_output1 = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
        _, error_helm_delete = cmd_output1.communicate()
        assert(cmd_output1.returncode == 0)
        disabled_cmd1 = json.loads(cmd_output1.communicate()[0].strip())
        assert(disabled_cmd1["systemDefaultValues"]['clusterconnect-agent']['enabled'] == bool(0))

        self.cmd('connectedk8s enable-features -n {name} -g {rg} --features custom-locations --kube-config {kubeconfig} --kube-context {managed_cluster_name}-admin --custom-locations-oid {custom_locations_oid}')
        cmd_output1 = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
        _, error_helm_delete = cmd_output1.communicate()
        assert(cmd_output1.returncode == 0)
        enabled_cmd1 = json.loads(cmd_output1.communicate()[0].strip())
        assert(enabled_cmd1["systemDefaultValues"]['customLocations']['enabled'] == bool(1))
        assert(enabled_cmd1["systemDefaultValues"]['clusterconnect-agent']['enabled'] == bool(1))

        # scenario-4: azure rbac turned off and turning azure rbac on again using 1P
        self.cmd('connectedk8s disable-features -n {name} -g {rg} --features azure-rbac --kube-config {kubeconfig} --kube-context {managed_cluster_name}-admin -y')
        cmd_output1 = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
        _, error_helm_delete = cmd_output1.communicate()
        assert(cmd_output1.returncode == 0)
        disabled_cmd1 = json.loads(cmd_output1.communicate()[0].strip())
        assert(disabled_cmd1["systemDefaultValues"]['guard']['enabled'] == bool(0))

        self.cmd('az connectedk8s enable-features -n {name} -g {rg} --kube-config {kubeconfig} --kube-context {managed_cluster_name}-admin --features azure-rbac')

        # deleting the cluster
        self.cmd('connectedk8s delete -g {rg} -n {name} --kube-config {kubeconfig} --kube-context {managed_cluster_name}-admin -y')
        self.cmd('aks delete -g {rg} -n {managed_cluster_name} -y')

        # delete the kube config
        os.remove("%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml')))


    @live_only()
    @ResourceGroupPreparer(name_prefix='conk8stest', location=CONFIG['location'], random_name_length=16)
    def test_connectedk8s_list(self,resource_group):
        managed_cluster_name = self.create_random_name(prefix='first', length=24)
        managed_cluster_name_second = self.create_random_name(prefix='second', length=24)
        kubeconfig="%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml'))
        kubeconfigpls="%s" % (_get_test_data_file('pls-config.yaml'))
        name = self.create_random_name(prefix='cc-', length=12)
        name_second = self.create_random_name(prefix='cc-', length=12)
        managed_cluster_list=[]
        managed_cluster_list.append(name)
        managed_cluster_list.append(name_second)
        managed_cluster_list.sort()
        self.kwargs.update({
            'rg': resource_group,
            'name': name,
            'name_second': name_second,
            'kubeconfig': kubeconfig,
            'kubeconfigpls': kubeconfigpls,
            'managed_cluster_name': managed_cluster_name,
            'managed_cluster_name_second': managed_cluster_name_second,
            'location': CONFIG['location']
        })
        # create two clusters and then list the cluster names
        self.cmd('aks create -g {rg} -n {managed_cluster_name} --generate-ssh-keys')
        self.cmd('aks get-credentials -g {rg} -n {managed_cluster_name} -f {kubeconfig} --admin')
        self.cmd('connectedk8s connect -g {rg} -n {name} -l {location} --tags foo=doo --kube-config {kubeconfig} --kube-context {managed_cluster_name}-admin', checks=[
            self.check('tags.foo', 'doo'),
            self.check('name', '{name}')
        ])
        self.cmd('connectedk8s show -g {rg} -n {name}', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', '{rg}'),
            self.check('tags.foo', 'doo')
        ])

        self.cmd('aks create -g {rg} -n {managed_cluster_name_second} --generate-ssh-keys')
        self.cmd('aks get-credentials -g {rg} -n {managed_cluster_name_second} -f {kubeconfigpls} --admin')
        self.cmd('connectedk8s connect -g {rg} -n {name_second} -l {location} --tags foo=doo --kube-config {kubeconfigpls} --kube-context {managed_cluster_name_second}-admin', checks=[
            self.check('tags.foo', 'doo'),
            self.check('name', '{name_second}')
        ])
        self.cmd('connectedk8s show -g {rg} -n {name_second}', checks=[
            self.check('name', '{name_second}'),
            self.check('resourceGroup', '{rg}'),
            self.check('tags.foo', 'doo')
        ])

        clusters_list = self.cmd('az connectedk8s list -g {rg}').get_output_in_json()
        # fetching names of all clusters
        cluster_name_list=[]
        for clusterdesc in clusters_list:
            cluster_name_list.append(clusterdesc['name'])

        assert(len(cluster_name_list) == len(managed_cluster_list))

        # checking if the output is correct with original list of cluster names
        cluster_name_list.sort()
        for i in range(0,len(cluster_name_list)):
            assert(cluster_name_list[i] == managed_cluster_list[i])

        # deleting the clusters
        self.cmd('connectedk8s delete -g {rg} -n {name_second} --kube-config {kubeconfigpls} --kube-context {managed_cluster_name_second}-admin -y')
        self.cmd('aks delete -g {rg} -n {managed_cluster_name_second} -y')

        self.cmd('connectedk8s delete -g {rg} -n {name} --kube-config {kubeconfig} --kube-context {managed_cluster_name}-admin -y')
        self.cmd('aks delete -g {rg} -n {managed_cluster_name} -y')

        # delete the kube config
        os.remove("%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml')))
        os.remove("%s" % (_get_test_data_file('pls-config.yaml')))


    @live_only()
    @ResourceGroupPreparer(name_prefix='conk8stest', location=CONFIG['location'], random_name_length=16)
    def test_upgrade(self,resource_group):
        # os.environ.setdefault('HELMREGISTRY', 'mcr.microsoft.com/azurearck8s/batch1/preview/azure-arc-k8sagents:1.1.59-preview')

        managed_cluster_name = self.create_random_name(prefix='test-upgrade', length=24)
        kubeconfig="%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml'))
        self.kwargs.update({
            'name': self.create_random_name(prefix='cc-', length=12),
            'rg': resource_group,
            'kubeconfig': kubeconfig,
            'managed_cluster_name': managed_cluster_name,
            'location': CONFIG['location']
        })

        self.cmd('aks create -g {rg} -n {managed_cluster_name} --generate-ssh-keys')
        self.cmd('aks get-credentials -g {rg} -n {managed_cluster_name} -f {kubeconfig} --admin')

        self.cmd('connectedk8s connect -g {rg} -n {name} -l {location} --tags foo=doo --kube-config {kubeconfig} --kube-context {managed_cluster_name}-admin', checks=[
            self.check('tags.foo', 'doo'),
            self.check('name', '{name}')
        ])
        self.cmd('connectedk8s show -g {rg} -n {name}', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', '{rg}'),
            self.check('tags.foo', 'doo')
        ])

        os.environ.setdefault('KUBECONFIG', kubeconfig)
        helm_client_location = install_helm_client()
        cmd = [helm_client_location, 'get', 'values', 'azure-arc', "--namespace", "azure-arc-release", "-ojson"]

        with self.assertRaisesRegexp(CLIError, "az connectedk8s upgrade to manually upgrade agents and extensions is only supported when auto-upgrade is set to false"):
            self.cmd('connectedk8s upgrade -g {rg} -n {name} --kube-config {kubeconfig} --kube-context {managed_cluster_name}-admin')

        # scenario - Turning off auto upgrade ,then updating agnets to latest and check if the version of agents matches with latest version
        self.cmd('connectedk8s update -n {name} -g {rg} --auto-upgrade false --kube-config {kubeconfig} --kube-context {managed_cluster_name}-admin')
        cmd_output1 = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
        _, error_helm_delete = cmd_output1.communicate()
        assert(cmd_output1.returncode == 0)
        updated_cmd1 = json.loads(cmd_output1.communicate()[0].strip())
        assert(updated_cmd1["systemDefaultValues"]['azureArcAgents']['autoUpdate'] == bool(0))

        self.cmd('connectedk8s upgrade -g {rg} -n {name} --kube-config {kubeconfig} --kube-context {managed_cluster_name}-admin')
        response= requests.post(f'https://{CONFIG["location"]}.dp.kubernetesconfiguration.azure.com/azure-arc-k8sagents/GetLatestHelmPackagePath?api-version=2019-11-01-preview&releaseTrain=stable')
        jsonData = json.loads(response.text)
        repo_path=jsonData['repositoryPath']
        index_value = 0
        for ind in range (0,len(repo_path)):
            if  repo_path[ind]==':':
                break
            index_value += 1

        self.cmd('connectedk8s show -g {rg} -n {name}', checks=[
            self.check('agentVersion', jsonData['repositoryPath'][index_value+1:]),
        ])

        # scenario : changing the upgrade timeout
        self.cmd('connectedk8s upgrade -g {rg} -n {name} --upgrade-timeout 650 --kube-config {kubeconfig} --kube-context {managed_cluster_name}-admin')

        self.cmd('connectedk8s delete -g {rg} -n {name} --kube-config {kubeconfig} --kube-context {managed_cluster_name}-admin -y')
        self.cmd('aks delete -g {rg} -n {managed_cluster_name} -y')

        # delete the kube config
        os.remove("%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml')))


    @live_only()
    @ResourceGroupPreparer(name_prefix='conk8stest', location=CONFIG['location'], random_name_length=16)
    def test_update(self,resource_group):
        # os.environ.setdefault('HELMREGISTRY', 'mcr.microsoft.com/azurearck8s/batch1/preview/azure-arc-k8sagents:1.1.59-preview')

        managed_cluster_name = self.create_random_name(prefix='test-update', length=24)
        kubeconfig="%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml'))
        self.kwargs.update({
            'name': self.create_random_name(prefix='cc-', length=12),
            'kubeconfig': kubeconfig,
            'rg':resource_group,
            'managed_cluster_name': managed_cluster_name,
            'location': CONFIG['location']
        })

        self.cmd('aks create -g {rg} -n {managed_cluster_name} --generate-ssh-keys')
        self.cmd('aks get-credentials -g {rg} -n {managed_cluster_name} -f {kubeconfig} --admin')
        self.cmd('connectedk8s connect -g {rg} -n {name} -l {location} --tags foo=doo --kube-config {kubeconfig} --kube-context {managed_cluster_name}-admin', checks=[
            self.check('tags.foo', 'doo'),
            self.check('name', '{name}')
        ])
        self.cmd('connectedk8s show -g {rg} -n {name}', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', '{rg}'),
            self.check('tags.foo', 'doo')
        ])

        os.environ.setdefault('KUBECONFIG', kubeconfig)
        helm_client_location = install_helm_client()
        cmd = [helm_client_location, 'get', 'values', 'azure-arc', "--namespace", "azure-arc-release", "-ojson"]

        # scenario - auto-upgrade is turned on
        self.cmd('connectedk8s update -n {name} -g {rg} --auto-upgrade true --kube-config {kubeconfig} --kube-context {managed_cluster_name}-admin')
        cmd_output1 = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
        _, error_helm_delete = cmd_output1.communicate()
        assert(cmd_output1.returncode == 0)
        updated_cmd1 = json.loads(cmd_output1.communicate()[0].strip())
        assert(updated_cmd1["systemDefaultValues"]['azureArcAgents']['autoUpdate'] == bool(1))

        # scenario - auto-upgrade is turned off
        self.cmd('connectedk8s update -n {name} -g {rg} --auto-upgrade false --kube-config {kubeconfig} --kube-context {managed_cluster_name}-admin')
        cmd_output1 = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
        _, error_helm_delete = cmd_output1.communicate()
        assert(cmd_output1.returncode == 0)
        updated_cmd1 = json.loads(cmd_output1.communicate()[0].strip())
        assert(updated_cmd1["systemDefaultValues"]['azureArcAgents']['autoUpdate'] == bool(0))

        #scenario - updating the tags
        self.cmd('connectedk8s update -n {name} -g {rg} --kube-config {kubeconfig} --kube-context {managed_cluster_name}-admin --tags foo=moo')
        self.cmd('connectedk8s show -g {rg} -n {name}', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', '{rg}'),
            self.check('tags.foo', 'moo')
        ])

        self.cmd('connectedk8s delete -g {rg} -n {name} --kube-config {kubeconfig} --kube-context {managed_cluster_name}-admin -y')
        self.cmd('aks delete -g {rg} -n {managed_cluster_name} -y')

        # delete the kube config
        os.remove("%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml')))


    @live_only()
    @ResourceGroupPreparer(name_prefix='conk8stest', location=CONFIG['location'], random_name_length=16)
    def test_troubleshoot(self,resource_group):
        managed_cluster_name = self.create_random_name(prefix='test-troubleshoot', length=24)
        kubeconfig="%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml'))
        self.kwargs.update({
            'name': self.create_random_name(prefix='cc-', length=12),
            'kubeconfig': kubeconfig,
            'rg':resource_group,
            'managed_cluster_name': managed_cluster_name,
            'location': CONFIG['location']
        })

        self.cmd('aks create -g {rg} -n {managed_cluster_name} --generate-ssh-keys')
        self.cmd('aks get-credentials -g {rg} -n {managed_cluster_name} -f {kubeconfig} --admin')
        self.cmd('connectedk8s connect -g {rg} -n {name} -l {location} --tags foo=doo --kube-config {kubeconfig} --kube-context {managed_cluster_name}-admin', checks=[
            self.check('tags.foo', 'doo'),
            self.check('name', '{name}')
        ])
        self.cmd('connectedk8s show -g {rg} -n {name}', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', '{rg}'),
            self.check('tags.foo', 'doo')
        ])

        self.cmd('connectedk8s troubleshoot -g {rg} -n {name} --kube-config {kubeconfig} --kube-context {managed_cluster_name}-admin')

        self.cmd('connectedk8s delete -g {rg} -n {name} --kube-config {kubeconfig} --kube-context {managed_cluster_name}-admin -y')
        self.cmd('aks delete -g {rg} -n {managed_cluster_name} -y')

        # delete the kube config
        os.remove("%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml')))

    @live_only()
    @ResourceGroupPreparer(name_prefix='conk8stest', location=CONFIG['location'], random_name_length=16)
    def test_proxy(self,resource_group):
        managed_cluster_name = self.create_random_name(prefix='test-proxy', length=24)
        kubeconfig="%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml'))
        kubeconfig2="%s" % (_get_test_data_file(managed_cluster_name + '-config2.yaml'))
        name = self.create_random_name(prefix='cc-', length=12)
        self.kwargs.update({
            'name': name,
            'kubeconfig': kubeconfig,
            'kubeconfig2': kubeconfig2,
            'rg':resource_group,
            'managed_cluster_name': managed_cluster_name,
            'location': CONFIG['location']
        })

        self.cmd('aks create -g {rg} -n {managed_cluster_name} --generate-ssh-keys')
        self.cmd('aks get-credentials -g {rg} -n {managed_cluster_name} -f {kubeconfig} --admin')
        self.cmd('connectedk8s connect -g {rg} -n {name} -l {location} --tags foo=doo --kube-config {kubeconfig} --kube-context {managed_cluster_name}-admin', checks=[
            self.check('tags.foo', 'doo'),
            self.check('name', '{name}')
        ])
        self.cmd('connectedk8s show -g {rg} -n {name}', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', '{rg}'),
            self.check('tags.foo', 'doo')
        ])
        # starting the proxy
        script = ['az','connectedk8s', 'proxy', '-n', name, '-g', resource_group, '-f' , kubeconfig2, '&']
        process = subprocess.Popen(script, shell=True)

        # Time to let the kubeconfig merge in current context
        time.sleep(10)

        # Start running proxy as a background process
        process2 = subprocess.Popen(['disown %1'],shell=True)

        # testing if the proxy kubeconfig file is created
        process3 = ['sudo', 'cat', kubeconfig2]
        process3 = subprocess.run(process3,shell=True)

        # Cleaning up the cluster
        self.cmd('connectedk8s delete -g {rg} -n {name} --kube-config {kubeconfig} --kube-context {managed_cluster_name}-admin -y')
        self.cmd('aks delete -g {rg} -n {managed_cluster_name} -y')

        # delete the kube config
        os.remove("%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml')))