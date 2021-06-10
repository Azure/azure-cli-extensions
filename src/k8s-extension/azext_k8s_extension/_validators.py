# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger
from ._client_factory import _resource_providers_client
from . import consts


logger = get_logger(__name__)


# pylint: disable=broad-except
def validate_cc_registration(cmd):
    try:
        rp_client = _resource_providers_client(cmd.cli_ctx)
        registration_state = rp_client.get(consts.PROVIDER_NAMESPACE).registration_state

        if registration_state.lower() != consts.REGISTERED.lower():
            logger.warning("'Extensions' cannot be used because '%s' provider has not been registered."
                           "More details for registering this provider can be found here - "
                           "https://aka.ms/RegisterKubernetesConfigurationProvider", consts.PROVIDER_NAMESPACE)
    except Exception:
        logger.warning("Unable to fetch registration state of '%s' provider. "
                       "Failed to enable 'extensions' feature...", consts.PROVIDER_NAMESPACE)
