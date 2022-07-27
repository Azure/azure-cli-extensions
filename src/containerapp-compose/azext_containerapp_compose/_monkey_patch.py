# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger
from azure.cli.core.azclierror import AzCLIError


class RequiredExtensionMissing(AzCLIError):
    def __init__(self, error_msg) -> None:
        recommendation = "Please install the containerapp extension: "
        recommendation += "`az extension add containerapp`"
        super().__init__(error_msg, recommendation)


logger = get_logger(__name__)


def log_containerapp_extension_required():
    message = "Please install the containerapp extension before proceeding with "
    message += "`az containerapp compose create`"
    logger.fatal(message)
    raise RequiredExtensionMissing(message)


try:
    from azext_containerapp import custom
    from azext_containerapp import _utils
    from azext_containerapp._up_utils import (ContainerApp,
                                              ContainerAppEnvironment,
                                              ResourceGroup,
                                              _get_registry_from_app,
                                              _get_registry_details,
                                              )   # pylint: disable=unused-import
    from azext_containerapp import _clients  # pylint: disable=unused-import
    from azext_containerapp._clients import ManagedEnvironmentClient   # pylint: disable=unused-import
except ModuleNotFoundError:
    log_containerapp_extension_required()
except ImportError:
    log_containerapp_extension_required()


# Monkey patch for log analytics workspace name
# this allows the test framework to pass down a specific
# name to support playback of recorded tests.
def override_random_log_analytics_name(resource_group_name):  # pylint: disable=unused-argument
    return _utils.logs_workspace_name  # noqa: F821 pylint: disable=undefined-variable


def create_containerapps_compose_environment(cmd,
                                             name,
                                             resource_group_name,
                                             logs_workspace_name=None,
                                             tags=None):
    if logs_workspace_name is not None:
        monkey_patch = override_random_log_analytics_name
        _utils._generate_log_analytics_workspace_name = monkey_patch  # pylint: disable=protected-access
        _utils.logs_workspace_name = logs_workspace_name
    return custom.create_managed_environment(cmd,
                                             name,
                                             resource_group_name,
                                             tags=tags)


def build_containerapp_from_compose_service(cmd,
                                            name,
                                            source,
                                            dockerfile,
                                            resource_group_name,
                                            managed_env,
                                            location,
                                            image,
                                            target_port,
                                            ingress,
                                            registry_server,
                                            registry_user,
                                            registry_pass,
                                            env_vars,
                                            logs_key=None,
                                            logs_customer_id=None):

    resource_group = ResourceGroup(cmd, name=resource_group_name, location=location)
    env = ContainerAppEnvironment(cmd,
                                  managed_env,
                                  resource_group,
                                  location=location,
                                  logs_key=logs_key,
                                  logs_customer_id=logs_customer_id)
    app = ContainerApp(cmd,
                       name,
                       resource_group,
                       None,
                       image,
                       env,
                       target_port,
                       registry_server,
                       registry_user,
                       registry_pass,
                       env_vars,
                       ingress)

    if not registry_server:
        _get_registry_from_app(app, True)  # if the app exists, get the registry
    _get_registry_details(cmd, app, True)  # fetch ACR creds from arguments registry arguments

    app.create_acr_if_needed()
    app.run_acr_build(dockerfile, source, False)
    return app.image, app.registry_server, app.registry_user, app.registry_pass


def create_containerapp_from_service(*args, **kwargs):
    return custom.create_containerapp(*args, **kwargs)


def load_yaml_file(filename):
    return custom.load_yaml_file(filename)


def show_managed_environment(cmd, resource_group_name, managed_env_name):
    return ManagedEnvironmentClient.show(cmd=cmd,
                                         resource_group_name=resource_group_name,
                                         name=managed_env_name)
