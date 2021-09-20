import pytest


def get_kubernetes_server_version(api_instance):
    try:
        api_response = api_instance.get_code()
        return api_response.git_version
    except Exception as e:
        pytest.fail("Error occured when retrieving kubernetes server version: " + str(e))

