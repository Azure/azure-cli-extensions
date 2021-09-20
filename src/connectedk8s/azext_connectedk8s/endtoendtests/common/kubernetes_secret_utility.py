import sys

from kubernetes import watch


# This function returns the kubernetes secret object present in a given namespace
def get_kubernetes_secret(api_instance, namespace, secret_name):
    try:
        return api_instance.read_namespaced_secret(secret_name, namespace)
    except Exception as e:
        sys.exit("Error occurred when retrieving secret '{}': ".format(secret_name) + str(e))


# Function that watches events corresponding to kubernetes secrets and passes the events to a callback function
def watch_kubernetes_secret(api_instance, namespace, secret_name, timeout, callback=None):
    if not callback:
        return
    field_selector = "metadata.name={}".format(secret_name) if secret_name else ""
    try:
        w = watch.Watch()
        for event in w.stream(api_instance.list_namespaced_secret, namespace, field_selector=field_selector, timeout_seconds=timeout):
            if callback(event):
                return
    except Exception as e:
        sys.exit("Error occurred when watching kubernetes secret events: " + str(e))
    sys.exit("The watch on the kubernetes secret events has timed out. Please see the pod logs for more info.")
