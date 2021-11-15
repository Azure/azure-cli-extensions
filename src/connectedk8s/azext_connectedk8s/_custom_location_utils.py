# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger
from azure.cli.core import telemetry
from azext_connectedk8s._client_factory import _resource_providers_client
from azext_connectedk8s._client_factory import get_graph_client_service_principals
import azext_connectedk8s._constants as consts

logger = get_logger(__name__)


def get_custom_locations_oid(cmd, cl_oid):
    try:
        sp_graph_client = get_graph_client_service_principals(cmd.cli_ctx)
        sub_filters = []
        sub_filters.append("displayName eq '{}'".format("Custom Locations RP"))
        result = list(sp_graph_client.list(filter=(' and '.join(sub_filters))))
        if len(result) != 0:
            if cl_oid is not None and cl_oid != result[0].object_id:
                logger.debug("The 'Custom-locations' OID passed is different" +
                             " from the actual OID({}) of the Custom Locations"
                             .format(result[0].object_id) + " RP app. Proceeding with the correct one...")
            return result[0].object_id  # Using the fetched OID

        #Below if else might not execute check? sp_graph_client.list(filter=(' and '.join(sub_filters))) 
        # is None then list(None) will throw exception
        if cl_oid is None:
            logger.warning("Failed to enable Custom Locations feature on the cluster." +
                           " Unable to fetch Object ID of Azure AD application used by" +
                           " Azure Arc service. Try enabling the feature by passing the" +
                           " --custom-locations-oid parameter directly." +
                           " Learn more at https://aka.ms/CustomLocationsObjectID")
            telemetry.set_exception(exception='Unable to fetch oid of custom locations app.',
                                    fault_type=consts.Custom_Locations_OID_Fetch_Fault_Type,
                                    summary='Unable to fetch oid for custom locations app.')
            return ""
        else:
            return cl_oid
    except Exception as e:
        log_string = "Unable to fetch the Object ID of the Azure AD application used by Azure Arc service. "
        telemetry.set_exception(exception=e, fault_type=consts.Custom_Locations_OID_Fetch_Fault_Type,
                                summary='Unable to fetch oid for custom locations app.')
        if cl_oid:
            log_string += "Proceeding with the Object ID provided to enable the 'custom-locations' feature."
            logger.warning(log_string)
            return cl_oid
        log_string += "Unable to enable the 'custom-locations' feature. " + str(e)
        logger.warning(log_string)
        return ""


def check_cl_registration_and_get_oid(cmd, cl_oid):
    enable_custom_locations = True
    custom_locations_oid = ""
    try:
        rp_client = _resource_providers_client(cmd.cli_ctx)
        cl_registration_state = rp_client.get(consts.Custom_Locations_Provider_Namespace).registration_state
        if cl_registration_state != "Registered":
            enable_custom_locations = False
            logger.warning("'Custom-locations' feature couldn't be enabled on this cluster as the" +
                           " pre-requisite registration of 'Microsoft.ExtendedLocation' was not met." +
                           " More details for enabling this feature later on this cluster can be found here" +
                           " - https://aka.ms/EnableCustomLocations")
        else:
            custom_locations_oid = get_custom_locations_oid(cmd, cl_oid)
            if custom_locations_oid == "":
                enable_custom_locations = False
    except Exception as e:
        enable_custom_locations = False
        logger.warning("Unable to fetch registration state of 'Microsoft.ExtendedLocation'. Failed to enable" +
                       " 'custom-locations' feature...")
        telemetry.set_exception(exception=e, fault_type=consts.Custom_Locations_Registration_Check_Fault_Type,
                                summary='Unable to fetch status of Custom Locations RP registration.')
    return enable_custom_locations, custom_locations_oid
