# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=protected-access, too-few-public-methods
# pylint: disable=duplicate-code

"""
This custom code deregisters the 'metrics_configuration_name' argument and sets
the default value to "default".
"""


class ClusterMetricsConfiguration:
    """Common custom class cluster's metrics configuration CRUD operations"""

    @classmethod
    def _build_arguments_schema(cls, args_schema):
        # deregister the Cluster metrics configuration name argument which users
        # should not interact with
        args_schema.metrics_configuration_name._registered = False
        args_schema.metrics_configuration_name._required = False
        return args_schema

    @classmethod
    def pre_operations(cls, args):
        """ "default" is the default name for the metrics configuration name"""
        args.metrics_configuration_name = "default"
