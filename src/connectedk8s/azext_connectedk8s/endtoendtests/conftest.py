import pytest
from .common.constants import *

def pytest_addoption(parser):
    parser.addoption("--name", action="store")
    parser.addoption("--resourceGroup", action="store")
    parser.addoption("--clientId", action="store")
    parser.addoption("--clientSecret", action="store")
    parser.addoption("--tenantId", action="store")
    parser.addoption("--subscriptionId", action="store")
    parser.addoption("--cloud", action="store")


@pytest.fixture(scope='session')
def env_dict(request):
    config_param = {}
    config_param["name"] = request.config.getoption("--name")
    config_param["resourceGroup"] = request.config.getoption("--resourceGroup")
    config_param["clientId"] = request.config.getoption("--clientId")
    config_param["clientSecret"] = request.config.getoption("--clientSecret")
    config_param["tenantId"] = request.config.getoption("--tenantId")
    config_param["subscriptionId"] = request.config.getoption("--subscriptionId")
    config_param["cloud"] = request.config.getoption("--cloud")
    return config_param