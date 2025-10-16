# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------
from datetime import datetime, timezone
from enum import Enum

from knack.cli import CLIError
from knack.log import get_logger

from azext_arcdata.vendored_sdks.kubernetes_sdk.client import (
    KubernetesError,
)
from azext_arcdata.core.constants import (
    USE_K8S_EXCEPTION_TEXT,
)
from dateutil import parser, tz

CONNECTION_RETRY_ATTEMPTS = 12
RETRY_INTERVAL = 5

logger = get_logger(__name__)


class progress_state(str, Enum):
    active = "active"
    done = "done"
    failed = "failed"
    pending = "pending"


# ------------------------------------------------------------------------------
# Server Commands
# ------------------------------------------------------------------------------


def postgres_server_arc_create(
    client,
    name,
    path=None,
    namespace=None,
    admin_login_secret=None,
    certificate_private_key_file=None,
    certificate_public_key_file=None,
    cores_limit=None,
    cores_request=None,
    log_level=None,
    memory_limit=None,
    memory_request=None,
    service_annotations=None,
    service_certificate_secret=None,
    service_labels=None,
    service_type=None,
    storage_class_data=None,
    storage_class_logs=None,
    storage_class_backups=None,
    volume_size_data=None,
    volume_size_logs=None,
    volume_size_backups=None,
    no_external_endpoint=None,
    dev=None,
    port=None,
    nowait=False,
    use_k8s=None,
    ad_connector_name=None,
    ad_account_name=None,
    keytab_secret=None,
    dns_name=None,
    extensions=None,
    retention_days=None,
):
    """
    Create an Azure Arc enabled PostgreSQL server.
    :param client:
    :param name: The name of the Azure Arc enabled PostgreSQL server.
    :param path: The src filepath of the postgres resource.
    :param namespace: Namespace where the Azure Arc enabled PostgreSQL server is deployed.
    :param admin_login_secret: Name of the Kubernetes secret to generate that hosts or will host
        user admin login account credential.
    :param certificate_private_key_file: Path to the file containing a PEM formatted certificate
        private key to be used for client SSL connections.
    :param certificate_public_key_file: Path to the file containing a PEM formatted certificate
        public key to be used for client SSL connections.
    :param cores_limit: The limit of cores of the managed instance in integer number of vCores.
    :param cores_request: The request for cores of the managed instance in integer number of
        vCores.
    :param extensions: Comma seperated list of PostgreSql extensions to be configured.
    :param log_level: Sets the log_min_messages setting for the PostgreSQL engine.
    :param memory_limit: The limit of the capacity of the managed instance in integer amount of
        memory in GBs.
    :param memory_request: The request for the capacity of the managed instance in integer amount
        of memory in GBs.
    :param retention_days: Backup retention period, specified in days. Allowed values are 0 to 35.
        Default is 7
    :param service_annotations: Comma-separated list of annotations to apply to all external
        services.
    :param service_certificate_secret: Name of the Kubernetes secret to generate that hosts
        the SSL certificate.
    :param service_labels: Comma-separated list of labels to apply to all external services.
    :param service_type: The type for the primary service.
    :param storage_class_data: The storage classes to be used for data persistent volumes.
    :param storage_class_logs: The storage classes to be used for logs persistent volumes.
    :param storage_class_backups: The storage classes to be used for backups persistent volumes.
    :param volume_size_data: The volume size for the storage classes to be used for data.
    :param volume_size_logs: The volume size for the storage classes to be used for logs.
    :param volume_size_backups: The volume size for the storage classes to be used for backups.
    :param no_external_endpoint: If not specified, an external service is created using the
        same service type as the data controller.
    :param dev: If this is specified, then it is considered a dev instance and will not be billed
        for.
    :param port: Optional parameter for the service port.
    :param nowait: Do not wait for deployment to be ready before returning.
    :param use_k8s: Use the current kubeconfig to perform this action.
    :param ad_connector_name: the name of the Active Directory Connector resource. This parameter
        indicates an intent to deploy with AD support.
    :param ad_account_name: Active Directory account name for this Azure Arc enabled PostgreSQL
        server.
    :param keytab_secret: The name of the Kubernetes secret that contains the keytab
        file for this Azure Arc enabled PostgreSQL server.
    :param dns_name: The primary service DNS name exposed to the end-users to
        connect to this Azure Arc enabled PostgreSQL server.
    :param extensions: Command seperated list of postgresql extensions.
    :param retention_days: Retention period in days, ranging from 0 to 35.
    :return:
    """
    if not use_k8s:
        raise ValueError(USE_K8S_EXCEPTION_TEXT)

    cvo = client.args_to_command_value_object(locals())
    try:
        client.services.pg.create(cvo)
    except KubernetesError as e:
        raise CLIError(e.message) from e
    except Exception as e:
        raise CLIError(e) from e


def postgres_server_arc_restore(
    client,
    name,
    namespace,
    source_server,
    time=None,
    storage_class_data=None,
    storage_class_logs=None,
    storage_class_backups=None,
    volume_size_data=None,
    volume_size_logs=None,
    volume_size_backups=None,
    dry_run=False,
    nowait=False,
    use_k8s=None,
):
    """
    Create an Azure Arc enabled PostgreSQL server.
    :param client:
    :param name: The name of the Azure Arc enabled PostgreSQL server.
    :param namespace: Namespace where the Azure Arc enabled PostgreSQL server
    is deployed.
    :param source_server:  The name of the Azure Arc enabled PostgreSQL server
    to restore from.
    :param time: Restore time.
    :param storage_class_data: The storage classes to be used for data
    persistent volumes.
    :param storage_class_logs: The storage classes to be used for logs
    persistent volumes.
    :param storage_class_backups: The storage classes to be used for backups
    persistent volumes.
    :param volume_size_data: The volume size for the storage classes to be used
    for data.
    :param volume_size_logs: The volume size for the storage classes to be used
    or logs.
    :param volume_size_backups: The volume size for the storage classes to be
    used for backups.
    :param dry_run: If set, validates the source and destination resources, and
    the restore time.
    :param nowait: Do not wait for deployment to be ready before returning.
    :param use_k8s: Use the current kubeconfig to perform this action.
    :return:
    """
    if not use_k8s:
        raise ValueError(USE_K8S_EXCEPTION_TEXT)

    if time is None:
        time = _parse_restore_time(
            str(datetime(1, 1, 1, 0, 0, 0, tzinfo=timezone.utc))
        )
    elif len(time) > 27:
        raise ValueError(
            "Nanosecond precision not supported, please specify timestamp in"
            + " the format: YYYY-MM-DDTHH:MM:SS.FFFFFFZ"
        )

    task_name = "postgresql-restore-" + str(datetime.timestamp(datetime.now()))

    cvo = client.args_to_command_value_object(
        {
            "name": task_name,
            "namespace": namespace,
            "source_name": source_server,
            "destination_name": name,
            "restore_point": time,
            "storage_class_data": storage_class_data,
            "storage_class_logs": storage_class_logs,
            "storage_class_backups": storage_class_backups,
            "volume_size_data": volume_size_data,
            "volume_size_logs": volume_size_logs,
            "volume_size_backups": volume_size_backups,
            "dry_run": dry_run,
            "nowait": nowait,
        }
    )
    try:
        client.services.pg.restore(cvo)
    except KubernetesError as err:
        raise CLIError(err.message) from err
    except Exception as err:
        raise CLIError(err) from err


def postgres_server_arc_update(
    client,
    name,
    namespace=None,
    path=None,
    certificate_private_key_file=None,
    certificate_public_key_file=None,
    cores_limit=None,
    cores_request=None,
    log_level=None,
    memory_limit=None,
    memory_request=None,
    no_external_endpoint=None,
    service_annotations=None,
    service_certificate_secret=None,
    service_labels=None,
    service_type=None,
    dev=None,
    port=None,
    nowait=False,
    use_k8s=None,
    keytab_secret=None,
    retention_days=None,
    extensions=None,
):
    """
    Update the configuration of an Azure Arc enabled PostgreSQL server.
    :param client:
    :param name: The name of the Azure Arc enabled PostgreSQL server you would like to update.
    :param namespace: Namespace where the Azure Arc enabled PostgreSQL server is deployed.
    :param path: The path to the source json file for the Azure Arc enabled PostgreSQL server.
        This is optional.
    :param certificate_private_key_file: Path to the file containing a PEM formatted certificate
        private key to be used for client SSL connections.
    :param certificate_public_key_file: Path to the file containing a PEM formatted certificate
        public key to be used for client SSL connections.
    :param cores_limit: The limit of cores of the managed instance in integer number of vCores.
    :param cores_request: The request for cores of the managed instance in integer number of
        vCores.
    :param extensions: Comma seperated list of PostgreSql extensions to be configured.
    :param log_level: Sets the log_min_messages setting for the PostgreSQL engine.
    :param memory_limit: The limit of the capacity of the managed instance in integer amount of
        memory in GBs.
    :param memory_request: The request for the capacity of the managed instance in integer amount
        of memory in GBs.
    :param retention_days: "Backup retention period, specified in days. Allowed values are 0 to 35.
        Default is 7.
    :param no_external_endpoint: If not specified, an external service is created using the
        same service type as the data controller.
    :param service_annotations: Comma-separated list of annotations to apply to all external
        services.
    :param service_certificate_secret: Name of the Kubernetes secret to generate that hosts
        the SSL certificate.
    :param service_labels: Comma-separated list of labels to apply to all external services.
    :param service_type: The type for the primary service.
    :param dev: If this is specified, then it is considered a dev instance and will not be billed
        for.
    :param port: Optional parameter for the service port.
    :param nowait: Do not wait for deployment to be ready before returning.
    :param use_k8s: Use the current kubeconfig to perform this action.
    :param keytab_secret: The name of the Kubernetes secret that contains the keytab
        file for this Azure Arc enabled PostgreSQL server.
    :param extensions: Command seperated list of postgresql extensions.
    :param retention_days: Retention period in days, ranging from 0 to 35.
    :return:
    """
    if not use_k8s:
        raise ValueError(USE_K8S_EXCEPTION_TEXT)

    cvo = client.args_to_command_value_object(locals())
    try:
        client.services.pg.update(cvo)
    except KubernetesError as e:
        raise CLIError(e.message) from e
    except Exception as e:
        raise CLIError(e) from e


def postgres_server_arc_delete(
    client, name, namespace=None, force=False, use_k8s=None
):
    """
    Delete an Azure Arc enabled PostgreSQL server.
    :param client:
    :param name: Name of the Azure Arc enabled PostgreSQL server.
    :param namespace: Namespace where the Azure Arc enabled PostgreSQL server is deployed.
    :param force: Delete the Azure Arc enabled PostgreSQL server without confirmation.
    :param use_k8s: Use the current kubeconfig to perform this action.
    :return:
    """
    if not use_k8s:
        raise ValueError(USE_K8S_EXCEPTION_TEXT)

    cvo = client.args_to_command_value_object(locals())
    try:
        client.services.pg.delete(cvo)
    except KubernetesError as e:
        raise CLIError(e.message)
    except Exception as e:
        raise CLIError(e)


def postgres_server_arc_show(
    client, name, namespace=None, path=None, use_k8s=None
):
    """
    Show the details of an Azure Arc enabled PostgreSQL server.
    :param client:
    :param name: Name of the Azure Arc enabled PostgreSQL server.
    :param namespace: Namespace where the Azure Arc enabled PostgreSQL server is deployed.
    :param path: A path to a json file where the full specification for the Azure Arc enabled
        PostgreSQL server should be written.
    :param use_k8s: Use the current kubeconfig to perform this action.
    :return:
    """
    if not use_k8s:
        raise ValueError(USE_K8S_EXCEPTION_TEXT)

    cvo = client.args_to_command_value_object(locals())
    try:
        result = client.services.pg.show(cvo)
        if not path:
            return result
    except KubernetesError as e:
        raise CLIError(e.message)
    except Exception as e:
        raise CLIError(e)


def postgres_server_arc_list(client, namespace=None, use_k8s=None):
    """
    List Azure Arc enabled PostgreSQL servers.
    :param client:
    :param namespace: Namespace where the Azure Arc enabled PostgreSQL server is deployed.
    :param use_k8s: Use the current kubeconfig to perform this action.
    :return:
    """
    if not use_k8s:
        raise ValueError(USE_K8S_EXCEPTION_TEXT)

    try:
        return client.services.pg.list(namespace)
    except KubernetesError as e:
        raise CLIError(e.message)
    except Exception as e:
        raise CLIError(e)


def arc_postgres_endpoint_list(client, name=None, namespace=None, use_k8s=None):
    """
    List Azure Arc enabled PostgreSQL server endpoints.
    :param client:
    :param name: Name of the Azure Arc enabled PostgreSQL server.
    :param namespace: Namespace where the Azure Arc enabled PostgreSQL server is deployed.
    :param use_k8s: Use the current kubeconfig to perform this action.
    :return:
    """
    if not use_k8s:
        raise ValueError(USE_K8S_EXCEPTION_TEXT)

    try:
        return client.services.pg.endpoint_list(name, namespace)
    except KubernetesError as e:
        raise CLIError(e.message)
    except Exception as e:
        raise CLIError(e)


def _parse_restore_time(time):
    t = parser.parse(time)
    if t.tzinfo is None:
        t = datetime(
            t.year,
            t.month,
            t.day,
            t.hour,
            t.minute,
            t.second,
            t.microsecond,
            tz.tzlocal(),
        )
    return t.astimezone(tz.tzutc())
