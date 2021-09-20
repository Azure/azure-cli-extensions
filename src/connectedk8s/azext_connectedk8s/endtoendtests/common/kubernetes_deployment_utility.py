import pytest


# Returns a list of deployments in a given namespace
def list_deployment(api_instance, namespace, field_selector="", label_selector=""):
    try:
        return api_instance.list_namespaced_deployment(namespace, field_selector=field_selector, label_selector=label_selector)
    except Exception as e:
        pytest.fail("Error occured when retrieving deployments: " + str(e))

# Deletes a deployment
def delete_deployment(api_instance, namespace, deployment_name):
    try:
        return api_instance.delete_namespaced_deployment(deployment_name, namespace)
    except Exception as e:
        pytest.fail("Error occured when deleting deployment: " + str(e))


# Read a deployment
def read_deployment(api_instance, namespace, deployment_name):
    try:
        return api_instance.read_namespaced_deployment(deployment_name, namespace)
    except Exception as e:
        pytest.fail("Error occured when reading deployment: " + str(e))
