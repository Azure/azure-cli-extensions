import pytest
import time
from datetime import datetime, timezone
from .common.connected_cluster_utility import get_connected_cluster_client, get_connected_cluster
from .common.arm_rest_utility import fetch_aad_token_credentials
from .common.constants import *

from kubernetes import client, config
from .helper import get_azure_arc_agent_version, check_kubernetes_crd_status, check_kubernetes_secret, check_kubernetes_secret_with_key
from .common.kubernetes_node_utility import get_kubernetes_node_count, get_kubernetes_core_count
from .common.kubernetes_version_utility import get_kubernetes_server_version
from .common.helm_utility import list_helm_release, delete_helm_release


@pytest.mark.dependency()
def test_env_vars(env_dict):
    for key, value in env_dict.items():
        if not value:
            pytest.fail("Value for {} not provided".format(key))



@pytest.mark.dependency(depends=['test_env_vars'])
def test_connected_cluster(env_dict):
    cloud = env_dict["cloud"]
    if cloud == "AzureUSGovernment":
        azure_endpoints = AZURE_FAIRFAX_ENDPOINTS
    else:
        azure_endpoints = AZURE_PUBLIC_CLOUD_ENDPOINTS

    # Fetch aad token credentials from spn
    authority_uri = azure_endpoints.get('activeDirectory') + env_dict["tenantId"]
    credential = fetch_aad_token_credentials(env_dict["clientId"], env_dict["clientSecret"], authority_uri, azure_endpoints.get('management'))
    print("Successfully fetched credentials object.")

    # Check provisioning state of the connected cluster resource
    cc_client = get_connected_cluster_client(credential, env_dict["subscriptionId"], azure_endpoints["resourceManager"])

    timeout_seconds = TIMEOUT
    timeout = time.time() + timeout_seconds

    while True:
        provisioning_state = get_connected_cluster(cc_client, env_dict["resourceGroup"], env_dict["name"]).provisioning_state
        # append_result_output("Provisioning State: {}\n".format(provisioning_state), env_dict['TEST_CONNECTED_CLUSTER_LOG_FILE'])
        if provisioning_state == 'Succeeded':
            break
        if (provisioning_state == 'Failed' or provisioning_state == 'Cancelled'):
            pytest.fail("ERROR: The connected cluster creation finished with terminal provisioning state {}. ".format(provisioning_state))
        if time.time() > timeout:
            pytest.fail("ERROR: Timeout. The connected cluster is in non terminal provisioning state.")
        time.sleep(10)
    print("The connected cluster resource was created with succeeded provisioning state.")


@pytest.mark.dependency(depends=['test_env_vars', 'test_connected_cluster'])
def test_identity_operator(env_dict):
    timeout_seconds = TIMEOUT

    try:
        config.load_kube_config()
    except Exception as e:
        pytest.fail("Problem loading the kubeconfig file." + str(e))

    # Checking identity certificate secret
    print("Checking the azure identity certificate secret.")
    check_kubernetes_secret_with_key(AZURE_ARC_NAMESPACE, AZURE_IDENTITY_CERTIFICATE_SECRET, AZURE_IDENTITY_CERTIFICATE_EXPIRATION_TIME, timeout_seconds)
    print("The azure identity certificate secret data with cert expiration time was retrieved successfully.")


@pytest.mark.dependency(depends=['test_env_vars', 'test_identity_operator'])
def test_cluster_metadata_operator(env_dict):
    try:
        config.load_kube_config()
    except Exception as e:
        pytest.fail("Problem loading the kubeconfig file." + str(e))

    status_dict = {}
    api_instance = client.CoreV1Api()
    status_dict['nodeCount'] = get_kubernetes_node_count(api_instance)
    status_dict['coreCount'] = get_kubernetes_core_count(api_instance)
    status_dict['arcAgentVersion'] = get_azure_arc_agent_version(api_instance, AZURE_ARC_NAMESPACE, ARC_CONFIG_NAME)
    api_instance = client.VersionApi()
    kubernetes_server_version = get_kubernetes_server_version(api_instance)
    status_dict['kubernetesAPIServerVersion'] = kubernetes_server_version[1:]
    status_dict['lastConnectivityTime'] = ""
    status_dict['managedIdentityCertificateExpirationTime'] = ""
    print("Generated the status fields dictionary.")

    timeout = TIMEOUT
    check_kubernetes_crd_status(CLUSTER_METADATA_CRD_GROUP, CLUSTER_METADATA_CRD_VERSION,
                                AZURE_ARC_NAMESPACE, CLUSTER_METADATA_CRD_PLURAL,
                                CLUSTER_METADATA_CRD_NAME, status_dict, timeout)

    print("The status fields have been successfully updated in the CRD instance")

    print("Starting the check of the cluster metadata properties in the connected cluster resource.")

    cloud = env_dict["cloud"]
    if cloud == "AzureUSGovernment":
        azure_endpoints = AZURE_FAIRFAX_ENDPOINTS
    else:
        azure_endpoints = AZURE_PUBLIC_CLOUD_ENDPOINTS

    # Fetch aad token credentials from spn
    authority_uri = azure_endpoints.get('activeDirectory') + env_dict["tenantId"]
    credential = fetch_aad_token_credentials(env_dict["clientId"], env_dict["clientSecret"], authority_uri, azure_endpoints.get('management'))
    print("Successfully fetched credentials object.")

    # Setting a dictionary of cluster metadata fields that will be monitored for presence in the connected cluster resource
    metadata_dict = CLUSTER_METADATA_DICT
    print("Generated the metadata fields dictionary.")

    # Check metadata properties of the connected cluster resource
    cc_client = get_connected_cluster_client(credential, env_dict["subscriptionId"], azure_endpoints["resourceManager"])
    timeout_seconds = TIMEOUT
    timeout = time.time() + timeout_seconds
    while True:
        cc_object = get_connected_cluster(cc_client, env_dict["resourceGroup"], env_dict["name"])
        for metadata_field in metadata_dict.keys():
            try:
                metadata_field_value = getattr(cc_object, metadata_field)
            except Exception as e:
                pytest.fail("Error occured while fetching connected cluster attribute: " + str(e))
            if metadata_field_value:
                metadata_dict[metadata_field] = 1
        if all(ele == 1 for ele in list(metadata_dict.values())):
            break
        time.sleep(10)
        if time.time() > timeout:
            pytest.fail("ERROR: Timeout. The connected cluster has not been updated with metadata properties.")

    try:
        connectivity_status = getattr(cc_object, "connectivity_status")
        agent_version = getattr(cc_object, "agent_version")
    except Exception as e:
        pytest.fail("ERROR: The connected cluster doesn't have the required attribute." + str(e))
    assert connectivity_status == "Connected"

    print("Arc agent version: {}".format(agent_version))
    print("The connected cluster resource was updated with metadata properties successfully.")


@pytest.mark.dependency(depends=['test_env_vars', 'test_cluster_metadata_operator'])
def test_connectivity_status_transition(env_dict):

    helm_release_namespace = HELM_RELEASE_NAMESPACE
    helm_release_name = HELM_RELEASE_NAME

    if helm_release_name in list_helm_release(helm_release_namespace):
        delete_helm_release(helm_release_name, helm_release_namespace)
    print("Uninstalled the azure-arc agents successfully")

    time.sleep(60) #Some Time taken to sync last metadata update

    cloud = env_dict["cloud"]
    if cloud == "AzureUSGovernment":
        azure_endpoints = AZURE_FAIRFAX_ENDPOINTS
    else:
        azure_endpoints = AZURE_PUBLIC_CLOUD_ENDPOINTS

    authority_uri = azure_endpoints.get('activeDirectory') + env_dict["tenantId"]
    credential = fetch_aad_token_credentials(env_dict["clientId"], env_dict["clientSecret"], authority_uri, azure_endpoints.get('management'))
    print("Successfully fetched credentials object.")
    cc_client = get_connected_cluster_client(credential, env_dict["subscriptionId"], azure_endpoints["resourceManager"])
    cc_object = get_connected_cluster(cc_client, env_dict["resourceGroup"], env_dict["name"])
    try:
        connectivity_status = getattr(cc_object, "connectivity_status")
    except Exception as e:
        pytest.fail("ERROR: The connected cluster doesn't have the required attribute." + str(e))

    try:
        last_connectivity_time = getattr(cc_object, "last_connectivity_time")
        cert_expirn_time = getattr(cc_object, "managed_identity_certificate_expiration_time")
        connectivity_status = getattr(cc_object, "connectivity_status")
    except Exception as e:
        pytest.fail("ERROR: The connected cluster doesn't have the required attribute." + str(e))


    print("After deleting arc agents, the CC attributes were:")
    current_time = datetime.now(timezone.utc)
    print("Current Time: {}".format(current_time))
    print("Last connectivity time : {}".format(last_connectivity_time))
    print("Managed identity cert expiration time : {}".format(cert_expirn_time))
    print("Connectivity Status : {}".format(connectivity_status))

    transition_timeout_seconds = 15*60 # 15 minutes since offline
    print("Sleeping for 15 minutes to wait for transition to Offline/Expired")
    time.sleep(transition_timeout_seconds)

    #Regenerating token as the token will be expired if the cloud is FairFax
    if cloud == "AzureUSGovernment":
        credential = fetch_aad_token_credentials(env_dict["clientId"], env_dict["clientSecret"], authority_uri, azure_endpoints.get('management'))
        print("Fairfax: Successfully fetched credentials object again.")
        cc_client = get_connected_cluster_client(credential, env_dict["subscriptionId"], azure_endpoints["resourceManager"])
        cc_object = get_connected_cluster(cc_client, env_dict["resourceGroup"], env_dict["name"])
        try:
            connectivity_status = getattr(cc_object, "connectivity_status")
        except Exception as e:
            pytest.fail("ERROR: The connected cluster doesn't have the required attribute." + str(e))

        try:
            last_connectivity_time = getattr(cc_object, "last_connectivity_time")
            cert_expirn_time = getattr(cc_object, "managed_identity_certificate_expiration_time")
            connectivity_status = getattr(cc_object, "connectivity_status")
        except Exception as e:
            pytest.fail("ERROR: The connected cluster doesn't have the required attribute." + str(e))

    current_time = datetime.now(timezone.utc)
    counter = 1
    success = False
    while (current_time-last_connectivity_time).total_seconds() < 30*60:   # Max 30 minutes wait
        print("Polling status count: {}".format(counter))
        print("Current time difference: {}".format((current_time-last_connectivity_time).total_seconds()))
        try:
            cc_object = get_connected_cluster(cc_client, env_dict["resourceGroup"], env_dict["name"])
            connectivity_status = getattr(cc_object, "connectivity_status")
        except Exception as e:
            pytest.fail("ERROR: The connected cluster doesn't have the required attribute." + str(e))
        if connectivity_status != "Connected":
            print("The connected cluster has successfully transitioned to {}".format(connectivity_status))
            success = True
            break
        time.sleep(120)
        current_time = datetime.now(timezone.utc)
        counter += 1

    try:
        last_connectivity_time = getattr(cc_object, "last_connectivity_time")
        cert_expirn_time = getattr(cc_object, "managed_identity_certificate_expiration_time")
        connectivity_status = getattr(cc_object, "connectivity_status")
    except Exception as e:
        pytest.fail("ERROR: The connected cluster doesn't have the required attribute." + str(e))

    current_time = datetime.now(timezone.utc)
    print("Current Time: {}".format(current_time))
    print("Last connectivity time : {}".format(last_connectivity_time))
    print("Managed identity cert expiration time : {}".format(cert_expirn_time))
    print("Connectivity Status : {}".format(connectivity_status))

    if not success:
        pytest.fail("The connected cluster connectivity status has not transitioned")

    if cert_expirn_time != datetime.min and cert_expirn_time < current_time:
        if connectivity_status != "Expired":
            counter = 0
            while counter < 4:
                cc_object = get_connected_cluster(cc_client, env_dict["resourceGroup"], env_dict["name"])
                try:
                    connectivity_status = getattr(cc_object, "connectivity_status")
                except Exception as e:
                    pytest.fail("ERROR: The connected cluster doesn't have the required attribute." + str(e))
                if connectivity_status == "Expired":
                    print("The connected cluster has successfully transitioned to Expired")
                    break
                time.sleep(80)
                counter += 1
        assert connectivity_status == "Expired"
    else:
        assert connectivity_status == "Offline"
