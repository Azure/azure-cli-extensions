# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long, logging-fstring-interpolation

from datetime import datetime
from time import sleep
from knack.log import get_logger
from azure.cli.core.commands.client_factory import get_subscription_id, get_mgmt_service_client
from azure.cli.core.profiles import ResourceType
from azure.cli.core.azclierror import ValidationError, CLIInternalError

logger = get_logger(__name__)

rp_name_hybrid_connectivity = "Microsoft.HybridConnectivity"
rp_name_aws_connector = "Microsoft.AwsConnector"
rp_name_hybrid_compute = "Microsoft.HybridCompute"

required_rps = [rp_name_hybrid_connectivity, rp_name_aws_connector, rp_name_hybrid_compute]


# We call this method before running each individual command. See usage in src/multicloud-connector/azext_multicloud_connector/custom.py
def register_providers_if_needed(cmd):
    logger.debug("Start to check if required RPs are registered ...")
    for rp_name in required_rps:
        if not _is_resource_provider_registered(cmd, rp_name):
            logger.info(f"RP {rp_name} is not registered, try to register")
            _register_resource_provider(cmd, rp_name)
    logger.debug("All required RPs are registered successfully")


def _is_resource_provider_registered(cmd, resource_provider, subscription_id=None):
    registered = None
    if not subscription_id:
        subscription_id = get_subscription_id(cmd.cli_ctx)
    try:
        providers_client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES,
                                                   subscription_id=subscription_id).providers
        # default to "NotRegistered" if the registration_state is not available
        registration_state = getattr(providers_client.get(resource_provider), 'registration_state', "NotRegistered")

        registered = (registration_state and registration_state.lower() == 'registered')
    except Exception:  # pylint: disable=broad-except
        pass
    return registered


def _register_resource_provider(cmd, resource_provider):
    from azure.mgmt.resource.resources.models import ProviderRegistrationRequest, ProviderConsentDefinition

    logger.debug(f"Registering resource provider {resource_provider} ...")
    properties = ProviderRegistrationRequest(
        third_party_provider_consent=ProviderConsentDefinition(consent_to_authorization=True))

    client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES).providers
    try:
        client.register(resource_provider, properties=properties)
        # wait for registration to finish
        timeout_secs = 120
        registered = _is_resource_provider_registered(cmd, resource_provider)
        start = datetime.utcnow()
        while not registered:
            # iteratively check if the RP is registered every 3 secs until it reaches to the 120s timeout
            registered = _is_resource_provider_registered(cmd, resource_provider)
            sleep(3)
            if (datetime.utcnow() - start).seconds >= timeout_secs:
                raise CLIInternalError(
                    f"Timed out while waiting for the {resource_provider} resource provider to be registered.")

    except Exception as e:
        raise ValidationError(f"This operation requires registering the resource provider {resource_provider}. \n"
                              f"We were unable to perform that registration on your behalf. \n"
                              f"Server responded with error message: {str(e)}. \n"
                              "Please check with your admin on permissions, "
                              f"or try running registration manually with: az provider register --wait --namespace {resource_provider}"
                              )
