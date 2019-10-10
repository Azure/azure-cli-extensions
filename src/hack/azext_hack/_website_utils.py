from uuid import uuid4
from azure.cli.command_modules.appservice._client_factory import (
    web_client_factory
)
from azure.cli.command_modules.appservice.custom import (
    create_app_service_plan,
    create_webapp,
    update_app_settings,
    set_deployment_user,
    list_app_service_plans
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
        'name': 'node|10.6',
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


class Website:
    def __init__(self, cmd, name: str, location: str, runtime: str):
        self.name = name
        self.location = location
        self.runtime = runtime
        self._deployment_user_name = None
        self._deployment_user_password = None
        self._deployment_url = None
        self._host_name = None
        self._resource_group = None
        self._id = None
        self.__cmd = cmd

    def create(self):
        app_service_plan = self.__get_or_create_app_service_plan()
        webapp = self.__create_webapp(app_service_plan)

        self.__set_deployment_user()

        self.deployment_url = webapp.deploymentLocalGitUrl
        self.host_name = 'https://' + webapp.host_names[0]

    def update_settings(self, settings):
        app_settings = []
        for key in settings:
            app_settings.append('{}={}'.format(key, settings[key]))
        update_app_settings(self.__cmd, resource_group_name=self._resource_group,
                            name=self.name, settings=app_settings)

    def finalize_resource_group(self):
        if self._resource_group.lower() == self.name:
            return
        # Need to move to correct resource group
        logger.warning('Moving website. This will take a few minutes...')
        poller = move_resource(self.__cmd, [self._id], self.name)
        while not poller.done():
            poller.result(15)
        self._resource_group = self.name

    def __get_or_create_app_service_plan(self) -> str:
        plans = list_app_service_plans(self.__cmd)
        for plan in plans:
            if plan.sku.family == 'F':
                logger.warning('Using existing free plan...')
                return plan
        # Reached here, no free plan found
        logger.warning('Creating free App Service plan named free_app_service_plan...')
        default_free_plan_name = 'free_app_service_plan'
        app_service_plan = create_app_service_plan(self.__cmd, resource_group_name=self.name, sku='F1',
                                       name=default_free_plan_name, is_linux=True, hyper_v=False).result()
        self._resource_group = app_service_plan.resource_group
        return app_service_plan

    def __create_webapp(self, app_service_plan):
        # create in the app plans resource group
        # TODO: get logger
        runtime_setting = _RUNTIME_SETTINGS[self.runtime]
        logger.warning('Creating website...')
        webapp = create_webapp(self.__cmd, resource_group_name=app_service_plan.resource_group, name=self.name,
                               plan=app_service_plan.name, runtime=runtime_setting['name'], deployment_local_git=True)
        self._resource_group = app_service_plan.resource_group
        self._id = webapp.id
        return webapp

    def __set_deployment_user(self):
        deployment_user = web_client_factory(
            self.__cmd.cli_ctx).get_publishing_user()
        # Check for existing deployment user
        if not deployment_user:
            # Create random password, set name to first 10 characters of app name
            self.deployment_user_password = str(uuid4())
            set_deployment_user(self.__cmd,
                                user_name=self.name[:10],
                                password=self.deployment_user_password)
            self.deployment_user_name = self.name[:10]
        else:
            self.deployment_user_name = deployment_user.publishing_user_name

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, val: str):
        if not val:
            raise "name is required"
        self._name = val

    @property
    def location(self) -> str:
        return self.location

    @location.setter
    def location(self, val: str):
        if not val:
            raise "location is required"
        self._location = val

    @property
    def runtime(self) -> str:
        return self._runtime

    @runtime.setter
    def runtime(self, val: str):
        if not val:
            raise "runtime is required"
        self._runtime = val

    @property
    def deployment_user_name(self) -> str:
        return self._deployment_user_name

    @deployment_user_name.setter
    def deployment_user_name(self, val: str):
        if not val:
            raise "deployment_user_name is required"
        self._deployment_user_name = val

    @property
    def deployment_user_password(self) -> str:
        return self._deployment_user_password

    @deployment_user_password.setter
    def deployment_user_password(self, val: str):
        if not val:
            raise "deployment_user_password is required"
        self._deployment_user_password = val

    @property
    def deployment_url(self) -> str:
        return self._deployment_url

    @deployment_url.setter
    def deployment_url(self, val: str):
        if not val:
            raise "deployment_url is required"
        self._deployment_url = val

    @property
    def host_name(self) -> str:
        return self._host_name

    @host_name.setter
    def host_name(self, val: str):
        if not val:
            raise "host_name is required"
        self._host_name = val

    @property
    def resource_group(self) -> str:
        return self._resource_group
