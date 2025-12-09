# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------
from azext_arcdata.failover_group.exceptions import FailoverGroupError
from azext_arcdata.vendored_sdks.kubernetes_sdk.client import (
    KubernetesError,
)
from knack.cli import CLIError
from knack.log import get_logger

logger = get_logger(__name__)


def arc_sql_mi_fog_create(
    client,
    **kwargs,
):
    try:
        cvo = client.args_to_command_value_object(kwargs)
        return client.services.failover_group.create(cvo)
    except KubernetesError as e:
        raise FailoverGroupError(e.message)
    except Exception as e:
        raise CLIError(e)


def arc_sql_mi_fog_update(
    client,
    **kwargs,
):
    try:
        cvo = client.args_to_command_value_object(kwargs)
        return client.services.failover_group.update(cvo)
    except KubernetesError as e:
        raise FailoverGroupError(e.message)
    except Exception as e:
        raise CLIError(e)


def arc_sql_mi_fog_delete(
    client,
    **kwargs,
):
    try:
        cvo = client.args_to_command_value_object(kwargs)
        return client.services.failover_group.delete(cvo)
    except KubernetesError as e:
        raise FailoverGroupError(e.message)
    except Exception as e:
        raise CLIError(e)


def arc_sql_mi_fog_show(
    client,
    **kwargs,
):
    try:
        cvo = client.args_to_command_value_object(kwargs)
        return client.services.failover_group.show(cvo)
    except KubernetesError as e:
        raise FailoverGroupError(e.message)
    except Exception as e:
        raise CLIError(e)


def arc_sql_mi_fog_list(
    client,
    **kwargs,
):
    try:
        cvo = client.args_to_command_value_object(kwargs)
        return client.services.failover_group.list(cvo)
    except KubernetesError as e:
        raise FailoverGroupError(e.message)
    except Exception as e:
        raise CLIError(e)
