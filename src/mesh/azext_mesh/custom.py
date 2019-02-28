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

from six.moves.urllib.request import urlopen  # pylint: disable=import-error
from knack.log import get_logger
from knack.prompting import prompt, prompt_pass, prompt_t_f, prompt_choice_list, prompt_int, NoTTYException
from knack.util import CLIError

from azure.cli.core.util import get_file_json, shell_safe_json_parse, sdk_no_wait
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import ResourceType, get_sdk
from sfmergeutility import SFMergeUtility  # pylint: disable=E0611,import-error


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


def _invoke_mergeutil(input_yaml_files=None, parameters=None):
    # call merge utility
    file_path_list = []
    prefix = "merged-"
    output_file_path = os.path.join(os.getcwd(), prefix + 'arm_rp.json')
    if os.path.isdir(input_yaml_files):
        for root, _, files in os.walk(input_yaml_files):
            for filename in files:
                if filename.endswith(".yaml"):
                    file_path_list.append(os.path.join(root, filename))
    else:
        file_path_list = input_yaml_files.split(',')
    if os.path.exists(output_file_path):
        os.remove(output_file_path)
    SFMergeUtility.sf_merge_utility(file_path_list, "SF_SBZ_RP_JSON", parameters=parameters, output_dir=None, prefix=prefix)
    return output_file_path


def _generate_arm_template_core(input_yaml_files=None, parameters=None):
    output_file_path = _invoke_mergeutil(input_yaml_files, parameters)
    logger.warning("Generated ARM template file at {0}.".format(output_file_path))


def _deploy_arm_template_core(cli_ctx, resource_group_name,  # pylint: disable=too-many-arguments
                              template_file=None, template_uri=None, input_yaml_files=None, deployment_name=None,
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
    elif template_file:
        template = get_file_json(template_file, preserve_order=True)
        template_obj = template
    else:
        output_file_path = _invoke_mergeutil(input_yaml_files, parameters)
        parameters = None
        template = get_file_json(output_file_path, preserve_order=True)
        template_obj = template

    template_param_defs = template_obj.get('parameters', {})
    template_obj['resources'] = template_obj.get('resources', [])

    template = json.loads(json.dumps(template))

    if parameters is not None:
        parameters = _process_parameters(template_param_defs, parameters) or {}
        parameters = _get_missing_parameters(parameters, template_obj, _prompt_for_parameters)
        parameters = json.loads(json.dumps(parameters))

    properties = DeploymentProperties(template=template, template_link=template_link,
                                      parameters=parameters, mode=mode)
    # workaround
    properties.mode = 'incremental'
    smc = get_mgmt_service_client(cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES)

    logger.warning("Deploying . . .")
    logger.warning("You can get the state of the deployment with the cmd")
    logger.warning("az group deployment show --name {0} --resource-group {1}".format(deployment_name, resource_group_name))
    if validate_only:
        return sdk_no_wait(no_wait, smc.deployments.validate, resource_group_name, deployment_name, properties)

    return sdk_no_wait(no_wait, smc.deployments.create_or_update, resource_group_name, deployment_name, properties)


def deploy_arm_template(cmd, resource_group_name,
                        template_file=None, template_uri=None, input_yaml_files=None, deployment_name=None,
                        parameters=None, mode=None, no_wait=False):
    return _deploy_arm_template_core(cmd.cli_ctx, resource_group_name, template_file, template_uri,
                                     input_yaml_files, deployment_name, parameters, mode, no_wait=no_wait)


def generate_arm_template(cmd, input_yaml_files=None, parameters=None):
    return _generate_arm_template_core(input_yaml_files, parameters)


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


def list_secrets(client, resource_group_name=None):
    """List all networks in a resource group. """
    if resource_group_name is None:
        return client.list_by_subscription()
    return client.list_by_resource_group(resource_group_name)


def secret_show(client, resource_group_name, secret_name, secret_value_resource_name, show_value=False):
    secret_data = client.get(resource_group_name, secret_name, secret_value_resource_name)
    if show_value:
        secret_value = client.list_value(resource_group_name, secret_name, secret_value_resource_name)
        secret_data.value = secret_value.value
    return secret_data


def list_secret_values(client, resource_group_name, secret_name):
    secret_data = client.list(resource_group_name, secret_name)
    return secret_data
