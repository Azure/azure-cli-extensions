# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk.preparers import NoTrafficRecordingPreparer, SingleValueReplacer, get_dummy_cli, CliTestError, ResourceGroupPreparer
from azure.core.exceptions import HttpResponseError
from .constants import USERASSIGNED_IDENTITY

class ApicServicePreparer(NoTrafficRecordingPreparer, SingleValueReplacer):
    def __init__(self, name_prefix='clitest', length=24,
                 parameter_name='service_name', resource_group_parameter_name='resource_group', key='s', 
                 user_assigned_identity = None):
        super(ApicServicePreparer, self).__init__(name_prefix, length)
        self.cli_ctx = get_dummy_cli()
        self.resource_group_parameter_name = resource_group_parameter_name
        self.parameter_name = parameter_name
        self.user_assigned_identity = user_assigned_identity
        self.key = key

    def create_resource(self, name, **kwargs):
        group = self._get_resource_group(**kwargs)

        template = 'az apic create --name {} -g {}'

        if self.user_assigned_identity is None:
            template += ' --identity \'{{type:SystemAssigned}}\''
            cmd = template.format(name, group)
        else:
            template += ' --identity \'{{type:UserAssigned,user-assigned-identities:\'{{{}}}\'}}\''
            cmd = template.format(name, group, self.user_assigned_identity)

        print(cmd)
        self.live_only_execute(self.cli_ctx, cmd)

        self.test_class_instance.kwargs[self.key] = name
            
        return {self.parameter_name: name}

    def remove_resource(self, name, **kwargs):
        # ResourceGroupPreparer will delete everything
        pass

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = 'To create a API Center service a resource group is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ResourceGroupPreparer.__name__))

class ApicMetadataPreparer(NoTrafficRecordingPreparer, SingleValueReplacer):
    def __init__(self, name_prefix='clitest', length=24,
                 parameter_name='metadata_name', resource_group_parameter_name='resource_group',
                 apic_service_parameter_name='service_name',
                 schema='{"type":"boolean", "title":"Public Facing"}',
                 assignments='[{entity:api,required:true,deprecated:false},{entity:environment,required:false,deprecated:false},{entity:deployment,required:true,deprecated:false}]',
                 key='m'):
        super(ApicMetadataPreparer, self).__init__(name_prefix, length)
        self.cli_ctx = get_dummy_cli()
        self.resource_group_parameter_name = resource_group_parameter_name
        self.api_service_parameter_name = apic_service_parameter_name
        self.parameter_name = parameter_name
        self.schema = schema
        self.assignments = assignments
        self.key = key

    def create_resource(self, name, **kwargs):
        group = self._get_resource_group(**kwargs)
        service = self._get_apic_service(**kwargs)

        template = 'az apic metadata create -g {} -n {} --metadata-name {} --schema \'{}\' --assignments \'{}\''
        cmd = template.format(group, service, name, self.schema, self.assignments)
        print(cmd)
        self.live_only_execute(self.cli_ctx, cmd)

        self.test_class_instance.kwargs[self.key] = name
        return {self.parameter_name: name}

    def remove_resource(self, name, **kwargs):
        # ResourceGroupPreparer will delete everything
        pass

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = 'To create an API Center metadata a resource group is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ResourceGroupPreparer.__name__))

    def _get_apic_service(self, **kwargs):
        try:
            return kwargs.get(self.api_service_parameter_name)
        except KeyError:
            template = 'To create an API Center metadata a API Center service is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ApicServicePreparer.__name__))

class ApicEnvironmentPreparer(NoTrafficRecordingPreparer, SingleValueReplacer):
    def __init__(self, name_prefix='clitest', length=24,
                 parameter_name='environment_id', resource_group_parameter_name='resource_group',
                 apic_service_parameter_name='service_name', key='e'):
        super(ApicEnvironmentPreparer, self).__init__(name_prefix, length)
        self.cli_ctx = get_dummy_cli()
        self.resource_group_parameter_name = resource_group_parameter_name
        self.api_service_parameter_name = apic_service_parameter_name
        self.parameter_name = parameter_name
        self.key = key

    def create_resource(self, name, **kwargs):
        group = self._get_resource_group(**kwargs)
        service = self._get_apic_service(**kwargs)

        template = 'az apic environment create -g {} -n {} --environment-id {} --title "test environment" --type testing'
        cmd = template.format(group, service, name)
        print(cmd)
        self.live_only_execute(self.cli_ctx, cmd)

        self.test_class_instance.kwargs[self.key] = name
        return {self.parameter_name: name}

    def remove_resource(self, name, **kwargs):
        # ResourceGroupPreparer will delete everything
        pass

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = 'To create an API Center environment a resource group is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ResourceGroupPreparer.__name__))

    def _get_apic_service(self, **kwargs):
        try:
            return kwargs.get(self.api_service_parameter_name)
        except KeyError:
            template = 'To create an API Center environment an API Center service is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ApicServicePreparer.__name__))

class ApicApiPreparer(NoTrafficRecordingPreparer, SingleValueReplacer):
    def __init__(self, name_prefix='clitest', length=24,
                 parameter_name='api_id', resource_group_parameter_name='resource_group',
                 apic_service_parameter_name='service_name', key='api'):
        super(ApicApiPreparer, self).__init__(name_prefix, length)
        self.cli_ctx = get_dummy_cli()
        self.resource_group_parameter_name = resource_group_parameter_name
        self.api_service_parameter_name = apic_service_parameter_name
        self.parameter_name = parameter_name
        self.key = key

    def create_resource(self, name, **kwargs):
        group = self._get_resource_group(**kwargs)
        service = self._get_apic_service(**kwargs)

        template = 'az apic api create -g {} -n {} --api-id {} --title "Echo API" --type rest'
        cmd = template.format(group, service, name)
        print(cmd)
        self.live_only_execute(self.cli_ctx, cmd)

        self.test_class_instance.kwargs[self.key] = name
        return {self.parameter_name: name}

    def remove_resource(self, name, **kwargs):
        # ResourceGroupPreparer will delete everything
        pass

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = 'To create an API Center API a resource group is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ResourceGroupPreparer.__name__))

    def _get_apic_service(self, **kwargs):
        try:
            return kwargs.get(self.api_service_parameter_name)
        except KeyError:
            template = 'To create an API Center API an API Center service is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ApicServicePreparer.__name__))

class ApicVersionPreparer(NoTrafficRecordingPreparer, SingleValueReplacer):
    def __init__(self, name_prefix='clitest', length=24,
                 parameter_name='version_id', resource_group_parameter_name='resource_group',
                 apic_service_parameter_name='service_name', apic_api_parameter_name='api_id',
                 key='v'):
        super(ApicVersionPreparer, self).__init__(name_prefix, length)
        self.cli_ctx = get_dummy_cli()
        self.resource_group_parameter_name = resource_group_parameter_name
        self.apic_service_parameter_name = apic_service_parameter_name
        self.parameter_name = parameter_name
        self.apic_api_parameter_name = apic_api_parameter_name
        self.key = key

    def create_resource(self, name, **kwargs):
        group = self._get_resource_group(**kwargs)
        service = self._get_apic_service(**kwargs)
        api = self._get_apic_api(**kwargs)

        template = 'az apic api version create -g {} -n {} --api-id {} --version-id {} --lifecycle-stage production --title "v1.0.0"'
        cmd = template.format(group, service, api, name)
        print(cmd)
        self.live_only_execute(self.cli_ctx, cmd)

        self.test_class_instance.kwargs[self.key] = name
        return {self.parameter_name: name}

    def remove_resource(self, name, **kwargs):
        # ResourceGroupPreparer will delete everything
        pass

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = 'To create an API Center API a resource group is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ResourceGroupPreparer.__name__))

    def _get_apic_service(self, **kwargs):
        try:
            return kwargs.get(self.apic_service_parameter_name)
        except KeyError:
            template = 'To create an API Center API an API Center service is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ApicServicePreparer.__name__))

    def _get_apic_api(self, **kwargs):
        try:
            return kwargs.get(self.apic_api_parameter_name)
        except KeyError:
            template = 'To create an API Center Version an API Center API is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ApicApiPreparer.__name__))
        
class ApicDefinitionPreparer(NoTrafficRecordingPreparer, SingleValueReplacer):
    def __init__(self, name_prefix='clitest', length=24,
                 parameter_name='definition_id', resource_group_parameter_name='resource_group',
                 apic_service_parameter_name='service_name', apic_api_parameter_name='api_id',
                 apic_version_parameter_name='version_id', key='d'):
        super(ApicDefinitionPreparer, self).__init__(name_prefix, length)
        self.cli_ctx = get_dummy_cli()
        self.resource_group_parameter_name = resource_group_parameter_name
        self.apic_service_parameter_name = apic_service_parameter_name
        self.parameter_name = parameter_name
        self.apic_api_parameter_name = apic_api_parameter_name
        self.apic_version_parameter_name = apic_version_parameter_name
        self.key = key

    def create_resource(self, name, **kwargs):
        group = self._get_resource_group(**kwargs)
        service = self._get_apic_service(**kwargs)
        api = self._get_apic_api(**kwargs)
        version = self._get_apic_version(**kwargs)

        template = 'az apic api definition create -g {} -n {} --api-id {} --version-id {} --definition-id {} --title "OpenAPI"'
        cmd = template.format(group, service, api, version, name)
        print(cmd)
        self.live_only_execute(self.cli_ctx, cmd)

        self.test_class_instance.kwargs[self.key] = name
        return {self.parameter_name: name}

    def remove_resource(self, name, **kwargs):
        # ResourceGroupPreparer will delete everything
        pass

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = 'To create an API Center API a resource group is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ResourceGroupPreparer.__name__))

    def _get_apic_service(self, **kwargs):
        try:
            return kwargs.get(self.apic_service_parameter_name)
        except KeyError:
            template = 'To create an API Center API an API Center service is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ApicServicePreparer.__name__))

    def _get_apic_api(self, **kwargs):
        try:
            return kwargs.get(self.apic_api_parameter_name)
        except KeyError:
            template = 'To create an API Center Version an API Center API is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ApicApiPreparer.__name__))
        
    def _get_apic_version(self, **kwargs):
        try:
            return kwargs.get(self.apic_version_parameter_name)
        except KeyError:
            template = 'To create an API Center Definition an API Center Version is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ApicVersionPreparer.__name__))
        
class ApicDeploymentPreparer(NoTrafficRecordingPreparer, SingleValueReplacer):
    def __init__(self, name_prefix='clitest', length=24,
                 parameter_name='deployment_id', resource_group_parameter_name='resource_group',
                 apic_service_parameter_name='service_name', apic_api_parameter_name='api_id',
                 apic_version_parameter_name='version_id', apic_definition_parameter_name='definition_id',
                 apic_environment_parameter_name='environment_id', key='dep'):
        super(ApicDeploymentPreparer, self).__init__(name_prefix, length)
        self.cli_ctx = get_dummy_cli()
        self.resource_group_parameter_name = resource_group_parameter_name
        self.apic_service_parameter_name = apic_service_parameter_name
        self.parameter_name = parameter_name
        self.apic_api_parameter_name = apic_api_parameter_name
        self.apic_version_parameter_name = apic_version_parameter_name
        self.apic_definition_parameter_name = apic_definition_parameter_name
        self.apic_environment_parameter_name = apic_environment_parameter_name
        self.key = key

    def create_resource(self, name, **kwargs):
        group = self._get_resource_group(**kwargs)
        service = self._get_apic_service(**kwargs)
        api = self._get_apic_api(**kwargs)
        version = self._get_apic_version(**kwargs)
        definition = self._get_apic_definition(**kwargs)
        environment = self._get_apic_environment(**kwargs)

        template = 'az apic api deployment create -g {} -n {} --api-id {} --definition-id /workspaces/default/apis/{}/versions/{}/definitions/{} --environment-id /workspaces/default/environments/{} --deployment-id {} --title "test deployment" --server \'{{"runtimeUri":["https://example.com"]}}\''
        cmd = template.format(group, service, api, api, version, definition, environment, name)
        print(cmd)
        self.live_only_execute(self.cli_ctx, cmd)

        self.test_class_instance.kwargs[self.key] = name
        return {self.parameter_name: name}

    def remove_resource(self, name, **kwargs):
        # ResourceGroupPreparer will delete everything
        pass

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = 'To create an API Center Deployment a resource group is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ResourceGroupPreparer.__name__))

    def _get_apic_service(self, **kwargs):
        try:
            return kwargs.get(self.apic_service_parameter_name)
        except KeyError:
            template = 'To create an API Center Deployment an API Center service is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ApicServicePreparer.__name__))

    def _get_apic_api(self, **kwargs):
        try:
            return kwargs.get(self.apic_api_parameter_name)
        except KeyError:
            template = 'To create an API Center Deployment an API Center API is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ApicApiPreparer.__name__))
        
    def _get_apic_version(self, **kwargs):
        try:
            return kwargs.get(self.apic_version_parameter_name)
        except KeyError:
            template = 'To create an API Center Deployment an API Center Version is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ApicVersionPreparer.__name__))
        
    def _get_apic_definition(self, **kwargs):
        try:
            return kwargs.get(self.apic_definition_parameter_name)
        except KeyError:
            template = 'To create an API Center Deployment an API Center Definition is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ApicDefinitionPreparer.__name__))
        
    def _get_apic_environment(self, **kwargs):
        try:
            return kwargs.get(self.apic_environment_parameter_name)
        except KeyError:
            template = 'To create an API Center Deployment an API Center Environment is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ApicEnvironmentPreparer.__name__))
        
class ApimServicePreparer(NoTrafficRecordingPreparer, SingleValueReplacer):
    def __init__(self, name_prefix='clitest', length=24,
                 parameter_name='apim_name', resource_group_parameter_name='resource_group',
                 apic_service_name = 'service_name',
                 key='apim'):
        super(ApimServicePreparer, self).__init__(name_prefix, length)
        self.cli_ctx = get_dummy_cli()
        self.resource_group_parameter_name = resource_group_parameter_name
        self.apic_service_name = apic_service_name
        self.parameter_name = parameter_name
        self.use_system_assigned_identity = False if USERASSIGNED_IDENTITY else True
        self.key = key

    def create_resource(self, name, **kwargs):
        self.test_class_instance.kwargs['use_system_assigned_identity'] = self.use_system_assigned_identity
        group = self._get_resource_group(**kwargs)
        service_name = self._get_apic_service(**kwargs)

        # Only setup APIM in live mode
        if self.test_class_instance.is_live:
            # Get system assigned identity id for API Center
            apic_service = self.test_class_instance.cmd('az apic show -g {} -n {}'.format(group, service_name)).get_output_in_json()
            if self.use_system_assigned_identity:
                self.test_class_instance.kwargs.update({
                    'identity_id': apic_service['identity']['principalId']
                })

            # Create APIM service
            apim_service = self.test_class_instance.cmd('az apim create -g {} --name {} --publisher-name test --publisher-email test@example.com --sku-name Consumption'.format(group, name)).get_output_in_json()
            apim_id = apim_service['id']
            self.test_class_instance.kwargs[self.parameter_name] = name
            self.test_class_instance.kwargs.update({
                'apim_id': apim_id,
                'usi_id': USERASSIGNED_IDENTITY,
                'apic_service_name': service_name,
                'group': group
            })

            # Add echo api
            self.test_class_instance.cmd('az apim api create -g {} --service-name {} --api-id echotest --display-name "Echo API Test" --path "/echotest"'.format(group, name))
            self.test_class_instance.cmd('az apim api operation create -g {} --service-name {} --api-id echotest --url-template "/echotest" --method "GET" --display-name "GetOperation"'.format(group, name))
            # Add foo api
            self.test_class_instance.cmd('az apim api create -g {} --service-name {} --api-id footest --display-name "Foo API Test" --path "/footest"'.format(group, name))
            self.test_class_instance.cmd('az apim api operation create -g {} --service-name {} --api-id footest --url-template "/footest" --method "GET" --display-name "GetOperation"'.format(group, name))

            if self.use_system_assigned_identity:
                # Grant system assigned identity of API Center access to APIM
                self.test_class_instance.cmd('az role assignment create --role "API Management Service Reader Role" --assignee-object-id {} --assignee-principal-type ServicePrincipal --scope {}'.format(self.test_class_instance.kwargs['identity_id'], apim_id))
            else:
                # Attach user assigned identity with access to APIM to API Center
                # In APICServicePreparer, we already attached the user assigned identity provided by user to API Center. Please check it.
                self.test_class_instance.cmd('az apic update --name {apic_service_name} -g {group} --identity {{type:UserAssigned,user-assigned-identities:{{{usi_id}}}}}')

        self.test_class_instance.kwargs[self.parameter_name] = name
        return {self.parameter_name: name}

    def remove_resource(self, name, **kwargs):
        # ResourceGroupPreparer will delete everything
        pass

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = 'To create an API Management service a resource group is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ResourceGroupPreparer.__name__))    

    def _get_apic_service(self, **kwargs):
        try:
            return kwargs.get(self.apic_service_name)
        except KeyError:
            template = 'To create an API Center service is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ApicServicePreparer.__name__))    


class ApiAnalysisPreparer(NoTrafficRecordingPreparer, SingleValueReplacer):
    def __init__(self, config_name='spectral-config', parameter_name='config_name', resource_group_parameter_name='resource_group', api_service_parameter_name='service_name', ensure_clean=False):
        # Use a shorter prefix and set appropriate length to avoid validation errors
        super(ApiAnalysisPreparer, self).__init__('spec', 24)  # Short prefix with standard length
        self.cli_ctx = get_dummy_cli()
        self.parameter_name = parameter_name
        self.resource_group_parameter_name = resource_group_parameter_name
        self.api_service_parameter_name = api_service_parameter_name
        self.key = parameter_name
        self.fixed_name = config_name
        self.ensure_clean = ensure_clean  # Flag to determine if we should delete existing configs

    def create_resource(self, name, **kwargs):
        group = self._get_resource_group(**kwargs)
        service = self._get_apic_service(**kwargs)
        
        # Always use the fixed name for consistency
        name = self.fixed_name

        # Check if we need to ensure a clean state (for create tests)
        if self.ensure_clean:
            # Delete all existing analyzer configs first
            try:
                configs = self.live_only_execute(self.cli_ctx, 'az apic api-analysis list -g {} -n {}'.format(group, service)).get_output_in_json()
                for config in configs:
                    config_name = config.get('name')
                    if config_name:
                        try:
                            self.live_only_execute(self.cli_ctx, 'az apic api-analysis delete -g {} -n {} -c {} --yes'.format(group, service, config_name))
                        except Exception:
                            # Ignore errors if deletion fails
                            pass
            except Exception:
                # If listing fails, continue anyway
                pass

            # Now create the new analyzer config
            template = 'az apic api-analysis create -g {} -n {} -c {}'
            cmd = template.format(group, service, name)
            print(cmd)
            self.live_only_execute(self.cli_ctx, cmd)
        else:
            # For other tests, use any existing config or create our default one
            try:
                configs = self.live_only_execute(self.cli_ctx, 'az apic api-analysis list -g {} -n {}'.format(group, service)).get_output_in_json()
                if configs:
                    # Use the first existing config (could be service default or our default)
                    name = configs[0].get('name')
                    print(f"Using existing analyzer config: {name}")
                else:
                    # No configs exist, create our default one
                    template = 'az apic api-analysis create -g {} -n {} -c {}'
                    cmd = template.format(group, service, name)
                    print(cmd)
                    self.live_only_execute(self.cli_ctx, cmd)
            except Exception:
                # If listing fails, try to create our default config
                template = 'az apic api-analysis create -g {} -n {} -c {}'
                cmd = template.format(group, service, name)
                print(cmd)
                try:
                    self.live_only_execute(self.cli_ctx, cmd)
                except HttpResponseError as e:
                    if "Number of analyzer configs for this service" in str(e):
                        # If creation fails due to limit, list and use existing
                        configs = self.live_only_execute(self.cli_ctx, 'az apic api-analysis list -g {} -n {}'.format(group, service)).get_output_in_json()
                        if configs:
                            name = configs[0].get('name')
                            print(f"Using existing analyzer config due to limit: {name}")
                        else:
                            raise
                    else:
                        raise

        self.test_class_instance.kwargs[self.key] = name
        return {self.parameter_name: name}

    def remove_resource(self, name, **kwargs):
        # ResourceGroupPreparer will delete everything
        pass

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = 'To create an API Analysis configuration, a resource group is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ResourceGroupPreparer.__name__))

    def _get_apic_service(self, **kwargs):
        try:
            return kwargs.get(self.api_service_parameter_name)
        except KeyError:
            template = 'To create an API Analysis configuration, an API Center service is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ApicServicePreparer.__name__))


class ApiAnalysisCreatePreparer(ApiAnalysisPreparer):
    """Special preparer for create tests that ensures clean state"""
    def __init__(self, config_name='spectral-config', parameter_name='config_name', resource_group_parameter_name='resource_group', api_service_parameter_name='service_name'):
        super().__init__(config_name, parameter_name, resource_group_parameter_name, api_service_parameter_name, ensure_clean=True)
