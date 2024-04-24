# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import Dict, Any

from azure.cli.core.azclierror import (ValidationError, ResourceNotFoundError)
from azure.cli.core.commands import AzCliCommand
from msrest.exceptions import DeserializationError

from ._decorator_utils import load_yaml_file, create_deserializer, process_containerapp_resiliency_yaml
from ._models import (
    ContainerAppsResiliency as ContainerAppsResiliencyModel)

from knack.log import get_logger

from azure.cli.command_modules.containerapp.base_resource import BaseResource
from azure.cli.command_modules.containerapp._utils import (
    clean_null_values, safe_get, _convert_object_from_snake_to_camel_case,
    _object_to_dict, _remove_additional_attributes, _remove_readonly_attributes)
from ._clients import ContainerAppsResiliencyPreviewClient
from ._client_factory import handle_raw_exception

from ._constants import (DEFAULT_INTERVAL, DEFAULT_MAX_EJECTION, DEFAULT_HTTP2_MAX_REQ, DEFAULT_RESPONSE_TIMEOUT,
                         DEFAULT_CONNECTION_TIMEOUT, DEFAULT_HTTP_RETRY_MAX,
                         DEFAULT_HTTP1_MAX_PENDING_REQ, DEFAULT_CONSECUTIVE_ERRORS, DEFAULT_HTTP_RETRY_DELAY_IN_MILLISECONDS,
                         DEFAULT_HTTP_RETRY_INTERVAL_IN_MILLISECONDS, DEFAULT_HTTP_RETRY_ERRORS)

from ._models import (HttpRetryPolicy as HttpRetryPolicyModel,
                      TimeoutPolicy as TimeoutPolicyModel,
                      TcpRetryPolicy as TcpRetryPolicyModel,
                      CircuitBreakerPolicy as CircuitBreakerPolicyModel,
                      TcpConnectionPool as TcpConnectionPoolModel,
                      HttpConnectionPool as HttpConnectionPoolModel)

logger = get_logger(__name__)


class ContainerAppResiliencyDecorator(BaseResource):
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def get_argument_container_app_name(self):
        return self.get_param("container_app_name")

    def get_argument_disable_warnings(self):
        return self.get_param("disable_warnings")

    def get_argument_tcp_retry_max_connect_attempts(self):
        return self.get_param("tcp_retry_max_connect_attempts")

    def get_argument_circuit_breaker_consecutive_errors(self):
        return self.get_param("circuit_breaker_consecutive_errors")

    def get_argument_circuit_breaker_interval(self):
        return self.get_param("circuit_breaker_interval")

    def get_argument_circuit_breaker_max_ejection(self):
        return self.get_param("circuit_breaker_max_ejection")

    def get_argument_tcp_connection_pool_max_connections(self):
        return self.get_param("tcp_connection_pool_max_connections")

    def get_argument_http_connection_pool_http1_max_pending_req(self):
        return self.get_param("http_connection_pool_http1_max_pending_req")

    def get_argument_http_connection_pool_http2_max_req(self):
        return self.get_param("http_connection_pool_http2_max_req")

    def get_argument_timeout_response_in_seconds(self):
        return self.get_param("timeout_response_in_seconds")

    def get_argument_timeout_connection_in_seconds(self):
        return self.get_param("timeout_connection_in_seconds")

    def get_argument_http_retry_max(self):
        return self.get_param("http_retry_max")

    def get_argument_http_retry_delay_in_milliseconds(self):
        return self.get_param("http_retry_delay_in_milliseconds")

    def get_argument_http_retry_interval_in_milliseconds(self):
        return self.get_param("http_retry_interval_in_milliseconds")

    def get_argument_http_retry_status_codes(self):
        return self.get_param("http_retry_status_codes")

    def get_argument_http_retry_errors(self):
        return self.get_param("http_retry_errors")

    def get_argument_yaml(self):
        return self.get_param("yaml")

    def get_argument_default(self):
        return self.get_param("default")

    def set_argument_name(self, name):
        self.set_param("name", name)

    def set_argument_container_app_name(self, container_app_name):
        self.set_param("container_app_name", container_app_name)

    def validate_positive_argument(self, argument_name, param_name):
        argument_value = getattr(self, f"get_argument_{argument_name}")()
        if argument_value is not None and argument_value < 1:
            raise ValidationError(f"--{param_name} must be greater than 0")

    def validate_max_ejection(self):
        max_ejection = self.get_argument_circuit_breaker_max_ejection()
        if max_ejection is not None and (max_ejection < 1 or max_ejection > 100):
            raise ValidationError(f"--cb-max-ejection must be between 1 and 100")

    def validate_arguments(self):
        self.validate_positive_argument("circuit_breaker_consecutive_errors", "cb-sequential-errors")
        self.validate_positive_argument("circuit_breaker_interval", "cb-interval")
        self.validate_max_ejection()
        self.validate_positive_argument("tcp_connection_pool_max_connections", "tcp-connections")
        self.validate_positive_argument("http_connection_pool_http1_max_pending_req", "http1-pending")
        self.validate_positive_argument("http_connection_pool_http2_max_req", "http2-parallel")
        self.validate_positive_argument("timeout_response_in_seconds", "timeout")
        self.validate_positive_argument("timeout_connection_in_seconds", "timeout-connect")
        self.validate_positive_argument("tcp_retry_max_connect_attempts", "tcp-retries")
        self.validate_positive_argument("http_retry_max", "http-retries")
        self.validate_positive_argument("http_retry_delay_in_milliseconds", "http-delay")
        self.validate_positive_argument("http_retry_interval_in_milliseconds", "http-interval")

    def set_up_containerapp_resiliency_yaml(self, file_name):
        containerapp_def = ContainerAppsResiliencyModel
        if self.get_argument_tcp_retry_max_connect_attempts() or self.get_argument_circuit_breaker_consecutive_errors()\
                or self.get_argument_circuit_breaker_interval() or self.get_argument_circuit_breaker_max_ejection() or \
                self.get_argument_tcp_connection_pool_max_connections() or \
                self.get_argument_http_connection_pool_http1_max_pending_req() \
                or self.get_argument_http_connection_pool_http2_max_req() or self.get_argument_timeout_response_in_seconds() \
                or self.get_argument_timeout_connection_in_seconds() or self.get_argument_http_retry_max() \
                or self.get_argument_http_retry_delay_in_milliseconds() or self.get_argument_http_retry_interval_in_milliseconds() \
                or self.get_argument_http_retry_status_codes() or self.get_argument_http_retry_errors():
            not self.get_argument_disable_warnings() and logger.warning(
                'Additional flags were passed along with --yaml. These flags will be ignored, and the configuration '
                'defined in the yaml will be used instead')

        yaml_containerapps_resiliency = load_yaml_file(file_name)
        if type(yaml_containerapps_resiliency) != dict:  # pylint: disable=unidiomatic-typecheck
            raise ValidationError('Invalid YAML provided. Please supply a valid YAML spec.')

        if yaml_containerapps_resiliency.get('type') and yaml_containerapps_resiliency.get('type').lower() != "microsoft.app/containerapps/resiliencypolicies":
            raise ValidationError('Containerapp resiliency type must be \"Microsoft.App/containerApps/resiliencyPolicies\"')

        if yaml_containerapps_resiliency.get('name') and yaml_containerapps_resiliency.get('name').lower() != self.get_argument_name().lower():
            logger.warning(
                'The app name provided in the --yaml file "{}" does not match the one provided in the --name flag "{}". The one provided in the --yaml file will be used.'.format(
                    yaml_containerapps_resiliency.get('name'), self.get_argument_name()))
            self.set_argument_name(yaml_containerapps_resiliency.get('name'))

        if yaml_containerapps_resiliency.get('containerAppName') and yaml_containerapps_resiliency.get('containerAppName').lower() != self.get_argument_container_app_name().lower():
            logger.warning(
                'The containerapp name provided in the --yaml file "{}" does not match the one provided in the --container-app-name flag "{}". The one provided in the --yaml file will be used.'.format(
                    yaml_containerapps_resiliency.get('containerAppName'), self.get_argument_container_app_name()))
            self.set_argument_container_app_name(yaml_containerapps_resiliency.get('containerAppName'))

        # Deserialize the yaml into a ContainerAppsResiliency object. Need this since we're not using SDK
        try:
            deserializer = create_deserializer(self.models)

            containerapp_def = deserializer('AppResiliency', yaml_containerapps_resiliency)
        except DeserializationError as ex:
            raise ValidationError('Invalid YAML provided. Please supply a valid YAML spec.') from ex

        containerapp_def = _convert_object_from_snake_to_camel_case(
            _object_to_dict(containerapp_def))

        containerapp_def = process_containerapp_resiliency_yaml(containerapp_def)

        # Remove "additionalProperties" and read-only attributes that are introduced in the deserialization. Need this since we're not using SDK
        _remove_additional_attributes(containerapp_def)
        _remove_readonly_attributes(containerapp_def)
        containerapp_def = clean_null_values(containerapp_def)

        # Now we just add defaults where required
        # Retries
        http_retry_policy = safe_get(containerapp_def, 'properties', 'httpRetryPolicy')
        if http_retry_policy and ('maxRetries' in http_retry_policy or 'retryBackOff' in http_retry_policy or 'matches' in http_retry_policy):
            http_retry_policy['maxRetries'] = http_retry_policy.get('maxRetries', DEFAULT_HTTP_RETRY_MAX)
            retry_backoff = safe_get(http_retry_policy, 'retryBackOff')
            if retry_backoff and ('initialDelayInMilliseconds' in retry_backoff or 'maxIntervalInMilliseconds' in retry_backoff):
                retry_backoff['initialDelayInMilliseconds'] = retry_backoff.get('initialDelayInMilliseconds', DEFAULT_HTTP_RETRY_DELAY_IN_MILLISECONDS)
                retry_backoff['maxIntervalInMilliseconds'] = retry_backoff.get('maxIntervalInMilliseconds', DEFAULT_HTTP_RETRY_INTERVAL_IN_MILLISECONDS)
            else:
                retry_backoff = {
                    "initialDelayInMilliseconds": DEFAULT_HTTP_RETRY_DELAY_IN_MILLISECONDS,
                    "maxIntervalInMilliseconds": DEFAULT_HTTP_RETRY_INTERVAL_IN_MILLISECONDS
                }
            http_retry_policy['retryBackOff'] = retry_backoff
            matches = safe_get(http_retry_policy, 'matches')
            if matches and 'errors' in matches:
                matches['errors'] = matches.get('errors', DEFAULT_HTTP_RETRY_ERRORS)
            else:
                matches = {
                    "errors": DEFAULT_HTTP_RETRY_ERRORS
                }
            http_retry_policy['matches'] = matches
            containerapp_def['properties']['httpRetryPolicy'] = http_retry_policy

        # Timeouts
        timeout_policy = safe_get(containerapp_def, 'properties', 'timeoutPolicy')
        if timeout_policy and ('responseTimeoutInSeconds' in timeout_policy or 'connectionTimeoutInSeconds' in timeout_policy):
            timeout_policy['responseTimeoutInSeconds'] = timeout_policy.get('responseTimeoutInSeconds', DEFAULT_RESPONSE_TIMEOUT)
            timeout_policy['connectionTimeoutInSeconds'] = timeout_policy.get('connectionTimeoutInSeconds', DEFAULT_CONNECTION_TIMEOUT)
            containerapp_def['properties']['timeoutPolicy'] = timeout_policy

        # Circuit Breaker
        circuit_breaker_policy = safe_get(containerapp_def, 'properties', 'circuitBreakerPolicy')
        if circuit_breaker_policy and ('consecutiveErrors' in circuit_breaker_policy or 'intervalInSeconds' in circuit_breaker_policy or 'maxEjectionPercent' in circuit_breaker_policy):
            circuit_breaker_policy['consecutiveErrors'] = circuit_breaker_policy.get('consecutiveErrors', DEFAULT_CONSECUTIVE_ERRORS)
            circuit_breaker_policy['intervalInSeconds'] = circuit_breaker_policy.get('intervalInSeconds', DEFAULT_INTERVAL)
            circuit_breaker_policy['maxEjectionPercent'] = circuit_breaker_policy.get('maxEjectionPercent', DEFAULT_MAX_EJECTION)
            containerapp_def['properties']['circuitBreakerPolicy'] = circuit_breaker_policy

        # HTTP Connection Pool
        http_connection_pool = safe_get(containerapp_def, 'properties', 'httpConnectionPool')
        if http_connection_pool and ('http1MaxPendingRequests' in http_connection_pool or 'http2MaxRequests' in http_connection_pool):
            http_connection_pool['http1MaxPendingRequests'] = http_connection_pool.get('http1MaxPendingRequests', DEFAULT_HTTP1_MAX_PENDING_REQ)
            http_connection_pool['http2MaxRequests'] = http_connection_pool.get('http2MaxRequests', DEFAULT_HTTP2_MAX_REQ)
            containerapp_def['properties']['httpConnectionPool'] = http_connection_pool

        return containerapp_def


class ContainerAppResiliencyPreviewCreateDecorator(ContainerAppResiliencyDecorator):
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)
        self.containerapp_resiliency_def = ContainerAppsResiliencyModel

    def create(self):
        try:
            r = self.client.create_or_update(
                cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                name=self.get_argument_name(), container_app_name=self.get_argument_container_app_name(),
                container_app_resiliency_envelope=self.containerapp_resiliency_def,
                no_wait=self.get_argument_no_wait())
            r = clean_null_values(r)
            return r
        except Exception as e:
            handle_raw_exception(e)

    def construct_payload(self):
        if self.get_argument_yaml():
            self.containerapp_resiliency_def = self.set_up_containerapp_resiliency_yaml(file_name=self.get_argument_yaml())
            return

        if self.get_argument_default():
            return self.set_up_default_containerapp_resiliency()

        http_retry_def = HttpRetryPolicyModel
        if self.get_argument_http_retry_max() is not None or \
                self.get_argument_http_retry_delay_in_milliseconds() is not None or \
                self.get_argument_http_retry_interval_in_milliseconds() is not None or \
                self.get_argument_http_retry_status_codes() is not None or \
                self.get_argument_http_retry_errors() is not None:
            http_retry_def["maxRetries"] = self.get_argument_http_retry_max() if self.get_argument_http_retry_max() is not None else DEFAULT_HTTP_RETRY_MAX
            http_retry_def["retryBackOff"] = {
                "initialDelayInMilliseconds": self.get_argument_http_retry_delay_in_milliseconds() if self.get_argument_http_retry_delay_in_milliseconds() is not None else DEFAULT_HTTP_RETRY_DELAY_IN_MILLISECONDS,
                "maxIntervalInMilliseconds": self.get_argument_http_retry_interval_in_milliseconds() if self.get_argument_http_retry_interval_in_milliseconds() is not None else DEFAULT_HTTP_RETRY_INTERVAL_IN_MILLISECONDS
            }
            http_retry_def["matches"] = {
                "errors": self.get_argument_http_retry_errors() if self.get_argument_http_retry_errors() is not None else DEFAULT_HTTP_RETRY_ERRORS,
                "httpStatusCodes": self.get_argument_http_retry_status_codes() if self.get_argument_http_retry_status_codes() is not None else None
            }

        timeout_def = TimeoutPolicyModel
        if self.get_argument_timeout_response_in_seconds() is not None or \
           self.get_argument_timeout_connection_in_seconds() is not None:
            timeout_def["responseTimeoutInSeconds"] = self.get_argument_timeout_response_in_seconds() if self.get_argument_timeout_response_in_seconds() is not None else DEFAULT_RESPONSE_TIMEOUT
            timeout_def["connectionTimeoutInSeconds"] = self.get_argument_timeout_connection_in_seconds() if self.get_argument_timeout_connection_in_seconds() is not None else DEFAULT_CONNECTION_TIMEOUT

        tcpretry_def = TcpRetryPolicyModel
        if self.get_argument_tcp_retry_max_connect_attempts() is not None:
            tcpretry_def["maxConnectAttempts"] = self.get_argument_tcp_retry_max_connect_attempts()

        circuitbreaker_def = CircuitBreakerPolicyModel
        if self.get_argument_circuit_breaker_consecutive_errors() is not None or \
           self.get_argument_circuit_breaker_interval() is not None or \
           self.get_argument_circuit_breaker_max_ejection() is not None:
            circuitbreaker_def["consecutiveErrors"] = self.get_argument_circuit_breaker_consecutive_errors() if self.get_argument_circuit_breaker_consecutive_errors() is not None else DEFAULT_CONSECUTIVE_ERRORS
            circuitbreaker_def["intervalInSeconds"] = self.get_argument_circuit_breaker_interval() if self.get_argument_circuit_breaker_interval() is not None else DEFAULT_INTERVAL
            circuitbreaker_def["maxEjectionPercent"] = self.get_argument_circuit_breaker_max_ejection() if self.get_argument_circuit_breaker_max_ejection() is not None else DEFAULT_MAX_EJECTION

        tcp_connectionpool_def = TcpConnectionPoolModel
        if self.get_argument_tcp_connection_pool_max_connections() is not None:
            tcp_connectionpool_def["maxConnections"] = self.get_argument_tcp_connection_pool_max_connections()

        http_connectionpool_def = HttpConnectionPoolModel
        if self.get_argument_http_connection_pool_http1_max_pending_req() is not None or \
           self.get_argument_http_connection_pool_http2_max_req() is not None:
            http_connectionpool_def["http1MaxPendingRequests"] = self.get_argument_http_connection_pool_http1_max_pending_req() if self.get_argument_http_connection_pool_http1_max_pending_req() is not None else DEFAULT_HTTP1_MAX_PENDING_REQ
            http_connectionpool_def["http2MaxRequests"] = self.get_argument_http_connection_pool_http2_max_req() if self.get_argument_http_connection_pool_http2_max_req() is not None else DEFAULT_HTTP2_MAX_REQ

        self.containerapp_resiliency_def["properties"]["httpRetryPolicy"] = http_retry_def
        self.containerapp_resiliency_def["properties"]["timeoutPolicy"] = timeout_def
        self.containerapp_resiliency_def["properties"]["tcpRetryPolicy"] = tcpretry_def
        self.containerapp_resiliency_def["properties"]["circuitBreakerPolicy"] = circuitbreaker_def
        self.containerapp_resiliency_def["properties"]["tcpConnectionPool"] = tcp_connectionpool_def
        self.containerapp_resiliency_def["properties"]["httpConnectionPool"] = http_connectionpool_def

        self.containerapp_resiliency_def = clean_null_values(self.containerapp_resiliency_def)

        if self.containerapp_resiliency_def is None or self.containerapp_resiliency_def == {}:
            self.containerapp_resiliency_def["properties"] = {}

    def set_up_default_containerapp_resiliency(self):
        if self.get_argument_tcp_retry_max_connect_attempts() or self.get_argument_circuit_breaker_consecutive_errors()\
                or self.get_argument_circuit_breaker_interval() or self.get_argument_circuit_breaker_max_ejection() or \
                self.get_argument_tcp_connection_pool_max_connections() or self.get_argument_http_connection_pool_http1_max_pending_req() \
                or self.get_argument_http_connection_pool_http2_max_req() or self.get_argument_timeout_response_in_seconds() \
                or self.get_argument_timeout_connection_in_seconds() or self.get_argument_http_retry_max() \
                or self.get_argument_http_retry_delay_in_milliseconds() or self.get_argument_http_retry_interval_in_milliseconds() \
                or self.get_argument_http_retry_status_codes() or self.get_argument_http_retry_errors():
            not self.get_argument_disable_warnings() and logger.warning(
                'Additional flags were passed along with --recommended. These flags will be ignored, and recommended values will be applied.')

        timeout_def = TimeoutPolicyModel
        timeout_def["responseTimeoutInSeconds"] = DEFAULT_RESPONSE_TIMEOUT
        timeout_def["connectionTimeoutInSeconds"] = DEFAULT_CONNECTION_TIMEOUT
        self.containerapp_resiliency_def["properties"]["timeoutPolicy"] = timeout_def

        circuitbreaker_def = CircuitBreakerPolicyModel
        circuitbreaker_def["consecutiveErrors"] = DEFAULT_CONSECUTIVE_ERRORS
        circuitbreaker_def["intervalInSeconds"] = DEFAULT_INTERVAL
        circuitbreaker_def["maxEjectionPercent"] = DEFAULT_MAX_EJECTION
        self.containerapp_resiliency_def["properties"]["circuitBreakerPolicy"] = circuitbreaker_def

        http_retry_policy = {
            "maxRetries": DEFAULT_HTTP_RETRY_MAX,
            "retryBackOff": {
                "initialDelayInMilliseconds": DEFAULT_HTTP_RETRY_DELAY_IN_MILLISECONDS,
                "maxIntervalInMilliseconds": DEFAULT_HTTP_RETRY_INTERVAL_IN_MILLISECONDS
            },
            "matches": {
                "errors": DEFAULT_HTTP_RETRY_ERRORS
            }
        }
        self.containerapp_resiliency_def["properties"]["httpRetryPolicy"] = http_retry_policy


class ContainerAppResiliencyPreviewShowDecorator(ContainerAppResiliencyDecorator):
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def show(self):
        try:
            r = self.client.show(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                                 name=self.get_argument_name(), container_app_name=self.get_argument_container_app_name())
            r = clean_null_values(r)
            return r
        except Exception as e:
            handle_raw_exception(e)


class ContainerAppResiliencyPreviewListDecorator(ContainerAppResiliencyDecorator):
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def list(self):
        try:
            r = self.client.list(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                                 container_app_name=self.get_argument_container_app_name())
            r = clean_null_values(r)
            return r
        except Exception as e:
            handle_raw_exception(e)


class ContainerAppResiliencyPreviewDeleteDecorator(ContainerAppResiliencyDecorator):
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def delete(self):
        try:
            return self.client.delete(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                                      name=self.get_argument_name(), container_app_name=self.get_argument_container_app_name(),
                                      no_wait=self.get_argument_no_wait())
        except Exception as e:
            handle_raw_exception(e)


class ContainerAppResiliencyPreviewUpdateDecorator(ContainerAppResiliencyDecorator):
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)
        self.containerapp_resiliency_update_def = ContainerAppsResiliencyModel

    def construct_payload(self):
        if self.get_argument_yaml():
            self.containerapp_resiliency_update_def = self.set_up_containerapp_resiliency_yaml(file_name=self.get_argument_yaml())
            return

        containerapps_resiliency_def = None

        try:
            containerapps_resiliency_def = ContainerAppsResiliencyPreviewClient.show(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                                                                                     name=self.get_argument_name(), container_app_name=self.get_argument_container_app_name())
        except:
            pass

        if not containerapps_resiliency_def:
            raise ResourceNotFoundError("The containerapp resiliency policy '{}' does not exist".format(self.get_argument_name()))

        http_retry_def = HttpRetryPolicyModel
        if (self.get_argument_http_retry_max() is not None or
                self.get_argument_http_retry_delay_in_milliseconds() is not None or
                self.get_argument_http_retry_interval_in_milliseconds() is not None or
                self.get_argument_http_retry_status_codes() is not None or
                self.get_argument_http_retry_errors() is not None):
            http_retry_def["maxRetries"] = self.get_argument_http_retry_max() if self.get_argument_http_retry_max() is not None else safe_get(containerapps_resiliency_def, 'properties', 'httpRetryPolicy', 'maxRetries', default=DEFAULT_HTTP_RETRY_MAX)
            http_retry_def["retryBackOff"] = {
                "initialDelayInMilliseconds": self.get_argument_http_retry_delay_in_milliseconds() if self.get_argument_http_retry_delay_in_milliseconds() is not None else safe_get(containerapps_resiliency_def, 'properties', 'httpRetryPolicy', 'retryBackOff', 'initialDelayInMilliseconds', default=DEFAULT_HTTP_RETRY_DELAY_IN_MILLISECONDS),
                "maxIntervalInMilliseconds": self.get_argument_http_retry_interval_in_milliseconds() if self.get_argument_http_retry_interval_in_milliseconds() is not None else safe_get(containerapps_resiliency_def, 'properties', 'httpRetryPolicy', 'retryBackOff', 'maxIntervalInMilliseconds', default=DEFAULT_HTTP_RETRY_INTERVAL_IN_MILLISECONDS)
            }
            http_retry_def["matches"] = {
                "errors": self.get_argument_http_retry_errors() if self.get_argument_http_retry_errors() is not None else safe_get(containerapps_resiliency_def, 'properties', 'httpRetryPolicy', 'matches', 'errors', default=DEFAULT_HTTP_RETRY_ERRORS),
                "httpStatusCodes": self.get_argument_http_retry_status_codes() if self.get_argument_http_retry_status_codes() is not None else safe_get(containerapps_resiliency_def, 'properties', 'httpRetryPolicy', 'matches', 'httpStatusCodes', default=None),
                "headers": safe_get(containerapps_resiliency_def, 'properties', 'httpRetryPolicy', 'matches', 'headers', default=None)
            }

            self.containerapp_resiliency_update_def["properties"]["httpRetryPolicy"] = http_retry_def

        timeout_def = TimeoutPolicyModel
        if self.get_argument_timeout_response_in_seconds() is not None or self.get_argument_timeout_connection_in_seconds() is not None:
            timeout_def["responseTimeoutInSeconds"] = self.get_argument_timeout_response_in_seconds() if self.get_argument_timeout_response_in_seconds() is not None else safe_get(containerapps_resiliency_def, 'properties', 'timeoutPolicy', 'responseTimeoutInSeconds', default=DEFAULT_RESPONSE_TIMEOUT)
            timeout_def["connectionTimeoutInSeconds"] = self.get_argument_timeout_connection_in_seconds() if self.get_argument_timeout_connection_in_seconds() is not None else safe_get(containerapps_resiliency_def, 'properties', 'timeoutPolicy', 'connectionTimeoutInSeconds', default=DEFAULT_CONNECTION_TIMEOUT)
            self.containerapp_resiliency_update_def["properties"]["timeoutPolicy"] = timeout_def

        tcpretry_def = TcpRetryPolicyModel
        if self.get_argument_tcp_retry_max_connect_attempts() is not None:
            tcpretry_def["maxConnectAttempts"] = self.get_argument_tcp_retry_max_connect_attempts()
            self.containerapp_resiliency_update_def["properties"]["tcpRetryPolicy"] = tcpretry_def

        circuitbreaker_def = CircuitBreakerPolicyModel
        if self.get_argument_circuit_breaker_consecutive_errors() is not None or \
           self.get_argument_circuit_breaker_interval() is not None or \
           self.get_argument_circuit_breaker_max_ejection() is not None:
            circuitbreaker_def["consecutiveErrors"] = self.get_argument_circuit_breaker_consecutive_errors() if self.get_argument_circuit_breaker_consecutive_errors() is not None else safe_get(containerapps_resiliency_def, 'properties', 'circuitBreakerPolicy', 'consecutiveErrors', default=DEFAULT_CONSECUTIVE_ERRORS)
            circuitbreaker_def["intervalInSeconds"] = self.get_argument_circuit_breaker_interval() if self.get_argument_circuit_breaker_interval() is not None else safe_get(containerapps_resiliency_def, 'properties', 'circuitBreakerPolicy', 'intervalInSeconds', default=DEFAULT_INTERVAL)
            circuitbreaker_def["maxEjectionPercent"] = self.get_argument_circuit_breaker_max_ejection() if self.get_argument_circuit_breaker_max_ejection() is not None else safe_get(containerapps_resiliency_def, 'properties', 'circuitBreakerPolicy', 'maxEjectionPercent', default=DEFAULT_MAX_EJECTION)
            self.containerapp_resiliency_update_def["properties"]["circuitBreakerPolicy"] = circuitbreaker_def

        tcp_connectionpool_def = TcpConnectionPoolModel
        if self.get_argument_tcp_connection_pool_max_connections() is not None:
            tcp_connectionpool_def["maxConnections"] = self.get_argument_tcp_connection_pool_max_connections()
            self.containerapp_resiliency_update_def["properties"]["tcpConnectionPool"] = tcp_connectionpool_def

        http_connectionpool_def = HttpConnectionPoolModel
        if self.get_argument_http_connection_pool_http1_max_pending_req() is not None or \
           self.get_argument_http_connection_pool_http2_max_req() is not None:
            http_connectionpool_def["http1MaxPendingRequests"] = self.get_argument_http_connection_pool_http1_max_pending_req() if self.get_argument_http_connection_pool_http1_max_pending_req() is not None else DEFAULT_HTTP1_MAX_PENDING_REQ
            http_connectionpool_def["http2MaxRequests"] = self.get_argument_http_connection_pool_http2_max_req() if self.get_argument_http_connection_pool_http2_max_req() is not None else DEFAULT_HTTP2_MAX_REQ
            self.containerapp_resiliency_update_def["properties"]["httpConnectionPool"] = http_connectionpool_def

        self.containerapp_resiliency_update_def = clean_null_values(self.containerapp_resiliency_update_def)

    def update(self):
        try:
            if self.get_argument_yaml():
                r = self.client.create_or_update(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                                                 name=self.get_argument_name(), container_app_name=self.get_argument_container_app_name(),
                                                 container_app_resiliency_envelope=self.containerapp_resiliency_update_def,
                                                 no_wait=self.get_argument_no_wait())
            else:
                r = self.client.update(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                                       name=self.get_argument_name(), container_app_name=self.get_argument_container_app_name(),
                                       container_app_resiliency_envelope=self.containerapp_resiliency_update_def,
                                       no_wait=self.get_argument_no_wait())
            r = clean_null_values(r)
            return r
        except Exception as e:
            handle_raw_exception(e)
