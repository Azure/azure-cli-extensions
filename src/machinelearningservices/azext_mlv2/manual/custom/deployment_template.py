# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Dict

try:
    from azure.ai.ml.entities._load_functions import load_deployment_template
except ImportError:
    load_deployment_template = None

from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, UserErrorException, ValidationException

from .raise_error import log_and_raise_error
from .utils import (
    _dump_entity_with_warnings,
    get_ml_client,
    is_not_found_error,
    wrap_lro,
)

module_logger = logging.getLogger(__name__)
module_logger.propagate = 0
logger = logging.getLogger(__name__)


def ml_deployment_template_list(cmd, registry_name=None):
    """List deployment templates in a registry."""
    ml_client, debug = get_ml_client(
        cli_ctx=cmd.cli_ctx, registry_name=registry_name
    )
    
    try:
        deployment_templates = ml_client.deployment_templates.list()
        # Handle DeploymentTemplate serialization - try as_dict() first, then _to_dict()
        result = []
        for template in deployment_templates:
            try:
                if hasattr(template, 'as_dict'):
                    result.append(template.as_dict())
                elif hasattr(template, '_to_dict'):
                    result.append(template._to_dict())  # pylint: disable=protected-access
                else:
                    # Fallback to dict conversion
                    result.append(dict(template))
            except Exception as serialize_err:  # pylint: disable=broad-except
                module_logger.warning("Failed to serialize deployment template: %s", serialize_err)
                result.append(str(template))
        return result
    except Exception as err:  # pylint: disable=broad-except
        log_and_raise_error(err, debug)


def ml_deployment_template_get(cmd, name, version=None, registry_name=None):
    """Get a specific deployment template by name and version."""
    ml_client, debug = get_ml_client(
        cli_ctx=cmd.cli_ctx, registry_name=registry_name
    )
    
    try:
        deployment_template = ml_client.deployment_templates.get(name=name, version=version)
        # Handle DeploymentTemplate serialization
        if hasattr(deployment_template, 'as_dict'):
            return deployment_template.as_dict()
        elif hasattr(deployment_template, '_to_dict'):
            return deployment_template._to_dict()  # pylint: disable=protected-access
        else:
            return dict(deployment_template)
    except Exception as err:  # pylint: disable=broad-except
        if is_not_found_error(err):
            raise ValueError(f"Deployment template '{name}' with version '{version}' does not exist.") from err
        log_and_raise_error(err, debug)


def ml_deployment_template_create(
    cmd,
    file=None,
    name=None,
    version=None,
    registry_name=None,
    no_wait=False,
    params_override=None,
    **kwargs,  # pylint: disable=unused-argument
):
    """Create or update a deployment template."""
    ml_client, debug = get_ml_client(
        cli_ctx=cmd.cli_ctx, registry_name=registry_name
    )
    
    params_override = params_override or []
    
    try:
        if name:
            params_override.append({"name": name})
        if version:
            params_override.append({"version": version})
            
        if load_deployment_template:
            deployment_template = load_deployment_template(source=file, params_override=params_override)
        else:
            # Fallback: load YAML manually if load_deployment_template is not available
            import yaml
            if not file:
                raise ValueError("A YAML file must be provided for deployment template creation.")
                
            with open(file, 'r', encoding='utf-8') as f:
                yaml_content = yaml.safe_load(f)
            
            # Apply parameter overrides
            for override in params_override:
                if isinstance(override, dict):
                    yaml_content.update(override)
            
            deployment_template = yaml_content
            
        deployment_template_result = ml_client.deployment_templates.create_or_update(deployment_template)
        
        if no_wait:
            module_logger.warning(
                "Deployment template create/update request initiated. "
                "Status can be checked using `az ml deployment-template get -n %s -v %s`",
                deployment_template.name if hasattr(deployment_template, 'name') else name or "unknown",
                deployment_template.version if hasattr(deployment_template, 'version') else version or "unknown"
            )
            return None
        else:
            deployment_template_result = wrap_lro(cmd.cli_ctx, deployment_template_result)
            
        # Handle serialization
        if hasattr(deployment_template_result, 'as_dict'):
            return deployment_template_result.as_dict()
        elif hasattr(deployment_template_result, '_to_dict'):
            return deployment_template_result._to_dict()  # pylint: disable=protected-access
        else:
            return dict(deployment_template_result)
    except Exception as err:  # pylint: disable=broad-except
        yaml_operation = bool(file)
        log_and_raise_error(err, debug, yaml_operation=yaml_operation)


def _ml_deployment_template_update(
    cmd, registry_name=None, parameters: Dict = None
):
    """Update function for generic_update_command pattern."""
    ml_client, debug = get_ml_client(
        cli_ctx=cmd.cli_ctx, registry_name=registry_name
    )

    try:
        # Filter out internal/computed fields that cause validation errors
        # The generic_update_command passes all fields from the existing entity,
        # but many of these are internal fields that shouldn't be in a YAML template
        filtered_parameters = {}
        
        # Core fields that are typically in YAML templates
        core_fields = ['name', 'version', 'description', 'tags', 'endpoints', 'schema']
        for field in core_fields:
            if field in parameters:
                filtered_parameters[field] = parameters[field]
        
        # Add other fields that don't cause validation errors
        # Exclude fields that are typically computed/internal (both camelCase and snake_case variants)
        excluded_fields = {
            'requestSettings', 'request_settings', 'allowedInstanceType', 'allowed_instance_type', 
            'scoringPath', 'scoring_path', 'livenessProbe', 'liveness_probe',
            'environmentId', 'environment_id', 'scoringPort', 'scoring_port', 
            'modelMountPath', 'model_mount_path', 'defaultInstanceType', 'default_instance_type',
            'instanceCount', 'instance_count', 'environmentVariables', 'environment_variables', 
            'stage', 'deploymentTemplateType', 'deployment_template_type',
            'readinessProbe', 'readiness_probe', 'id', 'resourceGroup', 'resource_group', 
            'subscriptionId', 'subscription_id', 'createdTime', 'created_time',
            'modifiedTime', 'modified_time', 'createdBy', 'created_by', 'modifiedBy', 'modified_by'
        }
        
        for field, value in parameters.items():
            if field not in filtered_parameters:
                filtered_parameters[field] = value
        
        deployment_template_result = ml_client.deployment_templates.create_or_update(parameters)

        # Handle serialization
        if hasattr(deployment_template_result, 'as_dict'):
            return deployment_template_result.as_dict()
        elif hasattr(deployment_template_result, '_to_dict'):
            return deployment_template_result._to_dict()  # pylint: disable=protected-access
        else:
            return dict(deployment_template_result)
    except Exception as err:  # pylint: disable=broad-except
        log_and_raise_error(err, debug)


def _ml_deployment_template_show(cmd, name, version=None, registry_name=None):
    """Getter function for generic_update_command pattern."""
    ml_client, debug = get_ml_client(
        cli_ctx=cmd.cli_ctx, registry_name=registry_name
    )
    
    try:
        deployment_template = ml_client.deployment_templates.get(name=name, version=version)
        
        # Use to_rest_object to get proper field naming (snake_case instead of camelCase)
        if hasattr(deployment_template, 'to_rest_object'):
            return deployment_template.to_rest_object()
        elif hasattr(deployment_template, 'as_dict'):
            return deployment_template.as_dict()
        elif hasattr(deployment_template, '_to_dict'):
            return deployment_template._to_dict()  # pylint: disable=protected-access
        else:
            return dict(deployment_template)
    except Exception as err:  # pylint: disable=broad-except
        if is_not_found_error(err):
            raise ValueError(f"Deployment template '{name}' with version '{version}' does not exist.") from err
        log_and_raise_error(err, debug)


def ml_deployment_template_archive(
    cmd,
    name,
    version=None,
    registry_name=None,
    no_wait=False,
    **kwargs,  # pylint: disable=unused-argument
):
    """Archive a deployment template."""
    ml_client, debug = get_ml_client(
        cli_ctx=cmd.cli_ctx, registry_name=registry_name
    )
    
    try:
        ml_client.deployment_templates.archive(name=name, version=version)
    except Exception as err:  # pylint: disable=broad-except
        log_and_raise_error(err, debug)


def ml_deployment_template_restore(
    cmd,
    name,
    version=None,
    registry_name=None,
    no_wait=False,
    **kwargs,  # pylint: disable=unused-argument
):
    """Restore an archived deployment template."""
    ml_client, debug = get_ml_client(
        cli_ctx=cmd.cli_ctx, registry_name=registry_name
    )
    
    try:
        ml_client.deployment_templates.restore(name=name, version=version)
    except Exception as err:  # pylint: disable=broad-except
        log_and_raise_error(err, debug)



