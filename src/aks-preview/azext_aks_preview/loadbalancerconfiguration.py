# pylint: disable=too-many-lines
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger
from azure.cli.core.azclierror import (
    RequiredArgumentMissingError, ResourceNotFoundError,
    BadRequestError, AzureInternalError
)
from azure.cli.core.util import CLIError
from .vendored_sdks.azure_mgmt_preview_aks.models import RebalanceLoadBalancersRequestBody

from azext_aks_preview._client_factory import CUSTOM_MGMT_AKS_PREVIEW

logger = get_logger(__name__)


def aks_loadbalancer_update_internal(cmd, client, raw_parameters):
    resource_group_name = raw_parameters.get("resource_group_name")
    cluster_name = raw_parameters.get("cluster_name")
    loadbalancer_name = raw_parameters.get("name")
    aks_custom_headers = raw_parameters.get("aks_custom_headers")

    # Get custom headers if provided
    from azext_aks_preview.custom import get_aks_custom_headers
    headers = get_aks_custom_headers(aks_custom_headers)

    # Check if the LoadBalancer exists before updating
    existing_loadbalancers = client.list_by_managed_cluster(
        resource_group_name, cluster_name
    )
    existing_lb = None
    for lb in existing_loadbalancers:
        if lb.name == loadbalancer_name:
            existing_lb = lb
            break

    if not existing_lb:
        raise ResourceNotFoundError(
            f"Load balancer configuration '{loadbalancer_name}' not found. "
            "Use 'aks loadbalancer list' to get current list of load balancer configurations."
        )

    # Track what fields are being updated
    changes_requested = False

    # Extract parameters from raw_parameters, falling back to existing values
    primary_agent_pool_name = raw_parameters.get("primary_agent_pool_name")
    if primary_agent_pool_name:
        if (
            primary_agent_pool_name.lower()
            != existing_lb.primary_agent_pool_name.lower()
        ):
            raise BadRequestError(
                f"Cannot change primary agent pool name for load balancer configuration '{loadbalancer_name}'."
            )
    else:
        # Use existing value
        primary_agent_pool_name = existing_lb.primary_agent_pool_name

    # Allow service placement parameter
    allow_service_placement = raw_parameters.get("allow_service_placement")
    if allow_service_placement is not None:
        changes_requested = changes_requested or (
            allow_service_placement != existing_lb.allow_service_placement
        )
    else:
        # Use existing value
        allow_service_placement = existing_lb.allow_service_placement

    # Process selectors
    # Check for service_label_selector
    service_label_selector_param = raw_parameters.get("service_label_selector")
    if service_label_selector_param is not None:
        service_label_selector = construct_label_selector(cmd, service_label_selector_param)
        changes_requested = True
    else:
        service_label_selector = existing_lb.service_label_selector

    # Check for service_namespace_selector
    service_namespace_selector_param = raw_parameters.get("service_namespace_selector")
    if service_namespace_selector_param is not None:
        service_namespace_selector = construct_label_selector(cmd, service_namespace_selector_param)
        changes_requested = True
    else:
        service_namespace_selector = existing_lb.service_namespace_selector

    # Check for node_selector
    node_selector_param = raw_parameters.get("node_selector")
    if node_selector_param is not None:
        node_selector = construct_label_selector(cmd, node_selector_param)
        changes_requested = True
    else:
        node_selector = existing_lb.node_selector

    # Error if no changes are requested
    if not changes_requested:
        raise BadRequestError(
            f"No changes requested for load balancer configuration '{loadbalancer_name}'. "
            "Specify at least one property to update."
        )

    # Load the LoadBalancer model class
    LoadBalancer = cmd.get_models(
        "LoadBalancer",
        resource_type=CUSTOM_MGMT_AKS_PREVIEW,
        operation_group="load_balancers",
    )

    # Create the LoadBalancer object with updated or existing values
    config = LoadBalancer(
        primary_agent_pool_name=primary_agent_pool_name,
        allow_service_placement=allow_service_placement,
        service_label_selector=service_label_selector,
        service_namespace_selector=service_namespace_selector,
        node_selector=node_selector,
    )

    # Call create_or_update with the LoadBalancer object
    client.create_or_update(
        resource_group_name=resource_group_name,
        resource_name=cluster_name,
        load_balancer_name=loadbalancer_name,
        parameters=config,
        headers=headers,
    )

    # Wait for the load balancer to be provisioned and return the latest state
    return wait_for_loadbalancer_provisioning_state(
        client, resource_group_name, cluster_name, loadbalancer_name
    )


def aks_loadbalancer_add_internal(cmd, client, raw_parameters):
    resource_group_name = raw_parameters.get("resource_group_name")
    cluster_name = raw_parameters.get("cluster_name")
    loadbalancer_name = raw_parameters.get("name")
    aks_custom_headers = raw_parameters.get("aks_custom_headers")

    # Get custom headers if provided
    from azext_aks_preview.custom import get_aks_custom_headers
    headers = get_aks_custom_headers(aks_custom_headers)

    # Validate required parameters for adding a new LoadBalancer
    if not loadbalancer_name:
        raise RequiredArgumentMissingError(
            "Please specify --name for load balancer configuration."
        )

    # Check if the LoadBalancer exists before updating
    existing_loadbalancers = client.list_by_managed_cluster(
        resource_group_name, cluster_name
    )
    existing_lb = None
    for lb in existing_loadbalancers:
        if lb.name == loadbalancer_name:
            existing_lb = lb
            break

    if existing_lb:
        raise BadRequestError(
            f"Load balancer configuration '{loadbalancer_name}' already exists."
        )

    config = constructLoadBalancerConfiguration(cmd, raw_parameters)
    logger.debug("Load balancer configuration: %s", config)

    # Call create_or_update with the LoadBalancer object
    client.create_or_update(
        resource_group_name=resource_group_name,
        resource_name=cluster_name,
        load_balancer_name=loadbalancer_name,
        parameters=config,
        headers=headers,
    )

    # Wait for the load balancer to be provisioned and return the latest state
    return wait_for_loadbalancer_provisioning_state(
        client, resource_group_name, cluster_name, loadbalancer_name
    )


def constructLoadBalancerConfiguration(cmd, raw_parameters):
    primary_agent_pool_name = raw_parameters.get("primary_agent_pool_name")
    allow_service_placement = raw_parameters.get("allow_service_placement")

    # Check required parameters
    if primary_agent_pool_name is None:
        raise RequiredArgumentMissingError(
            "Please specify --primary-agent-pool-name for load balancer configuration."
        )

    # Get the model class
    LoadBalancer = cmd.get_models(
        "LoadBalancer",
        resource_type=CUSTOM_MGMT_AKS_PREVIEW,
        operation_group="load_balancers",
    )

    # Construct label selectors if provided
    service_label_selector = construct_label_selector(
        cmd, raw_parameters.get("service_label_selector")
    )
    service_namespace_selector = construct_label_selector(
        cmd, raw_parameters.get("service_namespace_selector")
    )
    node_selector = construct_label_selector(cmd, raw_parameters.get("node_selector"))

    result = LoadBalancer(
        primary_agent_pool_name=primary_agent_pool_name,
        allow_service_placement=allow_service_placement,
        service_label_selector=service_label_selector,
        service_namespace_selector=service_namespace_selector,
        node_selector=node_selector,
    )

    return result


def construct_label_selector(cmd, selector_param):
    """Construct a LabelSelector object from a parameter string.

    Supports both matchLabels (key=value) and matchExpressions with operators:
    - In: key In value1 value2 ...
    - NotIn: key NotIn value1 value2 ...
    - Exists: key Exists
    - DoesNotExist: key DoesNotExist

    Example: "app=frontend,environment=prod,tier In frontend backend,version NotIn v1.0 v1.1"
    """
    if not selector_param:
        return None

    LabelSelector = cmd.get_models(
        "LabelSelector",
        resource_type=CUSTOM_MGMT_AKS_PREVIEW,
        operation_group="load_balancers",
    )

    # Models for matchExpressions
    LabelSelectorRequirement = cmd.get_models(
        "LabelSelectorRequirement",
        resource_type=CUSTOM_MGMT_AKS_PREVIEW,
        operation_group="load_balancers",
    )

    # According to the SDK, matchLabels should be List[str] formatted as ["key=value", ...]
    match_labels_list = []
    match_expressions = []

    # Split by comma first, then process each segment
    segments = [seg.strip() for seg in selector_param.split(",")]

    for segment in segments:
        if "=" in segment:
            # Handle matchLabels (key=value)
            # Store as "key=value" in match_labels_list
            match_labels_list.append(segment.strip())
        else:
            # Handle matchExpressions (key operator [values])
            parts = segment.split()

            if len(parts) < 2:
                logger.warning("Skipping invalid expression: %s", segment)
                continue

            key = parts[0].strip()
            operator = parts[1].strip()
            values = [v.strip() for v in parts[2:]] if len(parts) > 2 else []

            # Validate operator
            if operator not in ["In", "NotIn", "Exists", "DoesNotExist"]:
                logger.warning("Skipping expression with invalid operator: %s", segment)
                continue

            # For Exists and DoesNotExist, values should be empty
            if operator in ["Exists", "DoesNotExist"] and values:
                logger.warning(
                    "Operator %s doesn't accept values, but values were provided: %s",
                    operator,
                    segment,
                )
                values = []

            # For In and NotIn, values should not be empty
            if operator in ["In", "NotIn"] and not values:
                logger.warning(
                    "Operator %s requires at least one value, but none were provided: %s",
                    operator,
                    segment,
                )
                continue

            # Create the matchExpression
            match_expressions.append(
                LabelSelectorRequirement(
                    key=key,
                    operator=operator,
                    values=values if operator in ["In", "NotIn"] else None,
                )
            )

    if not match_labels_list and not match_expressions:
        return None

    return LabelSelector(
        match_labels=match_labels_list, match_expressions=match_expressions
    )


def _check_loadbalancer_provisioning_states(
    client,
    resource_group_name,
    cluster_name,
    lb_names_list,
    timeout_seconds=600,
    polling_interval_seconds=30,
):
    """
    Helper function to check provisioning states of multiple load balancers using list operation.

    :param client: The LoadBalancers client
    :param resource_group_name: Name of resource group
    :param cluster_name: Name of the managed cluster
    :param lb_names_list: List of names of the load balancer configurations to check
    :param timeout_seconds: Maximum time to wait in seconds
    :param polling_interval_seconds: Time between polling attempts in seconds
    :return: Dictionary mapping load balancer names to their objects after successful provisioning
    :raises: CLIError if timeout is reached or provisioning fails for any load balancer
    """
    import time

    # Convert to set for O(1) lookups
    lb_names_to_check = set(lb_names_list if lb_names_list is not None else [])
    check_all = len(lb_names_to_check) == 0
    logger.debug("lb_names_to_check: %s, check_all: %s", lb_names_to_check, check_all)

    # Track load balancers that have been successfully provisioned
    results = {}

    start_time = time.time()
    while True:
        # Check if we've exceeded the timeout
        if time.time() - start_time > timeout_seconds:
            raise AzureInternalError(
                f"Timed out waiting for load balancers to reach 'Succeeded' state. "
                f"Operation took longer than {timeout_seconds} seconds."
            )

        # Get all load balancers in a single API call
        try:
            all_lbs = client.list_by_managed_cluster(resource_group_name, cluster_name)
            all_lbs = list(all_lbs)
            logger.debug(
                "resource group: %s, cluster name: %s",
                resource_group_name,
                cluster_name,
            )
            logger.debug("all load balancers: %s", all_lbs)

            # Process each load balancer
            for lb in all_lbs:
                logger.debug("checking load balancer '%s'", lb.name)
                # Skip load balancers we're not interested in when check_all is False
                if not check_all and lb.name not in lb_names_to_check:
                    logger.debug("Skipping waiting for load balancer '%s'", lb.name)
                    continue

                # Check the provisioning state
                if hasattr(lb, "provisioning_state"):
                    if lb.provisioning_state == "Succeeded":
                        logger.info(
                            "Load balancer '%s' provisioning succeeded.", lb.name
                        )
                        # Add to results
                        results[lb.name] = lb
                    elif lb.provisioning_state == "Failed":
                        # Report failure immediately
                        raise AzureInternalError(
                            f"Load balancer '{lb.name}' failed provisioning with state {lb.provisioning_state}"
                        )
                    else:
                        # Still in progress, log and continue
                        logger.info(
                            "Load balancer '%s' provisioning state: %s. Waiting...",
                            lb.name,
                            lb.provisioning_state,
                        )
                else:
                    # If provisioning_state is not available, assume it's ready
                    logger.info(
                        "Load balancer '%s' doesn't have provisioning_state attribute, assuming ready.",
                        lb.name,
                    )
                    # Add to results
                    results[lb.name] = lb

            # Check if we're done
            logger.debug("number of succeeded load balancers: %s", len(results))
            logger.debug("number of all load balancers: %s", len(all_lbs))
            if check_all:
                # For check_all, we need all load balancers in the response to be in results
                if len(results) == len(all_lbs):
                    break
            else:
                # For specific load balancers, check if all requested ones are in results
                if all(lb_name in results for lb_name in lb_names_to_check):
                    break

            # If not done, wait and retry
            logger.info(
                "Waiting %s seconds before checking again...", polling_interval_seconds
            )
            time.sleep(polling_interval_seconds)

        except CLIError as ex:
            # Re-raise errors about load balancer failures
            if "failed provisioning with state" in str(ex):
                raise

            # Handle case where the list operation might fail
            logger.info(
                "Error listing load balancers: %s. Waiting %s seconds...",
                str(ex),
                polling_interval_seconds,
            )
            time.sleep(polling_interval_seconds)

    return results


def wait_for_loadbalancer_provisioning_state(
    client,
    resource_group_name,
    cluster_name,
    loadbalancer_name,
    timeout_seconds=600,
    polling_interval_seconds=30,
):
    """
    Poll the load balancer until its provisioning state is 'Succeeded' or until timeout.

    :param client: The LoadBalancers client
    :param resource_group_name: Name of resource group
    :param cluster_name: Name of the managed cluster
    :param loadbalancer_name: Name of the load balancer configuration
    :param timeout_seconds: Maximum time to wait in seconds (default: 10 minutes)
    :param polling_interval_seconds: Time between polling attempts in seconds (default: 30 seconds)
    :return: The load balancer object after successful provisioning
    :raises: CLIError if timeout is reached or provisioning fails
    """
    # Reuse the multiple load balancer check function with a single name
    results = _check_loadbalancer_provisioning_states(
        client,
        resource_group_name,
        cluster_name,
        [loadbalancer_name],
        timeout_seconds,
        polling_interval_seconds,
    )

    # Return the single load balancer object
    return results.get(loadbalancer_name)


def aks_loadbalancer_rebalance_internal(client, raw_parameters):
    """Rebalance load balancers in an AKS cluster."""

    # Extract parameters
    resource_group_name = raw_parameters.get("resource_group_name")
    cluster_name = raw_parameters.get("cluster_name")
    load_balancer_names = raw_parameters.get("load_balancer_names")

    # If lb-names parameter is not specified, use an empty string
    if load_balancer_names is None:
        load_balancer_names = ""

    if not resource_group_name or not cluster_name:
        raise RequiredArgumentMissingError(
            "--resource-group and --name are required for rebalancing load balancers."
        )

    lb_names_list = []
    if isinstance(load_balancer_names, list) and load_balancer_names:
        # Split the first element by comma if it contains multiple names
        lb_names_list = [name.strip() for name in load_balancer_names[0].split(",")]

    rebalance_params = RebalanceLoadBalancersRequestBody(
        load_balancer_names=lb_names_list
    )

    # Call the SDK's begin_rebalance_load_balancers method
    # This returns a poller which the CLI framework should handle.
    poller = client.begin_rebalance_load_balancers(
        resource_group_name=resource_group_name,
        resource_name=cluster_name,
        parameters=rebalance_params,
    )

    # Return the poller for the CLI framework to handle waiting and result processing
    return poller
