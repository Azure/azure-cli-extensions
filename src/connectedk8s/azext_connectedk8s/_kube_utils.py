# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import errno
import os
import platform
import stat
import tempfile
import re
from base64 import b64encode, b64decode

import yaml

from knack.log import get_logger
from knack.prompting import prompt_y_n
from knack.prompting import NoTTYException
from azure.cli.core import telemetry
from azure.cli.core.azclierror import CLIInternalError, FileOperationError
import azext_connectedk8s._constants as consts
import azext_connectedk8s._kube_core_utils as kube_core_utils


logger = get_logger(__name__)


def load_kubernetes_configuration(filename):
    try:
        with open(filename) as stream:
            return yaml.safe_load(stream)
    except (IOError, OSError) as ex:
        if getattr(ex, 'errno', 0) == errno.ENOENT:
            telemetry.set_exception(exception=ex, fault_type=consts.Kubeconfig_Failed_To_Load_Fault_Type,
                                    summary='{} does not exist'.format(filename))
            raise FileOperationError('{} does not exist'.format(filename))
    except (yaml.parser.ParserError, UnicodeDecodeError) as ex:
        telemetry.set_exception(exception=ex, fault_type=consts.Kubeconfig_Failed_To_Load_Fault_Type,
                                summary='Error parsing {} ({})'.format(filename, str(ex)))
        raise FileOperationError('Error parsing {} ({})'.format(filename, str(ex)))
    return None


def print_or_merge_credentials(path, kubeconfig, overwrite_existing, context_name):
    """Merge an unencrypted kubeconfig into the file at the specified path, or print it to
    stdout if the path is "-".
    """
    # Special case for printing to stdout
    if path == "-":
        print(kubeconfig)
        return

    # ensure that at least an empty ~/.kube/config exists
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError as ex:
            if ex.errno != errno.EEXIST:
                telemetry.set_exception(exception=ex,
                                        fault_type=consts.Failed_To_Merge_Credentials_Fault_Type,
                                        summary='Could not create a kubeconfig directory.')
                raise FileOperationError("Could not create a kubeconfig directory." + str(ex))
    if not os.path.exists(path):
        with os.fdopen(os.open(path, os.O_CREAT | os.O_WRONLY, 0o600), 'wt'):
            pass

    # merge the new kubeconfig into the existing one
    fd, temp_path = tempfile.mkstemp()
    additional_file = os.fdopen(fd, 'w+t')
    try:
        additional_file.write(kubeconfig)
        additional_file.flush()
        merge_kubernetes_configurations(path, temp_path, overwrite_existing, context_name)
    except yaml.YAMLError as ex:
        logger.warning('Failed to merge credentials to kube config file: %s', ex)
    finally:
        additional_file.close()
        os.remove(temp_path)


def merge_kubernetes_configurations(existing_file, addition_file, replace, context_name=None):
    try:
        existing = load_kubernetes_configuration(existing_file)
        addition = load_kubernetes_configuration(addition_file)
    except Exception as ex:
        telemetry.set_exception(exception=ex,
                                fault_type=consts.Failed_To_Load_K8s_Configuration_Fault_Type,
                                summary='Exception while loading kubernetes configuration')
        raise CLIInternalError('Exception while loading kubernetes configuration.' + str(ex))

    if context_name is not None:
        addition['contexts'][0]['name'] = context_name
        addition['contexts'][0]['context']['cluster'] = context_name
        addition['clusters'][0]['name'] = context_name
        addition['current-context'] = context_name

    # rename the admin context so it doesn't overwrite the user context
    for ctx in addition.get('contexts', []):
        try:
            if ctx['context']['user'].startswith('clusterAdmin'):
                admin_name = ctx['name'] + '-admin'
                addition['current-context'] = ctx['name'] = admin_name
                break
        except (KeyError, TypeError):
            continue

    if addition is None:
        telemetry.set_exception(exception='Failed to load additional configuration',
                                fault_type=consts.Failed_To_Load_K8s_Configuration_Fault_Type,
                                summary='failed to load additional configuration from {}'.format(addition_file))
        raise CLIInternalError('failed to load additional configuration from {}'.format(addition_file))

    if existing is None:
        existing = addition
    else:
        handle_merge(existing, addition, 'clusters', replace)
        handle_merge(existing, addition, 'users', replace)
        handle_merge(existing, addition, 'contexts', replace)
        existing['current-context'] = addition['current-context']

    # check that ~/.kube/config is only read- and writable by its owner
    if platform.system() != 'Windows':
        existing_file_perms = "{:o}".format(stat.S_IMODE(os.lstat(existing_file).st_mode))
        if not existing_file_perms.endswith('600'):
            logger.warning('%s has permissions "%s".\nIt should be readable and writable only by its owner.',
                           existing_file, existing_file_perms)

    with open(existing_file, 'w+') as stream:
        try:
            yaml.safe_dump(existing, stream, default_flow_style=False)
        except Exception as e:
            telemetry.set_exception(exception=e, fault_type=consts.Failed_To_Merge_Kubeconfig_File,
                                    summary='Exception while merging the kubeconfig file')
            raise CLIInternalError('Exception while merging the kubeconfig file.' + str(e))

    current_context = addition.get('current-context', 'UNKNOWN')
    msg = 'Merged "{}" as current context in {}'.format(current_context, existing_file)
    print(msg)


def handle_merge(existing, addition, key, replace):
    if not addition[key]:
        return
    if existing[key] is None:
        existing[key] = addition[key]
        return

    i = addition[key][0]
    temp_list = []
    for j in existing[key]:
        remove_flag = False
        if not i.get('name', False) or not j.get('name', False):
            continue
        if i['name'] == j['name']:
            if replace or i == j:
                remove_flag = True
            else:
                msg = 'A different object named {} already exists in your kubeconfig file.\nOverwrite?'
                overwrite = False
                try:
                    overwrite = prompt_y_n(msg.format(i['name']))
                except NoTTYException:
                    pass
                if overwrite:
                    remove_flag = True
                else:
                    msg = 'A different object named {} already exists in {} in your kubeconfig file.'
                    telemetry.set_exception(exception='A different object with same name exists in' +
                                            ' the kubeconfig file',
                                            fault_type=consts.Different_Object_With_Same_Name_Fault_Type,
                                            summary=msg.format(i['name'], key))
                    raise FileOperationError(msg.format(i['name'], key))
        if not remove_flag:
            temp_list.append(j)

    existing[key][:] = temp_list
    existing[key].append(i)


def set_kube_config(kube_config):
    if kube_config:
        # Trim kubeconfig. This is required for windows os.
        if (kube_config.startswith("'") or kube_config.startswith('"')):
            kube_config = kube_config[1:]
        if (kube_config.endswith("'") or kube_config.endswith('"')):
            kube_config = kube_config[:-1]
        return kube_config
    return None


def get_kubeconfig_node_dict(config, kube_config=None):
    if kube_config is None:
        kube_config = (os.getenv('KUBECONFIG') if os.getenv('KUBECONFIG')
                       else os.path.join(os.path.expanduser('~'), '.kube', 'config'))
    try:
        kubeconfig_data = config.kube_config._get_kube_config_loader_for_yaml_file(kube_config)._config
    except Exception as ex:
        telemetry.set_exception(exception=ex, fault_type=consts.Load_Kubeconfig_Fault_Type,
                                summary='Error while fetching details from kubeconfig')
        raise FileOperationError("Error while fetching details from kubeconfig." + str(ex))
    return kubeconfig_data


def get_server_address(config, kube_config, kube_context):
    config_data = get_kubeconfig_node_dict(config, kube_config=kube_config)
    try:
        all_contexts, current_context = config.list_kube_config_contexts(config_file=kube_config)
    except Exception as e:  # pylint: disable=broad-except
        logger.warning("Exception while trying to list kube contexts: %s\n", e)

    if kube_context is None:
        # Get name of the cluster from current context as kube_context is none.
        cluster_name = current_context.get('context').get('cluster')
        if cluster_name is None:
            logger.warning("Cluster not found in currentcontext: " + str(current_context))
    else:
        cluster_found = False
        for context in all_contexts:
            if context.get('name') == kube_context:
                cluster_found = True
                cluster_name = context.get('context').get('cluster')
                break
        if not cluster_found or cluster_name is None:
            logger.warning("Cluster not found in kubecontext: " + str(kube_context))

    clusters = config_data.safe_get('clusters')
    server_address = ""
    for cluster in clusters:
        if cluster.safe_get('name') == cluster_name:
            server_address = cluster.safe_get('cluster').get('server')
            break
    return server_address


def check_proxy_kubeconfig(config, kube_config, kube_context, arm_hash):
    server_address = get_server_address(config, kube_config, kube_context)
    regex_string = r'https://127.0.0.1:[0-9]{1,5}/' + arm_hash
    p = re.compile(regex_string)
    if p.fullmatch(server_address) is not None:
        return True
    else:
        return False


def check_aks_cluster(config, kube_config, kube_context):
    server_address = get_server_address(config, kube_config, kube_context)
    if server_address.find(".azmk8s.io:") == -1:
        return False
    else:
        return True


def load_kube_config(config, kube_config, kube_context):
    try:
        config.load_kube_config(config_file=kube_config, context=kube_context)
    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=consts.Load_Kubeconfig_Fault_Type,
                                summary='Problem loading the kubeconfig file')
        raise FileOperationError("Problem loading the kubeconfig file." + str(e))


def insert_token_in_kubeconfig(data, token):
    b64kubeconfig = data['kubeconfigs'][0]['value']
    decoded_kubeconfig_str = b64decode(b64kubeconfig).decode("utf-8")
    dict_yaml = yaml.safe_load(decoded_kubeconfig_str)
    dict_yaml['users'][0]['user']['token'] = token
    kubeconfig = yaml.dump(dict_yaml).encode("utf-8")
    b64kubeconfig = b64encode(kubeconfig).decode("utf-8")
    return b64kubeconfig


def add_kubernetes_telemetry_extension_event(connected_cluster, configuration, api_instance):
    # Get kubernetes cluster info for telemetry
    node_api_response = None
    kubernetes_version = kube_core_utils.get_server_version(configuration)
    if hasattr(connected_cluster, 'distribution') and (connected_cluster.distribution is not None):
        kubernetes_distro = connected_cluster.distribution
    else:
        node_api_response = validate_node_api_response(api_instance, node_api_response)
        kubernetes_distro = kube_core_utils.get_kubernetes_distro(node_api_response)

    if hasattr(connected_cluster, 'infrastructure') and (connected_cluster.infrastructure is not None):
        kubernetes_infra = connected_cluster.infrastructure
    else:
        node_api_response = validate_node_api_response(api_instance, node_api_response)
        kubernetes_infra = kube_core_utils.get_kubernetes_infra(node_api_response)

    add_kubernetes_telemetry_extension_event_raw(kubernetes_version, kubernetes_distro, kubernetes_infra)


def add_kubernetes_telemetry_extension_event_raw(kubernetes_version, kubernetes_distro, kubernetes_infra):
    kubernetes_properties = {
        'Context.Default.AzureCLI.KubernetesVersion': kubernetes_version,
        'Context.Default.AzureCLI.KubernetesDistro': kubernetes_distro,
        'Context.Default.AzureCLI.KubernetesInfra': kubernetes_infra
    }
    telemetry.add_extension_event('connectedk8s', kubernetes_properties)


def validate_node_api_response(api_instance, node_api_response):
    if node_api_response is None:
        try:
            node_api_response = api_instance.list_node()
            return node_api_response
        except Exception as ex:
            logger.debug("Error occcured while listing nodes on this kubernetes cluster: {}".format(str(ex)))
            return None
    else:
        return node_api_response
