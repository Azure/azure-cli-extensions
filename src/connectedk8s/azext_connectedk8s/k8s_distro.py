import sys
import os
sys.path.insert(0, os.path.join(os.path.expanduser('~'), '.azure', 'cliextensions', 'connectedk8s'))

from kubernetes import client as kube_client, config

def try_list_node_fix():
    try:
        from kubernetes.client.models.v1_container_image import V1ContainerImage

        def names(self, names):
            self._names = names

        V1ContainerImage.names = V1ContainerImage.names.setter(names)
    except Exception as ex:
        print("Error while trying to monkey patch the fix for list_node(): {}".format(str(ex)))

def get_kubernetes_distro(configuration):  # Heuristic
    try_list_node_fix()
    api_instance = kube_client.CoreV1Api(kube_client.ApiClient(configuration))
    try:
        api_response = api_instance.list_node()
        if api_response.items:
            labels = api_response.items[0].metadata.labels
            print("Node Labels: {}".format(labels))
            provider_id = str(api_response.items[0].spec.provider_id)
            print("\nProviderID: {}".format(provider_id))
            annotations = list(api_response.items)[0].metadata.annotations
            if labels.get("node.openshift.io/os_id"):
                return "openshift"
            if labels.get("kubernetes.azure.com/node-image-version"):
                return "aks"
            if labels.get("cloud.google.com/gke-nodepool") or labels.get("cloud.google.com/gke-os-distribution"):
                return "gke"
            if labels.get("eks.amazonaws.com/nodegroup"):
                return "eks"
            if labels.get("minikube.k8s.io/version"):
                return "minikube"
            if provider_id.startswith("kind://"):
                return "kind"
            if provider_id.startswith("k3s://"):
                return "k3s"
            if annotations.get("rke.cattle.io/external-ip") or annotations.get("rke.cattle.io/internal-ip"):
                return "rancher_rke"
        return "generic"
    except Exception as e:  # pylint: disable=broad-except
        print("Error occured while trying to fetch kubernetes distribution: " + str(e))
        return "generic"

config.load_kube_config()
configuration = kube_client.Configuration()
distro = get_kubernetes_distro(configuration)

print(f"\nKubernetes distro: {distro}")