import pytest

def get_kubernetes_node_count(api_instance):
    node_list = list_kubernetes_nodes(api_instance)
    return len(node_list.items)

def get_kubernetes_core_count(api_instance):
    core_count = 0
    node_list = list_kubernetes_nodes(api_instance)
    for item in node_list.items:
        core_count += int(item.status.capacity['cpu'])
    return core_count

def list_kubernetes_nodes(api_instance):
    try:
        return api_instance.list_node()
    except Exception as e:
        pytest.fail("Error occured while retrieving node information: " + str(e))


