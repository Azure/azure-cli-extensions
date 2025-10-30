# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, consider-using-f-string, no-else-return, duplicate-string-formatting-argument, expression-not-assigned, too-many-locals, logging-fstring-interpolation, arguments-differ, abstract-method, logging-format-interpolation, broad-except

from knack.log import get_logger

logger = get_logger(__name__)


def valid_resource_settings():
    # vCPU and Memory reservations
    # https://docs.microsoft.com/azure/container-apps/containers#configuration
    return {
        "0.25": "0.5",
        "0.5": "1.0",
        "0.75": "1.5",
        "1.0": "2.0",
        "1.25": "2.5",
        "1.5": "3.0",
        "1.75": "3.5",
        "2.0": "4.0",
    }


def validate_memory_and_cpu_setting(cpu, memory, managed_environment):
    # only v1 cluster do the validation
    from ._utils import safe_get
    if safe_get(managed_environment, "properties", "workloadProfiles"):
        if memory:
            return cpu, f"{memory}Gi"
        return cpu, memory

    settings = valid_resource_settings()

    if cpu in settings.keys():  # pylint: disable=C0201
        if memory != settings[cpu]:
            if memory is not None:
                warning = f"Unsupported memory reservation request of {memory}."
                warning += f"The default value of {settings[cpu]}Gi will be used."
                logger.warning(warning)
            memory = settings[cpu]
        return (cpu, f"{memory}Gi")

    if cpu is not None:
        logger.warning(  # pylint: disable=W1203
            f"Invalid CPU reservation request of {cpu}. The default resource values will be used.")
    return (None, None)


def parse_models_section(compose_yaml):
    """
    Extract models section from raw YAML compose file.
    
    Args:
        compose_yaml: Dictionary representation of compose file
        
    Returns:
        Dictionary of models configuration or empty dict if not present
    """
    from knack.log import get_logger
    logger = get_logger(__name__)
    
    models = compose_yaml.get('models', {})
    if models:
        logger.info(f"Found {len(models)} model(s) in compose file: {list(models.keys())}")
    return models


def detect_mcp_gateway_service(service_name, service):
    """
    Check if a service is an MCP gateway by examining the image name.
    
    Args:
        service_name: Name of the service
        service: Service configuration object
        
    Returns:
        Boolean indicating if this is an MCP gateway service
    """
    if not hasattr(service, 'image') or not service.image:
        return False
    
    # Check if image contains 'mcp-gateway' substring
    is_mcp_gateway = 'mcp-gateway' in service.image.lower()
    
    if is_mcp_gateway:
        from knack.log import get_logger
        logger = get_logger(__name__)
        logger.info(f"Detected MCP gateway service: {service_name} (image: {service.image})")
    
    return is_mcp_gateway


def resolve_dependency_graph(services):
    """
    Build service dependency order from depends_on relationships.
    
    Args:
        services: Dictionary of service configurations
        
    Returns:
        List of service names in dependency order (dependencies first)
    """
    from knack.log import get_logger
    logger = get_logger(__name__)
    
    # Build adjacency list for dependencies
    dependencies = {}
    for service_name, service in services.items():
        deps = []
        if hasattr(service, 'depends_on') and service.depends_on:
            if isinstance(service.depends_on, list):
                deps = service.depends_on
            elif isinstance(service.depends_on, dict):
                deps = list(service.depends_on.keys())
        dependencies[service_name] = deps
    
    # Topological sort using DFS
    visited = set()
    result = []
    
    def visit(name):
        if name in visited:
            return
        visited.add(name)
        for dep in dependencies.get(name, []):
            if dep in services:  # Only visit dependencies that exist
                visit(dep)
        result.append(name)
    
    for service_name in services.keys():
        visit(service_name)
    
    logger.info(f"Resolved service deployment order: {result}")
    return result


# ============================================================================
# Phase 3: Models Deployment Implementation
# ============================================================================

def validate_models_configuration(models):
    """
    Validate models configuration from compose file.
    
    Args:
        models: Dictionary of model configurations from compose file
        
    Returns:
        Boolean indicating if models configuration is valid
        
    Raises:
        InvalidArgumentValueError: If model names are invalid DNS labels
    """
    from knack.log import get_logger
    from azure.cli.core.azclierror import InvalidArgumentValueError
    import re
    
    logger = get_logger(__name__)
    
    if not models:
        return True
        
    # DNS label regex: lowercase alphanumeric and hyphens, start/end with alphanumeric
    dns_label_pattern = re.compile(r'^[a-z0-9]([-a-z0-9]*[a-z0-9])?$')
    
    for model_name, model_config in models.items():
        # Skip x-azure-deployment metadata
        if model_name == 'x-azure-deployment':
            continue
            
        if not dns_label_pattern.match(model_name):
            raise InvalidArgumentValueError(
                f"Invalid model name '{model_name}'. Model names must be valid DNS labels: "
                f"lowercase alphanumeric characters or hyphens, starting and ending with alphanumeric."
            )
        
        # Validate source format
        if isinstance(model_config, dict) and 'source' in model_config:
            validate_model_source(model_name, model_config['source'])
            
    logger.info(f"Validated {len(models)} model configuration(s)")
    return True


def validate_model_source(model_name, source):
    """
    Validate model source format.
    
    Args:
        model_name: Name of the model
        source: Model source string (e.g., ollama://phi, hf://model-name)
        
    Raises:
        InvalidArgumentValueError: If source format is invalid
    """
    from knack.log import get_logger
    from azure.cli.core.azclierror import InvalidArgumentValueError
    
    logger = get_logger(__name__)
    
    if not source:
        raise InvalidArgumentValueError(
            f"Model '{model_name}' missing required 'source' field"
        )
    
    valid_prefixes = ['ollama://', 'hf://', 'https://', 'azureml://']
    
    if not any(source.startswith(prefix) for prefix in valid_prefixes):
        raise InvalidArgumentValueError(
            f"Invalid source '{source}' for model '{model_name}'. "
            f"Source must start with one of: {', '.join(valid_prefixes)}"
        )
    
    logger.info(f"Validated model source for '{model_name}': {source}")


def check_gpu_profile_availability(cmd, resource_group_name, env_name, location):
    """
    Check if GPU workload profiles are available in the region.
    
    Args:
        cmd: Azure CLI command context
        resource_group_name: Resource group name
        env_name: Container Apps environment name
        location: Azure region
    
    Returns:
        List of available GPU profile types
    """
    from knack.log import get_logger
    from azure.cli.core.util import send_raw_request
    from azure.cli.core.commands.client_factory import get_subscription_id
    import json
    
    logger = get_logger(__name__)
    
    try:
        # Use Azure REST API to list supported workload profiles
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        api_version = "2024-03-01"
        
        url_fmt = "{}/subscriptions/{}/providers/Microsoft.App/locations/{}/availableManagedEnvironmentsWorkloadProfileTypes?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            location,
            api_version
        )
        
        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        response = r.json()
        
        supported_profiles = response.get('value', [])
        
        # Filter for GPU profiles
        gpu_profiles = [
            profile for profile in supported_profiles
            if 'GPU' in profile.get('name', '').upper() or
               'GPU' in profile.get('properties', {}).get('category', '').upper()
        ]
        
        if gpu_profiles:
            logger.info(f"Found {len(gpu_profiles)} GPU profile(s) in {location}")
        else:
            logger.warning(f"No GPU profiles available in {location}")
        
        return gpu_profiles
    
    except Exception as e:
        logger.warning(f"Failed to check GPU profile availability: {str(e)}")
        return []

def wait_for_environment_provisioning(cmd, resource_group_name, env_name, timeout_seconds=600):
    """
    Wait for Container Apps environment to reach 'Succeeded' provisioning state.
    
    Args:
        cmd: Azure CLI command context
        resource_group_name: Resource group name
        env_name: Container Apps environment name
        timeout_seconds: Maximum time to wait (default 600 seconds = 10 minutes)
        
    Raises:
        Exception: If environment doesn't reach Succeeded state within timeout
    """
    from knack.log import get_logger
    from ._clients import ManagedEnvironmentClient
    import time
    
    logger = get_logger(__name__)
    logger.info(f"Waiting for environment '{env_name}' to be provisioned...")
    
    start_time = time.time()
    while True:
        env = ManagedEnvironmentClient.show(cmd, resource_group_name, env_name)
        provisioning_state = env.get('properties', {}).get('provisioningState', 'Unknown')
        
        logger.info(f"Environment provisioning state: {provisioning_state}")
        
        if provisioning_state == 'Succeeded':
            logger.info(f"Environment '{env_name}' is ready")
            return
        
        if provisioning_state in ['Failed', 'Canceled']:
            raise Exception(f"Environment provisioning failed with state: {provisioning_state}")
        
        elapsed = time.time() - start_time
        if elapsed > timeout_seconds:
            raise Exception(f"Timeout waiting for environment provisioning. Current state: {provisioning_state}")
        
        logger.info(f"Waiting... (elapsed: {int(elapsed)}s, timeout: {timeout_seconds}s)")
        time.sleep(5)  # Check every 5 seconds


def create_gpu_workload_profile_if_needed(cmd, resource_group_name, env_name, location, requested_gpu_profile_type=None):
    """
    Check for existing GPU profile and create one if needed.
    
    Args:
        cmd: Azure CLI command context
        resource_group_name: Resource group name
        env_name: Container Apps environment name
        location: Azure region
        requested_gpu_profile_type: Specific GPU profile type requested (e.g., Consumption-GPU-NC8as-T4)
        
    Returns:
        Name of the GPU workload profile to use
        
    Raises:
        ResourceNotFoundError: If no GPU profiles available in region
    """
    from knack.log import get_logger
    from azure.cli.core.azclierror import ResourceNotFoundError
    from ._client_factory import handle_raw_exception
    from ._clients import ManagedEnvironmentClient
    
    logger = get_logger(__name__)
    
    # Check if environment already has a GPU profile that matches the request
    try:
        # Use class methods directly - no instantiation needed
        env = ManagedEnvironmentClient.show(cmd, resource_group_name, env_name)
        
        workload_profiles = env.get('properties', {}).get('workloadProfiles', [])
        
        # If specific GPU type requested, check if it exists
        if requested_gpu_profile_type:
            for profile in workload_profiles:
                if profile.get('workloadProfileType') == requested_gpu_profile_type:
                    logger.info(f"Found requested GPU profile in environment: {requested_gpu_profile_type}")
                    return requested_gpu_profile_type
        else:
            # No specific request, return any GPU profile found
            for profile in workload_profiles:
                profile_type = profile.get('workloadProfileType', '')
                if 'GPU' in profile_type.upper():
                    logger.info(f"Found existing GPU profile: {profile.get('name')}")
                    return profile.get('name')
    except Exception as e:
        logger.warning(f"Failed to check existing profiles: {str(e)}")
    
    # Get available GPU profiles in region
    available_gpu = check_gpu_profile_availability(cmd, resource_group_name, env_name, location)
    
    if not available_gpu:
        alternatives_msg = "GPU workload profiles are not available in this region."
        # Try to suggest nearby regions (simplified - would need proper region mapping)
        alternatives_msg += "\n\nTry deploying to regions with GPU support: westus3, eastus, northeurope"
        raise ResourceNotFoundError(alternatives_msg)
    
    # Use requested GPU profile type if provided, otherwise use first available
    if requested_gpu_profile_type:
        # Validate that requested profile is available
        # The API returns profiles with 'name' field containing the workload profile type
        available_types = [p.get('name') for p in available_gpu]
        
        # Pass through the requested type as-is - it's already the API value
        # (e.g., Consumption-GPU-NC8as-T4, Consumption-GPU-NC24-A100, Consumption, Flex)
        if requested_gpu_profile_type in available_types:
            gpu_profile_type = requested_gpu_profile_type
            logger.info(f"Using requested GPU profile type: {gpu_profile_type}")
        else:
            # Don't fall back - user explicitly requested this type
            logger.error(f"Requested GPU profile '{requested_gpu_profile_type}' not available in {location}")
            logger.error(f"Available GPU profiles: {available_types}")
            raise ResourceNotFoundError(
                f"Requested workload profile type '{requested_gpu_profile_type}' is not available in region '{location}'. "
                f"Available types: {', '.join(available_types)}"
            )
    else:
        gpu_profile_type = available_gpu[0].get('name')
        logger.info(f"No specific GPU profile requested, using: {gpu_profile_type}")
    
    # Check if it's a consumption-based GPU profile
    if gpu_profile_type.startswith('Consumption-'):
        # Consumption profiles need to be added to the environment's workloadProfiles array
        logger.info(f"Adding consumption-based GPU profile to environment: {gpu_profile_type}")
        
        from azure.cli.core.util import send_raw_request
        from azure.cli.core.commands.client_factory import get_subscription_id
        import json
        
        # Get current environment configuration
        env = ManagedEnvironmentClient.show(cmd, resource_group_name, env_name)
        
        # Check if profile already exists
        existing_profiles = env.get('properties', {}).get('workloadProfiles', [])
        for profile in existing_profiles:
            if profile.get('workloadProfileType') == gpu_profile_type:
                logger.info(f"GPU profile already exists: {gpu_profile_type}")
                # Even if profile exists, environment might still be provisioning from a previous operation
                wait_for_environment_provisioning(cmd, resource_group_name, env_name)
                return gpu_profile_type
        
        # Add the consumption GPU profile to the environment
        new_profile = {
            "name": gpu_profile_type,
            "workloadProfileType": gpu_profile_type
        }
        
        # Clean existing profiles - remove unsupported properties like enableFips
        cleaned_profiles = []
        for profile in existing_profiles:
            cleaned = {
                "name": profile.get("name"),
                "workloadProfileType": profile.get("workloadProfileType")
            }
            # Only add minimumCount/maximumCount if they exist and aren't for Consumption profile
            if not profile.get("workloadProfileType", "").startswith("Consumption"):
                if "minimumCount" in profile:
                    cleaned["minimumCount"] = profile["minimumCount"]
                if "maximumCount" in profile:
                    cleaned["maximumCount"] = profile["maximumCount"]
            cleaned_profiles.append(cleaned)
        
        cleaned_profiles.append(new_profile)
        
        # Update the environment
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        api_version = "2024-03-01"
        
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            env_name,
            api_version
        )
        
        # Update environment with new workload profile
        env_update = {
            "properties": {
                "workloadProfiles": cleaned_profiles
            },
            "location": env.get('location')
        }
        
        r = send_raw_request(cmd.cli_ctx, "PATCH", request_url, body=json.dumps(env_update))
        logger.info(f"Added GPU profile to environment: {gpu_profile_type}")
        
        # Wait for environment to be provisioned before continuing
        wait_for_environment_provisioning(cmd, resource_group_name, env_name)
        
        return gpu_profile_type
    
    profile_name = 'gpu-profile'
    
    logger.info(f"Creating GPU workload profile '{profile_name}' of type '{gpu_profile_type}'")
    
    # Create the workload profile using existing add_workload_profile function
    # Create the workload profile using Azure REST API
    try:
        from azure.cli.core.util import send_raw_request
        from azure.cli.core.commands.client_factory import get_subscription_id
        import json
        
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        api_version = "2024-03-01"
        
        # Create workload profile
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}/workloadProfiles/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            env_name,
            profile_name,
            api_version
        )
        
        profile_body = {
            "properties": {
                "workloadProfileType": gpu_profile_type,
                "minimumCount": 1,
                "maximumCount": 3
            }
        }
        
        logger.info(f"Creating workload profile at: {request_url}")
        logger.info(f"Profile body: {json.dumps(profile_body)}")
        
        r = send_raw_request(cmd.cli_ctx, "PUT", request_url, body=json.dumps(profile_body))
        
        if r.status_code >= 400:
            logger.error(f"Failed to create workload profile. Status: {r.status_code}, Response: {r.text}")
            raise Exception(f"Failed to create workload profile: {r.status_code} - {r.text}")
        
        logger.info(f"Successfully created GPU profile: {profile_name}")
        return profile_name
    except Exception as e:
        logger.error(f"Exception creating workload profile: {str(e)}")
        handle_raw_exception(e)
        raise




def create_models_container_app(cmd, resource_group_name, env_name, env_id, models, 
                                 gpu_profile_name, location):
    """
    Create the models container app with model-runner and model-runner-config containers.
    
    Args:
        cmd: Azure CLI command context
        resource_group_name: Resource group name
        env_name: Container Apps environment name
        env_id: Full resource ID of the environment
        models: Dictionary of model configurations
        gpu_profile_name: Name of the GPU workload profile
        location: Azure region
        
    Returns:
        Created container app resource
    """
    from knack.log import get_logger
    from ._clients import ManagedEnvironmentClient
    import json
    
    logger = get_logger(__name__)
    
    app_name = 'models'
    logger.info(f"Creating models container app '{app_name}' with GPU profile '{gpu_profile_name}'")
    
    # MODEL_RUNNER_URL uses localhost since model-runner and model-runner-config
    # are in the same container app (in-app communication)
    model_runner_url = "http://localhost:12434"
    logger.info(f"Model runner URL (localhost): {model_runner_url}")
    
    # Determine GPU-appropriate resources based on profile type
    # T4 GPU: 8 vCPUs, 56GB memory (NC8as_T4_v3)
    # A100 GPU: 24 vCPUs, 220GB memory (NC24ads_A100_v4)
    if 'A100' in gpu_profile_name.upper():
        gpu_cpu = 24.0
        gpu_memory = '220Gi'
        logger.info(f"Detected A100 GPU profile - setting resources to {gpu_cpu} CPU / {gpu_memory}")
    else:
        # Default to T4 resources
        gpu_cpu = 8.0
        gpu_memory = '56Gi'
        logger.info(f"Detected T4 GPU profile - setting resources to {gpu_cpu} CPU / {gpu_memory}")
    
    # Build model configuration for model-runner-config
    model_config = {
        'models': {}
    }
    for model_name, model_spec in models.items():
        # Skip x-azure-deployment metadata
        if model_name == 'x-azure-deployment':
            continue
        if isinstance(model_spec, dict):
            # Exclude x-azure-deployment from model configuration
            clean_model_spec = {k: v for k, v in model_spec.items() if k != 'x-azure-deployment'}
            model_config['models'][model_name] = clean_model_spec
        else:
            # Simple string format (just model name)
            model_config['models'][model_name] = {'source': f'ollama://{model_spec}'}
    
    # Container configuration matching successful deployment pattern
    containers = [
        {
            'name': 'model-runner',
            'image': 'docker/model-runner:latest',
            'resources': {
                'cpu': gpu_cpu,
                'memory': gpu_memory
            },
            'env': [
                {
                    'name': 'MODEL_RUNNER_PORT',
                    'value': '12434'
                },
                {
                    'name': 'MODEL_RUNNER_HOST',
                    'value': '0.0.0.0'
                },
                {
                    'name': 'MODEL_RUNNER_ENVIRONMENT',
                    'value': 'moby'
                },
                {
                    'name': 'MODEL_RUNNER_GPU',
                    'value': 'cuda'
                }
            ]
        },
        {
            'name': 'model-runner-config',
            'image': 'simon.azurecr.io/model-runner-config:09112025-1504',
            'resources': {
                'cpu': 0.5,
                'memory': '1Gi'
            },
            'env': [
                {
                    'name': 'MODEL_RUNNER_URL',
                    'value': model_runner_url  # Use localhost for in-app communication
                },
                {
                    'name': 'MODELS_CONFIG',
                    'value': json.dumps(model_config)
                },
                {
                    'name': 'CONFIGURE_ON_STARTUP', # whether to configure models on startup
                    'value': 'true'
                },
                {
                    'name': 'STARTUP_DELAY', # how long do we want to wait after startup before configuring models
                    'value': '30' # seconds
                }
            ]
        }
    ]
    
    # Check for ingress configuration in x-azure-deployment
    ingress_config = {
        'external': False,
        'targetPort': 12434,  # MODEL_RUNNER_PORT
        'transport': 'http',
        'allowInsecure': False
    }
    
    # Override with x-azure-deployment ingress settings if present
    # Check inside each model (models.gemma.x-azure-deployment)
    for model_name, model_spec in models.items():
        if isinstance(model_spec, dict) and 'x-azure-deployment' in model_spec:
            azure_deployment = model_spec.get('x-azure-deployment', {})
            if 'ingress' in azure_deployment:
                ingress_override = azure_deployment['ingress']
                if 'internal' in ingress_override:
                    ingress_config['external'] = not ingress_override['internal']
                if 'external' in ingress_override:
                    ingress_config['external'] = ingress_override['external']
                if 'allowInsecure' in ingress_override:
                    ingress_config['allowInsecure'] = ingress_override['allowInsecure']
                logger.info(f"Applied ingress overrides from model '{model_name}': {ingress_override}")
                break  # Use first model's ingress settings
    
    # Build container app definition
    container_app_def = {
        'location': location,
        'properties': {
            'environmentId': env_id,
            'workloadProfileName': gpu_profile_name,
            'configuration': {
                'ingress': ingress_config
            },
            'template': {
                'containers': containers,
                'scale': {
                    'minReplicas': 1,
                    'maxReplicas': 1
                }
            }
        }
    }
    
    # Create the container app using REST API
    try:
        from azure.cli.core.util import send_raw_request
        from azure.cli.core.commands.client_factory import get_subscription_id
        
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        api_version = "2024-03-01"
        
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/containerApps/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            app_name,
            api_version
        )
        
        r = send_raw_request(cmd.cli_ctx, "PUT", request_url, body=json.dumps(container_app_def))
        models_app = r.json()
        logger.info(f"Successfully created models container app: {app_name}")
        return models_app
    except Exception as e:
        logger.error(f"Failed to create models container app: {str(e)}")
        raise


def get_containerapp_fqdn(cmd, resource_group_name, env_name, app_name, is_external=False):
    """
    Generate Container Apps FQDN for a given app.
    
    Args:
        cmd: Azure CLI command context
        resource_group_name: Resource group name
        env_name: Container Apps environment name
        app_name: Container app name
        is_external: Whether the app has external ingress (True) or internal (False)
        
    Returns:
        FQDN string (e.g., https://myapp.internal.example.azurecontainerapps.io)
    """
    from knack.log import get_logger
    from ._clients import ManagedEnvironmentClient
    
    logger = get_logger(__name__)
    
    # Get environment to retrieve the default domain
    env = ManagedEnvironmentClient.show(cmd, resource_group_name, env_name)
    env_default_domain = env.get('properties', {}).get('defaultDomain', '')
    
    if is_external:
        # External ingress: https://<app-name>.<env-default-domain>
        fqdn = f"https://{app_name}.{env_default_domain}"
    else:
        # Internal ingress: https://<app-name>.internal.<env-default-domain>
        fqdn = f"https://{app_name}.internal.{env_default_domain}"
    
    logger.info(f"Generated FQDN for '{app_name}': {fqdn}")
    return fqdn


def inject_models_environment_variables(app_def, models_endpoint, models_list):
    """
    Inject MODELS_ENDPOINT and MODELS_AVAILABLE environment variables into a container app.
    
    Args:
        app_def: Container app definition dictionary
        models_endpoint: URL of the models service endpoint
        models_list: List of available model names
        
    Returns:
        Modified app_def with injected environment variables
    """
    from knack.log import get_logger
    
    logger = get_logger(__name__)
    
    # Get existing environment variables from first container
    containers = app_def.get('properties', {}).get('template', {}).get('containers', [])
    if not containers:
        logger.warning("No containers found in app definition")
        return app_def
    
    env_vars = containers[0].get('env', [])
    
    # Add MODELS_ENDPOINT
    models_endpoint_var = {
        'name': 'MODELS_ENDPOINT',
        'value': models_endpoint
    }
    env_vars.append(models_endpoint_var)
    
    # Add MODELS_AVAILABLE (comma-separated list)
    models_available_var = {
        'name': 'MODELS_AVAILABLE',
        'value': ','.join(models_list)
    }
    env_vars.append(models_available_var)
    
    containers[0]['env'] = env_vars
    logger.info(f"Injected models environment variables: {models_endpoint}, {len(models_list)} model(s)")
    
    return app_def


# ============================================================================
# Phase 4: MCP Gateway Implementation
# ============================================================================

def get_mcp_gateway_configuration(service):
    """
    Extract MCP gateway configuration from compose service.
    
    Args:
        service: Compose service object
        
    Returns:
        Dictionary with gateway configuration settings
    """
    from knack.log import get_logger
    
    logger = get_logger(__name__)
    
    config = {
        'port': 8811,  # Standard MCP gateway port
        'ingress_type': 'internal',  # MCP gateway should be internal-only
        'image': service.image if hasattr(service, 'image') else 'mcr.microsoft.com/mcp-gateway:latest'
    }
    
    # Check for custom port in service ports
    if hasattr(service, 'ports') and service.ports:
        if isinstance(service.ports, list) and len(service.ports) > 0:
            # Port object has 'target' (internal) and 'published' (external) attributes
            port_obj = service.ports[0]
            if hasattr(port_obj, 'target'):
                # Use target (internal container port) for ingress
                config['port'] = int(port_obj.target)
            elif hasattr(port_obj, 'published'):
                config['port'] = int(port_obj.published)
            else:
                # Fallback: parse as string, removing /tcp suffix
                port_str = str(port_obj).split('/')[0]  # Remove /tcp suffix
                if ':' in port_str:
                    config['port'] = int(port_str.split(':')[-1])
                else:
                    config['port'] = int(port_str)
    
    logger.info(f"MCP Gateway configuration: port={config['port']}, ingress={config['ingress_type']}")
    return config


def enable_managed_identity(cmd, resource_group_name, app_name):
    """
    Enable system-assigned managed identity for a container app.
    
    Args:
        cmd: Azure CLI command context
        resource_group_name: Resource group name
        app_name: Container app name
        
    Returns:
        Dictionary with identity information including principal_id
    """
    from knack.log import get_logger
    from ._clients import ContainerAppClient
    
    logger = get_logger(__name__)
    
    logger.info(f"Enabling system-assigned managed identity for '{app_name}'")
    
    try:
        # Get current app using show classmethod
        app = ContainerAppClient.show(cmd, resource_group_name, app_name)
        
        # Set identity type to SystemAssigned
        if 'identity' not in app:
            app['identity'] = {}
        
        app['identity']['type'] = 'SystemAssigned'
        
        # Update the app using create_or_update classmethod
        updated_app = ContainerAppClient.create_or_update(cmd, resource_group_name, app_name, app)
        
        identity = updated_app.get('identity', {})
        principal_id = identity.get('principalId')
        
        if principal_id:
            logger.info(f"Successfully enabled managed identity. Principal ID: {principal_id}")
        else:
            logger.warning("Managed identity enabled but principal ID not yet available")
        
        return identity
        
    except Exception as e:
        logger.error(f"Failed to enable managed identity: {str(e)}")
        raise


def attempt_role_assignment(cmd, principal_id, resource_group_name, app_name):
    """
    Attempt to assign Container Apps Contributor role to managed identity at resource group scope.
    This allows the MCP gateway to modify container apps to add MCP server containers.
    
    Args:
        cmd: Azure CLI command context
        principal_id: Principal ID of the managed identity
        resource_group_name: Resource group name
        app_name: Container app name
        
    Returns:
        Boolean indicating if assignment succeeded
    """
    from knack.log import get_logger
    from azure.cli.core.commands.client_factory import get_subscription_id
    
    logger = get_logger(__name__)
    
    # Use the specific role definition ID for container app management
    # This role allows the MCP gateway to modify container apps
    role_definition_id = "/subscriptions/30501c6c-81f6-41ac-a388-d29cf43a020d/providers/Microsoft.Authorization/roleDefinitions/358470bc-b998-42bd-ab17-a7e34c199c0f"
    
    # Build scope - resource group level
    subscription_id = get_subscription_id(cmd.cli_ctx)
    scope = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}"
    
    logger.info(f"Attempting to assign role to principal {principal_id}")
    logger.info(f"Scope: Resource Group '{resource_group_name}'")
    
    try:
        # Import role assignment function
        from azure.cli.command_modules.role.custom import create_role_assignment
        
        # Attempt role assignment using the full role definition ID
        create_role_assignment(
            cmd,
            role=role_definition_id,
            assignee_object_id=principal_id,
            scope=scope,
            assignee_principal_type='ServicePrincipal'
        )
        
        logger.info(f"✅ Successfully assigned role to '{app_name}' managed identity")
        return True
        
    except Exception as e:
        # Log warning with manual assignment instructions
        logger.warning("━" * 70)
        logger.warning(f"⚠️  Could not automatically assign role: {str(e)}")
        logger.warning("")
        logger.warning("To manually assign the role, run:")
        logger.warning(f"  az role assignment create \\")
        logger.warning(f"    --role '{role_definition_id}' \\")
        logger.warning(f"    --assignee-object-id {principal_id} \\")
        logger.warning(f"    --assignee-principal-type ServicePrincipal \\")
        logger.warning(f"    --scope {scope}")
        logger.warning("━" * 70)
        
        return False


def inject_mcp_gateway_environment_variables(app_def, subscription_id, resource_group_name, app_name):
    """
    Inject MCP gateway-specific environment variables into the container app.
    
    Args:
        app_def: Container app definition dictionary
        subscription_id: Azure subscription ID
        resource_group_name: Resource group name
        app_name: Container app name
        
    Returns:
        Modified app_def with injected environment variables
    """
    from knack.log import get_logger
    
    logger = get_logger(__name__)
    
    # Get existing environment variables from first container
    containers = app_def.get('properties', {}).get('template', {}).get('containers', [])
    if not containers:
        logger.warning("No containers found in MCP gateway app definition")
        return app_def
    
    env_vars = containers[0].get('env', [])
    
    # Add MCP runtime identifier
    env_vars.append({
        'name': 'MCP_RUNTIME',
        'value': 'ACA'
    })
    
    # Add Azure context variables
    env_vars.append({
        'name': 'AZURE_SUBSCRIPTION_ID',
        'value': subscription_id
    })
    
    env_vars.append({
        'name': 'AZURE_RESOURCE_GROUP',
        'value': resource_group_name
    })
    
    env_vars.append({
        'name': 'AZURE_APP_NAME',
        'value': app_name
    })
    
    containers[0]['env'] = env_vars
    logger.info(f"Injected MCP gateway environment variables for '{app_name}'")
    
    return app_def


def inject_gateway_url_to_dependents(app_def, gateway_url):
    """
    Inject MCP_GATEWAY_URL environment variable to services that depend on MCP gateway.
    
    Args:
        app_def: Container app definition dictionary
        gateway_url: URL of the MCP gateway service
        
    Returns:
        Modified app_def with injected MCP_GATEWAY_URL
    """
    from knack.log import get_logger
    
    logger = get_logger(__name__)
    
    # Get existing environment variables from first container
    containers = app_def.get('properties', {}).get('template', {}).get('containers', [])
    if not containers:
        logger.warning("No containers found in app definition")
        return app_def
    
    env_vars = containers[0].get('env', [])
    
    # Add MCP_GATEWAY_URL
    env_vars.append({
        'name': 'MCP_GATEWAY_URL',
        'value': gateway_url
    })
    
    containers[0]['env'] = env_vars
    logger.info(f"Injected MCP_GATEWAY_URL: {gateway_url}")
    
    return app_def


# ============================================================================
# Phase 5: Dry-Run Mode Functions
# ============================================================================

def collect_dry_run_service_config(service_name, service, image=None, ingress_type=None, target_port=None,
                                      cpu=None, memory=None, environment=None, replicas=None, is_models_service=False, is_mcp_gateway=False, gpu_type=None, raw_service=None, models_config=None):
    """Collect service configuration for dry-run preview"""
    # Extract x-azure-deployment overrides
    # Use raw_service (YAML dict) if provided, otherwise use service object
    service_for_parse = raw_service if raw_service is not None else service
    overrides = parse_x_azure_deployment(service_for_parse)

    # Use x-azure-deployment overrides first, then parameters, then defaults
    # Service is a pycomposefile Service object, not a dict
    service_image = getattr(service, 'image', None)
    service_ports = getattr(service, 'ports', None)
    service_env = getattr(service, 'environment', None)
    service_depends_on = getattr(service, 'depends_on', None)
    service_command = getattr(service, 'command', None)

    # Get image with override priority (x-azure-deployment takes highest precedence)
    final_image = overrides.get('image') or image or service_image or 'Not specified'
    
    # Determine ingress enabled and type (x-azure-deployment takes highest precedence)
    ingress_enabled = service_ports is not None or overrides.get('ingress_type') is not None
    
    # Priority: x-azure-deployment override > parameter > default based on ports
    if overrides.get('ingress_type') is not None:
        final_ingress_type = overrides['ingress_type']
    elif ingress_type is not None:
        final_ingress_type = ingress_type
    elif service_ports:
        final_ingress_type = 'internal'  # Default to internal if ports exist
    else:
        final_ingress_type = None
    
    # Get target port from override or parameter
    final_target_port = overrides.get('target_port') or target_port
    
    # Get CPU and memory from overrides or parameters
    final_cpu = overrides.get('cpu') or cpu
    final_memory = overrides.get('memory') or memory
    
    # Get replica counts from overrides
    min_replicas = overrides.get('min_replicas')
    max_replicas = overrides.get('max_replicas')

    # Collect environment variables (handle both dict and string formats, avoid duplicates)
    env_vars = []
    env_var_names = set()  # Track names to avoid duplicates
    
    # Helper to add env var and track names
    def add_env_var(var):
        if isinstance(var, dict) and 'name' in var and 'value' in var:
            var_str = f"{var['name']}={var['value']}"
            var_name = var['name']
        elif isinstance(var, str):
            var_str = var
            var_name = var.split('=')[0] if '=' in var else var
        else:
            return  # Skip invalid format
        
        if var_name not in env_var_names:
            env_vars.append(var_str)
            env_var_names.add(var_name)
    
    # First add from service definition (compose file)
    if service_env:
        if isinstance(service_env, dict):
            for k, v in service_env.items():
                add_env_var(f"{k}={v}")
        elif isinstance(service_env, list):
            for var in service_env:
                add_env_var(var)
    
    # Then add from environment parameter (injected vars, these can override)
    if environment:
        for var in environment:
            if isinstance(var, dict) and 'name' in var:
                # For dict format, allow override by removing old value first
                var_name = var['name']
                if var_name in env_var_names:
                    # Remove old value
                    env_vars = [v for v in env_vars if not v.startswith(f"{var_name}=")]
                    env_var_names.discard(var_name)
            add_env_var(var)

    # Collect depends_on
    depends_on = []
    if service_depends_on:
        if isinstance(service_depends_on, list):
            depends_on = service_depends_on
        elif isinstance(service_depends_on, dict):
            depends_on = list(service_depends_on.keys())

    # Collect command
    command = []
    if service_command:
        if isinstance(service_command, list):
            command = service_command
        elif isinstance(service_command, str):
            command = [service_command]

    # Check for models reference in raw_service and resolve paths
    models_ref = []
    if raw_service and isinstance(raw_service, dict):
        service_models = raw_service.get('models')
        if service_models and isinstance(service_models, dict):
            # Resolve model names to paths using models_config
            for model_name in service_models.keys():
                if models_config and model_name in models_config:
                    model_info = models_config[model_name]
                    if isinstance(model_info, dict) and 'model' in model_info:
                        model_path = model_info['model']
                        models_ref.append(f"{model_name} ({model_path})")
                        
                        # Add environment variables for this model
                        model_env = service_models[model_name]
                        if isinstance(model_env, dict):
                            endpoint_var = model_env.get('endpoint_var')
                            model_var = model_env.get('model_var')
                            if endpoint_var:
                                env_vars.append(f"{endpoint_var}=https://<model-runner-ingress-url>/<model-specific-url>")
                            if model_var:
                                env_vars.append(f"{model_var}={model_path}")
                    elif isinstance(model_info, str):
                        models_ref.append(f"{model_name} ({model_info})")

    config = {
        'service_name': service_name,
        'image': final_image,
        'ingress_enabled': ingress_enabled,
        'ingress_type': final_ingress_type,
        'target_port': final_target_port,
        'cpu': final_cpu,
        'memory': final_memory,
        'min_replicas': min_replicas,
        'max_replicas': max_replicas,
        'environment': env_vars,
        'depends_on': depends_on,
        'command': command,
        'models': models_ref,
        'is_models_service': is_models_service,
        'is_mcp_gateway': is_mcp_gateway
    }

    return config

def parse_x_azure_deployment(service):
    """
    Parse x-azure-deployment custom extension from compose service.

    Supports overrides for:
    - cpu: Custom CPU allocation
    - memory: Custom memory allocation
    - min_replicas: Minimum replica count
    - max_replicas: Maximum replica count
    - ingress: Ingress type override
    - managed_identity: Managed identity configuration

    Args:
        service: Service object from parsed compose file OR raw dict from YAML

    Returns:
        Dictionary containing override values, or empty dict if no overrides
    """
    overrides = {}

    # Handle both Service objects and raw dicts
    if isinstance(service, dict):
        # Raw dict from YAML
        x_azure = service.get('x-azure-deployment')
    elif hasattr(service, 'x_azure_deployment'):
        # Service object
        x_azure = service.x_azure_deployment
    else:
        return overrides
    
    if not x_azure:
        return overrides

    # Parse image override
    if 'image' in x_azure:
        overrides['image'] = str(x_azure['image'])

    # Parse resources (cpu and memory can be at top level OR nested under 'resources')
    resources = x_azure.get('resources', {})
    if 'cpu' in resources:
        overrides['cpu'] = resources['cpu']  # Don't convert to string, keep as float/int
    elif 'cpu' in x_azure:
        overrides['cpu'] = x_azure['cpu']
    
    if 'memory' in resources:
        overrides['memory'] = str(resources['memory'])
    elif 'memory' in x_azure:
        overrides['memory'] = str(x_azure['memory'])

    # Parse replica overrides
    if 'min_replicas' in x_azure:
        overrides['min_replicas'] = int(x_azure['min_replicas'])

    if 'max_replicas' in x_azure:
        overrides['max_replicas'] = int(x_azure['max_replicas'])

    # Parse ingress override
    if 'ingress' in x_azure:
        ingress_config = x_azure['ingress']
        if isinstance(ingress_config, dict):
            # Handle 'external: true/false' format
            if 'external' in ingress_config:
                overrides['ingress_type'] = 'external' if ingress_config['external'] else 'internal'
            # Handle 'internal: true/false' format
            elif 'internal' in ingress_config:
                overrides['ingress_type'] = 'internal' if ingress_config['internal'] else 'external'
            # Handle 'type' field
            elif 'type' in ingress_config:
                overrides['ingress_type'] = ingress_config['type']
            # Handle port
            if 'port' in ingress_config:
                overrides['target_port'] = int(ingress_config['port'])
        elif isinstance(ingress_config, str):
            overrides['ingress_type'] = ingress_config

    # Parse managed identity override
    if 'managed_identity' in x_azure:
        overrides['managed_identity'] = x_azure['managed_identity']

    return overrides
def apply_resource_overrides(cpu, memory, min_replicas, max_replicas, overrides):
    """
    Apply x-azure-deployment overrides to resource configuration.
    
    Args:
        cpu: Default CPU value
        memory: Default memory value
        min_replicas: Default min replicas
        max_replicas: Default max replicas
        overrides: Dictionary from parse_x_azure_deployment
        
    Returns:
        Tuple of (cpu, memory, min_replicas, max_replicas) with overrides applied
    """
    final_cpu = overrides.get('cpu', cpu)
    final_memory = overrides.get('memory', memory)
    final_min_replicas = overrides.get('min_replicas', min_replicas)
    final_max_replicas = overrides.get('max_replicas', max_replicas)
    
    return final_cpu, final_memory, final_min_replicas, final_max_replicas


def apply_ingress_overrides(ingress_type, target_port, overrides):
    """
    Apply x-azure-deployment ingress overrides.
    
    Args:
        ingress_type: Default ingress type
        target_port: Default target port
        overrides: Dictionary from parse_x_azure_deployment
        
    Returns:
        Tuple of (ingress_type, target_port) with overrides applied
    """
    final_ingress_type = overrides.get('ingress_type', ingress_type)
    final_target_port = overrides.get('target_port', target_port)
    
    return final_ingress_type, final_target_port


def validate_x_azure_overrides(overrides, service_name, logger):
    """
    Validate x-azure-deployment overrides and log warnings for invalid values.
    
    Args:
        overrides: Dictionary from parse_x_azure_deployment
        service_name: Name of the service
        logger: Logger instance
        
    Returns:
        True if all overrides are valid, False otherwise
    """
    valid = True
    
    # Validate CPU
    if 'cpu' in overrides:
        cpu = overrides['cpu']
        try:
            cpu_float = float(cpu)
            if cpu_float <= 0 or cpu_float > 4:
                logger.warning(f"Service '{service_name}': Invalid CPU '{cpu}' (must be 0.25-4.0)")
                valid = False
        except ValueError:
            logger.warning(f"Service '{service_name}': Invalid CPU format '{cpu}'")
            valid = False
    
    # Validate memory
    if 'memory' in overrides:
        memory = overrides['memory']
        if not (memory.endswith('Gi') or memory.endswith('G')):
            logger.warning(f"Service '{service_name}': Memory '{memory}' should end with 'Gi' or 'G'")
            valid = False
    
    # Validate replicas
    if 'min_replicas' in overrides:
        min_rep = overrides['min_replicas']
        if min_rep < 0 or min_rep > 30:
            logger.warning(f"Service '{service_name}': min_replicas '{min_rep}' out of range (0-30)")
            valid = False
    
    if 'max_replicas' in overrides:
        max_rep = overrides['max_replicas']
        if max_rep < 1 or max_rep > 30:
            logger.warning(f"Service '{service_name}': max_replicas '{max_rep}' out of range (1-30)")
            valid = False
    
    # Validate min <= max
    if 'min_replicas' in overrides and 'max_replicas' in overrides:
        if overrides['min_replicas'] > overrides['max_replicas']:
            logger.warning(f"Service '{service_name}': min_replicas cannot exceed max_replicas")
            valid = False
    
    # Validate ingress type
    if 'ingress_type' in overrides:
        ingress = overrides['ingress_type'].lower()
        if ingress not in ['external', 'internal']:
            logger.warning(f"Service '{service_name}': Invalid ingress type '{ingress}' (use 'external' or 'internal')")
            valid = False
    
    return valid


def log_applied_overrides(service_name, overrides, logger):
    """
    Log which x-azure-deployment overrides were applied.
    
    Args:
        service_name: Name of the service
        overrides: Dictionary from parse_x_azure_deployment
        logger: Logger instance
    """
    if not overrides:
        return
    
    logger.info(f"Service '{service_name}': Applying x-azure-deployment overrides:")
    
    if 'cpu' in overrides:
        logger.info(f"  - CPU: {overrides['cpu']}")
    
    if 'memory' in overrides:
        logger.info(f"  - Memory: {overrides['memory']}")
    
    if 'min_replicas' in overrides:
        logger.info(f"  - Min Replicas: {overrides['min_replicas']}")
    
    if 'max_replicas' in overrides:
        logger.info(f"  - Max Replicas: {overrides['max_replicas']}")
    
    if 'ingress_type' in overrides:
        logger.info(f"  - Ingress Type: {overrides['ingress_type']}")
    
    if 'target_port' in overrides:
        logger.info(f"  - Target Port: {overrides['target_port']}")
    
    if 'managed_identity' in overrides:
        logger.info(f"  - Managed Identity: {overrides['managed_identity']}")



# ============================================================================
# Phase 7: Declarative Update Strategy Functions
# ============================================================================

def check_containerapp_exists(cmd, resource_group_name, app_name):
    """
    Check if a container app already exists.
    
    Args:
        cmd: Command context
        resource_group_name: Resource group name
        app_name: Container app name
        
    Returns:
        Existing containerapp object if it exists, None otherwise
    """
    from azure.core.exceptions import ResourceNotFoundError
    
    try:
        existing_app = ContainerAppClient.show(cmd, resource_group_name=resource_group_name, name=app_name)
        return existing_app
    except ResourceNotFoundError:
        return None
    except Exception:
        return None


def detect_configuration_changes(existing_app, new_config):
    """
    Detect changes between existing and new container app configuration.
    
    Args:
        existing_app: Existing container app object
        new_config: Dictionary with new configuration
        
    Returns:
        Dictionary describing detected changes
    """
    changes = {
        'has_changes': False,
        'image_changed': False,
        'env_vars_changed': False,
        'replicas_changed': False,
        'resources_changed': False,
        'ingress_changed': False
    }
    
    if not existing_app:
        changes['has_changes'] = True
        return changes
    
    # Check image change
    if hasattr(existing_app, 'properties'):
        props = existing_app.properties
        
        # Image change
        if hasattr(props, 'template') and hasattr(props.template, 'containers'):
            if props.template.containers and len(props.template.containers) > 0:
                existing_image = props.template.containers[0].image
                new_image = new_config.get('image', '')
                if existing_image != new_image:
                    changes['image_changed'] = True
                    changes['has_changes'] = True
        
        # Replica change
        if hasattr(props, 'template') and hasattr(props.template, 'scale'):
            existing_min = getattr(props.template.scale, 'minReplicas', 0)
            existing_max = getattr(props.template.scale, 'maxReplicas', 1)
            new_min = new_config.get('min_replicas', 1)
            new_max = new_config.get('max_replicas', 1)
            
            if existing_min != new_min or existing_max != new_max:
                changes['replicas_changed'] = True
                changes['has_changes'] = True
        
        # Resource change (CPU/Memory)
        if hasattr(props, 'template') and hasattr(props.template, 'containers'):
            if props.template.containers and len(props.template.containers) > 0:
                container = props.template.containers[0]
                if hasattr(container, 'resources'):
                    existing_cpu = getattr(container.resources, 'cpu', '0.5')
                    existing_memory = getattr(container.resources, 'memory', '1.0Gi')
                    new_cpu = new_config.get('cpu', '0.5')
                    new_memory = new_config.get('memory', '1.0Gi')
                    
                    if str(existing_cpu) != str(new_cpu) or str(existing_memory) != str(new_memory):
                        changes['resources_changed'] = True
                        changes['has_changes'] = True
    
    return changes


def update_containerapp_from_compose(cmd, resource_group_name, app_name, 
                                     image=None, env_vars=None, cpu=None, 
                                     memory=None, min_replicas=None, max_replicas=None,
                                     logger=None):
    """
    Update an existing container app with new configuration.
    
    Args:
        cmd: Command context
        resource_group_name: Resource group name
        app_name: Container app name
        image: New container image (optional)
        env_vars: New environment variables (optional)
        cpu: New CPU allocation (optional)
        memory: New memory allocation (optional)
        min_replicas: New min replicas (optional)
        max_replicas: New max replicas (optional)
        logger: Logger instance
        
    Returns:
        Updated containerapp object
    """
    from azure.cli.command_modules.containerapp.custom import update_containerapp
    
    if logger:
        logger.info(f"Updating existing container app: {app_name}")
    
    # Build update arguments
    update_args = {
        'cmd': cmd,
        'name': app_name,
        'resource_group_name': resource_group_name
    }
    
    if image:
        update_args['image'] = image
    
    if env_vars:
        update_args['set_env_vars'] = env_vars
    
    if cpu:
        update_args['cpu'] = cpu
    
    if memory:
        update_args['memory'] = memory
    
    if min_replicas is not None:
        update_args['min_replicas'] = min_replicas
    
    if max_replicas is not None:
        update_args['max_replicas'] = max_replicas
    
    # Perform update
    try:
        updated_app = update_containerapp(**update_args)
        if logger:
            logger.info(f"Successfully updated container app: {app_name}")
        return updated_app
    except Exception as e:
        if logger:
            logger.error(f"Failed to update container app '{app_name}': {str(e)}")
        raise


def log_update_detection(service_name, changes, logger):
    """
    Log detected changes for a container app update.
    
    Args:
        service_name: Name of the service
        changes: Dictionary from detect_configuration_changes
        logger: Logger instance
    """
    if not changes['has_changes']:
        logger.info(f"Service '{service_name}': No changes detected - skipping update")
        return
    
    logger.info(f"Service '{service_name}': Detected changes:")
    
    if changes['image_changed']:
        logger.info(f"  - Container image changed")
    
    if changes['env_vars_changed']:
        logger.info(f"  - Environment variables changed")
    
    if changes['replicas_changed']:
        logger.info(f"  - Replica configuration changed")
    
    if changes['resources_changed']:
        logger.info(f"  - Resource allocation (CPU/Memory) changed")
    
    if changes['ingress_changed']:
        logger.info(f"  - Ingress configuration changed")


# Dry-run print functions (stubs for now - can be enhanced later)
def print_dry_run_header(compose_file_path, resource_group_name, managed_env_name):
    """Print dry-run header"""
    print("\n" + "="*80)
    print("DRY-RUN MODE: Deployment Preview")
    print("="*80 + "\n")
    print(f"Compose File:          {compose_file_path}")
    print(f"Resource Group:        {resource_group_name}")
    print(f"Managed Environment:   {managed_env_name}")
    print("\nNote: No resources will be created. This is a preview only.\n")

def print_dry_run_service_plan(service_name, service_config):
    """Print dry-run service plan"""
    print(f"\nService: {service_name}")
    print("-" * 60)
    
    # Always show image
    if 'image' in service_config and service_config['image']:
        print(f"  Image: {service_config['image']}")
    
    # Show ingress if enabled or if type is specified
    ingress_type = service_config.get('ingress_type')
    if service_config.get('ingress_enabled') or ingress_type:
        if ingress_type:
            print(f"  Ingress: {ingress_type}")
        
        # Show target port if specified
        target_port = service_config.get('target_port')
        if target_port:
            print(f"  Target Port: {target_port}")
            # Show allow insecure if target port is set
            print(f"  Allow Insecure: true")
    
    # Show environment variables
    env_vars = service_config.get('environment', [])
    if env_vars:
        print(f"  Environment Variables:")
        for env_var in env_vars:
            print(f"    - {env_var}")
    
    # Show depends_on
    depends_on = service_config.get('depends_on', [])
    if depends_on:
        # Format as comma-separated string or single value
        if len(depends_on) == 1:
            print(f"  Depends On: {depends_on[0]}")
        else:
            print(f"  Depends On: {', '.join(depends_on)}")
    
    # Show models reference
    models = service_config.get('models', [])
    if models:
        print(f"  Models:")
        for model in models:
            print(f"    - {model}")
    
    # Show command
    command = service_config.get('command', [])
    if command:
        print(f"  Command:")
        for cmd in command:
            print(f"    - {cmd}")
    
    # Show CPU
    cpu = service_config.get('cpu')
    if cpu:
        print(f"  CPU: {cpu}")
    
    # Show memory with proper formatting
    memory = service_config.get('memory')
    if memory:
        # Add Gi suffix if it's a number
        if isinstance(memory, (int, float)):
            print(f"  Memory: {memory}Gi")
        elif isinstance(memory, str) and not memory.endswith('Gi'):
            print(f"  Memory: {memory}Gi")
        else:
            print(f"  Memory: {memory}")
    
    # Show replica counts
    min_replicas = service_config.get('min_replicas')
    max_replicas = service_config.get('max_replicas')
    if min_replicas is not None:
        print(f"  Min Replicas: {min_replicas}")
    if max_replicas is not None:
        print(f"  Max Replicas: {max_replicas}")

def print_dry_run_models_deployment(models_config, gpu_profile_info):
    """Print dry-run models deployment"""
    print("\nModels Deployment Preview")
    print("="*80)

    # Container App name
    print(f"  Container App: models")
    
    # Image
    print(f"  Image: docker/model-runner:latest")
    
    # Show model names and paths (filter out x-azure-* keys)
    model_names = [k for k in models_config.keys() if not k.startswith('x-')]
    if model_names:
        print(f"  Models:")
        for model_name in model_names:
            model_info = models_config[model_name]
            if isinstance(model_info, dict) and 'model' in model_info:
                print(f"    - {model_name}: {model_info['model']}")
            elif isinstance(model_info, str):
                print(f"    - {model_name}: {model_info}")

    # Show GPU workload profile
    if gpu_profile_info and 'type' in gpu_profile_info:
        print(f"  Workload Profile: {gpu_profile_info['type']}")
    
    # Ingress is always internal for models
    print(f"  Ingress: internal")

def print_dry_run_mcp_gateway(gateway_config):
    """Print dry-run MCP gateway"""
    print("\nMCP Gateway Preview")
    print("="*80)
    if 'service_name' in gateway_config:
        print(f"  Gateway: {gateway_config['service_name']}")

def print_dry_run_summary(total_services=0, has_models=False, has_gateway=False):
    """Print dry-run summary"""
    print("\n" + "="*80)
    print("Deployment Summary")
    print("="*80)
    print(f"Total Services: {total_services}")
    print(f"Has Models: {has_models}")
    print(f"Has MCP Gateway: {has_gateway}")
    print("="*80)
