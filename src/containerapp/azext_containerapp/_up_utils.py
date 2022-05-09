# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, consider-using-f-string, no-else-return, duplicate-string-formatting-argument, expression-not-assigned, too-many-locals, logging-fstring-interpolation, arguments-differ, abstract-method, logging-format-interpolation, broad-except


from urllib.parse import urlparse
import requests

from azure.cli.core.azclierror import (
    RequiredArgumentMissingError,
    ValidationError,
    InvalidArgumentValueError,
    MutuallyExclusiveArgumentError,
)
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.command_modules.appservice._create_util import (
    check_resource_group_exists,
)
from azure.cli.command_modules.acr.custom import acr_show
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.mgmt.containerregistry import ContainerRegistryManagementClient
from knack.log import get_logger

from msrestazure.tools import parse_resource_id, is_valid_resource_id, resource_id

from ._clients import ManagedEnvironmentClient, ContainerAppClient, GitHubActionClient

from ._utils import (
    get_randomized_name,
    get_profile_username,
    create_resource_group,
    get_resource_group,
    queue_acr_build,
    _get_acr_cred,
    create_new_acr,
    _get_default_containerapps_location,
    safe_get,
    is_int,
    create_service_principal_for_rbac,
    repo_url_to_name,
    get_container_app_if_exists,
    trigger_workflow,
    _ensure_location_allowed,
    _is_resource_provider_registered,
    _register_resource_provider
)

from ._constants import MAXIMUM_SECRET_LENGTH, LOG_ANALYTICS_RP

from .custom import (
    create_managed_environment,
    containerapp_up_logic,
    list_containerapp,
    list_managed_environments,
    create_or_update_github_action,
)

logger = get_logger(__name__)


class ResourceGroup:
    def __init__(self, cmd, name: str, location: str, exists: bool = None):
        self.cmd = cmd
        self.name = name
        self.location = _get_default_containerapps_location(cmd, location)
        if self.location.lower() == "northcentralusstage":
            self.location = "eastus"
        self.exists = exists

        self.check_exists()

    def create(self):
        g = create_resource_group(self.cmd, self.name, self.location)
        self.exists = True
        return g

    def _get(self):
        return get_resource_group(self.cmd, self.name)

    def get(self):
        r = None
        try:
            r = self._get()
        except:  # pylint: disable=bare-except
            pass
        return r

    def check_exists(self) -> bool:
        if self.name is None:
            self.exists = False
        else:
            self.exists = check_resource_group_exists(self.cmd, self.name)
        return self.exists

    def create_if_needed(self):
        if not self.check_exists():
            if not self.name:
                self.name = get_randomized_name(get_profile_username())
            logger.warning(f"Creating resource group '{self.name}'")
            self.create()
        else:
            logger.warning(f"Using resource group '{self.name}'")  # TODO use .info()


class Resource:
    def __init__(
        self, cmd, name: str, resource_group: "ResourceGroup", exists: bool = None
    ):
        self.cmd = cmd
        self.name = name
        self.resource_group = resource_group
        self.exists = exists

        self.check_exists()

    def create(self, *args, **kwargs):
        raise NotImplementedError()

    def _get(self):
        raise NotImplementedError()

    def get(self):
        r = None
        try:
            r = self._get()
        except:  # pylint: disable=bare-except
            pass
        return r

    def check_exists(self):
        if self.name is None or self.resource_group.name is None:
            self.exists = False
        else:
            self.exists = self.get() is not None
        return self.exists


class ContainerAppEnvironment(Resource):
    def __init__(
        self,
        cmd,
        name: str,
        resource_group: "ResourceGroup",
        exists: bool = None,
        location=None,
        logs_key=None,
        logs_customer_id=None,
    ):

        super().__init__(cmd, name, resource_group, exists)
        if is_valid_resource_id(name):
            self.name = parse_resource_id(name)["name"]
            if "resource_group" in parse_resource_id(name):
                rg = parse_resource_id(name)["resource_group"]
                if resource_group.name != rg:
                    self.resource_group = ResourceGroup(cmd, rg, location)
        self.location = location
        self.logs_key = logs_key
        self.logs_customer_id = logs_customer_id

    def set_name(self, name_or_rid):
        if is_valid_resource_id(name_or_rid):
            self.name = parse_resource_id(name_or_rid)["name"]
            if "resource_group" in parse_resource_id(name_or_rid):
                rg = parse_resource_id(name_or_rid)["resource_group"]
                if self.resource_group.name != rg:
                    self.resource_group = ResourceGroup(
                        self.cmd,
                        rg,
                        self.location,
                    )
        else:
            self.name = name_or_rid

    def _get(self):
        return ManagedEnvironmentClient.show(
            self.cmd, self.resource_group.name, self.name
        )

    def create_if_needed(self, app_name):
        if not self.check_exists():
            if self.name is None:
                self.name = "{}-env".format(app_name).replace("_", "-")
            logger.warning(
                f"Creating {type(self).__name__} '{self.name}' in resource group {self.resource_group.name}"
            )
            self.create()
        else:
            logger.warning(
                f"Using {type(self).__name__} '{self.name}' in resource group {self.resource_group.name}"
            )  # TODO use .info()

    def create(self):
        self.location = validate_environment_location(self.cmd, self.location)
        if not _is_resource_provider_registered(self.cmd, LOG_ANALYTICS_RP):
            _register_resource_provider(self.cmd, LOG_ANALYTICS_RP)
        env = create_managed_environment(
            self.cmd,
            self.name,
            location=self.location,
            resource_group_name=self.resource_group.name,
            logs_key=self.logs_key,
            logs_customer_id=self.logs_customer_id,
            disable_warnings=True,
        )
        self.exists = True
        return env

    def get_rid(self):
        rid = self.name
        if not is_valid_resource_id(self.name):
            rid = resource_id(
                subscription=get_subscription_id(self.cmd.cli_ctx),
                resource_group=self.resource_group.name,
                namespace="Microsoft.App",
                type="managedEnvironments",
                name=self.name,
            )
        return rid


class AzureContainerRegistry(Resource):
    def __init__(self, name: str, resource_group: "ResourceGroup"):  # pylint: disable=super-init-not-called

        self.name = name
        self.resource_group = resource_group


class ContainerApp(Resource):  # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        cmd,
        name: str,
        resource_group: "ResourceGroup",
        exists: bool = None,
        image=None,
        env: "ContainerAppEnvironment" = None,
        target_port=None,
        registry_server=None,
        registry_user=None,
        registry_pass=None,
        env_vars=None,
        ingress=None,
    ):

        super().__init__(cmd, name, resource_group, exists)
        self.image = image
        self.env = env
        self.target_port = target_port
        self.registry_server = registry_server
        self.registry_user = registry_user
        self.registry_pass = registry_pass
        self.env_vars = env_vars
        self.ingress = ingress

        self.should_create_acr = False
        self.acr: "AzureContainerRegistry" = None

    def _get(self):
        return ContainerAppClient.show(self.cmd, self.resource_group.name, self.name)

    def create(self, no_registry=False):
        # no_registry: don't pass in a registry during create even if the app has one (used for GH actions)
        if get_container_app_if_exists(self.cmd, self.resource_group.name, self.name):
            logger.warning(
                f"Updating Containerapp {self.name} in resource group {self.resource_group.name}"
            )
        else:
            logger.warning(
                f"Creating Containerapp {self.name} in resource group {self.resource_group.name}"
            )

        return containerapp_up_logic(
            cmd=self.cmd,
            name=self.name,
            resource_group_name=self.resource_group.name,
            image=self.image,
            managed_env=self.env.get_rid(),
            target_port=self.target_port,
            registry_server=None if no_registry else self.registry_server,
            registry_pass=None if no_registry else self.registry_pass,
            registry_user=None if no_registry else self.registry_user,
            env_vars=self.env_vars,
            ingress=self.ingress,
        )

    def create_acr_if_needed(self):
        if self.should_create_acr:
            logger.warning(
                f"Creating Azure Container Registry {self.acr.name} in resource group "
                f"{self.acr.resource_group.name}"
            )
            self.create_acr()

    def create_acr(self):
        registry_rg = self.resource_group
        url = self.registry_server
        registry_name = url[: url.rindex(".azurecr.io")]
        location = "eastus"
        if self.env.location and self.env.location.lower() != "northcentralusstage":
            location = self.env.location
        registry_def = create_new_acr(
            self.cmd, registry_name, registry_rg.name, location
        )
        self.registry_server = registry_def.login_server

        if not self.acr:
            self.acr = AzureContainerRegistry(registry_name, registry_rg)

        self.registry_user, self.registry_pass, _ = _get_acr_cred(
            self.cmd.cli_ctx, registry_name
        )

    def run_acr_build(self, dockerfile, source, quiet=False):
        image_name = self.image if self.image is not None else self.name
        from datetime import datetime

        now = datetime.now()
        # Add version tag for acr image
        image_name += ":{}".format(
            str(now).replace(" ", "").replace("-", "").replace(".", "").replace(":", "")
        )

        self.image = self.registry_server + "/" + image_name

        queue_acr_build(
            self.cmd,
            self.acr.resource_group.name,
            self.acr.name,
            image_name,
            source,
            dockerfile,
            quiet,
        )


def _create_service_principal(cmd, resource_group_name, env_resource_group_name):
    logger.warning(
        "No valid service principal provided. Creating a new service principal..."
    )
    scopes = [
        f"/subscriptions/{get_subscription_id(cmd.cli_ctx)}/resourceGroups/{resource_group_name}"
    ]
    if (
        env_resource_group_name is not None
        and env_resource_group_name != resource_group_name
    ):
        scopes.append(
            f"/subscriptions/{get_subscription_id(cmd.cli_ctx)}/resourceGroups/{env_resource_group_name}"
        )
    sp = create_service_principal_for_rbac(cmd, scopes=scopes, role="contributor")

    logger.warning(f"Created service principal: {sp['displayName']} with ID {sp['appId']}")

    return sp["appId"], sp["password"], sp["tenant"]


def _get_or_create_sp(  # pylint: disable=inconsistent-return-statements
    cmd,
    resource_group_name,
    env_resource_group_name,
    name,
    service_principal_client_id,
    service_principal_client_secret,
    service_principal_tenant_id,
):
    if service_principal_client_id and service_principal_client_secret and service_principal_tenant_id:
        return (
            service_principal_client_id,
            service_principal_client_secret,
            service_principal_tenant_id,
        )
    try:
        GitHubActionClient.show(
            cmd=cmd, resource_group_name=resource_group_name, name=name
        )
        return (
            service_principal_client_id,
            service_principal_client_secret,
            service_principal_tenant_id,
        )
    except:  # pylint: disable=bare-except
        service_principal = None

        # TODO if possible, search for SPs with the right credentials
        # I haven't found a way to get SP creds + secrets yet from the API

        if not service_principal:
            return _create_service_principal(
                cmd, resource_group_name, env_resource_group_name
            )
        # return client_id, secret, tenant_id


def _get_dockerfile_content_from_repo(
    repo_url, branch, token, context_path, dockerfile
):
    from github import Github

    g = Github(token)
    context_path = context_path or "."
    repo = repo_url_to_name(repo_url)
    try:
        r = g.get_repo(repo)
        if not branch:
            branch = r.default_branch
    except Exception as e:
        raise ValidationError(f"Could not find repo {repo_url}") from e
    try:
        files = r.get_contents(context_path, ref=branch)
    except Exception as e:
        raise ValidationError(f"Could not find branch {branch}") from e
    for f in files:
        if f.path == dockerfile or f.path.endswith(f"/{dockerfile}"):
            resp = requests.get(f.download_url)
            if resp.ok and resp.content:
                return resp.content.decode("utf-8").split("\n")
    raise ValidationError("Could not find Dockerfile in Github repo/branch. Please ensure it is named 'Dockerfile'. "
                          "Set the path with --context-path if not in the root directory.")


def _get_ingress_and_target_port(ingress, target_port, dockerfile_content: "list[str]"):
    if not target_port and not ingress and dockerfile_content is not None:  # pylint: disable=too-many-nested-blocks
        for line in dockerfile_content:
            if line:
                line = (
                    line.upper()
                    .strip()
                    .replace("/TCP", "")
                    .replace("/UDP", "")
                    .replace("\n", "")
                )
                if line and line[0] != "#":
                    if "EXPOSE" in line:
                        parts = line.split(" ")
                        for i, p in enumerate(parts[:-1]):
                            if "EXPOSE" in p and is_int(parts[i + 1]):
                                target_port = parts[i + 1]
                                ingress = "external"
                                logger.warning(
                                    "Adding external ingress port {} based on dockerfile expose.".format(
                                        target_port
                                    )
                                )
    ingress = "external" if target_port and not ingress else ingress
    return ingress, target_port


def _validate_up_args(cmd, source, image, repo, registry_server):
    disallowed_params = ["--only-show-errors", "--output", "-o"]
    command_args = cmd.cli_ctx.data.get("safe_params", [])
    for a in disallowed_params:
        if a in command_args:
            raise ValidationError(f"Argument {a} is not allowed for 'az containerapp up'")

    if not source and not image and not repo:
        raise RequiredArgumentMissingError(
            "You must specify either --source, --repo, or --image"
        )
    if source and repo:
        raise MutuallyExclusiveArgumentError(
            "Cannot use --source and --repo togther. "
            "Can either deploy from a local directory or a Github repo"
        )
    if repo and registry_server and "azurecr.io" in registry_server:
        parsed = urlparse(registry_server)
        registry_name = (parsed.netloc if parsed.scheme else parsed.path).split(".")[0]
        if registry_name and len(registry_name) > MAXIMUM_SECRET_LENGTH:
            raise ValidationError(f"--registry-server ACR name must be less than {MAXIMUM_SECRET_LENGTH} "
                                  "characters when using --repo")


def _reformat_image(source, repo, image):
    if source and (image or repo):
        image = image.split("/")[-1]  # if link is given
        image = image.replace(":", "")
    return image


def _get_dockerfile_content_local(source, dockerfile):
    lines = []
    if source:
        dockerfile_location = f"{source}/{dockerfile}"
        try:
            with open(dockerfile_location, "r") as fh:  # pylint: disable=unspecified-encoding
                lines = list(fh)
        except Exception as e:
            raise InvalidArgumentValueError(
                "Cannot open specified Dockerfile. Check dockerfile name, path, and permissions."
            ) from e
    return lines


def _get_dockerfile_content(repo, branch, token, source, context_path, dockerfile):
    if source:
        return _get_dockerfile_content_local(source, dockerfile)
    elif repo:
        return _get_dockerfile_content_from_repo(
            repo, branch, token, context_path, dockerfile
        )
    return []


def _get_app_env_and_group(
    cmd, name, resource_group: "ResourceGroup", env: "ContainerAppEnvironment", location
):
    if not resource_group.name and not resource_group.exists:
        matched_apps = [c for c in list_containerapp(cmd) if c["name"].lower() == name.lower()]
        if env.name:
            matched_apps = [c for c in matched_apps if parse_resource_id(c["properties"]["managedEnvironmentId"])["name"].lower() == env.name.lower()]
        if location:
            matched_apps = [c for c in matched_apps if c["location"].lower() == location.lower()]
        if len(matched_apps) == 1:
            resource_group.name = parse_resource_id(matched_apps[0]["id"])[
                "resource_group"
            ]
            env.set_name(matched_apps[0]["properties"]["managedEnvironmentId"])
        elif len(matched_apps) > 1:
            raise ValidationError(
                f"There are multiple containerapps with name {name} on the subscription. "
                "Please specify which resource group your Containerapp is in."
            )


def _get_env_and_group_from_log_analytics(
    cmd,
    resource_group_name,
    env: "ContainerAppEnvironment",
    resource_group: "ResourceGroup",
    logs_customer_id,
    location,
):
    # resource_group_name is the value the user passed in (if present)
    if not env.name:
        if (resource_group_name == resource_group.name and resource_group.exists) or (
            not resource_group_name
        ):
            env_list = list_managed_environments(
                cmd=cmd, resource_group_name=resource_group_name
            )
            if logs_customer_id:
                env_list = [
                    e
                    for e in env_list
                    if safe_get(
                        e,
                        "properties",
                        "appLogsConfiguration",
                        "logAnalyticsConfiguration",
                        "customerId",
                    )
                    == logs_customer_id
                ]
            if location:
                env_list = [e for e in env_list if e["location"] == location]
            if env_list:
                # TODO check how many CA in env
                env_details = parse_resource_id(env_list[0]["id"])
                env.set_name(env_details["name"])
                resource_group.name = env_details["resource_group"]


def _get_acr_from_image(cmd, app):
    if app.image is not None and "azurecr.io" in app.image:
        app.registry_server = app.image.split("/")[
            0
        ]  # TODO what if this conflicts with registry_server param?
        parsed = urlparse(app.image)
        registry_name = (parsed.netloc if parsed.scheme else parsed.path).split(".")[0]
        if app.registry_user is None or app.registry_pass is None:
            logger.info(
                "No credential was provided to access Azure Container Registry. Trying to look up..."
            )
            try:
                app.registry_user, app.registry_pass, registry_rg = _get_acr_cred(
                    cmd.cli_ctx, registry_name
                )
                app.acr = AzureContainerRegistry(
                    registry_name, ResourceGroup(cmd, registry_rg, None, None)
                )
            except Exception as ex:
                raise RequiredArgumentMissingError(
                    "Failed to retrieve credentials for container registry. Please provide the registry username and password"
                ) from ex
        else:
            acr_rg = _get_acr_rg(app)
            app.acr = AzureContainerRegistry(
                name=registry_name,
                resource_group=ResourceGroup(app.cmd, acr_rg, None, None),
            )


def _get_registry_from_app(app):
    containerapp_def = app.get()
    if containerapp_def:
        if (
            len(
                safe_get(
                    containerapp_def,
                    "properties",
                    "configuration",
                    "registries",
                    default=[],
                )
            )
            == 1
        ):
            app.registry_server = containerapp_def["properties"]["configuration"][
                "registries"
            ][0]["server"]


def _get_acr_rg(app):
    registry_name = app.registry_server[: app.registry_server.rindex(".azurecr.io")]
    client = get_mgmt_service_client(
        app.cmd.cli_ctx, ContainerRegistryManagementClient
    ).registries
    return parse_resource_id(acr_show(app.cmd, client, registry_name).id)[
        "resource_group"
    ]


def _get_default_registry_name(app):
    import hashlib

    h = hashlib.sha256()
    h.update(f"{get_subscription_id(app.cmd.cli_ctx)}/{app.env.resource_group.name}/{app.env.name}".encode("utf-8"))

    registry_name = f"{h.hexdigest()}"[:10]  # cap at 15 characters total
    return f"ca{registry_name}acr"  # ACR names must start + end in a letter


def _set_acr_creds(cmd, app: "ContainerApp", registry_name):
    logger.info("No credential was provided to access Azure Container Registry. Trying to look up...")
    try:
        app.registry_user, app.registry_pass, registry_rg = _get_acr_cred(
            cmd.cli_ctx, registry_name
        )
        return registry_rg
    except Exception as ex:
        raise RequiredArgumentMissingError(
            "Failed to retrieve credentials for container registry. Please provide the registry username and password"
        ) from ex


def _get_registry_details(cmd, app: "ContainerApp", source):
    registry_rg = None
    registry_name = None
    if app.registry_server:
        if "azurecr.io" not in app.registry_server and source:
            raise ValidationError(
                "Cannot supply non-Azure registry when using --source."
            )
        parsed = urlparse(app.registry_server)
        registry_name = (parsed.netloc if parsed.scheme else parsed.path).split(".")[0]
        if app.registry_user is None or app.registry_pass is None:
            registry_rg = _set_acr_creds(cmd, app, registry_name)
        else:
            registry_rg = _get_acr_rg(app)
    else:
        registry_name, registry_rg = find_existing_acr(cmd, app)
        if registry_name and registry_rg:
            _set_acr_creds(cmd, app, registry_name)
            app.registry_server = registry_name + ".azurecr.io"
        else:
            registry_rg = app.resource_group.name
            registry_name = _get_default_registry_name(app)
            app.registry_server = registry_name + ".azurecr.io"
            app.should_create_acr = True

    app.acr = AzureContainerRegistry(
        registry_name, ResourceGroup(cmd, registry_rg, None, None)
    )


# attempt to populate defaults for managed env, RG, ACR, etc
def _set_up_defaults(
    cmd,
    name,
    resource_group_name,
    logs_customer_id,
    location,
    resource_group: "ResourceGroup",
    env: "ContainerAppEnvironment",
    app: "ContainerApp",
):
    # If no RG passed in and a singular app exists with the same name, get its env and rg
    _get_app_env_and_group(cmd, name, resource_group, env, location)

    # If no env passed in (and not creating a new RG), then try getting an env by location / log analytics ID
    _get_env_and_group_from_log_analytics(
        cmd, resource_group_name, env, resource_group, logs_customer_id, location
    )

    # try to set RG name by env name
    if env.name and not resource_group.name:
        if not location:
            env_list = [e for e in list_managed_environments(cmd=cmd) if e["name"] == env.name]
        else:
            env_list = [e for e in list_managed_environments(cmd=cmd) if e["name"] == env.name and e["location"] == location]
        if len(env_list) == 1:
            resource_group.name = parse_resource_id(env_list[0]["id"])["resource_group"]
        if len(env_list) > 1:
            raise ValidationError(
                f"There are multiple environments with name {env.name} on the subscription. "
                "Please specify which resource group your Containerapp environment is in."
            )    # get ACR details from --image, if possible
    _get_acr_from_image(cmd, app)


def _create_github_action(
    app: "ContainerApp",
    env: "ContainerAppEnvironment",
    service_principal_client_id,
    service_principal_client_secret,
    service_principal_tenant_id,
    branch,
    token,
    repo,
    context_path,
):

    sp = _get_or_create_sp(
        app.cmd,
        app.resource_group.name,
        env.resource_group.name,
        app.name,
        service_principal_client_id,
        service_principal_client_secret,
        service_principal_tenant_id,
    )
    (
        service_principal_client_id,
        service_principal_client_secret,
        service_principal_tenant_id,
    ) = sp

    # need to trigger the workflow manually if it already exists (performing an update)
    try:
        action = GitHubActionClient.show(cmd=app.cmd, resource_group_name=app.resource_group.name, name=app.name)
        if action:
            trigger_workflow(token, repo, app.name, branch)
    except:  # pylint: disable=bare-except
        pass

    create_or_update_github_action(
        cmd=app.cmd,
        name=app.name,
        resource_group_name=app.resource_group.name,
        repo_url=repo,
        registry_url=app.registry_server,
        registry_username=app.registry_user,
        registry_password=app.registry_pass,
        branch=branch,
        token=token,
        login_with_github=False,
        service_principal_client_id=service_principal_client_id,
        service_principal_client_secret=service_principal_client_secret,
        service_principal_tenant_id=service_principal_tenant_id,
        image=app.image,
        context_path=context_path,
    )


def up_output(app):
    url = safe_get(
        ContainerAppClient.show(app.cmd, app.resource_group.name, app.name),
        "properties",
        "configuration",
        "ingress",
        "fqdn",
    )
    if url and not url.startswith("http"):
        url = f"http://{url}"

    logger.warning(
        f"\nYour container app {app.name} has been created and deployed! Congrats! \n"
    )
    url and logger.warning(f"Browse to your container app at: {url} \n")
    logger.warning(
        f"Stream logs for your container with: az containerapp logs show -n {app.name} -g {app.resource_group.name} \n"
    )
    logger.warning(
        f"See full output using: az containerapp show -n {app.name} -g {app.resource_group.name} \n"
    )


def find_existing_acr(cmd, app: "ContainerApp"):
    from azure.cli.command_modules.acr._client_factory import cf_acr_registries
    client = cf_acr_registries(cmd.cli_ctx)

    acr = None
    try:
        acr = acr_show(cmd, client=client, registry_name=_get_default_registry_name(app))
    except Exception:
        pass

    if acr:
        app.should_create_acr = False
        return acr.name, parse_resource_id(acr.id)["resource_group"]
    return None, None


def validate_environment_location(cmd, location):
    from ._constants import MAX_ENV_PER_LOCATION
    env_list = list_managed_environments(cmd)

    locations = [l["location"] for l in env_list]
    locations = list(set(locations))  # remove duplicates

    location_count = {}
    for loc in locations:
        location_count[loc] = len([e for e in env_list if e["location"] == loc])

    disallowed_locations = []
    for _, value in enumerate(location_count):
        if location_count[value] > MAX_ENV_PER_LOCATION - 1:
            disallowed_locations.append(value)

    res_locations = list_environment_locations(cmd)
    res_locations = [l for l in res_locations if l not in disallowed_locations]

    allowed_locs = ", ".join(res_locations)

    if location:
        try:
            _ensure_location_allowed(cmd, location, "Microsoft.App", "managedEnvironments")
        except Exception:  # pylint: disable=broad-except
            raise ValidationError("You cannot create a Containerapp environment in location {}. List of eligible locations: {}.".format(location, allowed_locs))

    if len(res_locations) > 0:
        if not location:
            logger.warning("Creating environment on location {}.".format(res_locations[0]))
            return res_locations[0]
        if location in disallowed_locations:
            raise ValidationError("You have more than {} environments in location {}. List of eligible locations: {}.".format(MAX_ENV_PER_LOCATION, location, allowed_locs))
        return location
    else:
        raise ValidationError("You cannot create any more environments. Environments are limited to {} per location in a subscription. Please specify an existing environment using --environment.".format(MAX_ENV_PER_LOCATION))


def list_environment_locations(cmd):
    from ._utils import providers_client_factory
    providers_client = providers_client_factory(cmd.cli_ctx, get_subscription_id(cmd.cli_ctx))
    resource_types = getattr(providers_client.get("Microsoft.App"), 'resource_types', [])
    res_locations = []
    for res in resource_types:
        if res and getattr(res, 'resource_type', "") == "managedEnvironments":
            res_locations = getattr(res, 'locations', [])

    res_locations = [res_loc.lower().replace(" ", "").replace("(", "").replace(")", "") for res_loc in res_locations if res_loc.strip()]

    return res_locations


def check_env_name_on_rg(cmd, managed_env, resource_group_name, location):
    if location:
        _ensure_location_allowed(cmd, location, "Microsoft.App", "managedEnvironments")
    if managed_env and resource_group_name and location:
        env_def = None
        try:
            env_def = ManagedEnvironmentClient.show(cmd, resource_group_name, parse_resource_id(managed_env)["name"])
        except:
            pass
        if env_def:
            if location != env_def["location"]:
                raise ValidationError("Environment {} already exists in resource group {} on location {}, cannot change location of existing environment to {}.".format(parse_resource_id(managed_env)["name"], resource_group_name, env_def["location"], location))
