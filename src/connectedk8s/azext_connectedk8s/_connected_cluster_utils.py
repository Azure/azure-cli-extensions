# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger
from azure.cli.core import telemetry
from azure.cli.core.util import sdk_no_wait
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.azclierror import AzureResponseError, ClientRequestError, AzureInternalError
from azure.cli.core.azclierror import ValidationError, AzureResponseError, ArgumentUsageError
from azure.core.exceptions import ResourceNotFoundError
from msrestazure.azure_exceptions import CloudError
from msrest.exceptions import ValidationError as MSRestValidationError
from msrest.exceptions import AuthenticationError, HttpOperationError, TokenExpiredError
from azext_connectedk8s._client_factory import cf_resource_groups
import azext_connectedk8s._constants as consts
from azext_connectedk8s._client_factory import _resource_client_factory


logger = get_logger(__name__)


def check_provider_registrations(rp_client):
    try:
        cc_registration_state = rp_client.get(consts.Connected_Cluster_Provider_Namespace).registration_state
        if cc_registration_state != "Registered":
            telemetry.set_exception(exception="{} provider is not registered"
                                    .format(consts.Connected_Cluster_Provider_Namespace),
                                    fault_type=consts.CC_Provider_Namespace_Not_Registered_Fault_Type,
                                    summary="{} provider is not registered"
                                    .format(consts.Connected_Cluster_Provider_Namespace))
            raise ValidationError("{} provider is not registered."
                                  .format(consts.Connected_Cluster_Provider_Namespace) +
                                  " Please register it using 'az provider register -n 'Microsoft.Kubernetes'" +
                                  " before running the connect command.")
        kc_registration_state = rp_client.get(consts.Kubernetes_Configuration_Provider_Namespace).registration_state
        if kc_registration_state != "Registered":
            telemetry.set_user_fault()
            logger.warning("{} provider is not registered".format(consts.Kubernetes_Configuration_Provider_Namespace))
    except ValidationError as e:
        raise e
    except Exception as ex:
        logger.warning("Couldn't check the required provider's registration status. Error: {}".format(str(ex)))


def connected_cluster_exists(client, resource_group_name, cluster_name):
    try:
        client.get(resource_group_name, cluster_name)
    except Exception as e:  # pylint: disable=broad-except
        arm_exception_handler(e, consts.Get_ConnectedCluster_Fault_Type,
                              'Failed to check if connected cluster resource already exists.',
                              return_if_not_found=True)
        return False
    return True


def resource_group_exists(ctx, resource_group_name, subscription_id=None):
    groups = cf_resource_groups(ctx, subscription_id=subscription_id)
    try:
        groups.get(resource_group_name)
        return True
    except:  # pylint: disable=bare-except
        return False


def create_cc_resource(client, resource_group_name, cluster_name, cc, no_wait):
    try:
        return sdk_no_wait(no_wait, client.begin_create, resource_group_name=resource_group_name,
                           cluster_name=cluster_name, connected_cluster=cc)
    except CloudError as e:
        arm_exception_handler(e, consts.Create_ConnectedCluster_Fault_Type,
                              'Unable to create connected cluster resource')


def delete_cc_resource(client, resource_group_name, cluster_name, no_wait):
    try:
        sdk_no_wait(no_wait, client.begin_delete,
                    resource_group_name=resource_group_name,
                    cluster_name=cluster_name)
    except CloudError as e:
        arm_exception_handler(e, consts.Delete_ConnectedCluster_Fault_Type,
                              'Unable to delete connected cluster resource')


def arm_exception_handler(ex, fault_type, summary, return_if_not_found=False):
    if isinstance(ex, AuthenticationError):
        telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
        raise AzureResponseError("Authentication error occured while making ARM request: " +
                                 str(ex) + "\nSummary: {}".format(summary))

    if isinstance(ex, TokenExpiredError):
        telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
        raise AzureResponseError("Token expiration error occured while making ARM request: " +
                                 str(ex) + "\nSummary: {}".format(summary))

    if isinstance(ex, HttpOperationError):
        status_code = ex.response.status_code
        if status_code == 404 and return_if_not_found:
            return
        if status_code // 100 == 4:
            telemetry.set_user_fault()
        telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
        if status_code // 100 == 5:
            raise AzureInternalError("Http operation error occured while making ARM request: " +
                                     str(ex) + "\nSummary: {}".format(summary))
        raise AzureResponseError("Http operation error occured while making ARM request: " +
                                 str(ex) + "\nSummary: {}".format(summary))

    if isinstance(ex, MSRestValidationError):
        telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
        raise AzureResponseError("Validation error occured while making ARM request: " +
                                 str(ex) + "\nSummary: {}".format(summary))

    if isinstance(ex, CloudError):
        status_code = ex.status_code
        if status_code == 404 and return_if_not_found:
            return
        if status_code // 100 == 4:
            telemetry.set_user_fault()
        telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
        if status_code // 100 == 5:
            raise AzureInternalError("Cloud error occured while making ARM request: " +
                                     str(ex) + "\nSummary: {}".format(summary))
        raise AzureResponseError("Cloud error occured while making ARM request: " +
                                 str(ex) + "\nSummary: {}".format(summary))

    if isinstance(ex, ResourceNotFoundError) and return_if_not_found:
        return

    telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
    raise ClientRequestError("Error occured while making ARM request: " + str(ex) + "\nSummary: {}".format(summary))


def get_resource_client(cmd):
    subscription_id = get_subscription_id(cmd.cli_ctx)
    return _resource_client_factory(cmd.cli_ctx, subscription_id=subscription_id)


def validate_location(location, resourceClient):
    try:
        providerDetails = resourceClient.providers.get('Microsoft.Kubernetes')
    except Exception as e:  # pylint: disable=broad-except
        arm_exception_handler(e, consts.Get_ResourceProvider_Fault_Type, 'Failed to fetch resource provider details')
    for resourceTypes in providerDetails.resource_types:
        if resourceTypes.resource_type == 'connectedClusters':
            rp_locations = [location.replace(" ", "").lower() for location in resourceTypes.locations]
            if location.lower() not in rp_locations:
                telemetry.set_exception(exception='Location not supported',
                                        fault_type=consts.Invalid_Location_Fault_Type,
                                        summary='Provided location is not supported for creating connected clusters')
                raise ArgumentUsageError("Connected cluster resource creation is supported only in the " +
                                         "following locations: " + ', '.join(map(str, rp_locations)),
                                         recommendation="Use the --location flag to specify one of these locations.")
            break
