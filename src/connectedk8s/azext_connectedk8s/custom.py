# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from azure.cli.core.commands.client_factory import get_subscription_id
from azext_connectedk8s._client_factory import _graph_client_factory
from azext_connectedk8s._client_factory import cf_resource_groups
from azext_connectedk8s._client_factory import _resource_client_factory
from azext_connectedk8s._client_factory import _auth_client_factory
from azext_connectedk8s._multi_api_adaptor import MultiAPIAdaptor
from msrest.serialization import TZ_UTC
from dateutil.relativedelta import relativedelta
from azure.graphrbac.models import (PasswordCredential, ApplicationCreateParameters, ServicePrincipalCreateParameters)
from azure.graphrbac.operations.service_principals_operations import ServicePrincipalsOperations
from knack.log import get_logger
from azure.graphrbac.models import GraphErrorException
from azure.cli.core.api import get_config_dir
from azure.cli.core.util import sdk_no_wait
from msrestazure.azure_exceptions import CloudError
from kubernetes import client, config
import kubernetes.client
from kubernetes.client.rest import ApiException
import os
import subprocess
from subprocess import Popen, PIPE
import json
import uuid
import datetime
import time
from applicationinsights import TelemetryClient


logger = get_logger(__name__)
APP_KEY = '9a93ae7c-eaf8-4e21-a1f2-6a424cc48a44'


def create_connectedk8s(cmd, client, resource_group_name, cluster_name,
                        onboarding_spn_id=None, onboarding_spn_secret=None,
                        location=None, kube_config=None, kube_context=None, no_wait=False,
                        location_data_name=None, location_data_country_or_region=None,
                        location_data_district=None, location_data_city=None):
    print("Ensure that you have the latest helm version installed before proceeding to avoid unexpected errors.")
    print("This operation might take a while...\n")

    tc = TelemetryClient(APP_KEY)
    tc.track_event('testEvent')
    tc.flush()

    # Checking location data info
    if location_data_name is None:
        if ((location_data_country_or_region is not None) or (location_data_district is not None) or (location_data_city is not None)):
            raise CLIError("--location-data-name is required when providing location data info.")

    # Setting subscription id
    subscription_id = get_subscription_id(cmd.cli_ctx)

    resourceClient = _resource_client_factory(cmd.cli_ctx, subscription_id=subscription_id)

    # Resource group Creation
    if location is None:
        try:
            location = resourceClient.resource_groups.get(resource_group_name).location
        except:
            raise CLIError("Resource Group Creation Failed. Please provide location to create the Resource Group")

    rp_locations = []
    providerDetails = resourceClient.providers.get('Microsoft.Kubernetes')
    for resourceTypes in providerDetails.resource_types:
        if resourceTypes.resource_type == 'connectedClusters':
            rp_locations = [location.replace(" ", "").lower() for location in resourceTypes.locations]
            if location.lower() not in rp_locations:
                raise CLIError("The connected cluster resource creation is supported only in the following locations: " + ', '.join(map(str, rp_locations)) + ". Please use the --location flag to specify right location.")
            break
    
    if (resource_group_exists(cmd.cli_ctx, resource_group_name, subscription_id) is False):
        resource_group_params = {'location': location}
        try:
            resourceClient.resource_groups.create_or_update(resource_group_name, resource_group_params)
        except Exception as e:
            raise CLIError("Resource Group Creation Failed." + str(e.message))

    # SPN creation
    graph_client = _graph_client_factory(cmd.cli_ctx)
    onboarding_tenant_id = graph_client.config.tenant_id

    if (onboarding_spn_id is not None and onboarding_spn_secret is None):
        raise CLIError("Provide the onboarding spn secret.")

    if onboarding_spn_id is None:
        try:
            spn_list = list_owned_objects(graph_client.signed_in_user, 'servicePrincipal')
        except Exception as ex:
            raise CLIError("Problem loading the service principals. Check if you have sufficient access to list/create service principals. Error Message: " + str(ex))
        spn_appid_list = []
        for spn in spn_list:
            spn_appid_list.append(spn.app_id)
        file_name_connectedk8s = 'azureArcServicePrincipal.json'   # File containing SPN details
        principal_obj = load_acs_service_principal(subscription_id,
                                                   file_name=file_name_connectedk8s)  # Loading spn from file
        spn_present = True
        if principal_obj:
            if principal_obj.get('service_principal') not in spn_appid_list:
                erase_acs_service_principal(file_name=file_name_connectedk8s)
                spn_present = False
        if (principal_obj and spn_present is True):
            onboarding_spn_id = principal_obj.get('service_principal')
            onboarding_spn_secret = principal_obj.get('client_secret')
        else:
            #print("Creating New SPN ...")
            graph_client = _graph_client_factory(cmd.cli_ctx)
            role_client = _auth_client_factory(cmd.cli_ctx).role_assignments
            scopes = ['/subscriptions/' + role_client.config.subscription_id]
            years = 1
            app_start_date = datetime.datetime.now(TZ_UTC)
            app_end_date = app_start_date + relativedelta(years=years)
            app_display_name = ('cluster-onboarding-spn-' + app_start_date.strftime('%Y-%m-%d-%H-%M-%S'))
            name = 'http://' + app_display_name
            password = str(uuid.uuid4())
            aad_application = create_aad_application(cmd,
                                                 display_name=app_display_name,
                                                 homepage='https://' + app_display_name,
                                                 identifier_uris=[name],
                                                 available_to_other_tenants=False,
                                                 password=password, key_value=None,
                                                 start_date=app_start_date,
                                                 end_date=app_end_date,
                                                 credential_description='rbac')
            _RETRY_TIMES = 36
            app_id = aad_application.app_id
            aad_sp = None
            for l in range(0, _RETRY_TIMES):
                try:
                    aad_sp = _create_service_principal(cmd.cli_ctx, app_id, resolve_app=False)
                    break
                except Exception as ex:  # pylint: disable=broad-except
                    if l < _RETRY_TIMES and (
                            ' does not reference ' in str(ex) or ' does not exist ' in str(ex)):
                        time.sleep(5)
                        logger.warning('Retrying service principal creation: %s/%s', l + 1, _RETRY_TIMES)
                    else:
                        logger.warning(
                            "Creating service principal failed for appid '%s'. Trace followed:\n%s",
                            name, ex.response.headers if hasattr(ex, 'response') else ex)   # pylint: disable=no-member
                        raise
            # correct
            

            # Creating Role Binding
            role = 'Kubernetes Cluster - Azure Arc Onborading Role'
            sp_oid = aad_sp.object_id
            for scope in scopes:
                for l in range(0, _RETRY_TIMES):
                    try:
                        _create_role_assignment(cmd.cli_ctx, role, sp_oid, None, scope, resolve_assignee=False)
                        break
                    except Exception as ex:
                        if l < _RETRY_TIMES and ' does not exist in the directory ' in str(ex):
                            time.sleep(5)
                            #logger.warning('  Retrying role assignment creation: %s/%s', l + 1, _RETRY_TIMES)
                            continue
                        elif _error_caused_by_role_assignment_exists(ex):
                            #logger.warning('  Role assignment already exits.\n')
                            break
                        else:
                            if getattr(ex, 'response', None) is not None:
                                logger.warning('  role assignment response headers: %s\n', ex.response.headers)  # pylint: disable=no-member
                        raise
            onboarding_spn_id = app_id
            onboarding_spn_secret = password
            store_acs_service_principal(subscription_id, onboarding_spn_secret, onboarding_spn_id, file_name=file_name_connectedk8s)

    # Setting kubeconfig
    if kube_config is None:
        kube_config = os.getenv('KUBECONFIG')
        if kube_config is None:
            kube_config = os.path.join(os.path.expanduser('~'), '.kube', 'config')

    # Removing quotes from kubeconfig path
    if (kube_config.startswith("'") or kube_config.startswith('"')):
        kube_config = kube_config[1:]
    if (kube_config.endswith("'") or kube_config.endswith('"')):
        kube_config = kube_config[:-1]

    # Loading the kubeconfig file in kubernetes client configuration
    configuration = kubernetes.client.Configuration()
    try:
        config.load_kube_config(config_file=kube_config, context=kube_context, client_configuration=configuration)
    except Exception as e:
        raise CLIError("Problem loading the kubeconfig file." + str(e))

    # Checking the connection to kubernetes cluster. This check was added to avoid large timeouts when connecting to AAD Enabled AKS clusters if the user had not logged in.
    api_instance = kubernetes.client.NetworkingV1Api(kubernetes.client.ApiClient(configuration))
    try:
        api_response = api_instance.get_api_resources()
    except ApiException as e:
        print("Exception when calling NetworkingV1Api->get_api_resources: %s\n" % e)
        raise CLIError("If you are using AAD Enabled cluster, check if you have logged in to the cluster properly and try again")

    
    # Checking helm installation
    if kube_context is None:
        cmd = ["helm", "--kubeconfig", kube_config, "--debug"]
    else:
        cmd = ["helm", "--kubeconfig", kube_config, "--kube-context", kube_context, "--debug"]
    try:
        response = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
        output, error = response.communicate()
        if response.returncode != 0:
            if "unknown flag" in error.decode("ascii"):
                raise CLIError("Please install the latest version of helm")
            raise CLIError(error.decode("ascii"))
    except FileNotFoundError:
        raise CLIError("Helm is not installed or requires elevated permissions. Please ensure that you have the latest version of helm installed on your machine.")
    except subprocess.CalledProcessError as e2:
        e2.output = e2.output.decode("ascii")
        print(e2.output)

    # Check helm version
    if kube_context is None:
        cmd = ["helm", "version", "--short", "--kubeconfig", kube_config]
    else:
        cmd = ["helm", "version", "--short", "--kubeconfig", kube_config, "--kube-context", kube_context]
    response = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
    output, error = response.communicate()
    if response.returncode != 0:
        raise CLIError("Unable to determine helm version: " + error.decode("ascii"))
    else:
        if "v2" in output.decode("ascii"):
            raise CLIError("Please install the latest version of helm and then try again")

    # Check Release Existance
    if kube_context is None:    
        cmd_list = ["helm", "list", "-a", "--all-namespaces", "--output", "json", "--kubeconfig", kube_config]
    else:
        cmd_list = ["helm", "list", "-a", "--all-namespaces", "--output", "json", "--kubeconfig", kube_config, "--kube-context", kube_context]
    response_list = subprocess.Popen(cmd_list, stdout=PIPE, stderr=PIPE)
    output_list, error_list = response_list.communicate()
    if response_list.returncode != 0:
        raise CLIError(error_list.decode("ascii"))
    else:
        output_list = output_list.decode("ascii")
        output_list = json.loads(output_list)
        release_name_list = []
        for release in output_list:
            release_name_list.append(release['name'])
        if "azure-arc" in release_name_list:
            # Loading config map
            api_instance = kubernetes.client.CoreV1Api(kubernetes.client.ApiClient(configuration))
            namespace = 'azure-arc'
            try:
                api_response = api_instance.list_namespaced_config_map(namespace)
            except ApiException as e:
                print("Exception when calling CoreV1Api->list_namespaced_config_map: %s\n" % e)
            config_present = False
            for configmap in api_response.items:
                if configmap.metadata.name == 'azure-clusterconfig':
                    config_present = True
                    if (configmap.data["AZURE_RESOURCE_GROUP"].lower() == resource_group_name.lower() and configmap.data["AZURE_RESOURCE_NAME"].lower() == cluster_name.lower()):
                        raise CLIError("Agents corresponding to the provided resource are already installed on this cluster. If the connected cluster resource does not exist, run 'az connectedk8s delete -g {} -n {}' to delete the agents and then try creating again.".format(resource_group_name, cluster_name))
                    else:
                        raise CLIError("Resource creation failed. Agents corresponding to some other resource are already installed on this cluster. Agents installed on this cluster correspond to the resource group name '{}' and resource name '{}'.".format(configmap.data["AZURE_RESOURCE_GROUP"], configmap.data["AZURE_RESOURCE_NAME"]))
            if config_present is False:
                raise CLIError("Helm release named 'azure-arc' is already present but the azure-arc agent pods are either missing or deployed unsuccessfully.")
    
    # Adding helm repo
    if kube_context is None:
        cmd1 = ["helm", "repo", "add", "azurearcfork8s", "https://azurearcfork8s.azurecr.io/helm/v1/repo", "--kubeconfig", kube_config]
    else:
        cmd1 = ["helm", "repo", "add", "azurearcfork8s", "https://azurearcfork8s.azurecr.io/helm/v1/repo", "--kubeconfig", kube_config, "--kube-context", kube_context]
    response1 = subprocess.Popen(cmd1, stdout=PIPE, stderr=PIPE)
    output1, error1 = response1.communicate()
    if response1.returncode != 0:
        raise CLIError("Helm unable to add repository: " + error1.decode("ascii"))

    # Install agents
    cmd4 = ["helm", "install", "azure-arc", "azurearcfork8s/azure-arc-k8sagents", "--set", "global.subscriptionId={}".format(subscription_id), "--set", "global.resourceGroupName={}".format(resource_group_name), "--set", "global.resourceName={}".format(cluster_name), "--set", "global.location={}".format(location), "--set", "global.tenantId={}".format(onboarding_tenant_id), "--set", "global.clientId={}".format(onboarding_spn_id), "--set", "global.clientSecret={}".format(onboarding_spn_secret), "--kubeconfig", kube_config, "--output", "json"]
    if kube_context:
        cmd.extend(["--kube-context", kube_context])
    if location_data_name:
        cmd.extend(["--set", "global.locationDataName={}".format(location_data_name)])
    if location_data_country_or_region:
        cmd.extend(["--set", "global.locationDataCountryOrRegion={}".format(location_data_country_or_region)])
    if location_data_district:
        cmd.extend(["--set", "global.locationDataDistrict={}".format(location_data_district)])
    if location_data_city:
        cmd.extend(["--set", "global.locationDataCity={}".format(location_data_city)])
    
    #if kube_context is None:
    #    cmd4 = ["helm", "install", "azure-arc", "azurearcfork8s/azure-arc-k8sagents", "--set", "global.subscriptionId={}".format(subscription_id), "--set", "global.resourceGroupName={}".format(resource_group_name), "--set", "global.resourceName={}".format(cluster_name), "--set", "global.location={}".format(location), "--set", "global.tenantId={}".format(onboarding_tenant_id), "--set", "global.clientId={}".format(onboarding_spn_id), "--set", "global.clientSecret={}".format(onboarding_spn_secret), "--kubeconfig", kube_config, "--output", "json"]
    #else:
    #    cmd4 = ["helm", "install", "azure-arc", "azurearcfork8s/azure-arc-k8sagents", "--set", "global.subscriptionId={}".format(subscription_id), "--set", "global.resourceGroupName={}".format(resource_group_name), "--set", "global.resourceName={}".format(cluster_name), "--set", "global.location={}".format(location), "--set", "global.tenantId={}".format(onboarding_tenant_id), "--set", "global.clientId={}".format(onboarding_spn_id), "--set", "global.clientSecret={}".format(onboarding_spn_secret), "--kubeconfig", kube_config, "--kube-context", kube_context, "--output", "json"]
    response4 = subprocess.Popen(cmd4, stdout=PIPE, stderr=PIPE)
    output4, error4 = response4.communicate()
    if response4.returncode != 0:
        raise CLIError("Unable to install helm release: " + error4.decode("ascii")) 
    
    if no_wait is True:
        print("Resource creation request accepted. Please run 'kubectl get pods -n azure-arc' to see whether the pods are in a running state and run 'az connectedk8s show -g {} -n {}' to check if the resource was created successfully".format(resource_group_name, cluster_name))
        return
    time.sleep(5)
    print()
    
    # Checking pod status 
    api_instance = kubernetes.client.CoreV1Api(kubernetes.client.ApiClient(configuration))
    namespace = 'azure-arc'
    connect_agent_state = None
    timeout = time.time() + 120
    found_running = 0
    while connect_agent_state is None:
        if(time.time()>timeout):
            break
        try:
            api_response = api_instance.list_namespaced_pod(namespace)
            #print(api_response.items)
        except ApiException as e:
            print("Exception when calling CoreV1Api->list_namespaced_pod: %s\n" % e)
        for pod in api_response.items:
            for container_status in pod.status.container_statuses:
                if container_status.name == 'connect-agent':
                    connect_agent_state = container_status.state.running
                    if connect_agent_state is not None:
                        found_running = found_running + 1
                        time.sleep(2)
        if found_running > 5:
            break
        else:
            connect_agent_state = None
    if connect_agent_state is None:
        raise CLIError("There was a problem with connect-agent deployment. Please run 'kubectl -n azure-arc logs -l app.kubernetes.io/component=connect-agent' to debug the error.")

    # Checking the status of connected cluster resource
    max_retry = 30
    retry_exception = Exception(None)
    for _ in range(0, max_retry):
        try:
            return sdk_no_wait(no_wait, client.create, resource_group_name=resource_group_name, cluster_name=cluster_name)
        except CloudError as ex:
            retry_exception = ex
            if ('not found' in ex.message or 'Not Found' in ex.message):
                time.sleep(3)
            else:
                raise ex
    if ('not found' in retry_exception.message or 'Not Found' in retry_exception.message):
        raise CLIError("Resource Creation Failed. Please run 'kubectl get pods -n azure-arc' to see whether the connect agent pod is in running state. If not, run 'kubectl -n azure-arc logs -l app.kubernetes.io/component=connect-agent' to debug the error.")
    else:
        raise retry_exception


def resource_group_exists(ctx, resource_group_name, subscription_id=None):
    groups = cf_resource_groups(ctx, subscription_id=subscription_id)
    try:
        rg = groups.get(resource_group_name)
        return True
    except:
        return False


def erase_acs_service_principal(file_name='acsServicePrincipal.json'):
    config_path = os.path.join(get_config_dir(), file_name)
    open(config_path, 'w').close()


def load_acs_service_principal(subscription_id, file_name='acsServicePrincipal.json'):
    config_path = os.path.join(get_config_dir(), file_name)
    config = load_service_principals(config_path)
    if not config:
        return None
    return config.get(subscription_id)


def load_service_principals(config_path):
    if not os.path.exists(config_path):
        return None
    fd = os.open(config_path, os.O_RDONLY)
    try:
        with os.fdopen(fd) as f:
            return json.loads(f.read())
    except:  # pylint: disable=bare-except
        return None


def store_acs_service_principal(subscription_id, client_secret, service_principal,
                                file_name='acsServicePrincipal.json'):
    obj = {}
    if client_secret:
        obj['client_secret'] = client_secret
    if service_principal:
        obj['service_principal'] = service_principal

    config_path = os.path.join(get_config_dir(), file_name)
    full_config = load_service_principals(config_path=config_path)
    if not full_config:
        full_config = {}
    full_config[subscription_id] = obj

    with os.fdopen(os.open(config_path, os.O_RDWR | os.O_CREAT | os.O_TRUNC, 0o600),
                   'w+') as spFile:
        json.dump(full_config, spFile)


def list_owned_objects(client, object_type=None):
    result = client.list_owned_objects()
    if object_type:
        result = [r for r in result if r.object_type and r.object_type.lower() == object_type.lower()]
    return result


def get_connectedk8s(cmd, client, resource_group_name, cluster_name):
    return client.get(resource_group_name, cluster_name)


def list_connectedk8s(cmd, client, resource_group_name=None):
    if resource_group_name is None:
        return client.list_by_subscription()
    return client.list_by_resource_group(resource_group_name)


def delete_connectedk8s(cmd, client, resource_group_name, cluster_name, kube_config=None, kube_context=None):
    print("Ensure that you have the latest helm version installed before proceeding to avoid unexpected errors.")
    print("This operation might take a while ...\n")
    
    # ARM delete Connected Cluster Resource
    client.delete_cluster(resource_group_name, cluster_name)

    # Setting kubeconfig
    if kube_config is None:
        kube_config = os.getenv('KUBECONFIG')
        if kube_config is None:
            kube_config = os.path.join(os.path.expanduser('~'), '.kube', 'config')

    # Loading the kubeconfig file in kubernetes client configuration
    configuration = kubernetes.client.Configuration()
    try:
        config.load_kube_config(config_file=kube_config, context=kube_context, client_configuration=configuration)
    except Exception as e:
        print("Problem loading the kubeconfig file.")
        raise CLIError(e)

    # Checking the connection to kubernetes cluster. This check was added to avoid large timeouts when connecting to AAD Enabled AKS clusters if the user had not logged in.
    api_instance = kubernetes.client.NetworkingV1Api(kubernetes.client.ApiClient(configuration))
    try:
        api_response = api_instance.get_api_resources()
    except ApiException as e:
        print("Exception when calling NetworkingV1Api->get_api_resources: %s\n" % e)
        raise CLIError("If you are using AAD Enabled cluster, check if you have logged in to the cluster properly and try again")

    # Checking helm installation
    if kube_context is None:
        cmd = ["helm", "--kubeconfig", kube_config, "--debug"]
    else:
        cmd = ["helm", "--kubeconfig", kube_config, "--kube-context", kube_context, "--debug"]
    try:
        response = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
        output, error = response.communicate()
        if response.returncode != 0:
            if "unknown flag" in error.decode("ascii"):
                raise CLIError("Please install the latest version of helm")
            raise CLIError(error.decode("ascii"))
    except FileNotFoundError:
        raise CLIError("Helm is not installed or requires elevated permissions.")
    except subprocess.CalledProcessError as e2:
        e2.output = e2.output.decode("ascii")
        print(e2.output)

    # Check helm version
    if kube_context is None:
        cmd = ["helm", "version", "--short", "--kubeconfig", kube_config]
    else:
        cmd = ["helm", "version", "--short", "--kubeconfig", kube_config, "--kube-context", kube_context]
    response = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
    output, error = response.communicate()
    if response.returncode != 0:
        raise CLIError("Unable to determine helm version: " + error.decode("ascii"))
    else:
        if "v2" in output.decode("ascii"):
            raise CLIError("Please install the latest version of helm and then try again")

    # Check Release Existance
    release_namespace = None
    if kube_context is None:    
        cmd_list = ["helm", "list", "-a", "--all-namespaces", "--output", "json", "--kubeconfig", kube_config]
    else:
        cmd_list = ["helm", "list", "-a", "--all-namespaces", "--output", "json", "--kubeconfig", kube_config, "--kube-context", kube_context]
    response_list = subprocess.Popen(cmd_list, stdout=PIPE, stderr=PIPE)
    output_list, error_list = response_list.communicate()
    if response_list.returncode != 0:
        raise CLIError(error_list.decode("ascii"))
    else:
        output_list = output_list.decode("ascii")
        output_list = json.loads(output_list)
        for release in output_list:
            if release['name'] == 'azure-arc':
                release_namespace = release['namespace']
                break
        if release_namespace is None:
            return

    # Loading config map
    api_instance = kubernetes.client.CoreV1Api(kubernetes.client.ApiClient(configuration))
    namespace = 'azure-arc'
    try:
        api_response = api_instance.list_namespaced_config_map(namespace)
    except ApiException as e:
        print("Exception when calling CoreV1Api->list_namespaced_config_map: %s\n" % e)
    for configmap in api_response.items:
        if configmap.metadata.name == 'azure-clusterconfig':
            if (configmap.data["AZURE_RESOURCE_GROUP"].lower() == resource_group_name.lower() and configmap.data["AZURE_RESOURCE_NAME"].lower() == cluster_name.lower()):
                break
            else:
                raise CLIError("The kube config does not correspond to the connected cluster resource provided. Agents installed on this cluster correspond to the resource group name '{}' and resource name '{}'.".format(configmap.data["AZURE_RESOURCE_GROUP"], configmap.data["AZURE_RESOURCE_NAME"]))

    # Deleting the azure-arc agents
    if kube_context is None:
        cmd1 = ["helm", "delete", "azure-arc", "--namespace", release_namespace, "--kubeconfig", kube_config]
    else:
        cmd1 = ["helm", "delete", "azure-arc", "--namespace", release_namespace, "--kubeconfig", kube_config, "--kube-context", kube_context]
    response1 = subprocess.Popen(cmd1, stdout=PIPE, stderr=PIPE)
    output1, error1 = response1.communicate()
    if response1.returncode != 0:
        raise CLIError("Helm release deletion failed: " + error1.decode("ascii"))
    return


def update_connectedk8s(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance


def create_aad_application(cmd, display_name, homepage=None, identifier_uris=None,  # pylint: disable=too-many-locals
                       available_to_other_tenants=False, password=None, reply_urls=None,
                       key_value=None, key_type=None, key_usage=None, start_date=None, end_date=None,
                       oauth2_allow_implicit_flow=None, required_resource_accesses=None, native_app=None,
                       credential_description=None, app_roles=None):
    graph_client = _graph_client_factory(cmd.cli_ctx)
    password_creds = [PasswordCredential(start_date=start_date,
                                         end_date=end_date, key_id=str(uuid.uuid4()),
                                         value=password,
                                         custom_key_identifier=None)]
    app_create_param = ApplicationCreateParameters(available_to_other_tenants=False,
                                                   display_name=display_name,
                                                   identifier_uris=identifier_uris,
                                                   homepage='https://' + display_name,
                                                   reply_urls=None,
                                                   key_credentials=None,
                                                   password_credentials=password_creds,
                                                   oauth2_allow_implicit_flow=None,
                                                   required_resource_access=None,
                                                   app_roles=None)
    try:
        result = graph_client.applications.create(app_create_param)
    except GraphErrorException as ex:
        if 'insufficient privileges' in str(ex).lower():
            link = 'https://docs.microsoft.com/azure/azure-resource-manager/resource-group-create-service-principal-portal'  # pylint: disable=line-too-long
            raise CLIError("Directory permission is needed for the current user to register the application. "
                           "For how to configure, please refer '{}'. Original error: {}".format(link, ex))
        raise
    return result


def _create_service_principal(cli_ctx, identifier, resolve_app=True):
    client = _graph_client_factory(cli_ctx)
    app_id = identifier
    if resolve_app:
        if _is_guid(identifier):
            result = list(client.applications.list(filter="appId eq '{}'".format(identifier)))
        else:
            result = list(client.applications.list(
                filter="identifierUris/any(s:s eq '{}')".format(identifier)))

        try:
            if not result:  # assume we get an object id
                result = [client.applications.get(identifier)]
            app_id = result[0].app_id
        except GraphErrorException:
            pass  # fallback to appid (maybe from an external tenant?)

    return client.service_principals.create(ServicePrincipalCreateParameters(app_id=app_id, account_enabled=True))


def _is_guid(guid):
    try:
        uuid.UUID(guid)
        return True
    except ValueError:
        return False


def _error_caused_by_role_assignment_exists(ex):
    return getattr(ex, 'status_code', None) == 409 and 'role assignment already exists' in ex.message


def _create_role_assignment(cli_ctx, role, assignee, resource_group_name=None, scope=None,
                            resolve_assignee=True, assignee_principal_type=None):
    factory = _auth_client_factory(cli_ctx, scope)
    assignments_client = factory.role_assignments
    definitions_client = factory.role_definitions
    role = '34e09817-6cbe-4d01-b1a2-e0eac5743d41'
    role_id = '/subscriptions/{}/providers/Microsoft.Authorization/roleDefinitions/{}'.format(definitions_client.config.subscription_id, role)
    object_id = assignee
    worker = MultiAPIAdaptor(cli_ctx)
    return worker.create_role_assignment(assignments_client, uuid.uuid4(), role_id,
                                         object_id, scope, assignee_principal_type)
