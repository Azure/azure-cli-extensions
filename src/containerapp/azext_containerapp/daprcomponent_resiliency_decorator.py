# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import Any, Dict

from azure.cli.core.commands import AzCliCommand
from msrest.exceptions import DeserializationError
from azure.cli.core.azclierror import (ValidationError, ResourceNotFoundError)
from azure.cli.command_modules.containerapp.base_resource import BaseResource
from azure.cli.command_modules.containerapp._utils import (clean_null_values, _convert_object_from_snake_to_camel_case, safe_get, safe_set,
                                                           _object_to_dict, _remove_additional_attributes, _remove_readonly_attributes)
from knack.log import get_logger

from copy import copy as shallowcopy

from ._decorator_utils import load_yaml_file, create_deserializer, process_dapr_component_resiliency_yaml
from ._models import (
    DaprComponentResiliency as DaprComponentResiliencyModel)

from ._clients import DaprComponentResiliencyPreviewClient
from ._client_factory import handle_raw_exception
from ._constants import (DEFAULT_COMPONENT_HTTP_RETRY_MAX,
                         DEFAULT_COMPONENT_HTTP_RETRY_BACKOFF_INITIAL_DELAY,
                         DEFAULT_COMPONENT_HTTP_RETRY_BACKOFF_MAX_DELAY)

logger = get_logger(__name__)


class DaprComponentResiliencyDecorator(BaseResource):
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def get_argument_disable_warnings(self):
        return self.get_param("disable_warnings")

    def get_argument_yaml(self):
        return self.get_param("yaml")

    def get_argument_in_timeout_response_in_seconds(self):
        return self.get_param("in_timeout_response_in_seconds")

    def get_argument_out_timeout_response_in_seconds(self):
        return self.get_param("out_timeout_response_in_seconds")

    def get_argument_in_http_retry_max(self):
        return self.get_param("in_http_retry_max")

    def get_argument_out_http_retry_max(self):
        return self.get_param("out_http_retry_max")

    def get_argument_in_http_retry_delay_in_milliseconds(self):
        return self.get_param("in_http_retry_delay_in_milliseconds")

    def get_argument_out_http_retry_delay_in_milliseconds(self):
        return self.get_param("out_http_retry_delay_in_milliseconds")

    def get_argument_in_http_retry_interval_in_milliseconds(self):
        return self.get_param("in_http_retry_interval_in_milliseconds")

    def get_argument_out_http_retry_interval_in_milliseconds(self):
        return self.get_param("out_http_retry_interval_in_milliseconds")

    def get_argument_environment(self):
        return self.get_param("environment")

    def get_argument_dapr_component_name(self):
        return self.get_param("dapr_component_name")

    def set_argument_name(self, name):
        self.set_param("name", name)

    def set_argument_dapr_component_name(self, dapr_component_name):
        self.set_param("dapr_component_name", dapr_component_name)

    def set_argument_environment(self, environment):
        self.set_param("environment", environment)

    def validate_positive_argument(self, argument_name, param_name):
        argument_value = getattr(self, f"get_argument_{argument_name}")()
        if argument_value is not None and argument_value < 1:
            raise ValidationError(f"--{param_name} must be greater than 0")

    def validate_arguments(self):
        self.validate_positive_argument("in_timeout_response_in_seconds", "in-timeout")
        self.validate_positive_argument("out_timeout_response_in_seconds", "out-timeout")
        self.validate_positive_argument("in_http_retry_max", "in-http-retries")
        self.validate_positive_argument("out_http_retry_max", "out-http-retries")
        self.validate_positive_argument("in_http_retry_delay_in_milliseconds", "in-http-delay")
        self.validate_positive_argument("out_http_retry_delay_in_milliseconds", "out-http-delay")
        self.validate_positive_argument("in_http_retry_interval_in_milliseconds", "in-http-interval")
        self.validate_positive_argument("out_http_retry_interval_in_milliseconds", "out-http-interval")

    def set_up_component_resiliency_yaml(self, file_name):
        component_resiliency_def = DaprComponentResiliencyModel
        if self.get_argument_in_http_retry_delay_in_milliseconds() or self.get_argument_in_http_retry_interval_in_milliseconds()\
                or self.get_argument_out_http_retry_delay_in_milliseconds() or self.get_argument_out_http_retry_interval_in_milliseconds() or \
                self.get_argument_in_http_retry_max() or self.get_argument_out_http_retry_max() \
                or self.get_argument_in_timeout_response_in_seconds() or self.get_argument_out_timeout_response_in_seconds():
            not self.get_argument_disable_warnings() and logger.warning(
                'Additional flags were passed along with --yaml. These flags will be ignored, and the configuration '
                'defined in the yaml will be used instead')

        yaml_component_resiliency = load_yaml_file(file_name)

        if type(yaml_component_resiliency) != dict:  # pylint: disable=unidiomatic-typecheck
            raise ValidationError('Invalid YAML provided. Please supply a valid YAML spec.')

        if yaml_component_resiliency.get('type') and yaml_component_resiliency.get('type').lower() != "microsoft.app/managedenvironments/daprcomponents/resiliencypolicies":
            raise ValidationError('Dapr Component resiliency type must be \"Microsoft.App/managedEnvironments/daprComponents/resiliencyPolicies\"')

        for arg_name in ["name", "dapr_component_name", "environment"]:
            arg_value = getattr(self, f"get_argument_{arg_name}")()
            yaml_value = yaml_component_resiliency.get(arg_name)
            if yaml_value and yaml_value.lower() != arg_value.lower():
                logger.warning(
                    f"The {arg_name} provided in the --yaml file \"{yaml_value}\" does not match the one provided in the --{arg_name.replace('_', '-')} flag \"{arg_value}\". The one provided in the --yaml file will be used.")
                setattr(self, f"set_argument_{arg_name}", yaml_value)

        # Deserialize the yaml into a DaprComponentResiliency object. Need this since we're not using SDK
        try:
            deserializer = create_deserializer(self.models)

            component_resiliency_def = deserializer('DaprComponentResiliencyPolicy', yaml_component_resiliency)
        except DeserializationError as ex:
            raise ValidationError('Invalid YAML provided. Please supply a valid YAML spec.') from ex

        component_resiliency_def = _convert_object_from_snake_to_camel_case(_object_to_dict(component_resiliency_def))
        component_resiliency_def = process_dapr_component_resiliency_yaml(component_resiliency_def)
        # Remove "additionalProperties" and read-only attributes that are introduced in the deserialization. Need this since we're not using SDK
        _remove_additional_attributes(component_resiliency_def)
        _remove_readonly_attributes(component_resiliency_def)

        component_resiliency_def = clean_null_values(component_resiliency_def)

        # Now we just add defaults where required
        # Inbound Retries
        in_retry_policy = safe_get(component_resiliency_def, 'properties', 'inboundPolicy', 'httpRetryPolicy')
        if in_retry_policy and ('maxRetries' in in_retry_policy or 'retryBackOff' in in_retry_policy):
            in_retry_policy['maxRetries'] = in_retry_policy['maxRetries'] if 'maxRetries' in in_retry_policy else DEFAULT_COMPONENT_HTTP_RETRY_MAX

            if 'retryBackOff' not in in_retry_policy:
                in_retry_policy['retryBackOff'] = {}
            if 'initialDelayInMilliseconds' not in in_retry_policy['retryBackOff']:
                in_retry_policy['retryBackOff']['initialDelayInMilliseconds'] = DEFAULT_COMPONENT_HTTP_RETRY_BACKOFF_INITIAL_DELAY
            if 'maxIntervalInMilliseconds' not in in_retry_policy['retryBackOff']:
                in_retry_policy['retryBackOff']['maxIntervalInMilliseconds'] = DEFAULT_COMPONENT_HTTP_RETRY_BACKOFF_MAX_DELAY

        # Outbound Retries
        out_retry_policy = safe_get(component_resiliency_def, 'properties', 'outboundPolicy', 'httpRetryPolicy')
        if out_retry_policy and ('maxRetries' in out_retry_policy or 'retryBackOff' in out_retry_policy):
            out_retry_policy['maxRetries'] = out_retry_policy['maxRetries'] if 'maxRetries' in out_retry_policy else DEFAULT_COMPONENT_HTTP_RETRY_MAX

            if 'retryBackOff' not in out_retry_policy:
                out_retry_policy['retryBackOff'] = {}
            if 'initialDelayInMilliseconds' not in out_retry_policy['retryBackOff']:
                out_retry_policy['retryBackOff']['initialDelayInMilliseconds'] = DEFAULT_COMPONENT_HTTP_RETRY_BACKOFF_INITIAL_DELAY
            if 'maxIntervalInMilliseconds' not in out_retry_policy['retryBackOff']:
                out_retry_policy['retryBackOff']['maxIntervalInMilliseconds'] = DEFAULT_COMPONENT_HTTP_RETRY_BACKOFF_MAX_DELAY

        return component_resiliency_def


class DaprComponentResiliencyPreviewCreateDecorator(DaprComponentResiliencyDecorator):
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)
        self.component_resiliency_def = DaprComponentResiliencyModel

    def create(self):
        try:
            r = self.client.create_or_update(
                cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                name=self.get_argument_name(), dapr_component_name=self.get_argument_dapr_component_name(),
                environment_name=self.get_argument_environment(), component_resiliency_envelope=self.component_resiliency_def,
                no_wait=self.get_argument_no_wait())
            r = clean_null_values(r)
            return r
        except Exception as e:
            handle_raw_exception(e)

    def construct_payload(self):
        if self.get_argument_yaml():
            self.component_resiliency_def = self.set_up_component_resiliency_yaml(file_name=self.get_argument_yaml())
            return

        # Inbound
        # TimeoutPolicy
        in_timeout_def = {"responseTimeoutInSeconds": None}
        if self.get_argument_in_timeout_response_in_seconds() is not None:
            in_timeout_def["responseTimeoutInSeconds"] = self.get_argument_in_timeout_response_in_seconds()
            self.component_resiliency_def["properties"]["inboundPolicy"]["timeoutPolicy"] = in_timeout_def

        # HTTPRetryPolicy
        in_retry_def = {
            "maxRetries": None,
            "retryBackOff": {
                "initialDelayInMilliseconds": None,
                "maxIntervalInMilliseconds": None,
            }
        }
        if self.get_argument_in_http_retry_delay_in_milliseconds() is not None or self.get_argument_in_http_retry_interval_in_milliseconds() is not None or self.get_argument_in_http_retry_max() is not None:
            in_retry_def["maxRetries"] = self.get_argument_in_http_retry_max() if self.get_argument_in_http_retry_max() is not None else DEFAULT_COMPONENT_HTTP_RETRY_MAX
            in_retry_def["retryBackOff"]["initialDelayInMilliseconds"] = self.get_argument_in_http_retry_delay_in_milliseconds() if self.get_argument_in_http_retry_delay_in_milliseconds() is not None else DEFAULT_COMPONENT_HTTP_RETRY_BACKOFF_INITIAL_DELAY
            in_retry_def["retryBackOff"]["maxIntervalInMilliseconds"] = self.get_argument_in_http_retry_interval_in_milliseconds() if self.get_argument_in_http_retry_interval_in_milliseconds() is not None else DEFAULT_COMPONENT_HTTP_RETRY_BACKOFF_MAX_DELAY
            self.component_resiliency_def["properties"]["inboundPolicy"]["httpRetryPolicy"] = in_retry_def

        # Outbound
        # TimeoutPolicy
        out_timeout_def = {"responseTimeoutInSeconds": None}
        if self.get_argument_out_timeout_response_in_seconds() is not None:
            out_timeout_def["responseTimeoutInSeconds"] = self.get_argument_out_timeout_response_in_seconds()
            self.component_resiliency_def["properties"]["outboundPolicy"]["timeoutPolicy"] = out_timeout_def

        # HTTPRetryPolicy
        out_retry_def = {
            "maxRetries": None,
            "retryBackOff": {
                "initialDelayInMilliseconds": None,
                "maxIntervalInMilliseconds": None,
            }
        }
        if self.get_argument_out_http_retry_delay_in_milliseconds() is not None or self.get_argument_out_http_retry_interval_in_milliseconds() is not None or self.get_argument_out_http_retry_max() is not None:
            out_retry_def["maxRetries"] = self.get_argument_out_http_retry_max() if self.get_argument_out_http_retry_max() is not None else DEFAULT_COMPONENT_HTTP_RETRY_MAX
            out_retry_def["retryBackOff"]["initialDelayInMilliseconds"] = self.get_argument_out_http_retry_delay_in_milliseconds() if self.get_argument_out_http_retry_delay_in_milliseconds() is not None else DEFAULT_COMPONENT_HTTP_RETRY_BACKOFF_INITIAL_DELAY
            out_retry_def["retryBackOff"]["maxIntervalInMilliseconds"] = self.get_argument_out_http_retry_interval_in_milliseconds() if self.get_argument_out_http_retry_interval_in_milliseconds() is not None else DEFAULT_COMPONENT_HTTP_RETRY_BACKOFF_MAX_DELAY
            self.component_resiliency_def["properties"]["outboundPolicy"]["httpRetryPolicy"] = out_retry_def

        self.component_resiliency_def = clean_null_values(self.component_resiliency_def)

        if self.component_resiliency_def is None or self.component_resiliency_def == {}:
            self.component_resiliency_def["properties"] = {}


class DaprComponentResiliencyPreviewUpdateDecorator(DaprComponentResiliencyDecorator):
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)
        self.component_resiliency_update_def = DaprComponentResiliencyModel
        self.component_resiliency_patch_def = shallowcopy(self.component_resiliency_update_def)

    def construct_payload(self):
        if self.get_argument_yaml():
            self.component_resiliency_update_def = self.set_up_component_resiliency_yaml(file_name=self.get_argument_yaml())
            return

        component_resiliency_def = None

        try:
            component_resiliency_def = DaprComponentResiliencyPreviewClient.show(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                                                                                 name=self.get_argument_name(), dapr_component_name=self.get_argument_dapr_component_name(),
                                                                                 environment_name=self.get_argument_environment())
        except:
            pass

        if not component_resiliency_def:
            raise ResourceNotFoundError("The dapr component resiliency policy '{}' does not exist".format(self.get_argument_name()))

        if self.get_argument_in_http_retry_delay_in_milliseconds() is not None or self.get_argument_in_http_retry_interval_in_milliseconds() is not None or self.get_argument_in_http_retry_max() is not None:
            # First, fetch the value from the flag if it exists, else fetch it from the existing component resiliency policy, else set it to default
            if self.get_argument_in_http_retry_max() is not None:
                safe_set(self.component_resiliency_patch_def, "properties", "inboundPolicy", "httpRetryPolicy", "maxRetries", value=self.get_argument_in_http_retry_max())
            elif safe_get(component_resiliency_def, "properties", "inboundPolicy", "httpRetryPolicy", "maxRetries"):
                safe_set(self.component_resiliency_patch_def, "properties", "inboundPolicy", "httpRetryPolicy", "maxRetries", value=safe_get(component_resiliency_def, "properties", "inboundPolicy", "httpRetryPolicy", "maxRetries"))
            else:
                safe_set(self.component_resiliency_patch_def, "properties", "inboundPolicy", "httpRetryPolicy", "maxRetries", value=DEFAULT_COMPONENT_HTTP_RETRY_MAX)

            if self.get_argument_in_http_retry_delay_in_milliseconds() is not None:
                safe_set(self.component_resiliency_patch_def, "properties", "inboundPolicy", "httpRetryPolicy", "retryBackOff", "initialDelayInMilliseconds", value=self.get_argument_in_http_retry_delay_in_milliseconds())
            elif safe_get(component_resiliency_def, "properties", "inboundPolicy", "httpRetryPolicy", "retryBackOff", "initialDelayInMilliseconds"):
                safe_set(self.component_resiliency_patch_def, "properties", "inboundPolicy", "httpRetryPolicy", "retryBackOff", "initialDelayInMilliseconds", value=safe_get(component_resiliency_def, "properties", "inboundPolicy", "httpRetryPolicy", "retryBackOff", "initialDelayInMilliseconds"))
            else:
                safe_set(self.component_resiliency_patch_def, "properties", "inboundPolicy", "httpRetryPolicy", "retryBackOff", "initialDelayInMilliseconds", value=DEFAULT_COMPONENT_HTTP_RETRY_BACKOFF_INITIAL_DELAY)

            if self.get_argument_in_http_retry_interval_in_milliseconds() is not None:
                safe_set(self.component_resiliency_patch_def, "properties", "inboundPolicy", "httpRetryPolicy", "retryBackOff", "maxIntervalInMilliseconds", value=self.get_argument_in_http_retry_interval_in_milliseconds())
            elif safe_get(component_resiliency_def, "properties", "inboundPolicy", "httpRetryPolicy", "retryBackOff", "maxIntervalInMilliseconds"):
                safe_set(self.component_resiliency_patch_def, "properties", "inboundPolicy", "httpRetryPolicy", "retryBackOff", "maxIntervalInMilliseconds", value=safe_get(component_resiliency_def, "properties", "inboundPolicy", "httpRetryPolicy", "retryBackOff", "maxIntervalInMilliseconds"))
            else:
                safe_set(self.component_resiliency_patch_def, "properties", "inboundPolicy", "httpRetryPolicy", "retryBackOff", "maxIntervalInMilliseconds", value=DEFAULT_COMPONENT_HTTP_RETRY_BACKOFF_MAX_DELAY)

        safe_set(self.component_resiliency_patch_def, "properties", "inboundPolicy", "timeoutPolicy", "responseTimeoutInSeconds", value=(self.get_argument_in_timeout_response_in_seconds() or safe_get(component_resiliency_def, "properties", "inboundPolicy", "timeoutPolicy", "responseTimeoutInSeconds")))

        if self.get_argument_out_http_retry_delay_in_milliseconds() is not None or self.get_argument_out_http_retry_interval_in_milliseconds() is not None or self.get_argument_out_http_retry_max() is not None:
            if self.get_argument_out_http_retry_max() is not None:
                safe_set(self.component_resiliency_patch_def, "properties", "outboundPolicy", "httpRetryPolicy", "maxRetries", value=self.get_argument_out_http_retry_max())
            elif safe_get(component_resiliency_def, "properties", "outboundPolicy", "httpRetryPolicy", "maxRetries"):
                safe_set(self.component_resiliency_patch_def, "properties", "outboundPolicy", "httpRetryPolicy", "maxRetries", value=safe_get(component_resiliency_def, "properties", "outboundPolicy", "httpRetryPolicy", "maxRetries"))
            else:
                safe_set(self.component_resiliency_patch_def, "properties", "outboundPolicy", "httpRetryPolicy", "maxRetries", value=DEFAULT_COMPONENT_HTTP_RETRY_MAX)

            if self.get_argument_out_http_retry_delay_in_milliseconds() is not None:
                safe_set(self.component_resiliency_patch_def, "properties", "outboundPolicy", "httpRetryPolicy", "retryBackOff", "initialDelayInMilliseconds", value=self.get_argument_out_http_retry_delay_in_milliseconds())
            elif safe_get(component_resiliency_def, "properties", "outboundPolicy", "httpRetryPolicy", "retryBackOff", "initialDelayInMilliseconds"):
                safe_set(self.component_resiliency_patch_def, "properties", "outboundPolicy", "httpRetryPolicy", "retryBackOff", "initialDelayInMilliseconds", value=safe_get(component_resiliency_def, "properties", "outboundPolicy", "httpRetryPolicy", "retryBackOff", "initialDelayInMilliseconds"))
            else:
                safe_set(self.component_resiliency_patch_def, "properties", "outboundPolicy", "httpRetryPolicy", "retryBackOff", "initialDelayInMilliseconds", value=DEFAULT_COMPONENT_HTTP_RETRY_BACKOFF_INITIAL_DELAY)

            if self.get_argument_out_http_retry_interval_in_milliseconds() is not None:
                safe_set(self.component_resiliency_patch_def, "properties", "outboundPolicy", "httpRetryPolicy", "retryBackOff", "maxIntervalInMilliseconds", value=self.get_argument_out_http_retry_interval_in_milliseconds())
            elif safe_get(component_resiliency_def, "properties", "outboundPolicy", "httpRetryPolicy", "retryBackOff", "maxIntervalInMilliseconds"):
                safe_set(self.component_resiliency_patch_def, "properties", "outboundPolicy", "httpRetryPolicy", "retryBackOff", "maxIntervalInMilliseconds", value=safe_get(component_resiliency_def, "properties", "outboundPolicy", "httpRetryPolicy", "retryBackOff", "maxIntervalInMilliseconds"))
            else:
                safe_set(self.component_resiliency_patch_def, "properties", "outboundPolicy", "httpRetryPolicy", "retryBackOff", "maxIntervalInMilliseconds", value=DEFAULT_COMPONENT_HTTP_RETRY_BACKOFF_MAX_DELAY)

        safe_set(self.component_resiliency_patch_def, "properties", "outboundPolicy", "timeoutPolicy", "responseTimeoutInSeconds", value=(self.get_argument_out_timeout_response_in_seconds() or safe_get(component_resiliency_def, "properties", "outboundPolicy", "timeoutPolicy", "responseTimeoutInSeconds")))

        if safe_get(self.component_resiliency_patch_def, "properties", "inboundPolicy", "httpRetryPolicy", "maxRetries") or safe_get(self.component_resiliency_patch_def, "properties", "inboundPolicy", "httpRetryPolicy", "retryBackOff", "initialDelayInMilliseconds") or safe_get(self.component_resiliency_patch_def, "properties", "inboundPolicy", "httpRetryPolicy", "retryBackOff", "maxIntervalInMilliseconds"):
            safe_set(component_resiliency_def, "properties", "inboundPolicy", "httpRetryPolicy", value=safe_get(self.component_resiliency_patch_def, "properties", "inboundPolicy", "httpRetryPolicy"))
        if safe_get(self.component_resiliency_patch_def, "properties", "inboundPolicy", "timeoutPolicy", "responseTimeoutInSeconds"):
            safe_set(component_resiliency_def, "properties", "inboundPolicy", "timeoutPolicy", value=safe_get(self.component_resiliency_patch_def, "properties", "inboundPolicy", "timeoutPolicy"))
        if safe_get(self.component_resiliency_patch_def, "properties", "outboundPolicy", "httpRetryPolicy", "maxRetries") or safe_get(self.component_resiliency_patch_def, "properties", "outboundPolicy", "httpRetryPolicy", "retryBackOff", "initialDelayInMilliseconds") or safe_get(self.component_resiliency_patch_def, "properties", "outboundPolicy", "httpRetryPolicy", "retryBackOff", "maxIntervalInMilliseconds"):
            safe_set(component_resiliency_def, "properties", "outboundPolicy", "httpRetryPolicy", value=safe_get(self.component_resiliency_patch_def, "properties", "outboundPolicy", "httpRetryPolicy"))
        if safe_get(self.component_resiliency_patch_def, "properties", "outboundPolicy", "timeoutPolicy", "responseTimeoutInSeconds"):
            safe_set(component_resiliency_def, "properties", "outboundPolicy", "timeoutPolicy", value=safe_get(self.component_resiliency_patch_def, "properties", "outboundPolicy", "timeoutPolicy"))

        component_resiliency_def = clean_null_values(component_resiliency_def)
        self.component_resiliency_update_def = component_resiliency_def

    def update(self):
        try:
            r = self.client.create_or_update(
                cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                name=self.get_argument_name(), dapr_component_name=self.get_argument_dapr_component_name(),
                environment_name=self.get_argument_environment(), component_resiliency_envelope=self.component_resiliency_update_def,
                no_wait=self.get_argument_no_wait())

            r = clean_null_values(r)

            return r

        except Exception as e:
            handle_raw_exception(e)


class DaprComponentResiliencyPreviewShowDecorator(DaprComponentResiliencyDecorator):
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def show(self):
        try:
            r = self.client.show(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                                 name=self.get_argument_name(), dapr_component_name=self.get_argument_dapr_component_name(),
                                 environment_name=self.get_argument_environment())
            r = clean_null_values(r)
            return r
        except Exception as e:
            handle_raw_exception(e)


class DaprComponentResiliencyPreviewListDecorator(DaprComponentResiliencyDecorator):
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def list(self):
        try:
            r = self.client.list(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                                 dapr_component_name=self.get_argument_dapr_component_name(), environment_name=self.get_argument_environment())
            r = clean_null_values(r)
            return r
        except Exception as e:
            handle_raw_exception(e)


class DaprComponentResiliencyPreviewDeleteDecorator(DaprComponentResiliencyDecorator):
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def delete(self):
        try:
            return self.client.delete(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                                      name=self.get_argument_name(), dapr_component_name=self.get_argument_dapr_component_name(),
                                      environment_name=self.get_argument_environment(), no_wait=self.get_argument_no_wait())
        except Exception as e:
            handle_raw_exception(e)
