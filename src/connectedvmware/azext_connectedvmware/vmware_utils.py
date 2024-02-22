# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging
from typing import Optional, Dict, Set, Union
from azure.cli.core.azclierror import InvalidArgumentValueError, CLIInternalError
from azure.cli.core.commands.client_factory import get_subscription_id
from msrestazure.tools import is_valid_resource_id, parse_resource_id, resource_id


# pylint: disable=too-many-statements
def get_resource_id(
    cmd,
    resource_group: str,
    namespace: str,
    _type: str,
    name: Optional[str],
    **kwargs: Optional[str],
):
    """
    Constructs the resource id for the arguments parts provided.

    name can be resource name, resource id or None.
    If name is None, it can be inferred from
    child_name_X where X > 0 and child_name_X is a resource id.
    If name is None, and there is no child, None is returned.
    If the name of the final child is None, None is returned.

    kwargs can contain multiple child_type_N, child_name_N, child_namespace_N, where N > 0.
    child_type_N, child_name_N are mandatory fields for each N > 0.

    child_name_N can be None.
    child_name_N can be either a resource name or a resource id.
    If child_name_N is None, it can be inferred from
    child_name_X where X > N and child_name_X is a resource id.

    child_namespace_N cannot be None.

    child_namespace_N is optional. If provided, it must not be None.
    If not provided, it can be inferred from
    child_name_X where X > N and child_name_X is a resource id.

    If the resource id provided as child_name_N is not a valid resource id,
    or if it not a valid resource id in the context of the parent resource,
    an InvalidArgumentValueError is raised.

    For any unexpected error, a CLIInternalError is raised, which should be
    treated as a bug.
    """

    if name is None and not kwargs:
        return None

    selected_keys = {
        "subscription", "resource_group", "namespace", "type", "name"
    }
    selected_key_prefixes = {
        "child_type_",
        "child_name_",
        "child_namespace_",
    }

    def process_resource_name(
        rid_parts: Dict[str, str],
        resource_name_key: str,
        resource_name: Optional[str],
    ):
        if resource_name is None:
            raise CLIInternalError(
                f"resource_name could not be processed since it is None; "
                f"resource_name_key = {resource_name_key}, "
                f"current_rid_parts = {rid_parts}"
            )
        if not is_valid_resource_id(resource_name):
            if "/" in resource_name:
                raise InvalidArgumentValueError(
                    f"'{resource_name}' is not a valid resource name or id"
                )
            rid_parts[resource_name_key] = resource_name
            return
        child_rid_parts = parse_resource_id(resource_name)
        child_rid_parts_keys = list(child_rid_parts.keys())
        for key in child_rid_parts_keys:
            if key in selected_keys:
                continue
            if any(key.startswith(prefix) for prefix in selected_key_prefixes):
                continue
            child_rid_parts.pop(key)
        child_set = {
            k.lower(): v.lower() for k, v in child_rid_parts.items() if v is not None
        }
        parent_set = {
            k.lower(): v.lower() for k, v in rid_parts.items() if v is not None
        }
        if not parent_set.items() <= child_set.items():
            raise InvalidArgumentValueError(
                f'"{resource_name}" is not a valid child resource id in the parent context: {parent_set}'
            )
        rid_parts.update(child_rid_parts)

    rid_parts: Dict[str, str] = {}
    rid_parts.update(
        namespace=namespace,
        type=_type,
    )
    null_keys: Set[str] = set()
    if name is not None:
        process_resource_name(rid_parts, "name", name)
    else:
        null_keys.add("name")

    max_child_level = 0
    while True:
        next_level = max_child_level + 1
        child_type_key = f"child_type_{next_level}"
        child_name_key = f"child_name_{next_level}"
        child_namespace_key = f"child_namespace_{next_level}"
        has_child_type = child_type_key in kwargs
        has_child_name = child_name_key in kwargs
        has_child_namespace = child_namespace_key in kwargs
        if not any([has_child_name, has_child_type]):
            if has_child_namespace:
                raise CLIInternalError(
                    f'unexpected error: "{child_namespace_key}" must be '
                    f'specified with "{child_type_key}": kwargs = {kwargs}'
                )
            break
        if not all([has_child_name, has_child_type]):
            raise CLIInternalError(
                f"unexpected error: '{child_type_key}' must be "
                f"specified with '{child_name_key}'; "
                f"type cannot be None, value can be None: kwargs = {kwargs}"
            )
        max_child_level = next_level
        child_type = kwargs.get(child_type_key)
        child_name = kwargs.get(child_name_key)
        child_namespace = kwargs.get(child_namespace_key, None)
        if has_child_namespace:
            if child_namespace is None:
                raise CLIInternalError(
                    f'unexpected error: "{child_namespace_key}", if provided,'
                    f" should not be None: kwargs = {kwargs}"
                )
            rid_parts[child_namespace_key] = child_namespace
        if child_type is None:
            raise CLIInternalError(
                f"unexpected error: '{child_type_key}' must be provided "
                f"and should not be None: kwargs = {kwargs}"
            )
        rid_parts[child_type_key] = child_type
        if child_name is None:
            # name was not specified, so it must be inferred
            # from a successor of this resource
            null_keys.add(child_name_key)
            continue
        process_resource_name(rid_parts, child_name_key, child_name)

    if f"child_name_{max_child_level}" in null_keys:
        return None

    for null_key in null_keys:
        if null_key not in rid_parts:
            raise CLIInternalError(
                f"unexpected error: '{null_key}' could not be populated "
                f"in rid_parts: rid_parts = {rid_parts}"
            )

    if "subscription" not in rid_parts:
        rid_parts["subscription"] = get_subscription_id(cmd.cli_ctx)
    if "resource_group" not in rid_parts:
        rid_parts["resource_group"] = resource_group

    return resource_id(**rid_parts)


def create_dictionary_from_arg_string(values, option_string=None):
    """
    Creates and returns dictionary from a string containing params in KEY=VALUE format.
    """
    params_dict = {}
    for item in values:
        try:
            key, value = item.split('=', 1)
            params_dict[key.lower()] = value
        except ValueError as item_no_exist:
            raise InvalidArgumentValueError(
                f'usage error: {option_string} KEY=VALUE [KEY=VALUE ...]'
            ) from item_no_exist
    return params_dict


class ColoredFormatter(logging.Formatter):
    default_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    def __init__(self, fmt: str = default_format):
        super().__init__()
        grey = "\x1b[38;20m"
        yellow = "\x1b[33;20m"
        red = "\x1b[31;20m"
        bold_red = "\x1b[31;1m"
        reset = "\x1b[0m"
        self.FORMATS = {
            logging.DEBUG: grey + fmt + reset,
            logging.INFO: grey + fmt + reset,
            logging.WARNING: yellow + fmt + reset,
            logging.ERROR: red + fmt + reset,
            logging.CRITICAL: bold_red + fmt + reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(fmt=log_fmt, datefmt='%Y-%m-%dT%H:%M:%S')
        return formatter.format(record)


def get_logger(name: str, file_path: Union[str, None] = None):
    logger = logging.getLogger(name)
    if file_path is not None:
        fh = logging.FileHandler(file_path)
        fh.setFormatter(
            logging.Formatter(
                fmt='%(asctime)s %(levelname)-8s %(name)-12s.%(lineno)-5d %(message)s',
                datefmt='%Y-%m-%dT%H:%M:%S',
            )
        )
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)
    sh = logging.StreamHandler()
    sh.setFormatter(
        ColoredFormatter('%(asctime)s %(levelname)-8s %(message)s')
    )
    sh.setLevel(logging.INFO)
    logger.addHandler(sh)
    logger.setLevel(logging.DEBUG)
    return logger
