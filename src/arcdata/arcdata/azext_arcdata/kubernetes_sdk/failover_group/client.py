# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

import time
from azext_arcdata.core.constants import DIRECT
from azext_arcdata.core.util import (
    check_and_set_kubectl_context,
    is_windows,
    retry,
)
from azext_arcdata.kubernetes_sdk.client import (
    KubernetesClient,
    KubernetesError,
)
from azext_arcdata.kubernetes_sdk.client import KubernetesError
from azext_arcdata.kubernetes_sdk.dc.constants import FOG_CRD_NAME
from azext_arcdata.kubernetes_sdk.dc.client import DataControllerClient
from azext_arcdata.kubernetes_sdk.models.custom_resource import CustomResource
from azext_arcdata.failover_group.constants import (
    DAG_ROLES_ALLOWED_VALUES_MSG_CREATE,
    DAG_ROLES_ALLOWED_VALUES_MSG_UPDATE,
    DAG_RPARTNER_SYNC_MODE_ALLOWED_MSG,
    FOG_API_GROUP,
    FOG_API_VERSION,
    FOG_RESOURCE_KIND,
    FOG_RESOURCE_KIND_PLURAL,
)
from azext_arcdata.failover_group.models.fog_cr import FogCustomResource
from azext_arcdata.kubernetes_sdk.util import is_valid_connectivity_mode
from azext_arcdata.sqlmi.models.sqlmi_cr_model import SqlmiCustomResource
from azext_arcdata.sqlmi.sqlmi_utilities import get_sqlmi_custom_resource
from azext_arcdata.failover_group.util import (
    CONNECTION_RETRY_ATTEMPTS,
    RETRY_INTERVAL,
    _get_error_message,
    _is_dag_in_error,
    _is_dag_ready,
    get_failover_group_custom_resource,
    poll_failover_group_state,
    validate_dag_partner_sync_mode,
    validate_dag_roles,
)
from humanfriendly.terminal.spinners import AutomaticSpinner
from knack.cli import CLIError
from knack.log import get_logger
from urllib3.exceptions import MaxRetryError, NewConnectionError


__all__ = ["FailoverGroupClient"]

logger = get_logger(__name__)


class FailoverGroupClient(object):
    def __init__(self, stdout, stderr):
        check_and_set_kubectl_context()
        self._client = KubernetesClient
        self.stdout = stdout
        self.stderr = stderr
        self.dc_client = DataControllerClient(stdout, stderr)

    # ------------------------------------------------------------------------ #
    # Failover Group Create
    # ------------------------------------------------------------------------ #

    def create(
        self,
        name,
        namespace,
        mi,
        partner_mi,
        partner_mirroring_url,
        partner_mirroring_cert_file,
        role,
        shared_name,
        partner_sync_mode,
        no_wait=False,
    ):
        client = self._client
        stdout = self.stdout

        if not validate_dag_roles(role, True):
            raise ValueError(DAG_ROLES_ALLOWED_VALUES_MSG_CREATE)

        if partner_sync_mode is not None:
            if not validate_dag_partner_sync_mode(partner_sync_mode):
                raise ValueError(DAG_RPARTNER_SYNC_MODE_ALLOWED_MSG)

        is_valid_connectivity_mode(client, namespace)

        if client.namespaced_custom_object_exists(
            name,
            namespace,
            group=FOG_API_GROUP,
            version=FOG_API_VERSION,
            plural=FOG_RESOURCE_KIND_PLURAL,
        ):
            raise ValueError(
                "Arc-enabled SQL managed instance failover group `{}` already exists in namespace `{}`.".format(
                    name, namespace
                )
            )

        spec_object = {
            "apiVersion": FOG_API_GROUP + "/" + FOG_API_VERSION,
            "kind": FOG_RESOURCE_KIND,
            "metadata": {"name": name},
            "spec": {
                "sharedName": shared_name,
                "sourceMI": mi,
                "partnerMI": partner_mi,
                "partnerMirroringURL": partner_mirroring_url,
                "partnerMirroringCert": "",
                "partnerSyncMode": partner_sync_mode,
                "role": role,
            },
        }

        # Decode base spec and apply args. Must patch namespace in separately
        # since it's not parameterized in this func
        #
        cr = CustomResource.decode(FogCustomResource, spec_object)
        cr.metadata.namespace = namespace
        cr.validate(client)

        # Fill out the owner reference.
        deployed_mi: SqlmiCustomResource = get_sqlmi_custom_resource(
            client, mi, namespace
        )

        ownerReference = cr.metadata.OwnerReference(
            deployed_mi.apiVersion,
            deployed_mi.kind,
            deployed_mi.metadata.name,
            deployed_mi.metadata.uid,
        )
        cr.metadata.ownerReferences.append(ownerReference)

        file = open(partner_mirroring_cert_file, "r")
        remote_public_cert = file.read()
        file.close()

        cr.spec.partnerMirroringCert = remote_public_cert

        # Create custom resource
        #
        retry(
            lambda: client.create_namespaced_custom_object(
                cr=cr, plural=FOG_RESOURCE_KIND_PLURAL, ignore_conflict=True
            ),
            retry_count=CONNECTION_RETRY_ATTEMPTS,
            retry_delay=RETRY_INTERVAL,
            retry_method="create namespaced custom object",
            retry_on_exceptions=(
                NewConnectionError,
                MaxRetryError,
                KubernetesError,
            ),
        )

        if no_wait:
            stdout(
                "Deployed Arc-enabled SQL managed instance failover group {0} in namespace `{1}`."
                "Please use `az sql instance-failover-group-arc show -n {0} --k8s-namespace {1} "
                "--use-k8s` to check its status.".format(
                    cr.metadata.name, cr.metadata.namespace
                )
            )
            return

        if not is_windows():
            with AutomaticSpinner(
                "Deploying {0} in namespace `{1}`".format(
                    cr.metadata.name, cr.metadata.namespace
                ),
                show_time=True,
            ):
                state, results = poll_failover_group_state(
                    client, name, namespace
                )
        else:
            stdout(
                "Deploying {0} in namespace `{1}`".format(
                    cr.metadata.name, cr.metadata.namespace
                )
            )
            state, results = poll_failover_group_state(client, name, namespace)

        if state != "succeeded":
            raise CLIError(
                "SQL managed instance failover group creation failed with the following error: \n {0}".format(
                    results
                )
            )
        else:
            stdout(
                "SQL managed instance failover group {0} has been created".format(
                    cr.metadata.name
                )
            )
            return self.show(name, namespace)

    # ------------------------------------------------------------------------ #
    # Failover Group Update
    # ------------------------------------------------------------------------ #

    def update(
        self,
        name,
        namespace,
        role,
        partner_sync_mode,
        mi=None,
        no_wait=False,
    ):
        """
        Update the configuration of a SQL managed instance.
        """
        client = self._client
        stdout = self.stdout

        connection_mode = self.dc_client.get_data_controller(namespace).get(
            "connectionMode"
        )
        cr: FogCustomResource
        if connection_mode == DIRECT:
            if not mi:
                raise ValueError(
                    "The name of the associated Arc-enabled SQL managed instance is required in direct connection mode."
                )
            cr = get_failover_group_custom_resource(client, name, namespace, mi)
            name = cr.metadata.name
        else:
            # Get CR
            cr = get_failover_group_custom_resource(client, name, namespace)

        if role is not None:
            if not validate_dag_roles(role, False):
                raise ValueError(DAG_ROLES_ALLOWED_VALUES_MSG_UPDATE)
            cr.spec.role = role

        if partner_sync_mode is not None:
            if not validate_dag_partner_sync_mode(partner_sync_mode):
                raise ValueError(DAG_RPARTNER_SYNC_MODE_ALLOWED_MSG)
            cr.spec.partnerSyncMode = partner_sync_mode

        # Patch CR
        client.patch_namespaced_custom_object(
            cr=cr, plural=FOG_RESOURCE_KIND_PLURAL
        )
        time.sleep(5)
        deployed_cr = get_failover_group_custom_resource(
            client, name, namespace
        )

        if no_wait:
            stdout(
                "Arc-enabled SQL managed instance failover group {0} is being updated. "
                "Please use `sql instance-failover-group-arc show -n {0} --k8s-namespace {1} "
                "--use-k8s` to check its status.".format(name, namespace)
            )
            return

        if not is_windows():
            with AutomaticSpinner(
                "Updating {0} in namespace `{1}`".format(name, namespace),
                show_time=True,
            ):
                while not _is_dag_ready(deployed_cr):
                    if _is_dag_in_error(deployed_cr):
                        stdout(
                            "SQL managed instance failover group {0} is in an error state:\n{1}".format(
                                name, deployed_cr.status.results
                            )
                        )
                        break

                    time.sleep(5)
                    deployed_cr = get_failover_group_custom_resource(
                        client, name, namespace
                    )
        else:
            stdout("Updating {0} in namespace `{1}`".format(name, namespace))
            while not _is_dag_ready(deployed_cr):
                if _is_dag_in_error(deployed_cr):
                    stdout(
                        "SQL managed instance failover group {0} is in an error state:\n{1}".format(
                            name, deployed_cr.status.results
                        )
                    )
                    break

                time.sleep(5)
                deployed_cr = get_failover_group_custom_resource(
                    client, name, namespace
                )

        if _is_dag_ready(deployed_cr):
            stdout("Successfully updated failover group '{0}'".format(name))

    # ------------------------------------------------------------------------ #
    # Failover Group Show
    # ------------------------------------------------------------------------ #

    def show(self, name, namespace, mi=None):
        client = self._client

        connection_mode = self.dc_client.get_data_controller(namespace).get(
            "connectionMode"
        )
        if connection_mode == DIRECT:
            if not mi:
                raise ValueError(
                    "The name of the associated Arc-enabled SQL managed instance is required in direct connection mode."
                )
            deployed_cr = get_failover_group_custom_resource(
                client, name, namespace, mi
            )
        else:
            # Get CR
            deployed_cr = get_failover_group_custom_resource(
                client, name, namespace
            )

        return deployed_cr.encode()

    # ------------------------------------------------------------------------ #
    # Failover Group Delete
    # ------------------------------------------------------------------------ #

    def delete(self, name, namespace, mi=None):
        client = self._client
        stdout = self.stdout

        connection_mode = self.dc_client.get_data_controller(namespace).get(
            "connectionMode"
        )
        cr: FogCustomResource
        if connection_mode == DIRECT:
            if not mi:
                raise ValueError(
                    "The name of the associated Arc-enabled SQL managed instance is required in direct connection mode."
                )
            cr = get_failover_group_custom_resource(client, name, namespace, mi)
            name = cr.metadata.name
        else:
            # Get CR
            cr = get_failover_group_custom_resource(client, name, namespace)

        client.delete_namespaced_custom_object(
            name=name,
            namespace=namespace,
            group=FOG_API_GROUP,
            version=KubernetesClient.get_crd_version(FOG_CRD_NAME),
            plural=FOG_RESOURCE_KIND_PLURAL,
        )
        stdout(
            "Deleted failover group {} from namespace {}".format(
                name, namespace
            )
        )

    # ------------------------------------------------------------------------ #
    # Failover Group List
    # ------------------------------------------------------------------------ #

    def list(self, namespace):
        client = self._client
        stdout = self.stdout

        crs = client.list_namespaced_custom_object(
            group=FOG_API_GROUP,
            version=KubernetesClient.get_crd_version(FOG_CRD_NAME),
            namespace=namespace,
            plural=FOG_RESOURCE_KIND_PLURAL,
        )

        result = []
        items = crs.get("items")
        for item in items:
            cr = CustomResource.decode(FogCustomResource, item)
            result.append(cr.encode())

        stdout(
            "Found {} Failover Group(s) in namespace {}".format(
                len(result), namespace
            )
        )

        return result if result else None
