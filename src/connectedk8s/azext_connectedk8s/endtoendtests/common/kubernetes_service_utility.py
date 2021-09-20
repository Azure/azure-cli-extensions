import pytest

from kubernetes import watch


# Returns a list of services in a given namespace
def list_service(api_instance, namespace, field_selector="", label_selector=""):
    try:
        return api_instance.list_namespaced_service(namespace, field_selector=field_selector, label_selector=label_selector)
    except Exception as e:
        pytest.fail("Error occured when retrieving services: " + str(e))


# Deletes a service
def delete_service(api_instance, namespace, service_name):
    try:
        return api_instance.delete_namespaced_service(service_name, namespace)
    except Exception as e:
        pytest.fail("Error occured when deleting service: " + str(e))
