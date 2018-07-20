# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-few-public-methods,too-many-arguments,no-self-use,too-many-locals,line-too-long,unused-argument

from __future__ import print_function
from collections import OrderedDict
import json
import ssl
import sys
import os
from time import sleep

from six.moves.urllib.request import urlopen  # pylint: disable=import-error
from knack.log import get_logger
from knack.prompting import prompt, prompt_pass, prompt_t_f, prompt_choice_list, prompt_int, NoTTYException
from knack.util import CLIError

from azure.cli.core.util import get_file_json, shell_safe_json_parse, sdk_no_wait
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import ResourceType, get_sdk

from azext_mesh._client_factory import cf_mesh_network, cf_mesh_application, cf_mesh_deployments
from azext_mesh.servicefabricmesh.mgmt.servicefabricmesh.models import ErrorModelException

logger = get_logger(__name__)


def list_application(client, resource_group_name=None):
    """List all applications. """
    if resource_group_name is None:
        return client.list_by_subscription()
    return client.list_by_resource_group(resource_group_name)


def show_application(client, resource_group_name, name):
    """Show details of an application. """
    return client.get(resource_group_name, name)


def delete_application(client, resource_group_name, name, **kwargs):
    """Delete an application. """
    return client.delete(resource_group_name, name)


def _ssl_context():
    if sys.version_info < (3, 4):
        return ssl.SSLContext(ssl.PROTOCOL_TLSv1)

    return ssl.create_default_context()


def _urlretrieve(url):
    req = urlopen(url, context=_ssl_context())
    return req.read()


def _process_parameters(template_param_defs, parameter_lists):

    def _try_parse_json_object(value):
        try:
            parsed = shell_safe_json_parse(value)
            return parsed.get('parameters', parsed)
        except CLIError:
            return None

    def _try_load_file_object(value):
        if os.path.isfile(value):
            parsed = get_file_json(value, throw_on_empty=False)
            return parsed.get('parameters', parsed)
        return None

    def _try_parse_key_value_object(template_param_defs, parameters, value):
        try:
            key, value = value.split('=', 1)
        except ValueError:
            return False

        param = template_param_defs.get(key, None)
        if param is None:
            raise CLIError("unrecognized template parameter '{}'. Allowed parameters: {}"
                           .format(key, ', '.join(sorted(template_param_defs.keys()))))

        param_type = param.get('type', None)
        if param_type:
            param_type = param_type.lower()
        if param_type in ['object', 'array']:
            parameters[key] = {'value': shell_safe_json_parse(value)}
        elif param_type in ['string', 'securestring']:
            parameters[key] = {'value': value}
        elif param_type == 'bool':
            parameters[key] = {'value': value.lower() == 'true'}
        elif param_type == 'int':
            parameters[key] = {'value': int(value)}
        else:
            logger.warning("Unrecognized type '%s' for parameter '%s'. Interpretting as string.", param_type, key)
            parameters[key] = {'value': value}

        return True

    parameters = {}
    for params in parameter_lists or []:
        for item in params:
            param_obj = _try_load_file_object(item) or _try_parse_json_object(item)
            if param_obj:
                parameters.update(param_obj)
            elif not _try_parse_key_value_object(template_param_defs, parameters, item):
                raise CLIError('Unable to parse parameter: {}'.format(item))

    return parameters


def _find_missing_parameters(parameters, template):
    if template is None:
        return {}
    template_parameters = template.get('parameters', None)
    if template_parameters is None:
        return {}

    missing = OrderedDict()
    for parameter_name in template_parameters:
        parameter = template_parameters[parameter_name]
        if 'defaultValue' in parameter:
            continue
        if parameters is not None and parameters.get(parameter_name, None) is not None:
            continue
        missing[parameter_name] = parameter
    return missing


def _prompt_for_parameters(missing_parameters, fail_on_no_tty=True):  # pylint: disable=too-many-statements

    prompt_list = missing_parameters.keys() if isinstance(missing_parameters, OrderedDict) \
        else sorted(missing_parameters)
    result = OrderedDict()
    no_tty = False
    for param_name in prompt_list:
        param = missing_parameters[param_name]
        param_type = param.get('type', 'string')
        description = 'Missing description'
        metadata = param.get('metadata', None)
        if metadata is not None:
            description = metadata.get('description', description)
        allowed_values = param.get('allowedValues', None)

        prompt_str = "Please provide {} value for '{}' (? for help): ".format(param_type, param_name)
        while True:
            if allowed_values is not None:
                try:
                    ix = prompt_choice_list(prompt_str, allowed_values, help_string=description)
                    result[param_name] = allowed_values[ix]
                except NoTTYException:
                    result[param_name] = None
                    no_tty = True
                break
            elif param_type == 'securestring':
                try:
                    value = prompt_pass(prompt_str, help_string=description)
                except NoTTYException:
                    value = None
                    no_tty = True
                result[param_name] = value
                break
            elif param_type == 'int':
                try:
                    int_value = prompt_int(prompt_str, help_string=description)
                    result[param_name] = int_value
                except NoTTYException:
                    result[param_name] = 0
                    no_tty = True
                break
            elif param_type == 'bool':
                try:
                    value = prompt_t_f(prompt_str, help_string=description)
                    result[param_name] = value
                except NoTTYException:
                    result[param_name] = False
                    no_tty = True
                break
            elif param_type in ['object', 'array']:
                try:
                    value = prompt(prompt_str, help_string=description)
                except NoTTYException:
                    value = ''
                    no_tty = True

                if value == '':
                    value = {} if param_type == 'object' else []
                else:
                    try:
                        value = shell_safe_json_parse(value)
                    except Exception as ex:  # pylint: disable=broad-except
                        logger.error(ex)
                        continue
                result[param_name] = value
                break
            else:
                try:
                    result[param_name] = prompt(prompt_str, help_string=description)
                except NoTTYException:
                    result[param_name] = None
                    no_tty = True
                break
    if no_tty and fail_on_no_tty:
        raise NoTTYException
    return result


def _get_missing_parameters(parameters, template, prompt_fn):
    missing = _find_missing_parameters(parameters, template)
    if missing:
        prompt_parameters = prompt_fn(missing)
        for param_name in prompt_parameters:
            parameters[param_name] = {
                "value": prompt_parameters[param_name]
            }
    return parameters


def _parse_network_ref(network_ref_name):
    # assume format of /subscriptions/subscriptionID/resourcegroups/resourcegroupname/providers/Microsoft.ServiceFabricMesh/networks/networkname
    resource_parts = network_ref_name.split('/')
    return resource_parts[-1]


def _display_successful_application(cfn, resource_group_name, resource):
    application_name = resource['name']
    services = resource['properties']['services']
    network_resource_information = None
    network_name = None

    if services:

        for service in services:
            if service['properties']['networkRefs']:
                for network_ref in service['properties']['networkRefs']:
                    network_name = _parse_network_ref(network_ref['name'])
                    if network_name:
                        break

        if network_name:
            try:
                network_resource_information = cfn.get(resource_group_name, network_name)
            except ErrorModelException:
                logger.warning("{application} network resource {network_name} can not be found."
                               .format(application=application_name, network_name=network_name))

    if network_resource_information and network_resource_information.ingress_config:
        public_ip_address = network_resource_information.ingress_config.public_ip_address
        logger.warning("application {application} has been deployed successfully on network {network} with public ip address {ip}"
                       .format(application=application_name, network=network_name, ip=public_ip_address))
    else:
        logger.warning("application {application} has been deployed successfully".format(application=application_name))


def _display_application_status(mesh_network_client, resource, resource_group_name, mesh_application_client):

    application_name = resource['name']
    try:
        application_operation_information = mesh_application_client.get(resource_group_name, application_name)
        application_status = application_operation_information.provisioning_state
        if application_status in ['Succeeded']:
            _display_successful_application(mesh_network_client, resource_group_name, resource)
        elif application_status in ['Failed']:
            status_details = application_operation_information.status_details
            if status_details:
                logger.warning("application {application} deployment failed with {status_details}"
                               .format(application=application_name, status_details=status_details))
            else:
                logger.warning("application {application} deployment failed".format(application=application_name))
        else:
            logger.warning("application {application} deployment not complete with status {status}"
                           .format(application=application_name, status=application_status))
    except ErrorModelException:
        logger.warning("There was an error when getting application resource {0}."
                       .format(application_name))


def _display_deployment_status(cli_ctx, operation_status, resource_group_name, deployment_name, template_obj):
    mesh_deployment_client = cf_mesh_deployments(cli_ctx, '')
    mesh_network_client = cf_mesh_network(cli_ctx, '')

    deployment_status = mesh_deployment_client.get(resource_group_name, deployment_name)

    if operation_status in ['Failed']:
        logger.warning("Deployment failed")
        logger.warning("deployment correlation ID: {deployment_correlation_id}"
                       .format(deployment_correlation_id=deployment_status.properties.correlation_id))

    application_count = 0
    only_application_name = None
    mesh_application_client = cf_mesh_application(cli_ctx, '')
    for resource in template_obj:
        if resource['type'] in ['Microsoft.ServiceFabricMesh/applications']:
            _display_application_status(mesh_network_client, resource, resource_group_name, mesh_application_client)
            only_application_name = resource['name']
            application_count += 1

    if application_count is 1:
        logger.warning(
            "To recieve additional information run the following to get the status of the application deployment.")
        logger.warning("az mesh app show --resource-group {resource_group_name} --name {application_name}"
                       .format(resource_group_name=resource_group_name, application_name=only_application_name))
    elif application_count > 1:
        logger.warning(
            "To recieve additional information run the following to get the status of the application's deployments")
        logger.warning("az mesh app list --resource-group {resource_group_name}"
                       .format(resource_group_name=resource_group_name))

    if 'error' in deployment_status.properties.additional_properties:
        logger.warning("Deployment Errors: ")
        for error in deployment_status.properties.additional_properties['error']['details']:
            # load error message into object to parse
            error_message = json.loads(error['message'])
            if 'innerError' in error_message['error']:
                del error_message['error']['innerError']
            logger.warning(json.dumps(error_message['error'], indent=4, sort_keys=True))

    if operation_status in ['Running']:
        logger.warning("The output should point to the potential issue. If the above cmd response does not have any errors listed, then it could just be that your image is taking long to download, rerun the above command again after 5 minutes.")


def _deploy_arm_template_core(cli_ctx, resource_group_name,  # pylint: disable=too-many-arguments
                              template_file=None, template_uri=None, deployment_name=None,
                              parameters=None, mode=None, validate_only=False,
                              no_wait=False):
    DeploymentProperties, TemplateLink = get_sdk(cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES,
                                                 'DeploymentProperties', 'TemplateLink', mod='models')
    template = None
    template_link = None
    template_obj = None
    if template_uri:
        template_link = TemplateLink(uri=template_uri)
        template_obj = shell_safe_json_parse(_urlretrieve(template_uri).decode('utf-8'), preserve_order=True)
    else:
        template = get_file_json(template_file, preserve_order=True)
        template_obj = template

    template_param_defs = template_obj.get('parameters', {})
    template_obj['resources'] = template_obj.get('resources', [])
    parameters = _process_parameters(template_param_defs, parameters) or {}
    parameters = _get_missing_parameters(parameters, template_obj, _prompt_for_parameters)

    template = json.loads(json.dumps(template))
    parameters = json.loads(json.dumps(parameters))

    properties = DeploymentProperties(template=template, template_link=template_link,
                                      parameters=parameters, mode=mode)
    # workaround
    properties.mode = 'incremental'
    smc = get_mgmt_service_client(cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES)

    if validate_only:
        return sdk_no_wait(no_wait, smc.deployments.validate, resource_group_name, deployment_name, properties)

    validation = smc.deployments.validate(resource_group_name, deployment_name, properties)

    if validation.error:
        logger.warning("deployment template validation failed:")
        logger.warning(validation.error)
    else:
        operation_status_poller = sdk_no_wait(no_wait, smc.deployments.create_or_update, resource_group_name,
                                              deployment_name, properties)
        if no_wait:
            return operation_status_poller

        wait_time = 0
        timestep = 5
        while operation_status_poller.status() in ['Running', 'InProgress'] and wait_time < 600:
            sleep(timestep)
            wait_time += timestep

        parsed_template = smc.deployments.validate(resource_group_name, deployment_name, properties).properties.additional_properties['validatedResources']

        return _display_deployment_status(cli_ctx, operation_status_poller.status(), resource_group_name,
                                          deployment_name, parsed_template)


def deploy_arm_template(cmd, resource_group_name,
                        template_file=None, template_uri=None, deployment_name=None,
                        parameters=None, mode=None, no_wait=False):
    logger.warning("Deploying . . .")
    return _deploy_arm_template_core(cmd.cli_ctx, resource_group_name, template_file, template_uri,
                                     deployment_name, parameters, mode, no_wait=no_wait)


def list_networks(client, resource_group_name=None):
    """List all networks in a resource group. """
    if resource_group_name is None:
        return client.list_by_subscription()
    return client.list_by_resource_group(resource_group_name)


def create_volume(client, resource_group_name,
                  name, location,
                  template_file=None, template_uri=None):
    """Create a volume. """
    volume_properties = None

    if template_uri:
        volume_properties = shell_safe_json_parse(_urlretrieve(template_uri).decode('utf-8'), preserve_order=True)
    elif template_file:
        volume_properties = get_file_json(template_file, preserve_order=True)
        volume_properties = json.loads(json.dumps(volume_properties))
    else:
        raise CLIError('One of --template-file or --template-uri has to be specified')

    volume_properties['location'] = location
    return client.create(resource_group_name, name, volume_properties)


def list_volumes(client, resource_group_name=None):
    """List all volumes in a resource group. """
    if resource_group_name is None:
        return client.list_by_subscription()
    return client.list_by_resource_group(resource_group_name)


def show_volume(client, resource_group_name, name):
    """Show details of a volume. """
    return client.get(resource_group_name, name)


def delete_volume(client, resource_group_name, name, **kwargs):
    """Delete a volume. """
    return client.delete(resource_group_name, name)
