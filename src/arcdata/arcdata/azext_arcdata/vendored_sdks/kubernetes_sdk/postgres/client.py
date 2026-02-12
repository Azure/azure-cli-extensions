# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

import base64
import copy
from datetime import datetime
import json
import os
import sys
import time
import yaml

from azext_arcdata.vendored_sdks.kubernetes_sdk.models.kube_quantity import KubeQuantity
from azext_arcdata.vendored_sdks.kubernetes_sdk.models.custom_resource import CustomResource
from azext_arcdata.vendored_sdks.kubernetes_sdk.models.data_controller_custom_resource import (
    DataControllerCustomResource,
)
from azext_arcdata.vendored_sdks.kubernetes_sdk.postgres._serialization import (
    last_restapi_key_transformer,
)
from azext_arcdata.vendored_sdks.kubernetes_sdk.models._models import (
    IoK8SApimachineryPkgApisMetaV1ObjectMeta as PostgresCustomResourceMetadata,
    ComMicrosoftArcdataV1Beta6PostgreSql as PostgresCustomResource,
    ComMicrosoftArcdataV1Beta6PostgreSqlSpec as PostgresCustomResourceSpec,
    ComMicrosoftArcdataV1Beta6PostgreSqlSpecConfig as PostgresCustomResourceSpecConfig,
    ComMicrosoftArcdataV1Beta6PostgreSqlSpecConfigStartup as PostgresCustomResourceSpecConfigStartup,
    ComMicrosoftArcdataV1Beta6PostgreSqlSpecBackup as PostgresCustomResourceSpecBackup,
    ComMicrosoftArcdataV1Beta6PostgreSqlSpecSecurity as PostgresCustomResourceSpecSecurity,
    ComMicrosoftArcdataV1Beta6PostgreSqlSpecSecurityActiveDirectory as PostgresCustomResourceSpecActiveDirectory,
    ComMicrosoftArcdataV1Beta6PostgreSqlSpecSecurityActiveDirectoryConnector as PostgresCustomResourceSpecActiveDirectoryConnector,
    ComMicrosoftArcdataV1Beta6PostgreSqlSpecScheduling as PostgresCustomResourceSpecScheduling,
    ComMicrosoftArcdataV1Beta6PostgreSqlSpecSchedulingDefault as PostgresCustomResourceSpecSchedulingDefault,
    ComMicrosoftArcdataV1Beta6PostgreSqlSpecSchedulingDefaultResources as PostgresCustomResourceSpecSchedulingDefaultResources,
    ComMicrosoftArcdataV1Beta6PostgreSqlSpecServices as PostgresCustomResourceSpecServices,
    ComMicrosoftArcdataV1Beta6PostgreSqlSpecServicesPrimary as PostgresCustomResourceSpecServicesPrimary,
    ComMicrosoftArcdataV1Beta6PostgreSqlSpecStorage as PostgresCustomResourceSpecStorage,
    ComMicrosoftArcdataV1Beta6PostgreSqlSpecStorageData as PostgresCustomResourceSpecStorageData,
    ComMicrosoftArcdataV1Beta6PostgreSqlSpecStorageBackups as PostgresCustomResourceSpecStorageBackups,
    ComMicrosoftArcdataV1Beta6PostgreSqlSpecStorageDataVolumesItem as PostgresCustomResourceSpecStorageDataVolumesItem,
    ComMicrosoftArcdataV1Beta6PostgreSqlSpecStorageLogs as PostgresCustomResourceSpecStorageLogs,
    ComMicrosoftArcdataV1Beta6PostgreSqlSpecStorageLogsVolumesItem as PostgresCustomResourceSpecStorageLogsVolumesItem,
    ComMicrosoftArcdataV1Beta6PostgreSqlSpecStorageBackupsVolumesItem as PostgresCustomResourceSpecStorageBackupsVolumesItem,
    ComMicrosoftArcdataPostgresqlTasksV1Beta1PostgreSqlRestoreTask as PostgreSqlRestoreTask,
    ComMicrosoftArcdataPostgresqlTasksV1Beta1PostgreSqlRestoreTaskSpec as PostgreSqlRestoreTaskSpec,
    ComMicrosoftArcdataPostgresqlTasksV1Beta1PostgreSqlRestoreTaskSpecDestinationStorage as RestoreTaskSpecStorage,
    ComMicrosoftArcdataPostgresqlTasksV1Beta1PostgreSqlRestoreTaskSpecDestinationStorageBackups as RestoreTaskSpecStorageBackups,
    ComMicrosoftArcdataPostgresqlTasksV1Beta1PostgreSqlRestoreTaskSpecDestinationStorageData as RestoreTaskSpecStorageData,
    ComMicrosoftArcdataPostgresqlTasksV1Beta1PostgreSqlRestoreTaskSpecDestinationStorageLogs as RestoreTaskSpecStorageLogs,
    ComMicrosoftArcdataPostgresqlTasksV1Beta1PostgreSqlRestoreTaskSpecDestinationStorageBackupsVolumesItem as RestoreTaskSpecStorageBackupsVolumesItem,
    ComMicrosoftArcdataPostgresqlTasksV1Beta1PostgreSqlRestoreTaskSpecDestinationStorageDataVolumesItem as RestoreTaskSpecStorageDataVolumesItem,
    ComMicrosoftArcdataPostgresqlTasksV1Beta1PostgreSqlRestoreTaskSpecDestinationStorageLogsVolumesItem as RestoreTaskSpecStorageLogsVolumesItem,
)

from azext_arcdata.ad_connector.validators import _validate_domain_name

from azext_arcdata.ad_connector.util import _get_ad_connector_custom_resource

from azext_arcdata.core.prompt import (
    prompt,
    prompt_pass,
    prompt_y_n,
)

from azext_arcdata.core.util import (
    FileUtil,
    is_windows,
    retry,
    check_and_set_kubectl_context,
    get_config_from_template,
    name_meets_dns_requirements,
    parse_cert_files,
)

from azext_arcdata.vendored_sdks.kubernetes_sdk.util import (
    validate_certificate_secret,
    create_certificate_secret,
)

from azext_arcdata.core.constants import (
    AZDATA_PASSWORD,
    ARC_GROUP,
    AZDATA_USERNAME,
    CERT_ARGUMENT_ERROR_TEMPLATE,
    DATA_CONTROLLER_PLURAL,
    DNS_NAME_REQUIREMENTS,
)
from azext_arcdata.core.kubernetes import (
    validate_rwx_storage_class,
)

from azext_arcdata.vendored_sdks.kubernetes_sdk.client import (
    KubernetesClient,
    K8sApiException,
    KubernetesError,
    http_status_codes,
)

from azext_arcdata.vendored_sdks.kubernetes_sdk.dc.constants import (
    DATA_CONTROLLER_CRD_NAME,
    POSTGRES_CRD_NAME,
)

from azext_arcdata.postgres.constants import (
    RESOURCE_KIND,
    API_GROUP,
    POSTGRES_MIN_CORES_SIZE,
    POSTGRES_MIN_MEMORY_SIZE,
    RESTORE_TASK_KIND,
    RESTORE_TASK_API_GROUP,
    RESTORE_TASK_API_VERSION,
)

from humanfriendly.terminal.spinners import AutomaticSpinner
from knack.cli import CLIError
from knack.log import get_logger
from knack.prompting import NoTTYException
from kubernetes import client as k8sClient
from urllib3.exceptions import NewConnectionError, MaxRetryError

__all__ = ["PostgreSqlClient"]

CONNECTION_RETRY_ATTEMPTS = 12
MAX_NAME_LENGTH = 13
RETRY_INTERVAL = 5
STORAGE_CLASS_ERROR = "Storage class '{}' does not exist"
SERVICE_TYPES = ["ClusterIP", "NodePort", "LoadBalancer", "ExternalName"]

logger = get_logger(__name__)


class PostgreSqlClient(object):
    def __init__(self, stdout, stderr):
        check_and_set_kubectl_context()
        self._client = KubernetesClient
        self.stdout = stdout
        self.stderr = stderr

    def create(
        self,
        name,
        namespace,
        path,
        admin_login_secret,
        certificate_private_key_file,
        certificate_public_key_file,
        cores_limit,
        cores_request,
        log_level,
        memory_limit,
        memory_request,
        service_annotations,
        service_certificate_secret,
        service_labels,
        service_type,
        storage_class_data,
        storage_class_logs,
        storage_class_backups,
        volume_size_data,
        volume_size_logs,
        volume_size_backups,
        no_external_endpoint,
        dev,
        port,
        nowait,
        ad_connector_name,
        ad_account_name,
        keytab_secret,
        dns_name,
        extensions=None,
        retention_days=None,
    ):
        """
        Create an Azure Arc enabled PostgreSQL server.
        :param name: The name of the Azure Arc enabled PostgreSQL server.
        :param namespace: Namespace where the Azure Arc enabled PostgreSQL server is deployed.
        :param path: The src filepath of the postgres resource.
        :param admin_login_secret: Name of the Kubernetes secret to generate that hosts or will
            host user admin login account credential.
        :param certificate_private_key_file: Path to the file containing a PEM formatted
            certificate private key to be used for client SSL connections.
        :param certificate_public_key_file: Path to the file containing a PEM formatted certificate
            public key to be used for client SSL connections.
        :param cores_limit: The limit of cores of the managed instance in integer number of vCores.
        :param cores_request: The request for cores of the managed instance in integer number of
            vCores.
        :param log_level: Sets the log_min_messages setting for the PostgreSQL engine.
        :param memory_limit: The limit of the capacity of the managed instance in integer amount
            of memory.
        :param memory_request: The request for the capacity of the managed instance in integer
            amount of memory.
        :param service_annotations: Comma-separated list of annotations to apply to all external
            services.
        :param service_certificate_secret: Name of the Kubernetes secret to generate that hosts
            the SSL certificate.
        :param service_labels: Comma-separated list of labels to apply to all external services.
        :param service_type: The type for the primary service.
        :param storage_class_data: The storage classes to be used for data persistent volumes.
        :param storage_class_logs: The storage classes to be used for logs persistent volumes.
        :param storage_class_backup: The storage classes to be used for logs persistent volumes.
        :param volume_size_data: The volume size for the storage classes to be used for data.
        :param volume_size_logs: The volume size for the storage classes to be used for logs.
        :param volume_size_backup: The volume size for the storage classes to be used for logs.
        :param no_external_endpoint: If not specified, an external service is created using the
            same service type as the data controller.
        :param dev: If this is specified, then it is considered a dev instance and will not be
            billed for.
        :param port: Optional parameter for the service port.
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
        """
        stdout = self.stdout
        check_and_set_kubectl_context()

        crd = _get_postgres_crd()
        crd_version = crd.spec.versions[-1].name

        _is_valid_connectivity_mode(namespace)

        api_version = f"{API_GROUP}/{crd_version}"

        if not path:
            custom_resource = PostgresCustomResource()
            custom_resource.kind = RESOURCE_KIND
            data_size = volume_size_data or "5Gi"
            logs_size = volume_size_logs or "5Gi"
            backups_size = volume_size_backups or "5Gi"
            memory_size = memory_request or "256Mi"

            self.apply_args(
                custom_resource,
                name,
                namespace,
                cores_limit,
                cores_request,
                log_level,
                memory_limit,
                memory_size,
                storage_class_data,
                storage_class_logs,
                storage_class_backups,
                data_size,
                logs_size,
                backups_size,
                api_version,
                dev,
                port,
                retention_days,
                extensions,
                ad_connector_name,
                ad_account_name,
                keytab_secret,
                dns_name,
            )
        else:
            spec_object = FileUtil.read_json(path)
            custom_resource = PostgresCustomResource.from_dict(spec_object)

            if not custom_resource.metadata.name:
                custom_resource.metadata.name = name
            elif not custom_resource.metadata.name == name:
                raise CLIError(
                    f"The name parameter '{name}' does not match the name "
                    f"'{custom_resource.metadata.name}' found in {path}"
                )

            if not custom_resource.metadata.namespace:
                custom_resource.metadata.namespace = namespace
            elif not custom_resource.metadata.namespace == namespace:
                raise CLIError(
                    f"The namespace parameter '{namespace}' does not match the"
                    f" namespace '{custom_resource.metadata.namespace}' found "
                    f"in {path}"
                )

        _validate_custom_resource(custom_resource)

        custom_object_exists = self.check_custom_object_exists(
            custom_resource.metadata.name,
            custom_resource.metadata.namespace,
            crd,
        )

        if custom_object_exists:
            raise ValueError(
                f"Postgres Server `{custom_resource.metadata.name}` already "
                f"exists in namespace `{custom_resource.metadata.namespace}`."
            )

        if not no_external_endpoint:
            self.set_external_service_type(custom_resource, service_type)
            self.set_external_service_annotations(
                custom_resource, service_annotations
            )
            self.set_external_service_labels(custom_resource, service_labels)

        if admin_login_secret:
            secret_name = admin_login_secret
        else:
            secret_name = custom_resource.metadata.name + "-login-secret"

        if not custom_resource.spec.security:
            custom_resource.spec.security = PostgresCustomResourceSpecSecurity(
                admin_login_secret=secret_name
            )
        else:
            custom_resource.spec.security.admin_login_secret = secret_name

        secret_exists = self.check_secret_exists(
            custom_resource.metadata.namespace,
            secret_name,
        )

        if not secret_exists:
            self.create_login_secret(custom_resource, stdout, secret_name)

        if (
            certificate_private_key_file
            or certificate_public_key_file
            or service_certificate_secret
        ):
            self.create_service_cert_secret(
                custom_resource,
                certificate_public_key_file,
                certificate_private_key_file,
                service_certificate_secret,
            )

        self.create_custom_object(custom_resource, crd)

        if nowait:
            stdout(
                f"Deployed {custom_resource.metadata.name} in namespace "
                f"`{custom_resource.metadata.name}`. Please use "
                "`az postgres server-arc show -n "
                f"{custom_resource.metadata.name} --namespace "
                f"{custom_resource.metadata.namespace}` to check its status."
            )
        else:
            self.wait_for_resource_ready(custom_resource, crd, stdout)

    def update(
        self,
        name,
        namespace,
        path,
        certificate_private_key_file,
        certificate_public_key_file,
        cores_limit,
        cores_request,
        log_level,
        memory_limit,
        memory_request,
        no_external_endpoint,
        service_annotations,
        service_certificate_secret,
        service_labels,
        service_type,
        dev,
        port,
        nowait,
        retention_days,
        keytab_secret,
        extensions,
    ):
        """
        Update the configuration of an Azure Arc enabled PostgreSQL server.
        :param name: The name of the Azure Arc enabled PostgreSQL server you would like to update.
        :param namespace: Namespace where the Azure Arc enabled PostgreSQL server is deployed.
        :param path: The path to the source json file for the Azure Arc enabled PostgreSQL server.
            This is optional.
        :param certificate_private_key_file: Path to the file containing a PEM formatted
            certificate private key to be used for client SSL connections.
        :param certificate_public_key_file: Path to the file containing a PEM formatted certificate
            public key to be used for client SSL connections.
        :param cores_limit: The limit of cores of the managed instance in integer number of vCores.
        :param cores_request: The request for cores of the managed instance in integer number of
            vCores.
        :param log_level: Sets the log_min_messages setting for the PostgreSQL engine.
        :param memory_limit: The limit of the capacity of the managed instance in integer amount of
            memory in GBs.
        :param memory_request: The request for the capacity of the managed instance in integer
            amount of memory in GBs.
        :param no_external_endpoint: If not specified, an external service is created using the
            same service type as the data controller.
        :param service_annotations: Comma-separated list of annotations to apply to all external
            services.
        :param service_certificate_secret: Name of the Kubernetes secret to generate that hosts
            the SSL certificate.
        :param service_labels: Comma-separated list of labels to apply to all external services.
        :param service_type: The type for the primary service.
        :param dev: If this is specified, then it is considered a dev instance and will not be
            billed for.
        :param port: Optional parameter for the service port.
        :param nowait: Do not wait for deployment to be ready before returning.
        :param keytab_secret: The name of the Kubernetes secret that contains the keytab
            file for this Azure Arc enabled PostgreSQL server.
        """
        stdout = self.stdout
        check_and_set_kubectl_context()

        # Get the Postgres resource
        crd = _get_postgres_crd()
        crd_version = crd.spec.versions[-1].name
        api_version = f"{API_GROUP}/{crd_version}"

        existing_cr = self.get_custom_object(name, namespace, crd)

        if existing_cr is None:
            raise CLIError(
                f"Azure Arc enabled PostgreSQL server {name} not found."
            )

        body = copy.deepcopy(existing_cr)
        updated_cr: PostgresCustomResource = PostgresCustomResource.from_dict(
            body
        )

        if path:
            # Load the spec from a file if provided
            update_data = FileUtil.read_json(path)
            update_spec: PostgresCustomResource = (
                PostgresCustomResource.from_dict(update_data)
            )

            if not update_spec.metadata.name:
                update_spec.metadata.name = name
            elif not update_spec.metadata.name == name:
                raise CLIError(
                    f"The name parameter '{name}' does not match the name "
                    f"'{update_spec.metadata.name}' found in {path}"
                )

            if not update_spec.metadata.namespace:
                update_spec.metadata.namespace = namespace
            elif not update_spec.metadata.namespace == namespace:
                raise CLIError(
                    f"The namespace parameter '{namespace}' does not match the"
                    f" namespace '{update_spec.metadata.namespace}' found in "
                    f"{path}"
                )

            if update_spec.spec.scheduling and (
                update_spec.spec.scheduling.default
            ):
                sched_default = update_spec.spec.scheduling.default
                if sched_default.resources and sched_default.resources.limits:
                    cores_limit = sched_default.resources.limits.get(
                        "cpu", None
                    )
                    memory_limit = sched_default.resources.limits.get(
                        "memory", None
                    )

                if sched_default.resources and (
                    sched_default.resources.requests
                ):
                    cores_request = sched_default.resources.requests.get(
                        "cpu", None
                    )
                    memory_request = sched_default.resources.requests.get(
                        "memory", None
                    )

            if update_spec.spec.services and update_spec.spec.services.primary:
                primary_svc = update_spec.spec.services.primary
                if primary_svc.port:
                    port = primary_svc.port

                if primary_svc.annotations:
                    existing_annotations = ",".join(
                        f"{item}={primary_svc.annotations[item]}"
                        for item in primary_svc.annotations
                    )

                    if service_annotations is None:
                        service_annotations = existing_annotations
                    else:
                        service_annotations += f",{existing_annotations}"

                if primary_svc.labels:
                    existing_labels = ",".join(
                        f"{item}={primary_svc.labels[item]}"
                        for item in primary_svc.labels
                    )

                    if service_labels is None:
                        service_labels = existing_labels
                    else:
                        service_labels += f",{existing_labels}"

        self.apply_args(
            updated_cr,
            name,
            namespace,
            cores_limit,
            cores_request,
            log_level,
            memory_limit,
            memory_request,
            storage_class_data=None,
            storage_class_logs=None,
            storage_class_backups=None,
            volume_size_data=None,
            volume_size_logs=None,
            volume_size_backups=None,
            api_version=api_version,
            dev=dev,
            port=port,
            retention_days=retention_days,
            extensions=extensions,
            ad_connector_name=None,
            ad_account_name=None,
            keytab_secret=keytab_secret,
            dns_name=None,
        )

        # Run validations that examine multiple custom resource properties
        #
        _validate_custom_resource(updated_cr)

        if keytab_secret:
            if (
                updated_cr.spec.security
                and not updated_cr.spec.security.active_directory
            ):
                raise CLIError(
                    "Cannot update Active Directory (AD) keytab if this "
                    "instance does not have AD enabled."
                )
            _validate_keytab_secret(namespace, keytab_secret)

        if not no_external_endpoint:
            self.set_external_service_type(updated_cr, service_type)
            self.set_external_service_annotations(
                updated_cr, service_annotations
            )
            self.set_external_service_labels(updated_cr, service_labels)

        # Replace SSL certs if provided
        #
        if (
            certificate_private_key_file
            or certificate_public_key_file
            or service_certificate_secret
        ):
            self.create_service_cert_secret(
                updated_cr,
                certificate_public_key_file,
                certificate_private_key_file,
                service_certificate_secret,
            )

        # Replace CR
        self.replace_custom_object(updated_cr, crd)

        if nowait:
            stdout(
                f"Updated {updated_cr.metadata.name} in namespace "
                f"`{updated_cr.metadata.namespace}`. Please use "
                "`az postgres server-arc show -n "
                f"{updated_cr.metadata.name} --namespace "
                f"{updated_cr.metadata.namespace}` to check its status."
            )
        else:
            # Wait for the CR to reflect new state
            time.sleep(5)

            self.wait_for_resource_ready(updated_cr, crd, stdout)

    def restore(
        self,
        name,
        namespace,
        source_name,
        destination_name,
        restore_point,
        storage_class_data,
        storage_class_logs,
        storage_class_backups,
        volume_size_data,
        volume_size_logs,
        volume_size_backups,
        dry_run,
        nowait,
    ):
        """
        Restores the source PostgreSql resource to a new PostgreSql resource
        with the given destination name.
        :param name: The name of the Azure Arc enabled PostgreSQL server you
        would like to update.
        :param namespace: Namespace where the Azure Arc enabled PostgreSQL
        server is deployed.
        :param source_name: The name of the PostgreSql resource to restore.
        :param destination_name: The name of the destination PostgreSql
        resource to create.
        :param restore_point: The point in time to restore to.
        :param dry_run: If set, validates the source and destination resources,
        and the restore time.
        :param nowait: Do not wait for deployment to be ready before returning.
        """
        check_and_set_kubectl_context()

        data_storage = None
        if storage_class_data or volume_size_data:
            data_volume = RestoreTaskSpecStorageDataVolumesItem(
                class_name=storage_class_data, size=volume_size_data
            )
            data_storage = RestoreTaskSpecStorageData(volumes=[data_volume])

        logs_storage = None
        if storage_class_logs or volume_size_logs:
            logs_volume = RestoreTaskSpecStorageLogsVolumesItem(
                class_name=storage_class_logs, size=volume_size_logs
            )
            logs_storage = RestoreTaskSpecStorageLogs(volumes=[logs_volume])

        backups_storage = None
        if storage_class_backups or volume_size_backups:
            backups_volume = RestoreTaskSpecStorageBackupsVolumesItem(
                class_name=storage_class_backups, size=volume_size_backups
            )
            backups_storage = RestoreTaskSpecStorageBackups(
                volumes=[backups_volume]
            )

        restore_task_storage_spec = None
        if data_storage or logs_storage or backups_storage:
            restore_task_storage_spec = RestoreTaskSpecStorage(
                data=data_storage, logs=logs_storage, backups=backups_storage
            )

        restore_task_spec = PostgreSqlRestoreTaskSpec(
            destination_name=destination_name,
            restore_point=restore_point,
            source_name=source_name,
            destination_storage=restore_task_storage_spec,
            dry_run=dry_run,
        )

        metadata = PostgresCustomResourceMetadata(
            name=name,
            namespace=namespace,
        )

        restore_task = PostgreSqlRestoreTask(
            api_version=f"{RESTORE_TASK_API_GROUP}/{RESTORE_TASK_API_VERSION}",
            kind=RESTORE_TASK_KIND,
            metadata=metadata,
            spec=restore_task_spec,
        )

        api = k8sClient.CustomObjectsApi()
        body = restore_task.as_dict(
            key_transformer=last_restapi_key_transformer
        )

        crd = _get_postgres_restore_task_crd()

        _execute_with_retry(
            api.create_namespaced_custom_object,
            RESTORE_TASK_API_GROUP,
            crd.spec.versions[-1].name,
            restore_task.metadata.namespace,
            crd.spec.names.plural,
            body,
        )

        if nowait:
            self.stdout(
                f"PostgreSqlRestoreTask {name} created to restore PostgreSql "
                f"resource {source_name} to {destination_name}"
            )
        else:
            self.stdout(f"Deploying {name} in namespace `{namespace}`")

            custom_object = self.get_custom_object(name, namespace, crd)
            deployed_task = PostgreSqlRestoreTask.from_dict(custom_object)

            while not _is_instance_ready(deployed_task):
                if _is_instance_in_error(deployed_task):
                    self.stdout(
                        f"{deployed_task.metadata.name} is in an"
                        f"error state: {_get_error_message(deployed_task)}"
                    )
                    break

                time.sleep(5)
                custom_object = self.get_custom_object(name, namespace, crd)
                deployed_task = PostgreSqlRestoreTask.from_dict(custom_object)

            if _is_instance_ready(deployed_task):
                result = {
                    "earliest_restore_time": deployed_task.status.earliest_restore_time.strftime(
                        "%Y-%m-%dT%H:%M:%S.%fZ"
                    ),
                    "latest_restore_time": deployed_task.status.latest_restore_time.strftime(
                        "%Y-%m-%dT%H:%M:%S.%fZ"
                    ),
                    "last_update_time": deployed_task.status.last_update_time.strftime(
                        "%Y-%m-%dT%H:%M:%S.%fZ"
                    ),
                    "message": deployed_task.status.message,
                    "state": deployed_task.status.state,
                }
                self.stdout(f"{json.dumps(result, indent=4)}")

    def delete(self, name, namespace, force):
        """
        Delete an Azure Arc enabled PostgreSQL server.
        :param name: The name of the Azure Arc enabled PostgreSQL server you would like to update.
        :param namespace: Namespace where the Azure Arc enabled PostgreSQL server is deployed.
        :param force: A boolean indicating whether to delete the Azure Arc enabled PostgreSQL
            server without confirmation.
        """
        stdout = self.stdout

        check_and_set_kubectl_context()

        crd = _get_postgres_crd()
        existing_cr = self.get_custom_object(name, namespace, crd)

        _is_valid_connectivity_mode(namespace)

        if existing_cr is None:
            raise CLIError(
                f"Azure Arc enabled PostgreSQL server {name} not found."
            )

        try:
            yes = force or prompt_y_n(
                "Do you want to delete Azure Arc enabled PostgreSQL "
                f"server {name}?"
            )
        except NoTTYException as err:
            raise CLIError(
                "Please specify --force in non-interactive mode."
            ) from err

        if not yes:
            stdout(f"Azure Arc enabled PostgreSQL server {name} not deleted.")
            return

        try:
            api = k8sClient.CustomObjectsApi()
            api.delete_namespaced_custom_object(
                group=crd.spec.group,
                version=crd.spec.versions[-1].name,
                plural=crd.spec.names.plural,
                namespace=namespace,
                name=name,
                body=k8sClient.V1DeleteOptions(),
            )

        except Exception as err:
            raise KubernetesError(err) from err

        stdout(
            f"Deleted Azure Arc enabled PostgreSQL server {name} "
            f"from namespace {namespace}"
        )

        stdout(
            "Note: Deleting a server does not remove its associated "
            "storage. Reach out to your Kubernetes administrator or "
            "read documentation article 'Delete an Azure Arc enabled"
            " PostgreSQL server' for possible next steps."
        )

    def show(self, name, namespace, path):
        """
        Show the details of an Azure Arc enabled PostgreSQL server.
        :param name: Name of the Azure Arc enabled PostgreSQL server.
        :param namespace: Namespace where the Azure Arc enabled PostgreSQL server is deployed.
        :param path: A path to a json file where the full specification for the Azure Arc enabled
            PostgreSQL server should be written.
        :param use_k8s: Use the current kubeconfig to perform this action.
        """
        stdout = self.stdout
        check_and_set_kubectl_context()

        crd = _get_postgres_crd()
        custom_resource = self.get_custom_object(name, namespace, crd)
        if custom_resource is None:
            raise CLIError(
                f"Azure Arc enabled PostgreSQL server {name} not found."
            )

        if path:
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join(path, f"{name}.json")
            with open(path, "w") as outfile:
                json.dump(custom_resource, outfile, indent=4)
            stdout(f"{name} specification written to {path}")
        else:
            return custom_resource

    def list(self, namespace):
        """
        List Azure Arc enabled PostgreSQL servers.
        :param namespace: Namespace where the Azure Arc enabled PostgreSQL servers are deployed.
        :param use_k8s: Use the current kubeconfig to perform this action.
        """
        check_and_set_kubectl_context()

        crd = _get_postgres_crd()
        crd_version = crd.spec.versions[-1].name

        response = KubernetesClient.list_namespaced_custom_object(
            namespace,
            group=API_GROUP,
            version=crd_version,
            plural=crd.spec.names.plural,
        )

        items = response.get("items")

        result = []
        items.sort(key=lambda i: i["kind"] + "\n" + i["metadata"]["name"])
        for item in items:
            custom_resource = PostgresCustomResource.from_dict(item)
            result.append(
                {
                    "desiredVersion": (
                        custom_resource.spec.update.desiredVersion
                        if custom_resource.spec.update
                        else None
                    ),
                    "name": custom_resource.metadata.name,
                    "primaryEndpoint": custom_resource.status.primary_endpoint,
                    "replicas": "{}/1".format(
                        1 if custom_resource.status.state == "Ready" else 0
                    ),
                    "runningVersion": custom_resource.status.running_version,
                    "state": custom_resource.status.state,
                }
            )

        return result

    def endpoint_list(self, name, namespace):
        check_and_set_kubectl_context()
        crd = _get_postgres_crd()

        custom_resources = []

        if name:
            custom_object = self.get_custom_object(name, namespace, crd)
            if custom_object is None:
                raise CLIError(
                    f"Azure Arc enabled PostgreSQL server {name} not found."
                )

            custom_resource = PostgresCustomResource.from_dict(custom_object)
            custom_resources.append(custom_resource)
        else:
            response = KubernetesClient.list_namespaced_custom_object(
                namespace,
                group=API_GROUP,
                version=KubernetesClient.get_crd_version(POSTGRES_CRD_NAME),
                plural=crd.spec.names.plural,
            )
            items = response.get("items")

            for item in items:
                custom_resource = PostgresCustomResource.from_dict(item)
                if custom_resource:
                    custom_resources.append(custom_resource)

        arc_postgres_endpoints = {"namespace": namespace}
        instances = []

        # Loop through the specified custom resources and retrieve their
        # endpoints from their status
        for custom_resource in custom_resources:
            endpoints = []

            if custom_resource.status:
                descrip_str = "description"
                endpoint_str = "endpoint"

                # Connection string
                ext_endpoint = custom_resource.status.primary_endpoint
                username = self.get_username(custom_resource)

                if ext_endpoint:
                    connection_str = (
                        f"postgresql://{username}:<replace with password>@"
                        f"{ext_endpoint}"
                    )
                else:
                    connection_str = "Not yet available"

                endpoints.append(
                    {
                        descrip_str: "PostgreSQL Instance",
                        endpoint_str: connection_str,
                    }
                )

                # Logs
                logs_endpoint = custom_resource.status.log_search_dashboard
                endpoints.append(
                    {
                        descrip_str: "Log Search Dashboard",
                        endpoint_str: logs_endpoint,
                    }
                )

                # Metrics
                metrics_endpoint = custom_resource.status.metrics_dashboard
                endpoints.append(
                    {
                        descrip_str: "Metrics Dashboard",
                        endpoint_str: metrics_endpoint,
                    }
                )

            instances.append(
                {
                    "name": custom_resource.metadata.name,
                    "engine": custom_resource.kind,
                    "endpoints": endpoints,
                }
            )

        arc_postgres_endpoints["instances"] = instances

        return arc_postgres_endpoints

    def apply_args(
        self,
        custom_resource: PostgresCustomResource,
        name,
        namespace,
        cores_limit,
        cores_request,
        log_level,
        memory_limit,
        memory_request,
        storage_class_data,
        storage_class_logs,
        storage_class_backups,
        volume_size_data,
        volume_size_logs,
        volume_size_backups,
        api_version,
        dev,
        port,
        retention_days,
        extensions,
        ad_connector_name,
        ad_account_name,
        keytab_secret,
        dns_name,
    ):
        if not custom_resource.metadata:
            custom_resource.metadata = PostgresCustomResourceMetadata()

        custom_resource.metadata.name = name
        custom_resource.metadata.namespace = namespace

        if not custom_resource.spec:
            custom_resource.spec = PostgresCustomResourceSpec()

        if not custom_resource.spec.scheduling:
            scheduling = PostgresCustomResourceSpecScheduling()
            custom_resource.spec.scheduling = scheduling

        if not custom_resource.spec.scheduling.default:
            default = PostgresCustomResourceSpecSchedulingDefault()
            custom_resource.spec.scheduling.default = default

        if not custom_resource.spec.scheduling.default.resources:
            resources = PostgresCustomResourceSpecSchedulingDefaultResources(
                limits={}, requests={}
            )
            custom_resource.spec.scheduling.default.resources = resources

        if not custom_resource.spec.scheduling.default.resources.limits:
            custom_resource.spec.scheduling.default.resources.limits = {}

        if not custom_resource.spec.scheduling.default.resources.requests:
            custom_resource.spec.scheduling.default.resources.requests = {}

        if cores_limit or cores_limit == "":
            custom_resource.spec.scheduling.default.resources.limits["cpu"] = (
                cores_limit
            )

        if memory_limit or memory_limit == "":
            custom_resource.spec.scheduling.default.resources.limits[
                "memory"
            ] = memory_limit

        if cores_request or cores_request == "":
            custom_resource.spec.scheduling.default.resources.requests[
                "cpu"
            ] = cores_request

        if memory_request or memory_request == "":
            custom_resource.spec.scheduling.default.resources.requests[
                "memory"
            ] = memory_request

        if not custom_resource.spec.services:
            services = PostgresCustomResourceSpecServices()
            custom_resource.spec.services = services

        if not custom_resource.spec.services.primary:
            primary = PostgresCustomResourceSpecServicesPrimary()
            custom_resource.spec.services.primary = primary

        if port:
            custom_resource.spec.services.primary.port = port

        if dns_name:
            custom_resource.spec.services.primary.dns_name = dns_name

        # AD configurations
        #
        if ad_connector_name:
            active_directory_connector = PostgresCustomResourceSpecActiveDirectoryConnector(
                name=ad_connector_name,
                namespace=namespace,  # Note: In line with SQL MI cli, but might not be equal in cross-namespace scenario
            )

            active_directory = PostgresCustomResourceSpecActiveDirectory(
                connector=active_directory_connector,
                keytab_secret=keytab_secret,
                account_name=ad_account_name,
            )

            custom_resource.spec.security = PostgresCustomResourceSpecSecurity(
                active_directory=active_directory,
            )

        if not custom_resource.spec.storage:
            data_volume = PostgresCustomResourceSpecStorageDataVolumesItem(
                class_name=storage_class_data, size=volume_size_data
            )
            data_storage = PostgresCustomResourceSpecStorageData(
                volumes=[data_volume]
            )

            logs_volume = PostgresCustomResourceSpecStorageLogsVolumesItem(
                class_name=storage_class_logs, size=volume_size_logs
            )
            logs_storage = PostgresCustomResourceSpecStorageLogs(
                volumes=[logs_volume]
            )

            backups_volume = (
                PostgresCustomResourceSpecStorageBackupsVolumesItem(
                    class_name=storage_class_backups, size=volume_size_backups
                )
            )
            backups_storage = PostgresCustomResourceSpecStorageBackups(
                volumes=[backups_volume]
            )

            storage = PostgresCustomResourceSpecStorage(
                data=data_storage,
                logs=logs_storage,
                backups=backups_storage,
            )
            custom_resource.spec.storage = storage

        custom_resource.api_version = api_version
        custom_resource.spec.dev = dev

        if retention_days is not None:
            custom_resource.spec.backup = PostgresCustomResourceSpecBackup(
                retention_period_in_days=retention_days
            )

        if log_level:
            if custom_resource.spec.settings is None:
                custom_resource.spec.settings = {}

            custom_resource.spec.settings["log_min_messages"] = log_level

            if log_level.startswith("DEBUG"):
                if custom_resource.spec.config is None:
                    custom_resource.spec.config = (
                        PostgresCustomResourceSpecConfig()
                    )

                custom_resource.spec.config.startup = (
                    PostgresCustomResourceSpecConfigStartup(
                        initdb_debug_flag=True
                    )
                )

        if extensions:
            if custom_resource.spec.config is None:
                custom_resource.spec.config = PostgresCustomResourceSpecConfig()

            custom_resource.spec.config.postgre_sql_extensions = extensions

            if len(extensions) > 0:
                shared_preload_libs = {
                    "pg_cron",
                    "pglogical",
                    "pg_partman_bgw",
                    "timescaledb",
                    "pgaudit",
                    "pg_repack",
                }
                extension_list = list(
                    set(
                        [s.strip().lower() for s in extensions.split(",")]
                    ).intersection(shared_preload_libs)
                )
                shared_libs = (
                    "'" + ",".join([str(s) for s in extension_list]) + "'"
                )
                if shared_libs and custom_resource.spec.settings:
                    custom_resource.spec.settings[
                        "shared_preload_libraries"
                    ] = shared_libs

    def set_external_service_type(
        self, custom_resource: PostgresCustomResource, service_type
    ):
        if not service_type:
            api = k8sClient.CustomObjectsApi()
            obj_list = _execute_with_retry(
                api.list_namespaced_custom_object,
                ARC_GROUP,
                KubernetesClient.get_crd_version(DATA_CONTROLLER_CRD_NAME),
                custom_resource.metadata.namespace,
                DATA_CONTROLLER_PLURAL,
            )

            dcs = obj_list.get("items")
            if not dcs:
                raise CLIError(
                    "No data controller exists in namespace "
                    f"`{custom_resource.metadata.namespace}`. "
                    "Cannot set external endpoint argument."
                )
            else:
                dc_cr = CustomResource.decode(
                    DataControllerCustomResource, dcs[0]
                )

            service_type = dc_cr.get_controller_service().serviceType

            self.init_service_model(custom_resource)
        else:
            if service_type not in SERVICE_TYPES:
                raise ValueError(
                    f"Invalid service type: {service_type}. "
                    f"Must be one of {SERVICE_TYPES}"
                )

        custom_resource.spec.services.primary.type = service_type

    def set_external_service_annotations(
        self, custom_resource: PostgresCustomResource, annotations
    ):
        if annotations:
            items = annotations.split(",")

            self.init_service_model(custom_resource)

            custom_resource.spec.services.primary.annotations = {}

            for item in items:
                annotation = item.split("=")
                if len(annotation) == 2:
                    custom_resource.spec.services.primary.annotations[
                        annotation[0]
                    ] = annotation[1]
                else:
                    raise ValueError(
                        "Annotations must be formatted: 'name=value,...'"
                    )
        elif annotations == "":
            if custom_resource.spec.services and (
                custom_resource.spec.services.primary
            ):
                self.clear_all(
                    custom_resource.spec.services.primary.annotations
                )

    def set_external_service_labels(
        self, custom_resource: PostgresCustomResource, labels
    ):
        if labels:
            items = labels.split(",")

            self.init_service_model(custom_resource)

            custom_resource.spec.services.primary.labels = {}

            for item in items:
                label = item.split("=")
                if len(label) == 2:
                    custom_resource.spec.services.primary.labels[label[0]] = (
                        label[1]
                    )
                else:
                    raise ValueError(
                        "Labels must be formatted: 'name=value,...'"
                    )
        elif labels == "":
            if custom_resource.spec.services and (
                custom_resource.spec.services.primary
            ):
                self.clear_all(custom_resource.spec.services.primary.labels)

    def clear_all(self, dict):
        if dict:
            for key in dict.keys():
                dict[key] = ""

    def init_service_model(self, custom_resource: PostgresCustomResource):
        if not custom_resource.spec.services:
            services = PostgresCustomResourceSpecServices()
            custom_resource.spec.services = services
        if not custom_resource.spec.services.primary:
            primary = PostgresCustomResourceSpecServicesPrimary()
            custom_resource.spec.services.primary = primary

    def get_custom_object(self, name, namespace, crd):
        api = k8sClient.CustomObjectsApi()

        try:
            custom_object = retry(
                api.get_namespaced_custom_object,
                crd.spec.group,
                crd.spec.versions[-1].name,
                namespace,
                crd.spec.names.plural,
                name,
                retry_count=CONNECTION_RETRY_ATTEMPTS,
                retry_delay=RETRY_INTERVAL,
                retry_method="get_namespaced_custom_object",
                retry_on_exceptions=(
                    NewConnectionError,
                    MaxRetryError,
                ),
            )

            return custom_object
        except K8sApiException as e:
            if e.status == http_status_codes.not_found:
                return None
            else:
                raise

    def check_custom_object_exists(self, name, namespace, crd):
        return self.get_custom_object(name, namespace, crd) is not None

    def create_custom_object(
        self, custom_resource: PostgresCustomResource, crd
    ):
        api = k8sClient.CustomObjectsApi()
        body = custom_resource.as_dict(
            key_transformer=last_restapi_key_transformer
        )

        return _execute_with_retry(
            api.create_namespaced_custom_object,
            API_GROUP,
            crd.spec.versions[-1].name,
            custom_resource.metadata.namespace,
            crd.spec.names.plural,
            body,
        )

    def replace_custom_object(
        self, custom_resource: PostgresCustomResource, crd
    ):
        try:
            api = k8sClient.CustomObjectsApi()
            return api.replace_namespaced_custom_object(
                body=custom_resource.as_dict(
                    key_transformer=last_restapi_key_transformer
                ),
                namespace=custom_resource.metadata.namespace,
                plural=crd.spec.names.plural,
                group=API_GROUP,
                version=crd.spec.versions[-1].name,
                name=custom_resource.metadata.name,
            )

        except Exception as e:
            raise KubernetesError(e) from e

    def check_secret_exists(self, namespace, secret_name):
        return _execute_with_retry(
            KubernetesClient.secret_exists,
            namespace,
            secret_name,
        )

    def create_login_secret(
        self, custom_resource: PostgresCustomResource, stdout, secret_name
    ):
        username = os.environ.get(AZDATA_USERNAME)
        pw = os.environ.get(AZDATA_PASSWORD)

        if not username:
            if sys.stdin.isatty():
                username = prompt("Postgres Server username:")
            else:
                raise NoTTYException(
                    "Please provide a Postgres Server username through the env "
                    "variable AZDATA_USERNAME."
                )

            while username == "":
                username = prompt(
                    "Postgres Server username required. Enter a username:"
                )
        else:
            stdout(
                "Using AZDATA_USERNAME environment variable for "
                f"`{custom_resource.metadata.name}` username."
            )

        if not pw:
            if sys.stdin.isatty():
                pw = prompt_pass(
                    "Postgres Server password:",
                    confirm=True,
                    allow_empty=False,
                )
            else:
                raise NoTTYException(
                    "Please provide a Postgres Server password through the env "
                    "variable AZDATA_PASSWORD."
                )
        else:
            stdout(
                "Using AZDATA_PASSWORD environment variable for "
                f"`{custom_resource.metadata.name}` password."
            )

        model = {"secretName": secret_name}
        encoding = "utf-8"
        model["base64Username"] = base64.b64encode(
            bytes(username, encoding)
        ).decode(encoding)
        model["base64Password"] = base64.b64encode(bytes(pw, encoding)).decode(
            encoding
        )
        temp = get_config_from_template(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "templates",
                "postgres-login.yaml.tmpl",
            ),
            model,
        )
        postgres_secret = yaml.safe_load(temp)

        _execute_with_retry(
            KubernetesClient.create_secret,
            custom_resource.metadata.namespace,
            postgres_secret,
            True,
        )

    def get_username(self, custom_resource: PostgresCustomResource):
        if custom_resource.spec.security.admin_login_secret:
            secret_name = custom_resource.spec.security.admin_login_secret
        else:
            secret_name = custom_resource.metadata.name + "-login-secret"

        try:
            secret = KubernetesClient.get_secret(
                custom_resource.metadata.namespace, secret_name
            )

            username = base64.b64decode(secret.data["username"]).decode("utf-8")
        except Exception:
            username = "<username>"

        return username

    def create_service_cert_secret(
        self,
        custom_resource: PostgresCustomResource,
        certificate_public_key_file,
        certificate_private_key_file,
        service_certificate_secret,
    ):
        """
        Creates a secret for the service SSL certificate and private key
        """

        if not certificate_public_key_file and certificate_private_key_file:
            raise ValueError(
                "Certificate public key file path must be provided "
                "when private key path is provided."
            )

        if certificate_public_key_file and not certificate_private_key_file:
            raise ValueError(
                "Certificate private key file path must be provided "
                "when public key path is provided."
            )

        if (
            not certificate_public_key_file
            and not certificate_private_key_file
            and service_certificate_secret
        ):
            # The secret must exist
            secret_exists = self.check_secret_exists(
                custom_resource.metadata.namespace,
                service_certificate_secret,
            )

            if not secret_exists:
                raise ValueError(
                    f"Kubernetes secret '{service_certificate_secret}' does not exist. If you "
                    "intend to use a pre-existing secret, please provide the correct name. If you "
                    "intend to use a certificate from public key and private key files, please "
                    "provide their paths in the parameters --cert-public-key-file and "
                    "--cert-private-key-file."
                )

            validate_certificate_secret(
                KubernetesClient,
                custom_resource.metadata.namespace,
                service_certificate_secret,
            )

            custom_resource.spec.security.service_certificate_secret = (
                service_certificate_secret
            )
        else:
            secret_name = custom_resource.metadata.name + "-pg-cert-secret"
            if service_certificate_secret:
                secret_name = service_certificate_secret

            # The secret must NOT exist
            secret_exists = self.check_secret_exists(
                custom_resource.metadata.namespace,
                secret_name,
            )

            if secret_exists and service_certificate_secret:
                # Ask the user for a different name
                raise ValueError(
                    CERT_ARGUMENT_ERROR_TEMPLATE.format(
                        service_certificate_secret
                    )
                )

            if secret_exists:
                # Update the default name until we get an unused one
                while secret_exists:
                    timestamp = datetime.now().strftime("%m-%d-%Y-%H-%M-%S-%f")
                    new_name = secret_name + "-" + timestamp

                    secret_exists = self.check_secret_exists(
                        custom_resource.metadata.namespace,
                        new_name,
                    )

                    if not secret_exists:
                        secret_name = new_name

            # Validate and parse data from files.
            #
            public_key, private_key = parse_cert_files(
                certificate_public_key_file, certificate_private_key_file
            )

            # Create secret.
            #
            create_certificate_secret(
                KubernetesClient,
                custom_resource.metadata.namespace,
                secret_name,
                public_key,
                private_key,
            )

            custom_resource.spec.security.service_certificate_secret = (
                secret_name
            )

    def wait_for_resource_ready(
        self, custom_resource: PostgresCustomResource, crd, stdout
    ):
        created_obj = self.get_custom_object(
            custom_resource.metadata.name,
            custom_resource.metadata.namespace,
            crd,
        )
        deployed_cr = PostgresCustomResource.from_dict(created_obj)

        if not is_windows():
            with AutomaticSpinner(
                f"Deploying {custom_resource.metadata.name} in namespace "
                f"`{custom_resource.metadata.namespace}`",
                show_time=True,
            ):
                while not _is_instance_ready(deployed_cr):
                    if _is_instance_in_error(deployed_cr):
                        stdout(
                            f"{custom_resource.metadata.name} is in an "
                            f"error state:{_get_error_message(deployed_cr)}"
                        )
                        break

                    time.sleep(5)
                    updated_obj = self.get_custom_object(
                        custom_resource.metadata.name,
                        custom_resource.metadata.namespace,
                        crd,
                    )

                    deployed_cr = PostgresCustomResource.from_dict(updated_obj)
        else:
            stdout(
                f"Deploying {custom_resource.metadata.name} in namespace "
                f"`{custom_resource.metadata.namespace}`"
            )
            while not _is_instance_ready(deployed_cr):
                if _is_instance_in_error(deployed_cr):
                    stdout(
                        f"{custom_resource.metadata.name} is in "
                        f"error state:{_get_error_message(deployed_cr)}"
                    )
                    break

                time.sleep(5)
                updated_obj = self.get_custom_object(
                    custom_resource.metadata.name,
                    custom_resource.metadata.namespace,
                    crd,
                )

                deployed_cr = PostgresCustomResource.from_dict(updated_obj)

        if _is_instance_ready(deployed_cr):
            stdout(f"{custom_resource.metadata.name} is Ready")


def _validate_custom_resource(custom_resource: PostgresCustomResource):
    if not custom_resource.metadata.name:
        raise ValueError(
            "Azure Arc enabled PostgreSQL server name cannot be empty"
        )

    if len(custom_resource.metadata.name) > MAX_NAME_LENGTH:
        raise ValueError(
            "Azure Arc enabled PostgreSQL server name "
            f"'{custom_resource.metadata.name}' exceeds "
            f"{MAX_NAME_LENGTH} character length limit"
        )

    if not name_meets_dns_requirements(custom_resource.metadata.name):
        raise ValueError(
            "Azure Arc enabled PostgreSQL server name "
            f"'{custom_resource.metadata.name}' does not follow DNS "
            f"requirements: {DNS_NAME_REQUIREMENTS}"
        )

    # -- validate active directory args if provided --
    #
    if (
        custom_resource.spec.security
        and custom_resource.spec.security.active_directory
    ):
        if not custom_resource.spec.security.active_directory.connector.name:
            raise ValueError(
                "To enable Active Directory (AD) authentication, the resource name of the AD connector is required."
            )

        if not custom_resource.spec.security.active_directory.account_name:
            raise ValueError(
                "The Active Directory account name for this Azure Arc enabled PostgreSQL server is missing or invalid."
            )

        if not custom_resource.spec.services.primary.dns_name:
            raise ValueError(
                "The DNS name for this Azure Arc enabled PostgreSQL server is missing or invalid."
            )

        if not custom_resource.spec.security.active_directory.keytab_secret:
            raise ValueError(
                "A keytab secret is required when Active Directory is enabled for Azure Arc enabled PostgreSQL server."
            )

        _validate_keytab_secret(
            custom_resource.metadata.namespace,
            custom_resource.spec.security.active_directory.keytab_secret,
        )
        _validate_ad_connector(
            KubernetesClient,
            custom_resource.spec.security.active_directory.connector.name,
            custom_resource.spec.security.active_directory.connector.namespace,
        )
        _validate_dns_service(
            name=custom_resource.spec.services.primary.dns_name,
            port=custom_resource.spec.services.primary.port,
            type="primary",
        )

    limits = custom_resource.spec.scheduling.default.resources.limits
    requests = custom_resource.spec.scheduling.default.resources.requests

    if "memory" in requests and requests["memory"] != "":
        val = KubeQuantity(requests["memory"])
        if val < POSTGRES_MIN_MEMORY_SIZE:
            raise ValueError(
                "Postgres memory request must be at least "
                f"'{POSTGRES_MIN_MEMORY_SIZE.quantity}'"
            )

    if "cpu" in requests and requests["cpu"] != "":
        val = KubeQuantity(str(requests["cpu"]))
        if val < POSTGRES_MIN_CORES_SIZE:
            raise ValueError(
                "Postgres cores request must be at least "
                f"'{POSTGRES_MIN_CORES_SIZE.quantity}'"
            )

    if "memory" in limits and limits["memory"] != "":
        val = KubeQuantity(limits["memory"])
        if val < POSTGRES_MIN_MEMORY_SIZE:
            raise ValueError(
                "Postgres memory limit must be at least "
                f"'{POSTGRES_MIN_MEMORY_SIZE.quantity}'"
            )

    if "cpu" in limits and limits["cpu"] != "":
        val = KubeQuantity(str(limits["cpu"]))
        if val < POSTGRES_MIN_CORES_SIZE:
            raise ValueError(
                "Postgres cores limit must be at least "
                f"'{POSTGRES_MIN_CORES_SIZE.quantity}'"
            )

    if "memory" in limits and "memory" in requests:
        mem_lim = limits["memory"]
        mem_req = requests["memory"]
        if mem_lim and mem_req:
            mem_lim_qty = KubeQuantity(mem_lim)
            mem_req_qty = KubeQuantity(mem_req)
            if mem_req_qty > mem_lim_qty:
                raise ValueError(
                    f"Memory request of {mem_req} cannot exceed memory "
                    f"limit of {mem_lim}"
                )

    if "cpu" in limits and "cpu" in requests:
        cpu_lim = str(limits["cpu"])
        cpu_req = str(requests["cpu"])
        if cpu_lim and cpu_req:
            cpu_lim_qty = KubeQuantity(cpu_lim)
            cpu_req_qty = KubeQuantity(cpu_req)
            if cpu_req_qty > cpu_lim_qty:
                raise ValueError(
                    f"Cores request of {cpu_req} cannot exceed cores "
                    f"limit of {cpu_lim}"
                )
    _validate_backup_storage(
        custom_resource.spec.storage.backups, custom_resource.spec.dev
    )
    _validate_storage(custom_resource.spec.storage.logs)
    _validate_storage(custom_resource.spec.storage.data)


def _validate_dns_service(name="", port=0, type="primary"):
    if not _validate_domain_name(name):
        raise ValueError(
            "The {0} DNS service name '{1}' is invalid.".format(type, name)
        )

    try:
        port = int(port)
        assert 0 < port <= 65535
        return True
    except:
        raise ValueError(
            "The {0} DNS service port '{1}' is invalid.".format(type, port)
        )


def _validate_ad_connector(client, name, namespace):
    if not name or not namespace:
        raise ValueError(
            "To enable Active Directory (AD) authentication, both the resource name and namespace of the AD connector are required."
        )

    check_and_set_kubectl_context()

    _get_ad_connector_custom_resource(client, name, namespace)


def _validate_keytab_secret(namespace, keytab_secret_name):
    """
    Validates that the given keytab secret exists
    """
    keytab_entry_in_secret = "keytab"

    if not keytab_secret_name:
        raise ValueError(
            "The name of the Kubernetes secret containing the Active Directory keytab is required."
        )

    check_and_set_kubectl_context()

    # Check if secret exists
    #
    #
    if not _execute_with_retry(
        KubernetesClient.secret_exists,
        namespace,
        keytab_secret_name,
    ):
        raise ValueError(
            "Kubernetes secret `{}` not found in namespace `{}`.".format(
                keytab_secret_name, namespace
            )
        )

    k8s_secret = retry(
        lambda: KubernetesClient.get_secret(namespace, keytab_secret_name),
        retry_method="get secret",
        retry_on_exceptions=(
            NewConnectionError,
            MaxRetryError,
            K8sApiException,
        ),
    )

    secret_data = k8s_secret.data

    # Check if keytab exists in the secret
    #
    if keytab_entry_in_secret not in secret_data:
        raise ValueError(
            "Kubernetes secret '{0}' does not have key '{1}'".format(
                keytab_secret_name, keytab_entry_in_secret
            )
        )


def _validate_storage(storage: PostgresCustomResourceSpecStorageData):
    if storage and storage.volumes:
        for v in storage.volumes:
            if v.class_name and not KubernetesClient.storage_class_exists(
                v.class_name
            ):
                raise ValueError(STORAGE_CLASS_ERROR.format(v.class_name))
            if v.size:
                KubeQuantity(v.size)


def _validate_backup_storage(
    storage: PostgresCustomResourceSpecStorageBackups,
    is_dev: PostgresCustomResourceSpec,
):
    if storage and storage.volumes:
        for v in storage.volumes:
            if v.class_name is None:
                continue
            elif not KubernetesClient.storage_class_exists(v.class_name):
                raise ValueError(STORAGE_CLASS_ERROR.format(v.class_name))
            if v.size:
                KubeQuantity(v.size)
            if is_dev is None:
                try:
                    validate_rwx_storage_class(
                        name=v.class_name,
                        storage_type="backup",
                        instance_type="Postgres",
                    )
                except Exception as e:
                    raise CLIError(
                        "Specify --dev option if not using a ReadWriteMany storage type for backups."
                    ) from e


def _get_postgres_crd():
    """
    Returns the PostgreSQL CRD.
    :return:
    """
    api = k8sClient.ApiextensionsV1Api()
    crds = api.list_custom_resource_definition()

    for crd in crds.items:
        if crd.spec.names.kind == RESOURCE_KIND:
            return crd

    raise CLIError("Unable to locate PostgreSQL custom resource definition.")


def _get_postgres_restore_task_crd():
    """
    Returns the PostgreSQLRestoreTask CRD.
    :return:
    """
    api = k8sClient.ApiextensionsV1Api()
    crds = api.list_custom_resource_definition()

    for crd in crds.items:
        if crd.spec.names.kind == RESTORE_TASK_KIND:
            return crd

    raise CLIError(
        "Unable to locate PostgreSQLRestoreTask custom resource definition."
    )


def _is_instance_ready(cr):
    """
    Check that the PostgreSQL or PostgreSQLRestoreTask instance is ready or
    completed.
    :param cr: Instance to check the readiness of
    :return: True if the instance is in error, False otherwise
    """
    return (
        cr.status
        and cr.metadata.generation == cr.status.observed_generation
        and cr.status.state is not None
        and (
            cr.status.state.lower() == "ready"
            or cr.status.state.lower() == "completed"
        )
    )


def _is_instance_in_error(cr):
    """
    Check that the PostgreSQL or PostgreSQLRestoreTask instance is in an error
    state.
    :param cr: Instance to check the readiness of
    :return: True if the instance is in error, False otherwise
    """
    return (
        cr.status
        and cr.status.state is not None
        and (
            cr.status.state.lower() == "error"
            or cr.status.state.lower() == "failed"
        )
    )


def _get_error_message(cr):
    """
    Get error message from the status of custom resource
    :param cr: Instance to get error message.
    """
    return cr.status.message


def _execute_with_retry(func, *args):
    return retry(
        func,
        *args,
        retry_count=CONNECTION_RETRY_ATTEMPTS,
        retry_delay=RETRY_INTERVAL,
        retry_method=func.__name__,
        retry_on_exceptions=(
            NewConnectionError,
            MaxRetryError,
            K8sApiException,
        ),
    )


def _is_valid_connectivity_mode(namespace):
    response = _execute_with_retry(
        KubernetesClient.list_namespaced_custom_object,
        namespace,
        None,
        ARC_GROUP,
        KubernetesClient.get_crd_version(DATA_CONTROLLER_CRD_NAME),
        DATA_CONTROLLER_PLURAL,
    )

    dcs = response.get("items")
    if not dcs:
        raise CLIError(f"No data controller exists in namespace `{namespace}`.")
