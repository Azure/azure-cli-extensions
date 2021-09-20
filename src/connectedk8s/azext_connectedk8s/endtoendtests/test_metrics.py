import pytest
import time

from azure.kusto.data import ClientRequestProperties, KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.exceptions import KustoServiceError
from azure.kusto.data.helpers import dataframe_from_result_table
from datetime import timedelta

@pytest.fixture(scope='session')
def cluster_details(env_dict):
    clusterDetails = {}
    clusterDetails["kustoCluster"] = "https://Clusterconfigprod.kusto.windows.net"
    clusterDetails["kustoDatabase"] = "ClusterConfig"
    clientProperties = ClientRequestProperties()
    clientProperties.set_option(clientProperties.request_timeout_option_name, timedelta(minutes=2))
    clusterDetails["clientProperties"] = clientProperties
    
    return clusterDetails

def test_env_vars(env_dict):
    for key, value in env_dict.items():
        if not value:
            pytest.fail("Value for {} not provided".format(key))

def test_cluster_metricsagent_logs(env_dict, cluster_details):
    kustoQueryURLsScraped = f'ConnectAgentTraces | where [\"time\"] >= ago(1h) | where ArmId == \"/subscriptions/{env_dict["subscriptionId"]}/resourceGroups/{env_dict["resourceGroup"]}/providers/Microsoft.Kubernetes/ConnectedClusters/{env_dict["name"]}\" | where LogLevel == \"Information\" and AgentName == \"MetricsAgent\" | where Message has \"Completed collecting urls\" | count'
    rowCount = kusto_query_helper(env_dict, cluster_details, kustoQueryURLsScraped)
    assert rowCount > 0

    kustoQueryInputPluginError = f'ConnectAgentTraces | where [\"time\"] >= ago(1h) | where ArmId == \"/subscriptions/{env_dict["subscriptionId"]}/resourceGroups/{env_dict["resourceGroup"]}/providers/Microsoft.Kubernetes/ConnectedClusters/{env_dict["name"]}\" | where LogLevel == \"Error\" and AgentName == \"MetricsAgent\" | where Message has \"unable to create new request\" or Message has \"error making HTTP request\" or Message has \"returned HTTP status\" or Message has \"error reading metrics\" or Message has \"error reading body\" | count'
    rowCount = kusto_query_helper(env_dict, cluster_details, kustoQueryInputPluginError)
    assert rowCount == 0

    kustoQuerySerializerError = f'ConnectAgentTraces | where [\"time\"] >= ago(1h) | where ArmId == \"/subscriptions/{env_dict["subscriptionId"]}/resourceGroups/{env_dict["resourceGroup"]}/providers/Microsoft.Kubernetes/ConnectedClusters/{env_dict["name"]}\" | where LogLevel == \"Error\" and AgentName == \"MetricsAgent\" | where Message has \"Dropping invalid metric\" or Message has \"Dropping nil metric\" or Message has \"Error in parsing metrics batch\" or Message has \"There is no matching type present for the service\" or Message has \"Unable to convert mdm dimension\" | count'
    rowCount = kusto_query_helper(env_dict, cluster_details, kustoQuerySerializerError)
    assert rowCount == 0

    kustoQueryMetricsWritten = f'ConnectAgentTraces | where [\"time\"] >= ago(1h) | where ArmId == \"/subscriptions/{env_dict["subscriptionId"]}/resourceGroups/{env_dict["resourceGroup"]}/providers/Microsoft.Kubernetes/ConnectedClusters/{env_dict["name"]}\" | where LogLevel == \"Information\" and AgentName == \"MetricsAgent\" | where Message has \"Wrote batch of\" | count'
    rowCount = kusto_query_helper(env_dict, cluster_details, kustoQueryMetricsWritten)
    assert rowCount > 0

    kustoQueryOutputPluginError = f'ConnectAgentTraces | where [\"time\"] >= ago(1h) | where ArmId == \"/subscriptions/{env_dict["subscriptionId"]}/resourceGroups/{env_dict["resourceGroup"]}/providers/Microsoft.Kubernetes/ConnectedClusters/{env_dict["name"]}\" | where LogLevel == \"Error\" and AgentName == \"MetricsAgent\" | where Message has \"Invalid method for\" or Message has \"Error in creating HTTP client for PostMetrics call\" or Message has \"Error in serializing metrics batch\" or Message has \"Error in writing metrics to the config data plane\" or Message has \"Error getting authorization headers for PostMetrics call.\" or Message has \"Unexpected error in PostMetrics call\" or Message has \"received status code\" | count'
    rowCount = kusto_query_helper(env_dict, cluster_details, kustoQueryOutputPluginError)
    assert rowCount == 0

def test_cluster_metrics(env_dict, cluster_details):
    kustoQueryConnectedClusterMDM = f'ClusterConfigTraces | where [\"time\"] >= ago(1h) | where Message has \"/subscriptions/{env_dict["subscriptionId"]}/resourceGroups/{env_dict["resourceGroup"]}/providers/Microsoft.Kubernetes/ConnectedClusters/{env_dict["name"]}\" | where Message startswith \"Partner trackMetric: Account:ConnectedClusterResourceHealth\" | count'
    rowCount = kusto_query_helper(env_dict, cluster_details, kustoQueryConnectedClusterMDM)
    assert rowCount > 0

    kustoQueryClusterConfigMDM = f'ClusterConfigTraces | where [\"time\"] >= ago(1h) | where Message has \"/subscriptions/{env_dict["subscriptionId"]}/resourceGroups/{env_dict["resourceGroup"]}/providers/Microsoft.Kubernetes/ConnectedClusters/{env_dict["name"]}\" | where Message startswith \"Partner trackMetric: Account:ClusterConfig\" | count'
    rowCount = kusto_query_helper(env_dict, cluster_details, kustoQueryClusterConfigMDM)
    assert rowCount > 0

    kustoQueryShoeboxMDM = f'ClusterConfigTraces | where [\"time\"] >= ago(1h) | where Message has \"/subscriptions/{env_dict["subscriptionId"]}/resourceGroups/{env_dict["resourceGroup"]}/providers/Microsoft.Kubernetes/ConnectedClusters/{env_dict["name"]}\" | where Message startswith \"Partner trackMetric: Account:MicrosoftKubernetesShoebox\" | count'
    rowCount = kusto_query_helper(env_dict, cluster_details, kustoQueryShoeboxMDM)
    assert rowCount > 0

def kusto_query_helper(env_dict, cluster_details, kustoQuery):
    kcsb = KustoConnectionStringBuilder.with_aad_application_key_authentication(cluster_details["kustoCluster"], env_dict["clientId"], env_dict["clientSecret"], env_dict["tenantId"])
    kustoClient = KustoClient(kcsb)

    rowCount = 0
    retryCount = 5
    try:
        while(retryCount > 0):
            response = kustoClient.execute(cluster_details["kustoDatabase"], kustoQuery)
            for row in response.primary_results[0]:
                rowCount = row[0]
            if rowCount > 0:
                break
            retryCount -= 1
    except KustoServiceError as error:
        print("Error in executing Kusto query for checking logs/metrics", error)
        pytest.fail("Error in executing the Kusto query: ", kustoQuery)

    print("Kusto query: ", kustoQuery)
    print("Row Count from query: ", rowCount)

    return rowCount
