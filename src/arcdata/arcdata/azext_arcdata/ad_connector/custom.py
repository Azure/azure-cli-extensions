# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------
from azext_arcdata.ad_connector.exceptions import ADConnectorError
from azext_arcdata.vendored_sdks.kubernetes_sdk.client import (
    KubernetesError,
)
from knack.cli import CLIError
from knack.log import get_logger

logger = get_logger(__name__)


def ad_connector_create(
    client,
    name,
    realm,
    nameserver_addresses,
    account_provisioning,
    primary_domain_controller=None,
    secondary_domain_controllers=None,
    netbios_domain_name=None,
    dns_domain_name=None,
    num_dns_replicas=1,
    prefer_k8s_dns="true",
    ou_distinguished_name=None,
    domain_service_account_secret=None,
    no_wait=False,
    # -- indirect --
    namespace=None,
    use_k8s=None,
    # -- direct --
    data_controller_name=None,
    resource_group=None,
):
    try:
        cvo = client.args_to_command_value_object(
            {
                "name": name,
                "namespace": namespace,
                "realm": realm,
                "nameserver_addresses": nameserver_addresses,
                "account_provisioning": account_provisioning,
                "primary_domain_controller": primary_domain_controller,
                "secondary_domain_controllers": secondary_domain_controllers,
                "netbios_domain_name": netbios_domain_name,
                "dns_domain_name": dns_domain_name,
                "num_dns_replicas": num_dns_replicas,
                "prefer_k8s_dns": prefer_k8s_dns,
                "ou_distinguished_name": ou_distinguished_name,
                "domain_service_account_secret": domain_service_account_secret,
                "data_controller_name": data_controller_name,
                "resource_group": resource_group,
                "no_wait": no_wait,
            }
        )

        return client.services.ad_connector.create(cvo)

    except KubernetesError as e:
        raise ADConnectorError(e.message)
    except Exception as e:
        raise CLIError(e)


def ad_connector_show(
    client,
    name,
    # -- indirect --
    namespace=None,
    use_k8s=None,
    # -- direct --
    data_controller_name=None,
    resource_group=None,
):
    """
    Show the details of an Active Directory connector.
    """
    try:
        cvo = client.args_to_command_value_object(
            {
                "name": name,
                "namespace": namespace,
                "data_controller_name": data_controller_name,
                "resource_group": resource_group,
            }
        )

        return client.services.ad_connector.show(cvo)

    except KubernetesError as e:
        raise ADConnectorError(e.message)
    except Exception as e:
        raise CLIError(e)


def ad_connector_update(
    client,
    name,
    nameserver_addresses=None,
    primary_domain_controller=None,
    secondary_domain_controllers=None,
    num_dns_replicas=None,
    prefer_k8s_dns=None,
    domain_service_account_secret=None,
    no_wait=False,
    # -- indirect --
    namespace=None,
    use_k8s=None,
    # -- direct --
    data_controller_name=None,
    resource_group=None,
):
    """
    Edit the details of an Active Directory connector.
    """
    try:
        cvo = client.args_to_command_value_object(
            {
                "name": name,
                "namespace": namespace,
                "nameserver_addresses": nameserver_addresses,
                "primary_domain_controller": primary_domain_controller,
                "secondary_domain_controllers": secondary_domain_controllers,
                "num_dns_replicas": num_dns_replicas,
                "prefer_k8s_dns": prefer_k8s_dns,
                "domain_service_account_secret": domain_service_account_secret,
                "data_controller_name": data_controller_name,
                "resource_group": resource_group,
                "no_wait": no_wait,
            }
        )

        return client.services.ad_connector.update(cvo)

    except KubernetesError as e:
        raise ADConnectorError(e.message)
    except Exception as e:
        raise CLIError(e)


def ad_connector_delete(
    client,
    name,
    no_wait=False,
    # -- indirect --
    namespace=None,
    use_k8s=None,
    # -- direct --
    data_controller_name=None,
    resource_group=None,
):
    """
    Delete an Active Directory connector.
    """
    try:
        cvo = client.args_to_command_value_object(
            {
                "name": name,
                "namespace": namespace,
                "data_controller_name": data_controller_name,
                "resource_group": resource_group,
                "no_wait": no_wait,
            }
        )

        return client.services.ad_connector.delete(cvo)

    except KubernetesError as e:
        raise ADConnectorError(e.message)
    except Exception as e:
        raise CLIError(e)


def ad_connector_list(
    client,
    # -- indirect --
    namespace=None,
    use_k8s=None,
    # -- direct --
    data_controller_name=None,
    resource_group=None,
):
    """
    List Active Directory connectors.
    """
    try:
        cvo = client.args_to_command_value_object(
            {
                "namespace": namespace,
                "data_controller_name": data_controller_name,
                "resource_group": resource_group,
            }
        )

        return client.services.ad_connector.list(cvo)

    except KubernetesError as e:
        raise ADConnectorError(e.message)
    except Exception as e:
        raise CLIError(e)
