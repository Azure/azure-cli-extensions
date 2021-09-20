import pytest
import requests
import time

from kubernetes import client
from .common.kubernetes_crd_utility import watch_crd_instance
from .common.kubernetes_pod_utility import watch_pod_status, watch_pod_logs
from .common.kubernetes_configmap_utility import get_namespaced_configmap
from .common.kubernetes_configuration_utility import show_kubernetes_configuration
from .common.kubernetes_secret_utility import watch_kubernetes_secret
from .common.kubernetes_namespace_utility import watch_namespace
from .common.results_utility import append_result_output


# Function to fetch the helm chart path.
def get_helm_registry(token, location, release_train):
    get_chart_location_url = "https://{}.dp.kubernetesconfiguration.azure.com/azure-arc-k8sagents/GetLatestHelmPackagePath?api-version=2019-11-01-preview".format(location)
    query_parameters = {}
    query_parameters['releaseTrain'] = release_train
    header_parameters = {}
    header_parameters['Authorization'] = "Bearer {}".format(str(token))
    try:
        response = requests.post(get_chart_location_url, params=query_parameters, headers=header_parameters)
    except Exception as e:
        pytest.fail("Error while fetching helm chart registry path: " + str(e))
    if response.status_code == 200:
        return response.json().get('repositoryPath')
    pytest.fail("Error while fetching helm chart registry path: {}".format(str(response.json())))


# This function checks the status of the namespaces of the kubernetes cluster. The namespaces to be monitored are passed in as a list.
def check_namespace_status(outfile=None, namespace_list=None, timeout=300):
    namespace_dict = {}
    for namespace in namespace_list:
        namespace_dict[namespace] = 0
    append_result_output("Namespace dict: {}\n".format(namespace_dict), outfile)
    print("Generated the namespace dictionary.")

    # THe callback function to check the namespace status
    def namespace_event_callback(event):
        try:
            append_result_output("{}\n".format(event), outfile)
            namespace_name = event['raw_object'].get('metadata').get('name')
            namespace_status = event['raw_object'].get('status')
            if not namespace_status:
                return False
            if namespace_status.get('phase') == 'Active':
                namespace_dict[namespace_name] = 1
            if all(ele == 1 for ele in list(namespace_dict.values())):
                return True
            return False
        except Exception as e:
            pytest.fail("Error occured while processing the namespace event: " + str(e))
    
    # Checking the namespace status
    api_instance = client.CoreV1Api()
    watch_namespace(api_instance, timeout, namespace_event_callback)
             

# This function checks the status of pods in a given namespace. The pods to be monitored are identified using the pod label list parameter.
def check_kubernetes_pods_status(pod_namespace, outfile=None, pod_label_list=None, timeout=300):
    pod_label_dict = {}
    if pod_label_list:  # This parameter is a list of label values to identify the pods that we want to monitor in the given namespace
        for pod_label in pod_label_list:
            pod_label_dict[pod_label] = 0
    append_result_output("Pod label dict: {}\n".format(pod_label_dict), outfile)
    print("Generated the pods dictionary.")

    # The callback function to check if the pod is in running state
    def pod_event_callback(event):
        try:
            append_result_output("{}\n".format(event), outfile)
            pod_status = event['raw_object'].get('status')
            pod_metadata = event['raw_object'].get('metadata')
            pod_metadata_labels = pod_metadata.get('labels')
            if not pod_metadata_labels:
                return False

            pod_metadata_label_values = pod_metadata_labels.values()  # It contains the list of all label values for the pod whose event was called.
            current_label_value = None  # This label value will be common in pod event and label list provided and will be monitored
            for label_value in pod_metadata_label_values:
                if label_value in pod_label_dict:
                    current_label_value = label_value
            if not current_label_value:
                return False

            if pod_status.get('containerStatuses'):
                for container in pod_status.get('containerStatuses'):
                    if container.get('restartCount') > 0:
                        pytest.fail("The pod {} was restarted. Please see the pod logs for more info.".format(container.get('name')))
                    if not container.get('state').get('running'):
                        pod_label_dict[current_label_value] = 0
                        return False
                    else:
                        pod_label_dict[current_label_value] = 1
            if all(ele == 1 for ele in list(pod_label_dict.values())):
                return True
            return False
        except Exception as e:
            pytest.fail("Error occured while processing the pod event: " + str(e))

    # Checking status of all pods
    if pod_label_dict:
        api_instance = client.CoreV1Api()
        watch_pod_status(api_instance, pod_namespace, timeout, pod_event_callback)


# Function to check if the crd instance status has been updated with the status fields mentioned in the 'status_list' parameter
def check_kubernetes_crd_status(crd_group, crd_version, crd_namespace, crd_plural, crd_name, status_dict={}, timeout=300):
    # The callback function to check if the crd event received has been updated with the status fields
    def crd_event_callback(event):
        try:
            # append_result_output("{}\n".format(event), outfile)
            crd_status = event['raw_object'].get('status')
            if not crd_status:
                return False
            for status_field in status_dict:
                if not crd_status.get(status_field):
                    return False
                if status_field == "lastConnectivityTime" or status_field == "managedIdentityCertificateExpirationTime":
                    continue
                if crd_status.get(status_field) != status_dict.get(status_field):
                    pytest.fail("The CRD instance status has been updated with incorrect value for '{}' field.".format(status_field))
            return True
        except Exception as e:
            pytest.fail("Error occured while processing crd event: " + str(e))

    # Checking if CRD instance has been updated with status fields
    api_instance = client.CustomObjectsApi()
    watch_crd_instance(api_instance, crd_group, crd_version, crd_namespace, crd_plural, crd_name, timeout, crd_event_callback)


# Function to monitor the pod logs. It will ensure that are logs passed in the 'log_list' parameter are present in the container logs.
def check_kubernetes_pod_logs(pod_namespace, pod_name, container_name, logs_list=None, error_logs_list=None, outfile=None, timeout=300):
    logs_dict = {}
    for log in logs_list:
        logs_dict[log] = 0
    print("Generated the logs dictionary.")

    # The callback function to examine the pod log
    def pod_log_event_callback(event):
        try:
            append_result_output("{}\n".format(event), outfile)
            for error_log in error_logs_list:
                if error_log in event:
                    pytest.fail("Error log found: " + event)
            for log in logs_dict:
                if log in event:
                    logs_dict[log] = 1
            if all(ele == 1 for ele in list(logs_dict.values())):
                return True
            return False
        except Exception as e:
            pytest.fail("Error occured while processing pod log event: " + str(e))

    # Checking the pod logs
    api_instance = client.CoreV1Api()
    watch_pod_logs(api_instance, pod_namespace, pod_name, container_name, timeout, pod_log_event_callback)


# Function to check the compliance state of the kubernetes configuration
def check_kubernetes_configuration_state(kc_client, resource_group, cluster_rp, cluster_type, cluster_name, configuration_name,
                                         outfile=None, timeout_seconds=300):
    timeout = time.time() + timeout_seconds
    while True:
        get_kc_response = show_kubernetes_configuration(kc_client, resource_group, cluster_rp, cluster_type, cluster_name, configuration_name)
        provisioning_state = get_kc_response.provisioning_state
        append_result_output("Provisioning State: {}\n".format(provisioning_state), outfile)
        compliance_state = get_kc_response.compliance_status.compliance_state
        append_result_output("Compliance State: {}\n".format(compliance_state), outfile)
        if (provisioning_state == 'Succeeded' and compliance_state == 'Installed'):
            break
        if (provisioning_state == 'Failed' or provisioning_state == 'Cancelled'):
            pytest.fail("ERROR: The kubernetes configuration creation finished with terminal provisioning state {}. ".format(provisioning_state))
        if (compliance_state == 'Failed' or compliance_state == 'Noncompliant'):
            pytest.fail("ERROR: The kubernetes configuration creation finished with terminal provisioning state {}. ".format(compliance_state))
        if time.time() > timeout:
            pytest.fail("ERROR: Timeout. The kubernetes configuration is in {} provisioning state and {} compliance state.".format(provisioning_state, compliance_state))
        time.sleep(10)


# Function to monitor the kubernetes secret. It will determine if the secret has been successfully created.
def check_kubernetes_secret(secret_namespace, secret_name, timeout=300):
    # The callback function to check if the secret event received has secret data
    def secret_event_callback(event):
        try:
            secret_data = event['raw_object'].get('data')
            if not secret_data:
                return False   
            return True
        except Exception as e:
            pytest.fail("Error occured while processing secret event: " + str(e))

    # Checking the kubernetes secret
    api_instance = client.CoreV1Api()
    watch_kubernetes_secret(api_instance, secret_namespace, secret_name, timeout, secret_event_callback)


# Function to monitor the kubernetes secret. It will determine if the secret has been successfully created.
def check_kubernetes_secret_with_key(secret_namespace, secret_name, key_name, timeout=300):
    # The callback function to check if the secret event received has secret data
    def secret_event_callback(event):
        try:
            secret_data = event['raw_object'].get('data')
            if not secret_data:
                return False
            secret_value = secret_data.get(key_name)
            if not secret_value:
                return False
            return True
        except Exception as e:
            pytest.fail("Error occured while processing secret event: " + str(e))

    # Checking the kubernetes secret
    api_instance = client.CoreV1Api()
    watch_kubernetes_secret(api_instance, secret_namespace, secret_name, timeout, secret_event_callback)


def get_azure_arc_agent_version(api_instance, namespace, configmap_name):
    configmap = get_namespaced_configmap(api_instance, namespace, configmap_name)
    azure_arc_agent_version = configmap.data.get('AZURE_ARC_AGENT_VERSION')
    if not azure_arc_agent_version:
        pytest.fail("The azure arc configmap does not contain the azure arc agent version.")
    return azure_arc_agent_version

