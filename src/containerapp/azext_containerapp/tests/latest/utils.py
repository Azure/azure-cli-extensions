# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import sys
import time
import requests
from azure.cli.command_modules.containerapp._utils import format_location

from .common import TEST_LOCATION, STAGE_LOCATION
from azure.cli.core.azclierror import MutuallyExclusiveArgumentError, RequiredArgumentMissingError, InvalidArgumentValueError
from msrestazure.tools import parse_resource_id

from azure.cli.testsdk import (JMESPathCheck)


def prepare_containerapp_env_for_app_e2e_tests(test_cls, location=TEST_LOCATION):
    from azure.cli.core.azclierror import CLIInternalError
    rg_name = f'client.env_rg_{location}'.lower().replace(" ", "").replace("(", "").replace(")", "")
    env_name = f'env-{location}'.lower().replace(" ", "").replace("(", "").replace(")", "")
    managed_env = None
    try:
        managed_env = test_cls.cmd('containerapp env show -g {} -n {}'.format(rg_name, env_name)).get_output_in_json()
    except CLIInternalError as e:
        if e.error_msg.__contains__('ResourceGroupNotFound') or e.error_msg.__contains__('ResourceNotFound'):
            # resource group is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
            rg_location = location
            if format_location(rg_location) == format_location(STAGE_LOCATION):
                rg_location = "eastus"
            test_cls.cmd(f'group create -n {rg_name} -l {rg_location}')
            test_cls.cmd(f'containerapp env create -g {rg_name} -n {env_name} --logs-destination none')
            managed_env = test_cls.cmd('containerapp env show -g {} -n {}'.format(rg_name, env_name)).get_output_in_json()

            while managed_env["properties"]["provisioningState"].lower() == "waiting":
                time.sleep(5)
                managed_env = test_cls.cmd('containerapp env show -g {} -n {}'.format(rg_name, env_name)).get_output_in_json()
    return managed_env["id"]


def create_containerapp_env(test_cls, env_name, resource_group, location=None, subnetId=None):
    logs_workspace_name = test_cls.create_random_name(prefix='containerapp-env', length=24)
    logs_workspace_location = location
    if logs_workspace_location is None or format_location(logs_workspace_location) == format_location(STAGE_LOCATION):
        logs_workspace_location = "eastus"
    logs_workspace_id = test_cls.cmd('monitor log-analytics workspace create -g {} -n {} -l {}'.format(resource_group, logs_workspace_name, logs_workspace_location)).get_output_in_json()["customerId"]
    logs_workspace_key = test_cls.cmd('monitor log-analytics workspace get-shared-keys -g {} -n {}'.format(resource_group, logs_workspace_name)).get_output_in_json()["primarySharedKey"]

    env_command = f'containerapp env create -g {resource_group} -n {env_name} --logs-workspace-id {logs_workspace_id} --logs-workspace-key {logs_workspace_key}'
    if location:
        env_command = f'{env_command} -l {location}'

    if subnetId:
        env_command = f'{env_command} --infrastructure-subnet-resource-id {subnetId}'
    test_cls.cmd(env_command)

    containerapp_env = test_cls.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

    while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
        time.sleep(5)
        containerapp_env = test_cls.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

def create_and_verify_containerapp_up(
            test_cls,
            resource_group,
            env_name = None,
            source_path = None,
            artifact_path = None,
            build_env_vars = None,
            image = None,
            location = None,
            ingress = None,
            target_port = None,
            app_name = None,
            requires_acr_prerequisite = False,
            no_log_destination = False):
        # Ensure that the Container App environment is created
        if env_name is None:
           env_name = test_cls.create_random_name(prefix='env', length=24)
           env_create_cmd = f'containerapp env create -g {resource_group} -n {env_name}'
           if no_log_destination:
               env_create_cmd += f" --logs-destination none"
           test_cls.cmd(env_create_cmd)

        if app_name is None:
            # Generate a name for the Container App
            app_name = test_cls.create_random_name(prefix='containerapp', length=24)

        # Construct the 'az containerapp up' command
        up_cmd = f"containerapp up -g {resource_group} -n {app_name} --environment {env_name}"
        if source_path:
            up_cmd += f" --source \"{source_path}\""
        if artifact_path:
            up_cmd += f" --artifact \"{artifact_path}\""
        if build_env_vars:
            up_cmd += f" --build-env-vars {build_env_vars}"
        if image:
            up_cmd += f" --image {image}"
        if ingress:
            up_cmd += f" --ingress {ingress}"
        if target_port:
            up_cmd += f" --target-port {target_port}"

        if requires_acr_prerequisite:
            # Create ACR
            registry_name = test_cls.create_random_name(prefix='containerapp', length=24)
            acr = test_cls.cmd('acr create -g {} -n {} --sku Basic --admin-enabled'.format(resource_group, registry_name)).get_output_in_json()
            registry_server = acr["loginServer"]
            acr_credentials = test_cls.cmd('acr credential show -g {} -n {}'.format(resource_group, registry_name)).get_output_in_json()
            registry_user = acr_credentials["username"]
            registry_pass = acr_credentials["passwords"][0]["value"]
            up_cmd += f" --registry-server {registry_server} --registry-username {registry_user} --registry-password {registry_pass}"

        # Execute the 'az containerapp up' command
        test_cls.cmd(up_cmd)

        # Verify that the Container App is running
        app = test_cls.cmd(f"containerapp show -g {resource_group} -n {app_name}").get_output_in_json()
        url = app["properties"]["configuration"]["ingress"]["fqdn"]
        url = url if url.startswith("http") else f"http://{url}"
        resp = requests.get(url)
        test_cls.assertTrue(resp.ok)

        # Re-run the 'az containerapp up' command with the location parameter if provided
        if location:
            up_cmd += f" -l {location.upper()}"
            test_cls.cmd(up_cmd)


def create_and_verify_containerapp_up_with_multiple_environments(
            test_cls,
            resource_group,
            source_path = None,
            location = None,
            ingress = None,
            image = None,
            target_port = None,
            app_name = None):

        if app_name is None:
            # Generate a name for the Container App
            app_name = test_cls.create_random_name(prefix='containerapp', length=24)
        if image is None:
            image = "mcr.microsoft.com/k8se/quickstart:latest"
        if location is None:
            location = TEST_LOCATION

        # Create multiple environments
        first_env_name = test_cls.create_random_name(prefix='env', length=24)
        test_cls.cmd(f'containerapp env create -g {resource_group} -n {first_env_name} -l {location}')

        second_env_name = test_cls.create_random_name(prefix='env', length=24)
        test_cls.cmd(f'containerapp env create -g {resource_group} -n {second_env_name} -l {location}')

        # Construct the 'az containerapp up' command
        up_cmd = f"containerapp up -g {resource_group} -n {app_name} --environment {second_env_name} --image {image} --location {location}"

        # Execute the 'az containerapp up' command to create the Container App
        test_cls.cmd(up_cmd)

        up_cmd = f"containerapp up -g {resource_group} -n {app_name}"
        if source_path:
            up_cmd += f" --source \"{source_path}\""
        if ingress:
            up_cmd += f" --ingress {ingress}"
        if target_port:
            up_cmd += f" --target-port {target_port}"
        if location:
            up_cmd += f" -l {location}"

        # Execute the 'az containerapp up' command with `--source` parameter to trigger cloud build
        test_cls.cmd(up_cmd)

        # Verify that the Container App is running
        app = test_cls.cmd(f"containerapp show -g {resource_group} -n {app_name}").get_output_in_json()
        url = app["properties"]["configuration"]["ingress"]["fqdn"]
        containerapp_env = test_cls.cmd('containerapp env show -g {} -n {}'.format(resource_group, second_env_name)).get_output_in_json()
        test_cls.assertEqual(app["properties"]["environmentId"], containerapp_env["id"])
        url = url if url.startswith("http") else f"http://{url}"
        resp = requests.get(url)
        test_cls.assertTrue(resp.ok)

        # Delete the Container App and the environments other than the one used for builder creation. (Cannot delete the environment used for builder creation without deleting the builder)
        test_cls.cmd('containerapp delete -g {} -n {} --yes --no-wait'.format(resource_group, app_name))
        test_cls.cmd('containerapp env delete -g {} -n {} --yes --no-wait'.format(resource_group, first_env_name))

def create_and_verify_containerapp_up_for_default_registry_image(
            test_cls,
            resource_group,
            source_path = None,
            location = None,
            ingress = None,
            image = None,
            target_port = None,
            app_name = None,
            env_name = None,
            container_name = None,
            cpu = None,
            memory = None):
         # Ensure that the Container App environment is created
        if env_name is None:
           env_name = test_cls.create_random_name(prefix='env', length=24)
        if app_name is None:
            # Generate a name for the Container App
            app_name = test_cls.create_random_name(prefix='containerapp', length=24)
        if image is None:
            image = "mcr.microsoft.com/k8se/quickstart:latest"
        if location is None:
            location = TEST_LOCATION

        # Create the environment
        create_containerapp_env(test_cls=test_cls,resource_group=resource_group, env_name=env_name, location=location)

        # Construct the 'az containerapp create' command
        create_cmd = f"containerapp create -g {resource_group} -n {app_name} --environment {env_name} --image {image} --container-name {container_name} --cpu {cpu} --memory {memory} --target-port {target_port} --ingress {ingress}"
        test_cls.cmd(create_cmd)

        # Assert that the Container App only has one container and the quickstart image is used
        app = test_cls.cmd(f"containerapp show -g {resource_group} -n {app_name}").get_output_in_json()
        test_cls.assertEqual(app["properties"]["template"]["containers"][0]["name"], container_name)
        test_cls.assertEqual(app["properties"]["template"]["containers"][0]["image"], image)
        test_cls.assertEqual(len(app["properties"]["template"]["containers"]), 1)

        up_cmd = f"containerapp up -g {resource_group} -n {app_name}"
        if source_path:
            up_cmd += f" --source \"{source_path}\""
        if ingress:
            up_cmd += f" --ingress {ingress}"
        if target_port:
            up_cmd += f" --target-port {target_port}"
        if location:
            up_cmd += f" -l {location}"

        # Execute the 'az containerapp up' command to run source to cloud and update the Container App
        test_cls.cmd(up_cmd)

        # Assert that the Containre App only has one container and the source to cloud image is used
        app = test_cls.cmd(f"containerapp show -g {resource_group} -n {app_name}").get_output_in_json()
        test_cls.assertEqual(app["properties"]["template"]["containers"][0]["name"], app_name)
        test_cls.assertEqual(app["properties"]["template"]["containers"][0]["image"].split("/")[0], "default")
        test_cls.assertEqual(len(app["properties"]["template"]["containers"]), 1)

        # Verify that the Container App is running
        app = test_cls.cmd(f"containerapp show -g {resource_group} -n {app_name}").get_output_in_json()
        url = app["properties"]["configuration"]["ingress"]["fqdn"]
        url = url if url.startswith("http") else f"http://{url}"
        resp = requests.get(url)
        test_cls.assertTrue(resp.ok)

        test_cls.cmd('containerapp delete -g {} -n {} --yes'.format(resource_group, app_name))
        test_cls.cmd('containerapp list -g {}'.format(resource_group), checks=[
            JMESPathCheck('length(@)', 0),
        ])


def create_extension_and_custom_location(test_cls, resource_group, connected_cluster_name, custom_location_name):
    try:
        connected_cluster = test_cls.cmd(f'az connectedk8s show --resource-group {resource_group} --name {connected_cluster_name}').get_output_in_json()
        while connected_cluster["connectivityStatus"] == "Connecting":
            time.sleep(5)
            connected_cluster = test_cls.cmd(f'az connectedk8s show --resource-group {resource_group} --name {connected_cluster_name}').get_output_in_json()

        connected_cluster_id = connected_cluster.get('id')
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus2euap"
        extension = test_cls.cmd(f'az k8s-extension create'
                                 f' --resource-group {resource_group}'
                                 f' --name containerapp-ext'
                                 f' --cluster-type connectedClusters'
                                 f' --cluster-name {connected_cluster_name}'
                                 f' --extension-type "Microsoft.App.Environment" '
                                 f' --release-train stable'
                                 f' --auto-upgrade-minor-version true'
                                 f' --scope cluster'
                                 f' --release-namespace appplat-ns'
                                 f' --configuration-settings "Microsoft.CustomLocation.ServiceAccount=default"'
                                 f' --configuration-settings "appsNamespace=appplat-ns"'
                                 f' --configuration-settings "clusterName={connected_cluster_name}"'
                                 f' --configuration-settings "envoy.annotations.service.beta.kubernetes.io/azure-load-balancer-resource-group={resource_group}"').get_output_in_json()
        test_cls.cmd(f'az customlocation create -g {resource_group} -n {custom_location_name} -l {location} --host-resource-id {connected_cluster_id} --namespace appplat-ns -c {extension["id"]}')
    except:
        pass


def verify_containerapp_create_exception(
            test_cls,
            resource_group,
            err,
            env_name = None,
            app_name = None,
            source_path = None,
            repo = None,
            yaml = None,
            environment_type = None,
            registry_server = None,
            registry_user = None,
            registry_pass = None):
        # Configure the default location
        test_cls.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        # Ensure that the Container App environment is created
        env_id = None
        if env_name is None:
            env_id = prepare_containerapp_env_for_app_e2e_tests(test_cls)
            env_name = parse_resource_id(env_id).get('name')

        if app_name is None:
            # Generate a name for the Container App
            app_name = test_cls.create_random_name(prefix='containerapp', length=24)

        # Construct the 'az containerapp create' command
        create_cmd = 'containerapp create -g {} -n {} --environment {}'.format(
            resource_group, app_name, env_id or env_name)
        if source_path:
            create_cmd += f" --source \"{source_path}\""
        if repo:
            create_cmd += f" --repo {repo}"
        if environment_type:
            create_cmd += f" --environment-type {environment_type}"
        if yaml:
            create_cmd += f" --yaml {yaml}"
        if registry_server:
            create_cmd += f" --registry-server {registry_server}"
        if registry_user:
            create_cmd += f" --registry-username {registry_user}"
        if registry_pass:
            create_cmd += f" --registry-password {registry_pass}"

        # Verify appropriate exception was raised
        if registry_server and registry_user and registry_pass:
            with test_cls.assertRaises(InvalidArgumentValueError) as cm:
                # Execute the 'az containerapp create' command
                test_cls.cmd(create_cmd)
        elif source_path and (not repo and not yaml and not environment_type):
            with test_cls.assertRaises(RequiredArgumentMissingError) as cm:
                # Execute the 'az containerapp create' command
                test_cls.cmd(create_cmd)
        else:
            with test_cls.assertRaises(MutuallyExclusiveArgumentError) as cm:
                # Execute the 'az containerapp create' command
                test_cls.cmd(create_cmd)

        test_cls.assertEqual(str(cm.exception), err)

        test_cls.cmd('containerapp delete -g {} -n {} --yes'.format(resource_group, app_name))
        test_cls.cmd('containerapp list -g {}'.format(resource_group), checks=[
            JMESPathCheck('length(@)', 0),
        ])

        test_cls.cmd('containerapp env delete -g {} -n {} --yes'.format(resource_group, env_name))
        test_cls.cmd('containerapp env list -g {}'.format(resource_group), checks=[
            JMESPathCheck('length(@)', 0),
        ])


def create_and_verify_containerapp_create_and_update(
            test_cls,
            resource_group,
            env_name = None,
            source_path = None,
            artifact_path = None,
            build_env_vars = None,
            image = None,
            ingress = None,
            target_port = None,
            app_name = None,
            registry_server = None,
            registry_user = None,
            registry_pass = None):
        # Configure the default location
        # 'Microsoft.ContainerRegistry/registries' is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        test_cls.cmd('configure --defaults location={}'.format(location))

        # Ensure that the Container App environment is created
        env_id = None
        if env_name is None:
            env_id = prepare_containerapp_env_for_app_e2e_tests(test_cls)
            env_name = parse_resource_id(env_id).get('name')

        if app_name is None:
            # Generate a name for the Container App
            app_name = test_cls.create_random_name(prefix='containerapp', length=24)

        registry_name = test_cls.create_random_name(prefix='containerapp', length=24)

        # Create ACR
        acr = test_cls.cmd('acr create -g {} -n {} --sku Basic --admin-enabled'.format(resource_group, registry_name)).get_output_in_json()
        if registry_server is None :
            registry_server = acr["loginServer"]

        acr_credentials = test_cls.cmd('acr credential show -g {} -n {}'.format(resource_group, registry_name)).get_output_in_json()
        if registry_user is None:
            registry_user = acr_credentials["username"]
        if registry_pass is None:
            registry_pass = acr_credentials["passwords"][0]["value"]
        image_name = registry_server + "/" + app_name

        # Construct the 'az containerapp create' command without registry username and password
        create_cmd = 'containerapp create -g {} -n {} --environment {} --registry-server {}'.format(
            resource_group, app_name, env_id or env_name, registry_server)
        if source_path:
            create_cmd += f" --source \"{source_path}\""
        if artifact_path:
            create_cmd += f" --artifact \"{artifact_path}\""
        if build_env_vars:
            create_cmd += f" --build-env-vars {build_env_vars}"
        if image:
            create_cmd += f" --image {image}"
            image_name = registry_server + "/" + _reformat_image(image)
        if ingress:
            create_cmd += f" --ingress {ingress}"
        if target_port:
            create_cmd += f" --target-port {target_port}"

        # Execute the 'az containerapp create' command
        test_cls.cmd(create_cmd)

         # Verify successful execution
        app = test_cls.cmd(f"containerapp show -g {resource_group} -n {app_name}", checks=[
            JMESPathCheck('properties.configuration.registries[0].server', registry_server),
            JMESPathCheck('properties.configuration.registries[0].username', registry_user),
            JMESPathCheck('properties.provisioningState', 'Succeeded'),
        ]).get_output_in_json()
        test_cls.assertEqual(app["properties"]["template"]["containers"][0]["image"].split(":")[0], image_name)

        # Re-construct the 'az containerapp create' command with registry username and password
        create_cmd = 'containerapp create -g {} -n {} --environment {} --registry-username {} --registry-server {} --registry-password {}'.format(
            resource_group, app_name, env_id or env_name, registry_user, registry_server, registry_pass)
        if source_path:
            create_cmd += f" --source \"{source_path}\""
        if artifact_path:
            create_cmd += f" --artifact \"{artifact_path}\""
        if image:
            create_cmd += f" --image {image}"
            image_name = registry_server + "/" + _reformat_image(image)
        if ingress:
            create_cmd += f" --ingress {ingress}"
        if target_port:
            create_cmd += f" --target-port {target_port}"

        # Re-execute the 'az containerapp create' command
        test_cls.cmd(create_cmd)

        # Verify successful execution
        app = test_cls.cmd(f"containerapp show -g {resource_group} -n {app_name}", checks=[
            JMESPathCheck('properties.configuration.registries[0].server', registry_server),
            JMESPathCheck('properties.configuration.registries[0].username', registry_user),
            JMESPathCheck('properties.provisioningState', 'Succeeded'),
        ]).get_output_in_json()
        test_cls.assertEqual(app["properties"]["template"]["containers"][0]["image"].split(":")[0], image_name)
        old_image = app["properties"]["template"]["containers"][0]["image"]

        # Construct the 'az containerapp update' command
        update_cmd = 'containerapp update -g {} -n {}'.format(
            resource_group, app_name)
        if source_path:
            update_cmd += f" --source \"{source_path}\""
        if artifact_path:
            update_cmd += f" --artifact \"{artifact_path}\""
        if image:
            update_cmd += f" --image {image}"

        # Execute the 'az containerapp update' command
        test_cls.cmd(update_cmd)

        # Verify successful execution
        app = test_cls.cmd(f"containerapp show -g {resource_group} -n {app_name}", checks=[
            JMESPathCheck('properties.configuration.registries[0].server', registry_server),
            JMESPathCheck('properties.configuration.registries[0].username', registry_user),
            JMESPathCheck('properties.provisioningState', 'Succeeded'),
        ]).get_output_in_json()
        test_cls.assertEqual(app["properties"]["template"]["containers"][0]["image"].split(":")[0], image_name)
        test_cls.assertNotEqual(app["properties"]["template"]["containers"][0]["image"], old_image)

        test_cls.cmd('containerapp delete -g {} -n {} --yes'.format(resource_group, app_name))
        test_cls.cmd('containerapp list -g {}'.format(resource_group), checks=[
            JMESPathCheck('length(@)', 0),
        ])

        test_cls.cmd('containerapp env delete -g {} -n {} --yes'.format(resource_group, env_name))
        test_cls.cmd('containerapp env list -g {}'.format(resource_group), checks=[
            JMESPathCheck('length(@)', 0),
        ])


def _reformat_image(image):
    image = image.split("/")[-1]
    image = image.replace(":","")
    return image
