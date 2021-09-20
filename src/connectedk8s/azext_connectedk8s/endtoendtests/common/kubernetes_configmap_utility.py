import pytest


def get_namespaced_configmap(api_instance, namespace, configmap_name):
    try:
        return api_instance.read_namespaced_config_map(configmap_name, namespace)
    except Exception as e:
        pytest.fail("Error occured when retrieving configmap: " + str(e))
