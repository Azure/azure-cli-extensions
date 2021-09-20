import pytest

from kubernetes import watch


# Function to get the CRD instance
def get_crd_instance(api_instance, group, version, namespace, plural, crd_name):
    try:
        return api_instance.get_namespaced_custom_object(group, version, namespace, plural, crd_name)
    except Exception as e:
        pytest.fail("Error occurred when retrieving crd information: " + str(e))


# Function that watches events corresponding to given CRD instance and passes the events to a callback function
def watch_crd_instance(api_instance, group, version, namespace, plural, crd_name, timeout, callback=None):
    if not callback:
        return
    field_selector = "metadata.name={}".format(crd_name) if crd_name else ""
    try:
        w = watch.Watch()
        for event in w.stream(api_instance.list_namespaced_custom_object, group, version, namespace, plural, field_selector=field_selector, timeout_seconds=timeout):
            if callback(event):
                return
    except Exception as e:
        pytest.fail("Error occurred when watching crd instance events: " + str(e))
    pytest.fail("The watch on the crd instance events has timed out.")
