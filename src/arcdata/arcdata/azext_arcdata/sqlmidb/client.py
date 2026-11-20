# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from azext_arcdata.core.cli_client import CliClient
from azext_arcdata.core.util import DeploymentConfigUtil

__all__ = ["beget"]


def beget(az_cli, kwargs):
    """Client factory"""
    return SqlmidbClientMixin(az_cli, kwargs)


def beget_no_namespace(az_cli, kwargs):
    """Client factory - no check on namespace"""
    return SqlmidbClientMixin(az_cli, kwargs, check_namespace=False)


class SqlmidbClientMixin(CliClient):
    def __init__(self, az_cli, kwargs, check_namespace=True):
        super(SqlmidbClientMixin, self).__init__(
            az_cli, kwargs, check_namespace=check_namespace
        )

    @staticmethod
    def add_configuration(path, json_values):
        config_object = DeploymentConfigUtil.config_add(path, json_values)
        DeploymentConfigUtil.write_config_file(path, config_object)

    @staticmethod
    def replace_configuration(path, json_values):
        config_object = DeploymentConfigUtil.config_replace(path, json_values)
        DeploymentConfigUtil.write_config_file(path, config_object)

    @staticmethod
    def remove_configuration(path, json_path):
        config_object = DeploymentConfigUtil.config_remove(path, json_path)
        DeploymentConfigUtil.write_config_file(path, config_object)

    @staticmethod
    def patch_configuration(path, patch_file):
        config_object = DeploymentConfigUtil.config_patch(path, patch_file)
        DeploymentConfigUtil.write_config_file(path, config_object)
