# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from knack.util import CLIError
from knack.log import get_logger
from ._utils import (_get_azext_module, GA_CONTAINERAPP_EXTENSION_NAME, GA_CONTAINERAPP_EXTENSION_MODULE)

logger = get_logger(__name__)


def create_containerapp(cmd,
                        name,
                        resource_group_name,
                        yaml=None,
                        image=None,
                        container_name=None,
                        managed_env=None,
                        min_replicas=None,
                        max_replicas=None,
                        scale_rule_name=None,
                        scale_rule_type=None,
                        scale_rule_http_concurrency=None,
                        scale_rule_metadata=None,
                        scale_rule_auth=None,
                        target_port=None,
                        exposed_port=None,
                        transport="auto",
                        ingress=None,
                        revisions_mode="single",
                        secrets=None,
                        env_vars=None,
                        cpu=None,
                        memory=None,
                        registry_server=None,
                        registry_user=None,
                        registry_pass=None,
                        dapr_enabled=False,
                        dapr_app_port=None,
                        dapr_app_id=None,
                        dapr_app_protocol=None,
                        dapr_http_read_buffer_size=None,
                        dapr_http_max_request_size=None,
                        dapr_log_level=None,
                        dapr_enable_api_logging=False,
                        service_type=None,
                        service_bindings=None,
                        revision_suffix=None,
                        startup_command=None,
                        args=None,
                        tags=None,
                        no_wait=False,
                        system_assigned=False,
                        disable_warnings=False,
                        user_assigned=None,
                        registry_identity=None,
                        workload_profile_name=None,
                        secret_volume_mount=None):
    raw_parameters = locals()
    azext_custom = _get_azext_module(
        GA_CONTAINERAPP_EXTENSION_NAME, GA_CONTAINERAPP_EXTENSION_MODULE)
    try:
        return azext_custom.create_containerapp(cmd,
                                                resource_group_name,
                                                yaml,
                                                image,
                                                container_name,
                                                managed_env,
                                                min_replicas,
                                                max_replicas,
                                                scale_rule_name,
                                                scale_rule_type,
                                                scale_rule_http_concurrency,
                                                scale_rule_metadata,
                                                scale_rule_auth,
                                                target_port,
                                                exposed_port,
                                                transport,
                                                ingress,
                                                revisions_mode,
                                                secrets,
                                                env_vars,
                                                cpu,
                                                memory,
                                                registry_server,
                                                registry_user,
                                                registry_pass,
                                                dapr_enabled,
                                                dapr_app_port,
                                                dapr_app_id,
                                                dapr_app_protocol,
                                                dapr_http_read_buffer_size,
                                                dapr_http_max_request_size,
                                                dapr_log_level,
                                                dapr_enable_api_logging,
                                                service_type,
                                                service_bindings,
                                                revision_suffix,
                                                startup_command,
                                                args,
                                                tags,
                                                no_wait,
                                                system_assigned,
                                                disable_warnings,
                                                user_assigned,
                                                registry_identity,
                                                workload_profile_name,
                                                secret_volume_mount)
    except TypeError:
        raise CLIError(
            "Use 'az extension add --upgrade --name containerapp-preview' to get the latest containerapp-preview components.")
    except AttributeError as ae:
        raise CLIError(ae)
