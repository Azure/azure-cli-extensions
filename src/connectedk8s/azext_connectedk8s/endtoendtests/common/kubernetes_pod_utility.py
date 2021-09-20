import pytest
import time

from kubernetes import watch


# Returns a kubernetes pod object in given namespace. Object description at: https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1PodList.md
def get_pod(api_instance, namespace, pod_name):
    try:
        return api_instance.read_namespaced_pod(pod_name, namespace)
    except Exception as e:
        pytest.fail("Error occured when retrieving pod information: " + str(e))


# Returns a list of kubernetes pod objects in a given namespace. Object description at: https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1PodList.md
def get_pod_list(api_instance, namespace, label_selector=""):
    try:
        return api_instance.list_namespaced_pod(namespace, label_selector=label_selector)
    except Exception as e:
        pytest.fail("Error occurred when retrieving pod information: " + str(e))


# Function that watches events corresponding to pods in the given namespace and passes the events to a callback function
def watch_pod_status(api_instance, namespace, timeout, callback=None):
    if not callback:
        return
    try:
        w = watch.Watch()
        for event in w.stream(api_instance.list_namespaced_pod, namespace, timeout_seconds=timeout):
            if callback(event):
                return
    except Exception as e:
        pytest.fail("Error occurred when checking pod status: " + str(e))
    pytest.fail("The watch on the pods has timed out. Please see the pod logs for more info.")


# Function that watches events corresponding to pod logs and passes them to a callback function
def watch_pod_logs(api_instance, namespace, pod_name, container_name, timeout_seconds, callback=None):
    if not callback:
        return
    try:
        w = watch.Watch()
        timeout = time.time() + timeout_seconds
        for event in w.stream(api_instance.read_namespaced_pod_log, pod_name, namespace, container=container_name):
            if callback(event):
                return
            if time.time() > timeout:
                pytest.fail("The watch on the pod logs has timed out.")
    except Exception as e:
        pytest.fail("Error occurred when checking pod logs: " + str(e))


# Function that returns the pod logs of a given container.
def get_pod_logs(api_instance, pod_namespace, pod_name, container_name):
    try:
        return api_instance.read_namespaced_pod_log(pod_name, pod_namespace, container=container_name)
    except Exception as e:
        pytest.fail("Error occurred when fetching pod logs: " + str(e))


def delete_pod(api_instance, namespace, pod_name):
    try:
        api_instance.delete_namespaced_pod(pod_name, namespace)
    except Exception as e:
        pytest.fail("Error occured while deleting pod {}: ".format(pod_name) + str(e))
