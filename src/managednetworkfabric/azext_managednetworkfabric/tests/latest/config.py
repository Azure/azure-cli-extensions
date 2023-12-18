# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods

""" ManagedNetworkFabric resource specific configuration"""

import configparser
from os import path


class LoadConfig:
    ''' Loads the resource specific configuration for managednetworkfabric resources from config.ini.
    This configuration is loaded at the first instance and stored in the _config_instance
    Global parameter CONFIG can be used by calling classes to use the configuration values
    '''
    config = None

    def __init__(self):
        self._config_instance = None  # Initial value
        filename = path.dirname(__file__) + "/config.ini"
        self.config = self.readconfig(filename)

    def readconfig(self, filename):
        ''' Load resource config from configuration file'''
        if self._config_instance:
            return self._config_instance
        self._config_instance = configparser.ConfigParser()
        self._config_instance.read(filename)
        return self._config_instance


def get_config():
    ''' Load the config and return the class instance'''
    load_cnfig = LoadConfig()
    return load_cnfig.config


CONFIG = get_config()
