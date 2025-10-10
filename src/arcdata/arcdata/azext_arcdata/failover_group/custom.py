# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------
from azext_arcdata.failover_group.exceptions import FailoverGroupError
from azext_arcdata.kubernetes_sdk.client import (
    KubernetesError,
)
from knack.cli import CLIError
from knack.log import get_logger

logger = get_logger(__name__)


def arc_sql_mi_fog_create(
    client,
    name,
    mi,
    partner_mi,
    role=None,
    primary_mirroring_url=None,
    partner_mirroring_url=None,
    partner_mirroring_cert_file=None,
    partner_sync_mode=None,
    shared_name=None,
    namespace=None,
    use_k8s=None,
    resource_group=None,
    partner_resource_group=None,
    no_wait=False,
):
    try:
        cvo = client.args_to_command_value_object()
        return client.services.failover_group.create(cvo)
    except KubernetesError as e:
        raise FailoverGroupError(e.message)
    except Exception as e:
        raise CLIError(e)


def arc_sql_mi_fog_update(
    client,
    name,
    role=None,
    partner_sync_mode=None,
    namespace=None,
    use_k8s=None,
    mi=None,
    resource_group=None,
    no_wait=False,
):
    try:
        cvo = client.args_to_command_value_object()
        return client.services.failover_group.update(cvo)
    except KubernetesError as e:
        raise FailoverGroupError(e.message)
    except Exception as e:
        raise CLIError(e)


def arc_sql_mi_fog_delete(
    client,
    name,
    namespace=None,
    use_k8s=None,
    mi=None,
    resource_group=None,
):
    try:
        cvo = client.args_to_command_value_object()
        return client.services.failover_group.delete(cvo)
    except KubernetesError as e:
        raise FailoverGroupError(e.message)
    except Exception as e:
        raise CLIError(e)


def arc_sql_mi_fog_show(
    client,
    name,
    namespace=None,
    use_k8s=None,
    mi=None,
    resource_group=None,
):
    try:
        cvo = client.args_to_command_value_object()
        return client.services.failover_group.show(cvo)
    except KubernetesError as e:
        raise FailoverGroupError(e.message)
    except Exception as e:
        raise CLIError(e)


def arc_sql_mi_fog_list(
    client,
    namespace=None,
    use_k8s=None,
    mi=None,
    resource_group=None,
):
    try:
        cvo = client.args_to_command_value_object()
        return client.services.failover_group.list(cvo)
    except KubernetesError as e:
        raise FailoverGroupError(e.message)
    except Exception as e:
        raise CLIError(e)
