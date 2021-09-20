import pytest
from kubernetes import watch


# Function that watches events corresponding to kubernetes namespaces and passes the events to a callback function
def watch_namespace(api_instance, timeout, callback=None):
    if not callback:
        return
    try:
        w = watch.Watch()
        for event in w.stream(api_instance.list_namespace, timeout_seconds=timeout):
            if callback(event):
                return
    except Exception as e:
        pytest.fail("Error occurred when checking namespace status: " + str(e))
    pytest.fail("The watch on the namespaces has timed out.")


# Function to list all kubernetes namespaces
def list_namespace(api_instance):
    try:
        return api_instance.list_namespace()
    except Exception as e:
        pytest.fail("Error occured when retrieving namespaces: " + str(e))


# Function to delete a kubernetes namespaces
def delete_namespace(api_instance, namespace_name):
    try:
        return api_instance.delete_namespace(namespace_name)
    except Exception as e:
        pytest.fail("Error occured when deleting namespace: " + str(e))
