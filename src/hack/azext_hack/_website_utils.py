# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# # --------------------------------------------------------------------------------------------

from uuid import uuid4
from azure.cli.command_modules.appservice._client_factory import (
    web_client_factory
)
from azure.cli.command_modules.appservice.custom import (
    create_app_service_plan,
    create_webapp,
    update_app_settings,
    set_deployment_user,
    list_app_service_plans,
    get_app_settings
)
from azure.cli.command_modules.resource.custom import move_resource
from knack.log import get_logger

logger = get_logger(__name__)

_RUNTIME_SETTINGS = {
    'php': {
        'name': 'php|7.3',
        'is_linux': True
    },
    'node': {
        'name': 'node|LTS',
        'is_linux': True
    },
    'tomcat': {
        'name': 'java|11|Tomcat|9.0',
        'is_linux': True
    },
    'jetty': {
        'name': 'java|11|Jetty|9.3',
        'is_linux': True
    },
    'python': {
        'name': 'python|3.6',
        'is_linux': True
    },
    'aspnet': {
        'name': 'aspnet|4.7',
        'is_linux': False
    }
}


# pylint: disable=too-many-instance-attributes
class Website:
    def __init__(self, cmd, name: str, location: str, runtime: str):
        self.name = name
        self.location = location
        self.runtime = runtime
        self.deployment_user_name = None
        self.deployment_user_password = None
        self.deployment_url = None
        self.host_name = None
        self.resource_group = None
        self.id = None
        self.__cmd = cmd

    def create(self):
        app_service_plan = self.__get_or_create_app_service_plan()
        self.__set_deployment_user()

        webapp = self.__create_webapp(app_service_plan)

        self.deployment_url = 'https://{}.scm.azurewebsites.net/{}.git'.format(self.name, self.name)
        self.host_name = 'https://' + webapp.host_names[0]

    def update_settings(self, settings):
        app_settings = []
        for key in settings:
            app_settings.append('{}={}'.format(key, settings[key]))
        if app_settings:
            update_app_settings(self.__cmd, resource_group_name=self.resource_group,
                                name=self.name, settings=app_settings)

    def finalize_resource_group(self):
        if self.resource_group.lower() == self.name:
            return
        # Need to move to correct resource group
        logger.warning('Moving website. This will take a few minutes...')
        poller = move_resource(self.__cmd, [self.id], self.name)
        while not poller.done():
            poller.result(15)
        self.resource_group = self.name

    def show(self):
        output = {}
        settings = {}
        for setting in get_app_settings(self.__cmd, resource_group_name=self.name, name=self.name):
            settings.update({setting['name']: setting['value']})
        output.update({'App settings': settings})
        urls = {}
        repo_url = 'https://{}.scm.azurewebsites.net/{}.git'.format(self.name, self.name)
        urls.update({'Git url': repo_url})
        urls.update({'Website url': repo_url.replace('scm.', '')})
        output.update({'URLs': urls})
        return output

    def __get_or_create_app_service_plan(self) -> str:
        plans = list_app_service_plans(self.__cmd)
        for plan in plans:
            if plan.sku.family == 'F':
                logger.warning('Using existing free plan...')
                return plan
        # Reached here, no free plan found
        logger.warning(
            'Creating free App Service plan named free_app_service_plan...')
        default_free_plan_name = 'free_app_service_plan'
        app_service_plan = create_app_service_plan(self.__cmd, resource_group_name=self.name, sku='F1',
                                                   name=default_free_plan_name, is_linux=True, hyper_v=False).result()
        self.resource_group = app_service_plan.resource_group
        return app_service_plan

    def __create_webapp(self, app_service_plan):
        # create in the app plans resource group
        # TODO: get logger
        runtime_setting = _RUNTIME_SETTINGS[self.runtime]
        logger.warning('Creating website...')
        webapp = create_webapp(self.__cmd, resource_group_name=app_service_plan.resource_group, name=self.name,
                               plan=app_service_plan.name, runtime=runtime_setting['name'], deployment_local_git=True)
        self.resource_group = app_service_plan.resource_group
        self.id = webapp.id
        return webapp

    def __set_deployment_user(self):
        deployment_user = web_client_factory(
            self.__cmd.cli_ctx).get_publishing_user()
        # Check for existing deployment user
        if not deployment_user or not deployment_user.publishing_user_name:
            # Create random password, set name to base of app name
            logger.warning('Creating deployment user')
            password = str(uuid4())
            user_name = self.name
            set_deployment_user(self.__cmd, user_name=user_name, password=password)
            self.deployment_user_name = user_name
            self.deployment_user_password = password
        else:
            self.deployment_user_name = deployment_user.publishing_user_name
