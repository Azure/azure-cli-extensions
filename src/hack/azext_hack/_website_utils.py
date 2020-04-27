# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.command_modules.appservice.custom import (
    create_app_service_plan,
    create_webapp,
    update_app_settings,
    list_app_service_plans,
    get_app_settings,
    list_publishing_credentials
)
from azure.cli.command_modules.resource.custom import move_resource
from azure.cli.core.profiles import ResourceType
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
        self.host_name = None
        self.resource_group = None
        self.id = None
        self.__cmd = cmd
        self.__cmd.command_kwargs = {
            'resource_type': ResourceType.MGMT_APPSERVICE,
        }
        self.__deployment_info = None

    def create(self):
        app_service_plan = self.__get_or_create_app_service_plan()

        webapp = self.__create_webapp(app_service_plan)

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
        output = {'Application name': self.name}

        settings = {}
        for setting in get_app_settings(self.__cmd, resource_group_name=self.name, name=self.name):
            settings.update({setting['name']: setting['value']})
        if settings:
            output.update({'Application settings (stored as environmental variables on server)': settings})

        output.update({'Deployment info': {
            'Git url': self.deployment_info.git_url,
            'User name': self.deployment_info.name,
            'User password': self.deployment_info.password
        }})

        output.update({'Website url': 'https://{}.azurewebsites.net'.format(self.name)})

        return output

    @property
    def deployment_info(self):
        if not self.__deployment_info:
            publishing_info = list_publishing_credentials(self.__cmd, resource_group_name=self.name, name=self.name)
            self.__deployment_info = type('DeploymentInfo', (object, ), {
                'name': publishing_info.publishing_user_name,
                'password': publishing_info.publishing_password,
                'git_url': 'https://{}.scm.azurewebsites.net/{}.git'.format(self.name, self.name)
            })()

        return self.__deployment_info

    def __get_or_create_app_service_plan(self) -> str:
        plans = list_app_service_plans(self.__cmd, self.name)
        for plan in plans:
            if plan.sku.family == 'F':
                logger.warning('Using existing free plan: {}'.format(plan.name))
                return plan
        # Reached here, no free plan found
        logger.warning(
            'Creating free App Service plan named free_app_service_plan...')
        default_free_plan_name = 'free_app_service_plan'

        # app_service_cmd = cf_plans(self.__cmd, None)

        app_service_plan = create_app_service_plan(self.__cmd, resource_group_name=self.name, sku='F1',
                                                   name=default_free_plan_name, is_linux=True, hyper_v=False).result()
        self.resource_group = app_service_plan.resource_group
        return app_service_plan

    def __create_webapp(self, app_service_plan):
        # create in the app plans resource group
        # TODO: get logger
        runtime_setting = _RUNTIME_SETTINGS[self.runtime]
        logger.warning('Creating website: {}'.format(self.name))
        webapp = create_webapp(self.__cmd, resource_group_name=app_service_plan.resource_group, name=self.name,
                               plan=app_service_plan.name, runtime=runtime_setting['name'], deployment_local_git=True)
        self.resource_group = app_service_plan.resource_group
        self.id = webapp.id
        return webapp
