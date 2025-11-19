# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from OpenSSL import crypto
from typing import List, Tuple
from azext_arcdata.core.prompt import prompt, prompt_pass, prompt_for_input
from azext_arcdata.core.constants import (
    IO_DELIM,
    KEY_VALUE_SPLIT,
    AZDATA_USERNAME,
    AZDATA_PASSWORD,
    LOGSUI_USERNAME,
    LOGSUI_PASSWORD,
    METRICSUI_USERNAME,
    METRICSUI_PASSWORD,
    PASSWORD_MIN_LENGTH,
    PASSWORD_REQUIRED_GROUPS,
)
from knack.log import get_logger
from knack.cli import CLIError

from kubernetes import config as kconfig
from jsonpatch import JsonPatch
from jsonpath_ng.ext import parse
from humanfriendly.terminal.spinners import AutomaticSpinner
from jinja2 import Template as JinjaTemplate
from string import Template
from functools import wraps

import os
import time
import platform
import json
import re
import sys
import signal
import pydash as _
import yaml
import pem

logger = get_logger(__name__)


def BOOLEAN_STATES(x):
    """
    Mapping of different common logical prepositions to boolean equivalent.
    """
    return {
        "1": True,
        "yes": True,
        "true": True,
        "on": True,
        "0": False,
        "no": False,
        "false": False,
        "off": False,
        None: False,
        "none": False,
    }.get(str(x).lower() if x else x, False)


def is_windows():
    """
    A common convenience function for windows environment check.
    :return: `True` if windows otherwise `False`.
    """
    return os.name == "nt"


def merge(dict_1, dict_2):
    """
    Merge two dict's together.
    :return: The merged dict
    """

    result = dict_1.copy()
    result.update(dict_2)
    return result


def traceback():
    """
    Get the exection stacktrace.
    :return: The exception stacktrace.
    """
    import traceback
    import sys

    ex_t, ex_v, ex_tb = sys.exc_info()
    return traceback.format_exception(ex_t, ex_v, ex_tb)


def color_wrapper(color):
    import colorama

    def to_colored_msg(msg):
        return color + msg + colorama.Style.RESET_ALL

    return to_colored_msg


def time_ns():
    """
    Returns time as an integer number of nanoseconds since the epoch.
    """
    from datetime import datetime as dt

    return int(dt.now().timestamp() * 1e9)


def minutes_elapsed(num_intervals, retry_interval):
    """
    Retrieve the number of minutes that have elapsed based on the number of
    intervals.
    """
    return num_intervals * retry_interval / 60


def display(msg):
    """
    Displays message to `stdout` and send the message to `logger.info()` for
    debugging.
    """
    logger.info(msg)


# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
def get_controller_env_list() -> List[str]:
    """
    Get the list of environment variables required for the controller
    """

    return [AZDATA_USERNAME, AZDATA_PASSWORD]


def get_environment_list_by_target(target):
    """
    Gets the required environment variable list for the given target
    """
    active_directory_env_list = [
        "DOMAIN_SERVICE_ACCOUNT_USERNAME",
        "DOMAIN_SERVICE_ACCOUNT_PASSWORD",
    ]

    controller_env_list = get_controller_env_list()
    env_list = []

    if target == "arc":
        env_list = controller_env_list
    if target == "clean":
        env_list = controller_env_list
    elif target == "config":
        env_list = controller_env_list
    elif target == "controller":
        env_list = controller_env_list
    elif target == "cluster":
        env_list = controller_env_list
    elif target == "activeDirectory":
        env_list = active_directory_env_list
    elif target == "delete":
        env_list = controller_env_list
    elif target == "password":
        env_list = controller_env_list

    return env_list


def read_environment_variables(target, arc=False):
    """
    Reads environment variables for the given target
    :param target: target to read environment variables
    :param arc: boolean determining whether it is an arc deployment
    """

    def display_env_name(env):
        """
        Provides a user friendly display name for environment variables
        """
        return env.strip().replace("_", " ").capitalize()

    if (
        os.environ.get(LOGSUI_USERNAME)
        and os.environ.get(LOGSUI_PASSWORD)
        and os.environ.get(METRICSUI_USERNAME)
        and os.environ.get(METRICSUI_PASSWORD)
    ):
        return

    for env in get_controller_env_list():
        msg = "{}:".format(display_env_name(env))
        if not os.environ.get(env):
            if "PASSWORD" in env:
                if arc and env == AZDATA_PASSWORD:
                    msg = "Monitoring administrator password:"
                result = prompt_pass(msg, True)
            if arc and env == AZDATA_USERNAME:
                msg = "Monitoring administrator username:"
            result = prompt(msg)
            os.environ[env] = result.strip()


def is_set(env_var: str) -> bool:
    """
    Checks if the given environment variable is set and not empty/whitespace
    """
    var = os.getenv(env_var)
    return var is not None and len(var.strip()) != 0


def check_environment_variables(target):
    """
    Check if all necessary environment variables are set.
    """
    env_list = get_controller_env_list()
    missing_env = list()
    for env in env_list:
        if not is_set(env):
            missing_env.append(env)

    if len(missing_env) > 0:
        logger.error(
            "Please set the following environment variable(s): %s."
            % missing_env
        )
        sys.exit(1)


def env_vars_are_set(vars: List[str]) -> bool:
    """
    Checks if the given list of environment variables are set or not.
    :returns: True if all of the variables are set, false otherwise.
    """
    for var in vars:
        if not is_set(var):
            return False

    return True


def read_config(config_profile, config_filename):
    """
    Read selected profile into object
    """

    def substitute_env_variables(template_file):
        """
        Substitute env variables in a file and return the string.
        """
        with open(template_file, "r") as f:
            template = f.read()
            s = Template(template)
            config = s.substitute(os.environ)
            return config

    try:
        config = os.path.join(config_profile, config_filename)
        config_string = substitute_env_variables(config)
        return json.loads(config_string)
    except Exception as e:
        raise ValueError("Failed to read config profile {0}".format(e))


def check_missing(stdout, force, config_object, help_object, config_filename):
    """
    Check for missing values and prompt user for them or raise an error in no
    tty environments.
    """

    def parse_for_missing(cfg_object):
        """
        Parses the config json object for missing/falsey values
        Returns a list of json paths for the missing values
        """
        try:
            missing = []

            def iterate(dictionary, root):
                for key, value in dictionary.items():
                    new_root = root + "." + key if root else key
                    if isinstance(value, dict):
                        iterate(value, new_root)
                        continue
                    elif isinstance(value, list):
                        for index, item in enumerate(value):
                            arr_root = new_root + "[" + str(index) + "]"
                            if isinstance(item, dict):
                                iterate(item, arr_root)
                            elif item == "":
                                missing.append(arr_root)
                        continue
                    if value == "":
                        missing.append(new_root)

            iterate(cfg_object, "")
            return missing
        except Exception as e:
            raise ValueError(
                "Failed to parse for missing values in config file: {}".format(
                    e
                )
            )

    missing_values = parse_for_missing(config_object)
    if len(missing_values) > 0:
        if not force:
            stdout(
                "\nNeeded Configuration Values in {0}".format(config_filename)
            )
            try:
                for key in missing_values:
                    expr = parse(key)
                    find_result = [
                        match.value for match in expr.find(help_object)
                    ]
                    help_result = (
                        find_result[0] if len(find_result) > 0 else None
                    )
                    name = help_result["name"] if help_result else key
                    description = (
                        help_result["description"]
                        if help_result
                        else "Please consult documentation: "
                        "https://aka.ms/bdc-deploy"
                    )
                    stdout(
                        "\n{name}\n- Config Path: {key}\n- Description: {description}".format(
                            name=name, key=key, description=description
                        )
                    )
                    result = prompt_for_input(
                        "- Please provide a value: ",
                        "",
                        padding=False,
                        strip=True,
                    )
                    expr.update(config_object, result)
            except Exception:
                raise ValueError(
                    "Failed to set needed configuration values, "
                    "please initialize your chosen config profile "
                    "with 'az arc config init' and edit manually. "
                    "Missing Configuration Values: {0}".format(missing_values)
                )
        else:
            raise ValueError(
                "Missing Configuration Values: {0}".format(missing_values)
            )


def control_config_check(config_object):
    """
    Checks if config is valid.
    """

    def is_active_directory_security_enabled(cfg_object):
        """
        Returns if the active directory security is enabled by the config
        object.

        Here is the layout of active directory configuration:
        1. security.activeDirectory subobject has configured members
        2. security has the obsolete members, which is used before CU1 release.
        This is supporting the backward compatibility of the flat layout of
        active directory configuration.
        """

        if "security" not in cfg_object or not cfg_object["security"]:
            return False

        if "activeDirectory" in cfg_object["security"]:
            return True

        # For backward compatibility, if any obsolete active directory members
        # found, then we consider customer want the ad security with the
        # obsolete flat layout configuration.
        #
        obsolete_active_directory_members = [
            "useInternalDomain",
            "ouDistinguishedName",
            "dnsIpAddresses",
            "domainControllerFullyQualifiedDns",
            "realm",
            "domainDnsName",
            "clusterAdmins",
            "clusterUsers",
            "appOwners",
            "appReaders",
            "kerberosDelegationMode",
        ]

        for (
            obsolete_active_directory_member
        ) in obsolete_active_directory_members:
            if obsolete_active_directory_member in cfg_object["security"]:
                return True

        return False

    if "endpoints" in config_object["spec"]:
        ad_enabled = is_active_directory_security_enabled(
            config_object
        ) | is_active_directory_security_enabled(config_object["spec"])

        if ad_enabled:
            endpoints_no_dns = list(
                filter(
                    lambda x: "dnsName" not in x,
                    config_object["spec"]["endpoints"],
                )
            )

            if endpoints_no_dns:
                error_endpoints = map(lambda x: x["name"], endpoints_no_dns)
                raise ValueError(
                    "dnsName required for endpoint(s): {0}".format(
                        ", ".join(error_endpoints)
                    )
                )

        for endpoint in config_object["spec"]["endpoints"]:
            if "dnsName" in endpoint:
                if not re.match(
                    r"^[a-z]([-a-z0-9]*[a-z0-9])?(\.[a-z]([-a-z0-9]*[a-z0-9])?)+$",
                    endpoint["dnsName"],
                ):
                    raise ValueError(
                        "dnsName {0} for endpoint {1} is not a valid "
                        "RFC-1035 DNS domain.".format(
                            endpoint["dnsName"], endpoint["name"]
                        )
                    )


def parse_labels(label_str):
    labels = dict()
    labels_split = label_str.split(",")

    for label_raw in labels_split:
        label_kv = label_raw.split(":")

        if len(label_kv) != 2:
            raise ValueError(
                "Labels must be of form 'key1: value1, " "key2: value2,...'"
            )

        label_key, label_value = label_kv

        if label_key in labels.keys():
            raise ValueError("Duplicate label key {}".format(label_key))

        labels[label_key.strip()] = label_value.strip()

    return labels


# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #


def check_and_set_kubectl_context():
    """
    Check and set environment var for kubectl command context
    """
    try:
        if os.getenv("KUBERNETES_SERVICE_HOST"):
            kconfig.load_incluster_config()
        elif os.getenv("KUBECTL_CONTEXT") is None:
            load_kube_config()
        else:
            load_kube_config(os.environ["KUBECTL_CONTEXT"])
    except Exception as e:
        logger.debug(e)
        logger.error("Failed to complete kube config setup.")
        raise Exception("Failed to complete kube config setup.")


def load_kube_config(context=None):
    """
    Loads the kube config.
    :param context:
    :return:
    """

    # This is a temporary workaround until this change gets checked in.
    # Python Kubernetes Library does not handle cases where the KUBECONFIG
    # environment variable can have multiple kubeconfig files listed. It's an
    # open issue on github:
    # https://github.com/kubernetes-client/python-base/pull/94
    FILE_SEPARATOR = ";" if platform.system() == "Windows" else ":"
    kube_config_files = os.environ.get("KUBECONFIG")
    kube_context_loaded = False
    config_file = None

    if kube_config_files:
        config_file = None
        for config_file in kube_config_files.split(FILE_SEPARATOR):
            if config_file:
                # kubectl gives precedence to the order in which the files are
                # listed.
                try:
                    kconfig.load_kube_config(
                        config_file=config_file, context=context
                    )
                    kube_context_loaded = True
                    break
                except Exception:
                    raise (
                        "Could not find context %s in file - %s"
                        % (context, config_file)
                    )
        if not kube_context_loaded:
            raise (
                "Failed to load context %s from the listed kubeconfig files:"
                " %s." % (context, kube_config_files.split(FILE_SEPARATOR))
            )
    else:
        kconfig.load_kube_config(context=context)

    # set kubectl context to current context if not set
    #
    if context is None:
        contexts, current_context = kconfig.list_kube_config_contexts(
            config_file=config_file
        )
        if current_context:
            os.environ["KUBECTL_CONTEXT"] = current_context["name"]
        else:
            raise Exception("No active context is set in kubeconfig.")


# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #


class FileUtil(object):
    @staticmethod
    def read_json(file_path):
        """
        Deserialize file containing a JSON document into a Python dict.
        :param file_path: The path to the JSON document.
        :return: A `dict` of JSON otherwise `None` if file not found.
        """
        from codecs import open
        import json

        content = None
        # for encoding in ['utf-8-sig', 'utf-8', 'utf-16', 'utf-16le',
        # 'utf-16be']:
        for encoding in ["utf-8"]:
            try:
                with open(file_path, encoding=encoding) as f:
                    content = f.read()
            except (UnicodeError, UnicodeDecodeError):
                pass

        if not content:
            return None
        else:
            return json.loads(content)

    @staticmethod
    def read_text_file(file_path):
        """Helper to load text from a given file."""

        with open(FileUtil.strip_path(file_path), "r") as file:
            data = file.read()

        return data

    @staticmethod
    def is_lnk_path(file_path):
        """
        Helper to identify if file path contains the special lnk `@` prefix.
        """
        return file_path.strip().startswith("@")

    @staticmethod
    def strip_path(file_path):
        """
        Helper to tidy up a file path and strip of any special lnk `@` prefix.
        """
        return file_path.strip().lstrip("@")


# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #


def log_error(error_message, error_detail):
    """
    Log error messages
    :param error_message : Error thrown
    :param error_detail : Error info
    """

    logger.error(error_message + " : " + error_detail)


def retry_method(
    retry_count: int,
    retry_delay: int,
    retry_method_description: str,
    retry_on_exceptions: tuple,
):
    def retry_method_wrapper(f):
        """
        Decorator wraps the method with retry logic.  See retry
        """

        @wraps(f)
        def wrapper(*args, **kwargs):
            return retry(
                lambda: f(*args, **kwargs),
                retry_count=retry_count,
                retry_delay=retry_delay,
                retry_method=retry_method_description,
                retry_on_exceptions=retry_on_exceptions,
            )

        return wrapper

    return retry_method_wrapper


def retry(func, *func_args, **kwargs):
    """
    Function retry until max limit
    :param func : Function to retry
    :param func_args : Arguments to func
    :param int retry_count : Retry attempts
    :param int retry_delay : Retry delay
    :param string retry_method : func literal
    :param tuple retry_on_exceptions : Exceptions to ignore while retrying func
    """
    # Retry parameters for connection errors
    connection_retry_interval_seconds = 5
    connection_retry_attempts = 12

    retry_count = kwargs.get("retry_count", connection_retry_attempts)
    retry_delay = kwargs.get("retry_delay", connection_retry_interval_seconds)
    retry_method = kwargs.get("retry_method", None)
    retry_on_exceptions = kwargs.get("retry_on_exceptions", None)
    exception_caused = None
    for i in range(retry_count):
        try:
            return_value = func(*func_args)
            return return_value if return_value is not None else True
        except retry_on_exceptions as e:
            exception_caused = e
            logger.debug(
                "Waiting for %d seconds before trying to %s again"
                % (retry_delay, retry_method)
            )
            time.sleep(retry_delay)
            continue
    logger.debug(exception_caused)
    log_error(
        str(
            _.get(exception_caused, ["reason", "__context__"], exception_caused)
        ),
        "Failed to %s after retrying for %d minute(s)."
        % (retry_method, (retry_count * retry_delay) / 60),
    )
    raise Exception(
        "Failed to %s after retrying for %d minute(s)."
        % (retry_method, (retry_count * retry_delay) / 60)
    )


class TimeoutError(Exception):
    pass


def handle_timeout(signum, frame):
    """throws timeout error"""
    raise TimeoutError("Timeout occurred")


def with_timeout(timeout, function_to_run, *args, **kwargs):
    """Runs a function with timeout
    Args:
        timeout: the number of seconds to wait before fail the function with
        timeout error
        function_to_run: the function to run with given timeout
    """
    signal_handler = signal.signal(signal.SIGALRM, handle_timeout)
    signal.alarm(timeout)
    try:
        function_to_run(*args, **kwargs)
    finally:
        signal.signal(signal.SIGALRM, signal_handler)
        signal.alarm(0)


# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #


def singleton(cls, *args, **kw):
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return _singleton


def name_meets_dns_requirements(n: str):
    """
    Checks whether a given string constrains to dns requirements
    :n: string to validate
    :return: false if n does not match dns requirements, true otherwise
    """
    if not n:
        return False

    if not n[0].isalpha() or not n[-1].isalnum():
        return False

    if not n.islower():
        return False

    for c in n:
        if not c.isalnum() and not c == "-":
            return False

    return True


def is_valid_password(pw, user):
    """
    Checks if the provided pw is a sufficiently complex password i.e. is at least
    eight characters long and contains a char from at least three of these
    groups
    -Uppercase letters
    -Lowercase letters
    -Base 10 digits
    -Non-alphanumeric characters
    :param pw: the password
    :param user: username for the sql instance
    :return: True if pw meets requirements, False otherwise
    """
    if not pw:
        return False

    if user in pw:
        return False

    if len(pw) < PASSWORD_MIN_LENGTH:
        return False

    lower = 0
    upper = 0
    special = 0
    digit = 0

    for c in pw:
        if c.isdigit():
            digit = 1
        elif c.isalpha():
            if c.isupper():
                upper = 1
            else:
                lower = 1
        else:
            # Assume any other characters qualify as 'special' characters.
            # Work item to implement stricter policies: #1282103
            #
            special = 1

    return (lower + upper + special + digit) >= PASSWORD_REQUIRED_GROUPS


def validate_creds_from_env(username_var: str, password_var: str):
    """
    Ensures that both or neither of the username and password
    environment variables are set and that passwords meet complexity
    requirements
    """
    username = os.environ.get(username_var)
    password = os.environ.get(password_var)
    if bool(username) ^ bool(password):
        raise CLIError(
            "Must specify both {0} and {1} or neither.".format(
                username_var, password_var
            )
        )
    elif username and password and not is_valid_password(password, username):
        raise CLIError(
            "Invalid password from " + password_var + ". Passwords must be at "
            "least 8 characters long, cannot contain the "
            "username, and must contain characters from "
            "three of the following four sets: Uppercase "
            "letters, Lowercase letters, Base 10 digits, "
            "and Symbols. Please try again.\n"
        )


class ClearField:
    """
    A class that represents a field that should be cleared.
    """

    def __bool__(self):
        return False

    def __eq__(self, other):
        return isinstance(other, ClearField)


def prune_dict(d):
    """
    "Prunes" a dictionary by recursively removing all keys that do not result in
    a Non-Null attribute i.e. if you modeled the dictionary (nested) as a tree
    with the values as leaves, any branch with an "empty" attribute at the leaf
    would be removed. "Empty" meaning an empty dict, empty list, or None value.
    :param d: dict to prune:
    :returns d: d, but pruned
    """
    if d is None:
        return None

    if type(d) is dict:
        keys = list(d.keys())
        empty = True
        for k in keys:
            d[k] = prune_dict(d[k])
            if d[k] is None:
                del d[k]
            elif isinstance(d[k], ClearField):
                d[k] = None
            else:
                empty = False
        return None if empty else d
    elif type(d) is list:
        if len(d) == 0:
            return None
        else:
            for obj in d:
                prune_dict(obj)

    return d


def trim_dict_entries(d: dict):
    """
    Trims any values in d that are of type str
    :param d: The dict whose values to trim
    :returns: d
    """
    if type(d) is dict:
        for k in d.keys():
            if type(d[k]) is str:
                d[k] = d[k].strip()
            else:
                trim_dict_entries(d[k])

    return d


# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #


class DeploymentConfigUtil(object):
    """
    Utility methods for handling deployment configuration files.
    """

    @staticmethod
    def get_config_map(config_dir):
        """
        Gets the available config profiles and returns them as a dictionary
        where the key/value are the config profile name
        :param config_dir:
        :return dictionary of config profiles with directory name being the key:
        """
        files = {}
        for f in os.listdir(config_dir):
            if f != "help":
                files[f] = f
        return files

    @staticmethod
    def get_config_display_names(config_profile_dict):
        """
        Returns a display friendly list of config profile names
        :param config_profile_dict:
        :return:
        """
        display_list = list(config_profile_dict.keys())
        display_list.sort()
        return display_list

    @staticmethod
    def config_list(config_dir, config_profile=None, config_type="control"):
        """
        Lists available configuration file choices.
        :param config_dir:
        :param config_profile:
        :param config_type:
        :return:
        """
        try:
            configs = DeploymentConfigUtil.get_config_map(config_dir)
            if not config_profile:
                config_names = DeploymentConfigUtil.get_config_display_names(
                    configs
                )
                return config_names
            elif config_profile in configs.keys():
                config_profile = os.path.join(
                    config_dir, configs[config_profile]
                )
                config_file = os.path.join(
                    config_profile, config_type + ".json"
                )

                if os.path.isfile(config_file):
                    file = open(config_file, "r")
                    text = file.read()
                    return json.loads(text)
                else:
                    raise ValueError(
                        "Invalid config type: `{0}`".format(config_type)
                    )
            else:
                raise ValueError(
                    "Invalid default config profile, please consult [bdc "
                    "config list] for available types"
                )
        except ValueError as e:
            raise CLIError(e)
        except Exception as e:
            raise CLIError(e)

    @staticmethod
    def save_config_profile(
        path, source, config_dir, config_files, config_map, force
    ):
        """
        Saves the config profile from the source to the given target.
        :param path:
        :param source:
        :param config_dir:
        :param config_files:
        :param config_map:
        :param force:
        :return:
        """
        if not os.path.isdir(path):
            os.makedirs(path)

        result_path = os.path.join(config_dir, config_map[source.lower()])

        for config_filename in config_files:
            target_cluster_config_file = os.path.join(path, config_filename)
            if not force and os.path.isfile(target_cluster_config_file):
                raise FileExistsError(
                    "Please specify a directory that is empty "
                    "or use the force flag: config init -p {0} --force".format(
                        path
                    )
                )

            # Read the file and parse into Python dictionary
            cluster_config_file = os.path.join(result_path, config_filename)
            profile = FileUtil.read_json(cluster_config_file)

            if not is_windows():
                with AutomaticSpinner(
                    "Fetching {0} config".format(source), show_time=True
                ):
                    with open(target_cluster_config_file, "w") as outfile:
                        json.dump(profile, outfile, indent=4)
            else:
                with open(target_cluster_config_file, "w") as outfile:
                    json.dump(profile, outfile, indent=4)

        return path

    @staticmethod
    def write_config_file(filepath, config_object):
        """
        Writes the config object at the given filepath
        :param filepath:
        :param config_object:
        :return:
        """
        # -- write config --
        if not is_windows():
            with AutomaticSpinner(
                "Writing {0}".format(filepath), show_time=True
            ):
                with open(filepath, "w") as outfile:
                    json.dump(config_object, outfile, indent=4)
        else:
            with open(filepath, "w") as outfile:
                json.dump(config_object, outfile, indent=4)

    @staticmethod
    def config_add(config_file, json_values):
        """
        Add new key and value to the given config file
        :param config_file:
        :param json_values:
        :return:
        """
        config_object = FileUtil.read_json(config_file)
        DeploymentConfigUtil.inline_patch(config_object, json_values, "add")
        return config_object

    @staticmethod
    def config_replace(config_file, json_values):
        """
        Replace the value of a given key in the given config file
        :param config_file:
        :param json_values:
        :return:
        """
        config_object = FileUtil.read_json(config_file)
        DeploymentConfigUtil.inline_patch(config_object, json_values, "replace")
        return config_object

    @staticmethod
    def config_remove(config_file, json_path):
        """
        Remove a key from the given config file
        :param config_file:
        :param json_path:
        :return:
        """
        config_object = FileUtil.read_json(config_file)
        DeploymentConfigUtil.inline_patch(config_object, json_path, "remove")
        return config_object

    @staticmethod
    def config_patch(config_file, patch_file):
        """
        Patch a given file against the given config file
        :param config_file:
        :param patch_file:
        :return:
        """
        config_object = FileUtil.read_json(config_file)

        if os.path.isfile(patch_file):
            patch_json = FileUtil.read_json(patch_file)
            patch = patch_json.get("patch")
            if patch:
                patches = JsonPatch(patch)
                for p in patches:
                    path = p.get("path")
                    if not path:
                        raise ValueError(
                            "Please specify a 'path' for all patches"
                        )
                    op = p.get("op")
                    if not op:
                        raise ValueError(
                            "Please specify an 'op' for all patches"
                        )
                    value = p.get("value")
                    if value is None and op != "remove":
                        raise ValueError(
                            "Please specify a 'value' for all patches other "
                            "than 'remove' ops"
                        )
                    DeploymentConfigUtil.patch_value(
                        config_object, path, value, op
                    )
            else:
                raise ValueError(
                    "The patch file must be json and start with a key of "
                    "'patch' with its value as an array of patches."
                )
        else:
            raise ValueError(
                "Please specify a file for the --patch-file argument.  The "
                "patch file must be json and start with a key of patch with "
                "its value as an array of patches."
            )

        return config_object

    @staticmethod
    def inline_patch(config_object, json_values, op):
        """
        Values provided as an inline key=value comma separated list
        :param config_object:
        :param json_values:
        :param op:
        :return:
        """
        json_values = re.split(IO_DELIM, json_values)
        for param in json_values:
            var = re.split(KEY_VALUE_SPLIT, param.strip())
            json_path = var[0]
            value = None
            if len(var) > 1:
                if os.path.isfile(var[1].strip()):
                    value = FileUtil.read_json(var[1])
                else:
                    # Replace escaped commas and equality signs with normal
                    # symbols for the actual operation
                    value = var[1].replace("\\,", ",")
                    value = value.replace("\\=", "=")
                    try:
                        value = json.loads(value)
                    except Exception as e:
                        if value.startswith("{"):
                            raise ValueError(e)
            DeploymentConfigUtil.patch_value(
                config_object, json_path, value, op
            )

    @staticmethod
    def patch_value(config_object, json_path, value, op):
        """
        Patch the config_object with the value at the json_path with the given
        op (operation)
        :param config_object:
        :param json_path:
        :param value:
        :param op:
        :return:
        """
        msg = "'{op}' at '{json_path}' with value of \n{val}\n".format(
            op=op, json_path=json_path, val=json.dumps(value, indent=4)
        )

        # If doing a replace and using conditional subsetting, use the json
        # path library
        if op == "replace" and ("$" in json_path or "@" in json_path):
            try:
                json_path = DeploymentConfigUtil.replace_path(
                    json_path, ["/"], "."
                )
                expr = parse(json_path)
                find_result = [
                    match.value for match in expr.find(config_object)
                ]
                if len(find_result) > 0:
                    expr.update(config_object, value)
                else:
                    raise ValueError(
                        "Your given json path does not exist. Please give a "
                        "json path that exists."
                    )
            except Exception as e:
                raise ValueError(
                    "{msg}\nDetails: {error}\n\nPlease consult: "
                    "https://jsonpath.com/".format(msg=msg, error=e)
                )
        # Otherwise, use the patch library
        else:
            try:
                # Replace jsonpath related characters from the path with json
                # patch syntax
                json_path = DeploymentConfigUtil.replace_path(
                    json_path, [".", "[", "]", "//"], "/"
                )
                if json_path.startswith("$"):
                    json_path = json_path[1:]
                if not json_path.startswith("/"):
                    json_path = "/" + json_path
                if json_path.endswith("/"):
                    json_path = json_path[:-1]
                patch = JsonPatch(
                    [{"op": op, "path": json_path, "value": value}]
                )
                patch.apply(config_object, True)
            except Exception as e:
                raise ValueError(
                    "{msg}\nDetails: {error}\n\nPlease consult: "
                    "http://jsonpatch.com/".format(msg=msg, error=e)
                )

    @staticmethod
    def set_config_value(config_object, json_path, value, op=None):
        """
        Sets the given value at the json_path in the config_object
        :param config_object:
        :param json_path:
        :param value:
        :return:
        """
        if not op or op == "replace":
            json_path = DeploymentConfigUtil.replace_path(json_path, ["/"], ".")
            # Attempt to update the path if it already exists
            expr = parse(json_path)
            find_result = [match.value for match in expr.find(config_object)]
            if len(find_result) > 0:
                expr.update(config_object, value)
                return
            elif "$" in json_path:
                raise ValueError(json_path)

        # The path did not exist, so now try to patch it
        json_path = DeploymentConfigUtil.replace_path(
            json_path, [".", "[", "]", "//"], "/"
        )
        if not json_path.startswith("/"):
            json_path = "/" + json_path
        if json_path.endswith("/"):
            json_path = json_path[:-1]
        if not op:
            try:
                # Attempt a replace
                patch = JsonPatch(
                    [{"op": "replace", "path": json_path, "value": value}]
                )
                patch.apply(config_object, True)
            except:
                # If replace did not work, attempt an add
                patch = JsonPatch(
                    [{"op": "add", "path": json_path, "value": value}]
                )
                patch.apply(config_object, True)
        else:
            patch = JsonPatch([{"op": op, "path": json_path, "value": value}])
            patch.apply(config_object, True)

    @staticmethod
    def replace_path(json_path, old_sep, new_sep):
        """
        Replaces jsonpath with slashes for jsonpatch library if given as periods
        :param json_path:
        :param old_sep:
        :param new_sep:
        :return:
        """
        new_path = json_path.strip()
        for sep in old_sep:
            new_path = new_path.replace(sep, new_sep)
        return new_path


# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #


def get_config_from_template(template_file, cluster_object):
    """
    Get kubernetes config from template using environment variables.
    """
    with open(template_file, "r") as f:
        template = f.read()
        return JinjaTemplate(template).render(model=cluster_object)


def get_yaml_from_template(template_file, model):
    return yaml.safe_load(
        get_config_from_template(
            template_file,
            model,
        )
    )


def parse_cert_files(
    certificate_public_key_file: str, certificate_private_key_file: str
) -> Tuple[str, str]:
    """
    parses certificate and private key files and returns the values.
    """
    if not os.path.exists(certificate_public_key_file) or not os.path.isfile(
        certificate_public_key_file
    ):
        raise ValueError(
            "Certificate public key file '"
            + certificate_public_key_file
            + "' does not exist."
        )

    if not os.path.exists(certificate_private_key_file) or not os.path.isfile(
        certificate_private_key_file
    ):
        raise ValueError(
            "Certificate private key file '"
            + certificate_private_key_file
            + "' does not exist."
        )

    # Read certificate files.
    #
    with open(certificate_public_key_file) as f:
        cert_public_key = f.read()

    with open(certificate_private_key_file) as f:
        cert_private_key = f.read()

    # Validate PEM format.
    #
    try:
        parsed_certificates = pem.parse(bytes(cert_public_key, "utf-8"))
    except:
        raise ValueError(
            "Certificate public key does not have a valid PEM format."
        )

    if len(parsed_certificates) != 1:
        raise ValueError(
            "Certificate public key file '"
            + certificate_public_key_file
            + "' must contain one and only one valid PEM formatted certificate."
        )

    try:
        parsed_privatekeys = pem.parse(bytes(cert_private_key, "utf-8"))
    except:
        raise ValueError(
            "Certificate private key does not have a valid PEM format."
        )

    if len(parsed_privatekeys) != 1:
        raise ValueError(
            "Certificate private key file '"
            + certificate_private_key_file
            + "' must contain one and only one valid PEM formatted private key."
        )

    # Ensure that certificate is of type pem._core.Certificate and private key
    # is of type pem._core.RSAPrivateKey.
    #
    if not isinstance(parsed_certificates[0], pem._core.Certificate):
        raise ValueError(
            "Certificate data in file '"
            + certificate_public_key_file
            + "' must have a valid PEM formatted certificate."
        )

    if not isinstance(
        parsed_privatekeys[0], pem._core.RSAPrivateKey
    ) and not isinstance(parsed_privatekeys[0], pem._core.PrivateKey):
        raise ValueError(
            "Private key data in file '"
            + certificate_private_key_file
            + "' must have a valid PEM formatted private key."
        )

    return cert_public_key, cert_private_key


def generate_certificate_and_key(
    hostname: str, common_name: str, sans: List[str] = None
) -> Tuple:
    """
    Generates an RSA public/private key pair and uses them to create
    a self-signed server certificate.
    :returns: Tuple containing PEM formatted certificate and private key
    """
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization, hashes
    from cryptography.hazmat.backends import default_backend
    from cryptography.x509.oid import NameOID
    from cryptography import x509
    from datetime import datetime, timedelta

    # Generate public/private key pair
    #
    key_pair = rsa.generate_private_key(
        backend=default_backend(), key_size=2048, public_exponent=65537
    )

    cn = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)])
    if sans is None:
        sans = []
    additional_sans = x509.SubjectAlternativeName(
        [x509.DNSName(name) for name in sans]
    )

    cert = (
        x509.CertificateBuilder()
        .subject_name(x509.Name(cn))
        .issuer_name(cn)
        .serial_number(1001)
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.now() + timedelta(days=5 * 365))
        .public_key(key_pair.public_key())
        .add_extension(additional_sans, False)
        .sign(key_pair, hashes.SHA256(), default_backend())
    )

    cert_pem = cert.public_bytes(encoding=serialization.Encoding.PEM)
    key_pem = key_pair.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )

    return cert_pem, key_pem, cert.fingerprint(hashes.SHA256())


def get_private_key_from_data(
    private_key_data: bytes, private_key_password: str
):
    """
    get machine private key from private key file.
    """
    key = None
    if not private_key_password:
        key = crypto.load_privatekey(crypto.FILETYPE_PEM, private_key_data)
    else:
        key = crypto.load_privatekey(
            crypto.FILETYPE_PEM, private_key_data, private_key_password
        )

    pemDataBytes = crypto.dump_privatekey(crypto.FILETYPE_PEM, key)
    pem_data = pemDataBytes.decode()
    pem_data = pem_data.replace("-----BEGIN PRIVATE KEY-----", "")
    pem_data = pem_data.replace("-----END PRIVATE KEY-----", "")
    base64Data = pem_data.replace("\n", "")
    return base64Data


def get_private_key_from_file(private_key_file: str, private_key_password: str):
    """
    get machine private key from private key file.
    """
    key = None
    with open(private_key_file, "rb") as key_file:
        key_data = key_file.read()
        # Dump the private key
        key = get_private_key_from_data(key_data, private_key_password)
    return key
