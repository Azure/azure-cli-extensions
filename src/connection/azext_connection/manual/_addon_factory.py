# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import subprocess
from knack.log import get_logger
from ._resource_config import RESOURCE


logger = get_logger(__name__)



def get_source_rg():
    pass


def get_source_loc():
    pass


def generate_resource_name():
    pass


def generate_password():
    pass


AddOns = {
    RESOURCE.Postgres: {
        'steps': [
            {
                'create': 'az postgres server create -g {target_resource_group} -n {postgres_server} -l {location} -u {user} -p {password}',
                'delete': 'az postgres server delete -g {target_resource_group} -n {postgres_server}'
            },
            {
                'create': 'az postgres db create -g {target_resource_group} -s {postgres_server} -n {postgres_db}',
                'delete': 'az postgres db delete -g {target_resource_group} -s {postgres_server} -n {postgres_db}'
            }
        ],
        'params': {
            'target_resource_group': get_source_rg,
            'postgres_server': generate_resource_name,
            'location': get_source_loc,
            'user': generate_resource_name,
            'password': generate_password,
            'postgres_db': generate_resource_name,
        }
    },
    RESOURCE.KeyVault: [
        {
            'create': 'az postgres keyvault create -g {target_resource_group} -n {name} -l {loc}',
            'delete': 'az postgres keyvault delete -g {target_resource_group} -n {name}'
        }
    ]
}



class AddonFactory:

    def __init__(self, resource_type, source_id):
        self._resource_type = resource_type
        self._params = self._retrive_source_id(source_id)
        self._params.update(self._generate_additional_params())


    def create(self):
        addon = AddOns.get(self._resource_type)
        
        logger.warning('Start creating a new {}'.format(self._resource_type.value))
        for step in addon:
            cmd = step.get('create')
            self._run_cmd(cmd, kwargs)


    def _rollback(self):
        pass
    

    def _format_cmd(self, cmd, **kwargs):
        try:
            return cmd.format(kwargs)
        except:
            pass


    def _run_cmd(self, cmd, retry=0):
        from subprocess import CalledProcessError
        try:
            # CalledProcessError will be raised when exit code is not 0
            subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL)
            return True
        except CalledProcessError as e:
            if retry:
                self._run_cli_cmd(self, cmd, retry-1)
        return False


    def _retrive_source_id(self):
        from ._validators import get_resource_regex

        return None

    def _generate_additional_params(self):
        pass