# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

import base64
import json
import os
import shutil
import sys
import time
import yaml
import azext_arcdata.core.kubernetes as kubernetes_util

from datetime import datetime
from azext_arcdata.vendored_sdks.arm_sdk._arm_client import arm_clients
from azext_arcdata.vendored_sdks.kubernetes_sdk.json_serialization import ExtendedJsonEncoder
from azext_arcdata.core.identity import ArcDataCliCredential
from azext_arcdata.core.constants import (
    ARC_GROUP,
    AZDATA_PASSWORD,
    AZDATA_USERNAME,
    CERT_ARGUMENT_ERROR_TEMPLATE,
    DATA_CONTROLLER_PLURAL,
    USE_K8S_EXCEPTION_TEXT,
)
from azext_arcdata.core.prompt import prompt, prompt_pass
from azext_arcdata.core.util import (
    ClearField,
    FileUtil,
    check_and_set_kubectl_context,
    get_config_from_template,
    is_windows,
    retry,
    parse_cert_files,
    get_private_key_from_file,
)
from azext_arcdata.vendored_sdks.kubernetes_sdk.util import (
    validate_certificate_secret,
    create_certificate_secret,
    check_secret_exists_with_retries,
)
from azext_arcdata.vendored_sdks.kubernetes_sdk.dc.constants import (
    DATA_CONTROLLER_CRD_NAME,
    SQLMI_CRD_NAME,
    SQLMI_REPROVISION_REPLICA_TASK_CRD_NAME,
)
from azext_arcdata.vendored_sdks.kubernetes_sdk.client import (
    K8sApiException,
    KubernetesClient,
    KubernetesError,
    http_status_codes,
)
from azext_arcdata.vendored_sdks.kubernetes_sdk.models import CustomResourceDefinition
from azext_arcdata.vendored_sdks.kubernetes_sdk.models.custom_resource import CustomResource
from azext_arcdata.vendored_sdks.kubernetes_sdk.models.data_controller_custom_resource import (
    DataControllerCustomResource,
)
from azext_arcdata.sqlmi.constants import (
    API_GROUP,
    AZDATA_SQLMI_ID,
    RESOURCE_KIND,
    RESOURCE_KIND_PLURAL,
    SQLMI_LICENSE_TYPE_DEFAULT,
    SQLMI_SPEC,
    SQLMI_TIER_BUSINESS_CRITICAL,
    SQLMI_TIER_BUSINESS_CRITICAL_SHORT,
    SQLMI_TIER_DEFAULT,
    SQLMI_TIER_GENERAL_PURPOSE,
    TASK_API_GROUP,
)
from azext_arcdata.sqlmi.exceptions import SqlmiError
from azext_arcdata.vendored_sdks.kubernetes_sdk.models.reprovision_replica_cr_model import (
    SqlmiReprovisionReplicaTaskCustomResource,
)
from azext_arcdata.vendored_sdks.kubernetes_sdk.models.sqlmi_cr_model import SqlmiCustomResource
from azext_arcdata.sqlmi.sqlmi_utilities import (
    get_sqlmi_custom_resource,
    upgrade_sqlmi_instances,
)
from azext_arcdata.sqlmi.util import (
    CONNECTION_RETRY_ATTEMPTS,
    RETRY_INTERVAL,
    _parse_supported_ad_encryption_types,
    is_valid_sql_password,
    validate_ad_connector,
    validate_admin_login_secret,
    validate_keytab_secret,
    validate_labels_and_annotations,
    validate_sqlmi_name,
)
from humanfriendly.terminal.spinners import AutomaticSpinner
from knack.cli import CLIError
from knack.log import get_logger
from urllib3.exceptions import MaxRetryError, NewConnectionError

logger = get_logger(__name__)


def arc_sql_mi_create(
    client,
    name,
    no_wait=False,
    **kwargs
):
    """
    Create a SQL managed instance.
    """
    use_k8s = kwargs.get("use_k8s", False)
    path = kwargs.get("path")
    replicas = kwargs.get("replicas")
    readable_secondaries = kwargs.get("readable_secondaries")
    storage_class_backups = kwargs.get("storage_class_backups")
    tier = kwargs.get("tier")
    retention_days = kwargs.get("retention_days")

    try:
        if not use_k8s:
            validate_sqlmi_name(kwargs.get("name"))

            from azext_arcdata.vendored_sdks.arm_sdk.client import ArmClient

            cred = ArcDataCliCredential()
            subscription = client.subscription
            armclient = ArmClient(cred, subscription)
            armclients = arm_clients(cred, subscription)
            sqlmi_namespace = (
                armclients.dc.get_custom_location_namespace(
                    kwargs.get("custom_location"), kwargs.get("resource_group")
                )
            )
            azure_location = (
                armclients.dc.get_custom_location_region(
                    kwargs.get("custom_location"), kwargs.get("resource_group")
                )
            )

            # Note: might not be equal in a cross-namespace scenario
            #
            ad_connector_namespace = sqlmi_namespace

            return armclient.create_sqlmi(
                name=name,
                path=path,
                replicas=replicas,
                orchestrator_replicas=kwargs.get("orchestrator_replicas"),
                readable_secondaries=readable_secondaries,
                sync_secondary_to_commit=kwargs.get("sync_secondary_to_commit"),
                cores_limit=kwargs.get("cores_limit"),
                cores_request=kwargs.get("cores_request"),
                memory_limit=kwargs.get("memory_limit"),
                memory_request=kwargs.get("memory_request"),
                storage_class_data=kwargs.get("storage_class_data"),
                storage_class_logs=kwargs.get("storage_class_logs"),
                storage_class_datalogs=kwargs.get("storage_class_datalogs"),
                storage_class_backups=storage_class_backups,
                storage_class_orchestrator_logs=kwargs.get("storage_class_orchestrator_logs"),
                volume_size_data=kwargs.get("volume_size_data"),
                volume_size_logs=kwargs.get("volume_size_logs"),
                volume_size_datalogs=kwargs.get("volume_size_datalogs"),
                volume_size_backups=kwargs.get("volume_size_backups"),
                volume_size_orchestrator_logs=kwargs.get("volume_size_orchestrator_logs"),
                license_type=kwargs.get("license_type"),
                tier=tier,
                dev=kwargs.get("dev"),
                location=azure_location,
                custom_location=kwargs.get("custom_location"),
                resource_group=kwargs.get("resource_group"),
                ad_connector_name=kwargs.get("ad_connector_name"),
                ad_connector_namespace=ad_connector_namespace,
                ad_account_name=kwargs.get("ad_account_name"),
                keytab_secret=kwargs.get("keytab_secret"),
                ad_encryption_types=kwargs.get("ad_encryption_types"),
                tde_mode=kwargs.get("tde_mode"),
                tde_protector_secret=kwargs.get("tde_protector_secret"),
                primary_dns_name=kwargs.get("primary_dns_name"),
                primary_port_number=kwargs.get("primary_port_number"),
                secondary_dns_name=kwargs.get("secondary_dns_name"),
                secondary_port_number=kwargs.get("secondary_port_number"),
                polling=not no_wait,
                retention_days=retention_days,
                time_zone=kwargs.get("time_zone"),
                service_type=kwargs.get("service_type"),
                trace_flags=kwargs.get("trace_flags"),
                private_key_file=kwargs.get("private_key_file"),
            )

        check_and_set_kubectl_context()
        namespace = client.namespace

        rd = 7 if retention_days is None else retention_days
        # Determine source for the resource spec preferring path first
        #
        if not path:
            # TODO: Use mutating web hooks to set these default values
            #
            spec_object = {
                "apiVersion": API_GROUP
                + "/"
                + KubernetesClient.get_crd_version(SQLMI_CRD_NAME),
                "kind": RESOURCE_KIND,
                "metadata": {},
                "spec": {
                    "backup": {
                        "retentionPeriodInDays": rd,
                    },
                    "tier": SQLMI_TIER_DEFAULT,
                    "licenseType": SQLMI_LICENSE_TYPE_DEFAULT,
                    "storage": {
                        "data": {"volumes": [{"size": "5Gi"}]},
                        "logs": {"volumes": [{"size": "5Gi"}]},
                    },
                },
            }

        # Otherwise, use the provided azext_arcdata file.
        #
        else:
            spec_object = FileUtil.read_json(path)

        # Decode base spec and apply args. Must patch namespace in separately
        # since it's not parameterized in this func
        cr = CustomResource.decode(SqlmiCustomResource, spec_object)
        cr.metadata.namespace = namespace
        cr.apply_args(**kwargs)
        cr.validate(client.apis.kubernetes)

        logger.debug("Using --dev == '%s'", cr.spec.dev)

        # If tier is provided and not replicas, then default replicas based on
        #  given tier value
        #
        if tier:
            if not replicas:
                if (tier == SQLMI_TIER_BUSINESS_CRITICAL) or (
                    tier == SQLMI_TIER_BUSINESS_CRITICAL_SHORT
                ):
                    cr.spec.replicas = 3

        if replicas:
            try:
                cr.spec.replicas = int(replicas)

                # Set the tier based on specfied replicas. With fail safe
                # validation enabled, it will go in error if user specifies
                # incorrect value.
                #
                if not tier:
                    if cr.spec.replicas == 1:
                        cr.spec.tier = SQLMI_TIER_GENERAL_PURPOSE
                    else:
                        cr.spec.tier = SQLMI_TIER_BUSINESS_CRITICAL
            except ValueError as e:
                raise CLIError(e)

        if storage_class_backups is not None:
            kubernetes_util.validate_rwx_storage_class(
                name=storage_class_backups, storage_type="backup", instance_type="SQLMI"
            )

        # if readable_secondaries is not set. use default value
        #
        if readable_secondaries is None:
            cr.spec.readableSecondaries = min(cr.spec.replicas - 1, 1)

        validate_labels_and_annotations(
            kwargs.get("labels"),
            kwargs.get("annotations"),
            kwargs.get("service_labels"),
            kwargs.get("service_annotations"),
            kwargs.get("storage_labels"),
            kwargs.get("storage_annotations"),
        )

        custom_object_exists = retry(
            lambda: client.apis.kubernetes.namespaced_custom_object_exists(
                name,
                namespace,
                group=API_GROUP,
                version=KubernetesClient.get_crd_version(SQLMI_CRD_NAME),
                plural=RESOURCE_KIND_PLURAL,
            ),
            retry_count=CONNECTION_RETRY_ATTEMPTS,
            retry_delay=RETRY_INTERVAL,
            retry_method="get namespaced custom object",
            retry_on_exceptions=(
                NewConnectionError,
                MaxRetryError,
                KubernetesError,
            ),
        )
        if custom_object_exists:
            raise ValueError(
                "Arc SQL managed instance `{}` already exists in namespace "
                "`{}`.".format(name, namespace)
            )

        # Validate Active Directory args if enabling AD auth
        #
        ad_connector_name = kwargs.get("ad_connector_name")
        if ad_connector_name:
            # Note: might not be equal in a cross-namespace scenario
            #
            ad_connector_namespace = namespace

            validate_ad_connector(
                client.apis.kubernetes,
                ad_connector_name,
                ad_connector_namespace,
                namespace,
                kwargs.get("keytab_secret"),
            )

            ad_encryption_types = kwargs.get("ad_encryption_types")
            if ad_encryption_types:
                cr.spec.security.activeDirectory.encryption_types = (
                    _parse_supported_ad_encryption_types(ad_encryption_types)
                )

        noexternal_endpoint = kwargs.get("noexternal_endpoint")
        service_type = kwargs.get("service_type")
        if not noexternal_endpoint:
            if not service_type:
                response = retry(
                    lambda: client.apis.kubernetes.list_namespaced_custom_object(
                        namespace,
                        group=ARC_GROUP,
                        version=KubernetesClient.get_crd_version(
                            DATA_CONTROLLER_CRD_NAME
                        ),
                        plural=DATA_CONTROLLER_PLURAL,
                    ),
                    retry_count=CONNECTION_RETRY_ATTEMPTS,
                    retry_delay=RETRY_INTERVAL,
                    retry_method="list namespaced custom object",
                    retry_on_exceptions=(
                        NewConnectionError,
                        MaxRetryError,
                        K8sApiException,
                    ),
                )

                dcs = response.get("items")
                if not dcs:
                    raise CLIError(
                        "No data controller exists in namespace `{}`. Cannot set "
                        "external endpoint argument.".format(namespace)
                    )
                else:
                    dc_cr = CustomResource.decode(
                        DataControllerCustomResource, dcs[0]
                    )
                    service_type = dc_cr.get_controller_service().serviceType

            cr.spec.services.primary.serviceType = service_type
            cr.spec.services.readable_secondaries.serviceType = service_type

        # Create admin login secret
        #
        admin_login_secret = kwargs.get("admin_login_secret")
        if not admin_login_secret:
            # Use default secret name when the user does not provide one.
            #
            admin_login_secret = name + "-login-secret"

        # Stamp the secret name on the custom resource.
        #
        cr.spec.security.adminLoginSecret = admin_login_secret

        login_secret_exists = check_secret_exists_with_retries(
            client.apis.kubernetes, cr.metadata.namespace, admin_login_secret
        )

        if login_secret_exists:
            # Validate that the existing login secret has correct format.
            #
            validate_admin_login_secret(
                client, cr.metadata.namespace, admin_login_secret
            )
        else:
            username, pw = _get_user_pass(client, name)

            secrets = dict()
            encoding = "utf-8"
            secrets["secretName"] = admin_login_secret
            secrets["base64Username"] = base64.b64encode(
                bytes(username, encoding)
            ).decode(encoding)
            secrets["base64Password"] = base64.b64encode(
                bytes(pw, encoding)
            ).decode(encoding)

            machineId = _get_sql_mi_id(kwargs.get("private_key_file"))
            if machineId:
                secrets["base64MachineId"] = machineId

            temp = get_config_from_template(
                os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    "templates",
                    "useradmin-login.yaml.tmpl",
                ),
                secrets,
            )
            mssql_secret = yaml.safe_load(temp)

            try:
                retry(
                    lambda: client.apis.kubernetes.create_secret(
                        cr.metadata.namespace,
                        mssql_secret,
                        ignore_conflict=True,
                    ),
                    retry_count=CONNECTION_RETRY_ATTEMPTS,
                    retry_delay=RETRY_INTERVAL,
                    retry_method="create secret",
                    retry_on_exceptions=(
                        NewConnectionError,
                        MaxRetryError,
                        K8sApiException,
                    ),
                )

            except K8sApiException as e:
                if e.status != http_status_codes.conflict:
                    raise

        tde_mode = kwargs.get("tde_mode")
        if tde_mode:
            cr.spec.security.transparentDataEncryption.mode = tde_mode
            if tde_mode.lower() == "customermanaged":
                _create_service_certificate(
                    client,
                    cr,
                    name,
                    kwargs.get("tde_protector_public_key_file"),
                    kwargs.get("tde_protector_private_key_file"),
                    kwargs.get("tde_protector_secret"),
                    is_tde_protector=True,
                )
            elif not kwargs.get("tde_protector_secret"):
                cr.spec.security.transparentDataEncryption.protectorSecret = (
                    ClearField()
                )
            else:
                raise CLIError(
                    "Cannot specify --tde-protector-secret when --tde-mode is not "
                    "CustomerManaged."
                )

        # Create service certificate based on parameters
        #
        _create_service_certificate(
            client,
            cr,
            name,
            kwargs.get("certificate_public_key_file"),
            kwargs.get("certificate_private_key_file"),
            kwargs.get("service_certificate_secret"),
        )

        # Create custom resource.
        #
        retry(
            lambda: client.apis.kubernetes.create_namespaced_custom_object(
                cr=cr, plural=RESOURCE_KIND_PLURAL, ignore_conflict=True
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
            client.stdout(
                "Deployed {0} in namespace `{1}`. Please use `az sql mi-arc "
                "show -n {0} --k8s-namespace {1} --use-k8s` to check its "
                "status.".format(cr.metadata.name, cr.metadata.namespace)
            )
        else:
            deployed_cr = get_sqlmi_custom_resource(
                client.apis.kubernetes, name, namespace
            )

            if not is_windows():
                with AutomaticSpinner(
                    "Deploying {0} in namespace `{1}`".format(
                        cr.metadata.name, cr.metadata.namespace
                    ),
                    show_time=True,
                ):
                    while not _is_instance_ready(deployed_cr):
                        if _is_instance_in_error(deployed_cr):
                            raise SqlmiError(
                                "{0} is in error state: {1}".format(
                                    cr.metadata.name,
                                    _get_error_message(deployed_cr),
                                )
                            )

                        time.sleep(5)
                        deployed_cr = get_sqlmi_custom_resource(
                            client.apis.kubernetes, name, namespace
                        )
            else:
                client.stdout(
                    "Deploying {0} in namespace `{1}`".format(name, namespace)
                )
                while not _is_instance_ready(deployed_cr):
                    if _is_instance_in_error(deployed_cr):
                        raise SqlmiError(
                            "{0} is in error state: {1}".format(
                                cr.metadata.name,
                                _get_error_message(deployed_cr),
                            )
                        )

                    time.sleep(5)
                    deployed_cr = get_sqlmi_custom_resource(
                        client.apis.kubernetes, name, namespace
                    )

            if _is_instance_ready(deployed_cr):
                client.stdout("{0} is Ready".format(cr.metadata.name))

    except KubernetesError as e:
        raise SqlmiError(e.message)
    except ValueError as e:
        raise CLIError(e)
    except Exception as e:
        raise CLIError(e)


def arc_sql_mi_upgrade(
    client,
    namespace=None,
    name=None,
    field_filter=None,
    label_filter=None,
    desired_version=None,
    dry_run=None,
    force=False,
    use_k8s=None,
    resource_group=None,
    no_wait=False,
):
    if name is None and field_filter is None and label_filter is None:
        raise CLIError(
            "One of the following parameters is "
            "required: --name, --field-filter, --label-filter"
        )

    try:
        if not use_k8s:
            from azext_arcdata.vendored_sdks.arm_sdk.client import ArmClient

            if name is None:
                raise CLIError(
                    "Parameter --name must be used for connected mode upgrades"
                )

            cred = ArcDataCliCredential()
            subscription = client.subscription
            armclient = ArmClient(cred, subscription)

            armclient.upgrade_sqlmi(
                resource_group,
                name,
                desired_version,
                dry_run,
                no_wait,
            )

        else:
            namespace = client.namespace

            upgrade_sqlmi_instances(
                namespace,
                name,
                field_filter,
                label_filter,
                desired_version,
                dry_run,
                force,
                use_k8s,
            )
    except KubernetesError as e:
        raise SqlmiError(e.message)
    except Exception as e:
        raise CLIError(e)


def arc_sql_mi_edit(
    client,
    name,
    namespace=None,
    path=None,
    cores_limit=None,
    cores_request=None,
    memory_limit=None,
    memory_request=None,
    license_type=None,
    tier=None,
    nowait=False,
    dev=None,
    labels=None,
    annotations=None,
    service_labels=None,
    service_annotations=None,
    agent_enabled=None,
    trace_flags=None,
    time_zone=None,
    use_k8s=None,
    retention_days=None,
    # -- direct --
    resource_group=None,
    location=None,
    custom_location=None,
    tag_name=None,
    tag_value=None,
):
    """
    Deprecated, use update over edit.
    """
    try:
        arc_sql_mi_update(
            client,
            name,
            path=path,
            time_zone=time_zone,
            cores_limit=cores_limit,
            cores_request=cores_request,
            memory_limit=memory_limit,
            memory_request=memory_request,
            license_type=license_type,
            tier=tier,
            no_wait=nowait,
            labels=labels,
            annotations=annotations,
            service_labels=service_labels,
            service_annotations=service_annotations,
            agent_enabled=agent_enabled,
            trace_flags=trace_flags,
            retention_days=retention_days,
            certificate_public_key_file=None,
            certificate_private_key_file=None,
            service_certificate_secret=None,
            preferred_primary_replica=None,
            # -- indirect --
            use_k8s=use_k8s,
            namespace=namespace,
            # -- direct --
            resource_group=resource_group,
            # location=location,
            # custom_location=custom_location,
            # tag_name=tag_name,
            # tag_value=tag_value,
        )
    except KubernetesError as e:
        raise SqlmiError(e.message)
    except Exception as e:
        raise CLIError(e)


def arc_sql_mi_update(
    client,
    name,
    replicas=None,
    orchestrator_replicas=None,
    readable_secondaries=None,
    sync_secondary_to_commit=None,
    path=None,
    time_zone=None,
    cores_limit=None,
    cores_request=None,
    memory_limit=None,
    memory_request=None,
    license_type=None,
    tier=None,
    no_wait=False,
    labels=None,
    annotations=None,
    service_labels=None,
    service_annotations=None,
    agent_enabled=None,
    trace_flags=None,
    retention_days=None,
    certificate_public_key_file=None,
    certificate_private_key_file=None,
    service_certificate_secret=None,
    preferred_primary_replica=None,
    # -- indirect --
    use_k8s=None,
    namespace=None,
    # -- direct --
    resource_group=None,
    # -- Active Directory --
    keytab_secret=None,
    ad_encryption_types=None,
    # -- Transparent Data Encryption --
    tde_mode=None,
    tde_protector_secret=None,
    tde_protector_public_key_file=None,
    tde_protector_private_key_file=None,
):
    """
    Edit the configuration of a SQL managed instance.
    """
    # -- currently not used, setting to empty --
    primary_replica_failover_interval = None

    args = locals()

    def _check_replica_name(n, num_of_replicas, replica_name) -> bool:
        if replica_name == "any":
            return True
        x = replica_name.rfind("-")
        if x == -1:
            return False
        if replica_name[:x] != n:
            return False

        x += 1
        if int(replica_name[x:]) >= int(num_of_replicas):
            return False
        return True

    try:
        if not use_k8s:
            from azext_arcdata.vendored_sdks.arm_sdk.client import ArmClient

            cred = ArcDataCliCredential()
            subscription = client.subscription
            armclient = ArmClient(cred, subscription)

            validate_labels_and_annotations(
                labels,
                annotations,
                service_labels,
                service_annotations,
                None,
                None,
            )
            sqlmi = armclient.get_sqlmi(resource_group, name)

            if keytab_secret:
                sqlmi_namespace = sqlmi["properties"]["k8_s_raw"]["spec"][
                    "metadata"
                ]["namespace"]
                security = sqlmi["properties"]["k8_s_raw"]["spec"]["security"]
                if security and not security["activeDirectory"]:
                    raise CLIError(
                        "Cannot update Active Directory (AD) keytab if this "
                        "instance does not have AD enabled."
                    )
                validate_keytab_secret(
                    client.apis.kubernetes, sqlmi_namespace, keytab_secret
                )

            return armclient.update_sqlmi(
                name=name,
                replicas=replicas,
                orchestrator_replicas=orchestrator_replicas,
                readable_secondaries=readable_secondaries,
                sync_secondary_to_commit=sync_secondary_to_commit,
                cores_limit=cores_limit,
                cores_request=cores_request,
                memory_limit=memory_limit,
                memory_request=memory_request,
                license_type=license_type,
                tier=tier,
                polling=not no_wait,
                labels=labels,
                annotations=annotations,
                service_labels=service_labels,
                service_annotations=service_annotations,
                agent_enabled=agent_enabled,
                trace_flags=trace_flags,
                retention_days=retention_days,
                resource_group=resource_group,
                keytab_secret=keytab_secret,
                ad_encryption_types=ad_encryption_types,
                tde_mode=tde_mode,
                tde_protector_secret=tde_protector_secret,
            )

        check_and_set_kubectl_context()
        namespace = client.namespace

        validate_labels_and_annotations(
            labels, annotations, service_labels, service_annotations, None, None
        )

        if path:
            # Read azext_arcdata file for edit
            json_object = FileUtil.read_json(path)
            cr = CustomResource.decode(SqlmiCustomResource, json_object)
        else:
            cr = get_sqlmi_custom_resource(
                client.apis.kubernetes, name, namespace
            )

        cr.apply_args(**args)
        cr.validate(client.apis.kubernetes)

        # Active Directory only
        #
        if keytab_secret or ad_encryption_types:
            if not cr.spec.security.activeDirectory:
                raise CLIError(
                    "Cannot update Active Directory (AD) settings if this "
                    "instance does not have AD enabled."
                )
            if keytab_secret:
                validate_keytab_secret(client, namespace, keytab_secret)
                cr.spec.security.activeDirectory.keytab_secret = keytab_secret
            if ad_encryption_types:
                cr.spec.security.activeDirectory.encryption_types = (
                    _parse_supported_ad_encryption_types(ad_encryption_types)
                )

        if preferred_primary_replica:
            if not _check_replica_name(
                name,
                cr.spec.replicas,
                preferred_primary_replica,
            ):
                raise CLIError(
                    "Wrong pod name {0}".format(preferred_primary_replica)
                )
            cr.spec.preferredPrimaryReplicaSpec.preferredPrimaryReplica = (
                preferred_primary_replica
            )

        if not primary_replica_failover_interval:
            primary_replica_failover_interval = 600

        cr.spec.preferredPrimaryReplicaSpec.primaryReplicaFailoverInterval = (
            int(primary_replica_failover_interval)
        )
        cr.spec.backup.retentionPeriodInDays = retention_days

        if tde_mode:
            cr.spec.security.transparentDataEncryption.mode = tde_mode
            if tde_mode.lower() == "customermanaged":
                _create_service_certificate(
                    client,
                    cr,
                    name,
                    tde_protector_public_key_file,
                    tde_protector_private_key_file,
                    tde_protector_secret,
                    is_tde_protector=True,
                )
            elif not tde_protector_secret:
                cr.spec.security.transparentDataEncryption.protectorSecret = (
                    ClearField()
                )
            else:
                raise CLIError(
                    "Cannot specify --tde-protector-secret when --tde-mode is not "
                    "CustomerManaged."
                )

        _create_service_certificate(
            client,
            cr,
            name,
            certificate_public_key_file,
            certificate_private_key_file,
            service_certificate_secret,
            is_update=True,
        )

        # Patch CR
        client.apis.kubernetes.patch_namespaced_custom_object(
            cr=cr, plural=RESOURCE_KIND_PLURAL
        )

        if no_wait:
            client.stdout(
                "Updated {0} in namespace `{1}`. Please use `az sql mi-arc "
                "show -n {0} --k8s-namespace {1} --use-k8s` to check "
                "its status.".format(cr.metadata.name, cr.metadata.namespace)
            )
        else:
            # Wait for the CR to reflect new state
            time.sleep(5)

            deployed_cr = get_sqlmi_custom_resource(
                client.apis.kubernetes, name, namespace
            )

            if not is_windows():
                with AutomaticSpinner(
                    "Updating {0} in namespace `{1}`".format(
                        cr.metadata.name, cr.metadata.namespace
                    ),
                    show_time=True,
                ):
                    while not _is_instance_ready(deployed_cr):
                        if _is_instance_in_error(deployed_cr):
                            raise SqlmiError(
                                "{0} is in error state:{1}".format(
                                    cr.metadata.name,
                                    _get_error_message(deployed_cr),
                                )
                            )

                        time.sleep(5)
                        deployed_cr = get_sqlmi_custom_resource(
                            client.apis.kubernetes, name, namespace
                        )
            else:
                client.stdout(
                    "Updating {0} in namespace `{1}`".format(name, namespace)
                )
                while not _is_instance_ready(deployed_cr):
                    if _is_instance_in_error(deployed_cr):
                        raise SqlmiError(
                            "{0} is in error state:{1}".format(
                                cr.metadata.name,
                                _get_error_message(deployed_cr),
                            )
                        )

                    time.sleep(5)
                    deployed_cr = get_sqlmi_custom_resource(
                        client.apis.kubernetes, name, namespace
                    )

            if _is_instance_ready(deployed_cr):
                client.stdout("{0} is Ready".format(cr.metadata.name))

    except KubernetesError as e:
        raise SqlmiError(e.message)
    except Exception as e:
        raise CLIError(e)


def arc_sql_mi_delete(
    client, name, resource_group=None, namespace=None, use_k8s=None
):
    """
    Delete a SQL managed instance.
    """
    try:
        if not use_k8s:
            from azext_arcdata.vendored_sdks.arm_sdk.client import ArmClient

            cred = ArcDataCliCredential()
            subscription = client.subscription
            armclient = ArmClient(cred, subscription)
            return armclient.delete_sqlmi(
                rg_name=resource_group, sqlmi_name=name
            )

        check_and_set_kubectl_context()

        namespace = namespace or client.namespace

        client.apis.kubernetes.delete_namespaced_custom_object(
            name=name,
            namespace=namespace,
            group=API_GROUP,
            version=KubernetesClient.get_crd_version(SQLMI_CRD_NAME),
            plural=RESOURCE_KIND_PLURAL,
        )

        client.stdout("Deleted {} from namespace {}".format(name, namespace))

    except KubernetesError as e:
        raise SqlmiError(e.message)
    except Exception as e:
        raise CLIError(e)


def arc_sql_mi_show(
    client, name, resource_group=None, path=None, namespace=None, use_k8s=None
):
    """
    Show the details of a SQL managed instance.
    """
    try:
        if not use_k8s:
            from azext_arcdata.vendored_sdks.arm_sdk.client import ArmClient

            cred = ArcDataCliCredential()
            subscription = client.subscription
            arm_client = ArmClient(cred, subscription)

            response = arm_client.get_sqlmi_as_obj(
                rg_name=resource_group, sqlmi_name=name
            )

            # state = poller.as_dict()["properties"]["provisioning_state"]
            # if state:
            #    return {"provisioningState": state}
        else:
            check_and_set_kubectl_context()
            namespace = namespace or client.namespace

            response = get_sqlmi_custom_resource(
                client.apis.kubernetes, name, namespace
            ).encode()

        if path:
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join(path, "{}.json".format(name))
            with open(path, "w") as outfile:
                json.dump(response, outfile, indent=4)
            client.stdout("{0} specification written to {1}".format(name, path))
        else:
            return response

    except KubernetesError as e:
        raise SqlmiError(e.message)
    except Exception as e:
        raise CLIError(e)


def arc_sql_mi_getmirroringcert(
    client, name, cert_file, namespace=None, use_k8s=None
):
    try:
        if not use_k8s:
            raise ValueError(USE_K8S_EXCEPTION_TEXT)

        check_and_set_kubectl_context()
        namespace = namespace or client.namespace

        cr = get_sqlmi_custom_resource(client.apis.kubernetes, name, namespace)
        data_pem = cr.status.highAvailability.mirroringCertificate

        client.stdout(
            "The mirroring certificate has been written to file {0}:\n{1}".format(
                cert_file, data_pem
            )
        )

        file = open(cert_file, "w")
        file.write(data_pem)
        file.close()
    except Exception as e:
        raise CLIError(e)


def arc_sql_mi_list(
    client,
    resource_group=None,
    custom_location=None,
    namespace=None,
    use_k8s=None,
):
    """
    List SQL managed instances.
    """
    try:
        result = []
        if not use_k8s:
            from azext_arcdata.vendored_sdks.arm_sdk.client import ArmClient

            cred = ArcDataCliCredential()
            subscription = client.subscription
            armclient = ArmClient(cred, subscription)
            items = armclient.list_sqlmi(
                rg_name=resource_group, cl_name=custom_location
            )
            for item in items:
                result.append(item)

            client.stdout(
                "Found {} Arc-enabled SQL Managed Instances.".format(
                    len(result)
                )
            )

        else:
            check_and_set_kubectl_context()
            namespace = namespace or client.namespace

            response = client.apis.kubernetes.list_namespaced_custom_object(
                namespace,
                group=API_GROUP,
                version=KubernetesClient.get_crd_version(SQLMI_CRD_NAME),
                plural=RESOURCE_KIND_PLURAL,
            )
            items = response.get("items")
            # Temporary, need to discuss what the intended structure is across
            # partners
            for item in items:
                cr = CustomResource.decode(SqlmiCustomResource, item)
                result.append(
                    {
                        "name": cr.metadata.name,
                        "primaryEndpoint": (
                            cr.status.endpoints.primary
                            if cr.status.endpoints
                            else None
                        ),
                        "replicas": (
                            "{}/{}".format(
                                cr.status.roles.sql.readyReplicas,
                                cr.status.roles.sql.replicas,
                            )
                            if cr.status.roles.sql
                            else None
                        ),
                        "state": cr.status.state,
                        "desiredVersion": (
                            cr.spec.update.desiredVersion
                            if cr.spec.update
                            else None
                        ),
                        "runningVersion": cr.status.runningVersion,
                    }
                )

            client.stdout(
                "Found {} Arc-enabled SQL Managed Instances in namespace {}".format(
                    len(result), namespace
                )
            )

        return result

    except KubernetesError as e:
        raise SqlmiError(e.message)
    except Exception as e:
        raise CLIError(e)


def arc_sql_endpoint_list(client, name=None, namespace=None, use_k8s=None):
    """
    List endpoints for the given SQL managed instance(s).
    """
    try:
        if not use_k8s:
            raise ValueError(USE_K8S_EXCEPTION_TEXT)

        check_and_set_kubectl_context()

        namespace = namespace or client.namespace

        custom_resources = []

        if name:
            cr = get_sqlmi_custom_resource(
                client.apis.kubernetes, name, namespace
            )
            if cr is None:
                raise CLIError(
                    "SQL managed instance {0} not found in namespace {1}.".format(
                        name, namespace
                    )
                )
            custom_resources.append(cr)
        else:
            response = client.apis.kubernetes.list_namespaced_custom_object(
                namespace,
                group=API_GROUP,
                version=KubernetesClient.get_crd_version(SQLMI_CRD_NAME),
                plural=RESOURCE_KIND_PLURAL,
            )

            items = response.get("items")

            for item in items:
                cr = CustomResource.decode(SqlmiCustomResource, item)
                if cr:
                    custom_resources.append(cr)

        arc_sql_endpoints = {"namespace": namespace}
        instances = []

        # Loop through the specified custom resources and retrieve their
        # endpoints from their status
        for cr in custom_resources:
            endpoints = []

            if cr.status:
                descrip_str = "description"
                endpoint_str = "endpoint"

                # Connection string
                endpoints.append(
                    {
                        descrip_str: "SQL Managed Instance",
                        endpoint_str: (
                            cr.status.endpoints.primary
                            if cr.status.endpoints
                            and cr.status.endpoints.primary
                            else "Not yet available"
                        ),
                    }
                )

                # Logs
                endpoints.append(
                    {
                        descrip_str: "Log Search Dashboard",
                        endpoint_str: (
                            cr.status.endpoints.log_search_dashboard
                            if cr.status.endpoints
                            and cr.status.endpoints.log_search_dashboard
                            else "Not yet available"
                        ),
                    }
                )

                # Metrics
                endpoints.append(
                    {
                        descrip_str: "Metrics Dashboard",
                        endpoint_str: (
                            cr.status.endpoints.metrics_dashboard
                            if cr.status.endpoints
                            and cr.status.endpoints.metrics_dashboard
                            else "Not yet available"
                        ),
                    }
                )

                # Readable Secondary Endpoint
                if cr.status.endpoints and cr.status.endpoints.secondary:
                    endpoints.append(
                        {
                            descrip_str: "SQL Managed Instance Readable "
                            "Secondary Replicas",
                            endpoint_str: cr.status.endpoints.secondary,
                        }
                    )

            instances.append({"name": cr.metadata.name, "endpoints": endpoints})

        arc_sql_endpoints["instances"] = instances

        return arc_sql_endpoints

    except KubernetesError as e:
        raise CLIError(e.message)
    except Exception as e:
        raise CLIError(e)


def arc_sql_mi_config_init(client, path):
    """
    Returns a package of crd.json and spec-template.json.
    """
    try:
        if not os.path.isdir(path):
            os.makedirs(path, exist_ok=True)

        crd = KubernetesClient.get_crd(SQLMI_CRD_NAME).to_dict()

        # clean up fields not needed
        crd["metadata"].pop("managed_fields", None)
        crd.pop("status", None)

        with open(os.path.join(path, "crd.json"), "w") as output:
            json.dump(
                crd,
                output,
                check_circular=False,
                cls=ExtendedJsonEncoder,
                indent=4,
            )

        # Copy spec.json template to the new path
        shutil.copy(SQLMI_SPEC, os.path.join(path, "spec.json"))

        client.stdout(
            "{0} templates created in directory: {1}".format(
                RESOURCE_KIND, path
            )
        )

    except Exception as e:
        raise CLIError(e)


def arc_sql_mi_config_add(client, path, json_values):
    """
    Add new key and value to the given config file
    """
    try:
        client.add_configuration(path, json_values)
    except Exception as e:
        raise CLIError(e)


def arc_sql_mi_config_replace(client, path, json_values):
    """
    Replace the value of a given key in the given config file
    """
    try:
        client.replace_configuration(path, json_values)
    except Exception as e:
        raise CLIError(e)


def arc_sql_mi_config_remove(client, path, json_path):
    """
    Remove a key from the given config file
    """
    try:
        client.remove_configuration(path, json_path)
    except Exception as e:
        raise CLIError(e)


def arc_sql_mi_config_patch(client, path, patch_file):
    """
    Patch a given file against the given config file
    """
    try:
        client.patch_configuration(path, patch_file)
    except Exception as e:
        raise CLIError(e)


def arc_sql_mi_reprovision_replica(
    client,
    name,
    no_wait=False,
    # -- indirect --
    use_k8s=None,
    namespace=None,
):
    """
    reprovision a SQL managed instance replica.
    """

    try:
        if not use_k8s:
            raise ValueError(USE_K8S_EXCEPTION_TEXT)

        check_and_set_kubectl_context()
        namespace = namespace or client.namespace

        task_name = (
            "sql-reprov-replica-"
            + name
            + "-"
            + str(datetime.timestamp(datetime.now()))
        )
        crd = CustomResourceDefinition(
            KubernetesClient.get_crd(SQLMI_REPROVISION_REPLICA_TASK_CRD_NAME)
        )

        spec_object = {
            "apiVersion": crd.group + "/" + crd.stored_version,
            "kind": crd.kind,
            "metadata": {
                "name": task_name,
                "namespace": namespace,
            },
            "spec": {
                "replicaName": name,
            },
        }

        # Decode base spec and apply args. Must patch namespace in separately
        # since it's not parameterized in this func
        #
        cr = CustomResource.decode(
            SqlmiReprovisionReplicaTaskCustomResource, spec_object
        )

        cr.validate(client.apis.kubernetes)

        # Create custom resource.
        #
        retry(
            lambda: client.apis.kubernetes.create_namespaced_custom_object(
                cr=cr,
                plural=crd.plural,
                ignore_conflict=True,
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
            # get status via kubectl
            #
            client.stdout(
                "Reprovisioning replica {0} in namespace `{1}`. Please use\n"
                "`kubectl get -n {1} {2} {3}`\nto check its status or \n"
                "`kubectl get -n {1} {2}`\nto view all reprovision tasks.".format(
                    cr.spec.replicaName,
                    cr.metadata.namespace,
                    crd.kind,
                    task_name,
                )
            )
        else:
            response = retry(
                lambda: client.apis.kubernetes.get_namespaced_custom_object(
                    cr.metadata.name,
                    cr.metadata.namespace,
                    group=crd.group,
                    version=crd.stored_version,
                    plural=crd.plural,
                ),
                retry_count=CONNECTION_RETRY_ATTEMPTS,
                retry_delay=RETRY_INTERVAL,
                retry_method="get namespaced custom object",
                retry_on_exceptions=(
                    NewConnectionError,
                    MaxRetryError,
                    KubernetesError,
                ),
            )

            deployed_cr = CustomResource.decode(
                SqlmiReprovisionReplicaTaskCustomResource, response
            )

            get_namespaced_custom_object = (
                client.apis.kubernetes.get_namespaced_custom_object
            )

            def _is_task_failed():
                return (
                    deployed_cr.status.state is not None
                    and deployed_cr.status.state.lower() == "failed"
                )

            def _is_task_completed():
                return (
                    deployed_cr.status.state is not None
                    and deployed_cr.status.state.lower() == "completed"
                )

            if not is_windows():
                with AutomaticSpinner(
                    "Running task {0} in namespace `{1}`".format(
                        cr.metadata.name, cr.metadata.namespace
                    ),
                    show_time=True,
                ):
                    while not _is_task_completed():
                        if _is_task_failed():
                            raise SqlmiError(
                                "{0} is in error state: {1}".format(
                                    cr.metadata.name,
                                    _get_error_message(deployed_cr),
                                )
                            )

                        time.sleep(5)
                        response = retry(
                            lambda: get_namespaced_custom_object(
                                cr.metadata.name,
                                cr.metadata.namespace,
                                group=TASK_API_GROUP,
                                version=KubernetesClient.get_crd_version(
                                    SQLMI_REPROVISION_REPLICA_TASK_CRD_NAME
                                ),
                                plural=crd.plural,
                            ),
                            retry_count=CONNECTION_RETRY_ATTEMPTS,
                            retry_delay=RETRY_INTERVAL,
                            retry_method="get namespaced custom object",
                            retry_on_exceptions=(
                                NewConnectionError,
                                MaxRetryError,
                                KubernetesError,
                            ),
                        )

                        deployed_cr = CustomResource.decode(
                            SqlmiReprovisionReplicaTaskCustomResource, response
                        )
            else:
                client.stdout(
                    "Running task {0} in namespace `{1}`".format(
                        name, namespace
                    )
                )
                while not _is_task_completed():
                    if _is_task_failed():
                        raise SqlmiError(
                            "{0} is in error state: {1}".format(
                                cr.metadata.name,
                                _get_error_message(deployed_cr),
                            )
                        )

                    time.sleep(5)
                    response = retry(
                        lambda: get_namespaced_custom_object(
                            cr.metadata.name,
                            cr.metadata.namespace,
                            group=TASK_API_GROUP,
                            version=KubernetesClient.get_crd_version(
                                SQLMI_REPROVISION_REPLICA_TASK_CRD_NAME
                            ),
                            plural=crd.plural,
                        ),
                        retry_count=CONNECTION_RETRY_ATTEMPTS,
                        retry_delay=RETRY_INTERVAL,
                        retry_method="get namespaced custom object",
                        retry_on_exceptions=(
                            NewConnectionError,
                            MaxRetryError,
                            KubernetesError,
                        ),
                    )

                    deployed_cr = CustomResource.decode(
                        SqlmiReprovisionReplicaTaskCustomResource, response
                    )

            if _is_task_completed():
                client.stdout("{0} is Ready".format(cr.metadata.name))

    except KubernetesError as e:
        raise SqlmiError(e.message)
    except ValueError as e:
        raise CLIError(e)
    except Exception as e:
        raise CLIError(e)


def _is_instance_ready(cr):
    """
    Verify that the SQL Mi instance is ready
    :param cr: Instance to check the readiness of
    :return: True if the instance is ready, False otherwise
    """
    return cr.metadata.generation == cr.status.observed_generation and (
        cr.status.state is not None and cr.status.state.lower() == "ready"
    )


def _is_instance_in_error(cr):
    """
    Check that the SQL Mi instance is in error state
    :param cr: Instance to check the readiness of
    :return: True if the instance is in error, False otherwise
    """
    return cr.status.state is not None and cr.status.state.lower() == "error"


def _get_error_message(cr):
    """
    Get error message from the status of custom resource
    :param cr: Instance to get error message.
    """
    return cr.status.message


def _get_sql_mi_id(private_key_file):
    machineId = os.environ.get(AZDATA_SQLMI_ID)
    if not machineId:
        if private_key_file:
            if sys.stdin.isatty():
                print("Reading private key file.")
                machineId = get_private_key_from_file(private_key_file, None)
            else:
                raise ValueError(
                    "Please provide an Arc SQL managed instance id "
                    "through the env variable AZDATA_SQLMI_ID."
                )
    return machineId


def _get_user_pass(client, name):
    # Username
    username = os.environ.get(AZDATA_USERNAME)
    if not username:
        if sys.stdin.isatty():
            username = prompt("Arc SQL managed instance username:")
        else:
            raise ValueError(
                "Please provide an Arc SQL managed instance username "
                "through the env variable AZDATA_USERNAME."
            )
    else:
        client.stdout(
            "Using AZDATA_USERNAME environment variable for `{}` "
            "username.".format(name)
        )

    while username == "sa" or username == "":
        if username == "sa":
            username = prompt(
                "The login 'sa' is not allowed.  Please use a "
                "different login."
            )
        if username == "":
            username = prompt("Login username required. Please enter a login.")

    # Password
    pw = os.environ.get(AZDATA_PASSWORD)
    if not pw:
        if sys.stdin.isatty():
            while not pw:
                pw = prompt_pass("Arc SQL managed instance password:", True)
                if not is_valid_sql_password(pw, "sa"):
                    client.stderr(
                        "\nError: SQL Server passwords must be at "
                        "least 8 characters long, cannot contain the "
                        "username, and must contain characters from "
                        "three of the following four sets: Uppercase "
                        "letters, Lowercase letters, Base 10 digits, "
                        "and Symbols. Please try again.\n"
                    )
                    pw = None
        else:
            raise ValueError(
                "Please provide an Arc SQL managed instance password "
                "through the env variable AZDATA_PASSWORD."
            )
    else:
        client.stdout(
            "Using AZDATA_PASSWORD environment variable for `{}` "
            "password.".format(name)
        )

    return username, pw


def _create_service_certificate(
    client,
    cr,
    name,
    certificate_public_key_file,
    certificate_private_key_file,
    service_certificate_secret,
    is_update=False,
    is_tde_protector=False,
):
    """
    Creates service certificate based on parameters.
    """

    # Handle certificate secret related parameters.
    #
    # Cases:
    #
    # 1. When only one of certificate_public_key_file and certificate_
    #    private_key_file are provided, fail with a message saying both
    #    are required if one is provided.
    #
    # 2. When both certificate_public_key_file and
    #    certificate_private_key_file are provided, then there are
    #    two subcases:
    #
    #    2.1. If service_certificate_secret parameter is NOT provided, use
    #         default name for the secret along with a unique id such as
    #         timestamp appended to it. Check if the secret exists.
    #
    #         2.1.1. If secret does not exist, then create it.
    #
    #         2.1.2. If the secret exists, retry with a different unique
    #                identifier.
    #
    #    2.2. If service_certificate_secret parameter is provided, use that
    #         string as the secret name and check if the secret exists.
    #
    #         2.2.1. If secret does not exist, then create it.
    #
    #         2.2.2. If the secret exists, fail indicating that if the
    #                secret exists and the parameters for certificate files
    #                should not be provided.
    #
    # 3. When both certificate_public_key_file and
    #    certificate_private_key_file are NOT provided, then there are two
    #    subcases:
    #
    #    3.1. If service_certificate_secret parameter is NOT provided, do
    #         NOT use default value. User intends to use system generated
    #         certificate.
    #
    #    3.2. If service_certificate_secret parameter is provided, use that
    #         string as the secret name and check if the secret already
    #         exists.
    #
    #         3.2.1. If the secret exists, validate and use it.
    #
    #         3.2.2. If the secret does not exist, fail.

    create_new_secret = False
    use_existing_secret = False
    default_service_certificate_secret_name = name + "-certificate-secret"

    # Erase the certificate name from the custom resource for not update.
    # It will be added only if necessary upon validation.
    #
    if not is_update:
        cr.spec.security.serviceCertificateSecret = ""

    # Case 1. When only one of certificate_public_key_file and
    #         certificate_private_key_file are provided, fail with a
    #         message saying both are required if one is provided.
    #
    #
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

    # Case 2. When both certificate_public_key_file and
    #         certificate_private_key_file are provided.
    #
    if certificate_public_key_file and certificate_private_key_file:
        # Case 2.1. If service_certificate_secret parameter is NOT provided,
        #           use default name for the secret along with a unique id
        #           such as timestamp appended to it. Check if the secret
        #           exists.
        #
        if not service_certificate_secret:
            # Case 2.1.1. If secret does not exist, then create it.
            #
            # Case 2.1.2. If the secret exists, retry with a different
            # unique identifier.
            #
            certificate_secret_exists = True
            while certificate_secret_exists:
                timestamp = datetime.now().strftime(
                    "%m-%d-%Y-%H-%M-%S-%f"
                )  # e.g. '07-02-2021-23-00-37-846604'

                # Secret name must be a valid DNS-1123 subdomain name.
                # Kubernetes uses this regex for validation:
                # '[a-z0-9]([-a-z0-9]*[a-z0-9])?
                #  (\\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*'
                #
                service_certificate_secret = (
                    default_service_certificate_secret_name + "-" + timestamp
                )

                certificate_secret_exists = check_secret_exists_with_retries(
                    client.apis.kubernetes,
                    cr.metadata.namespace,
                    service_certificate_secret,
                )

            # Set flag to create new secret.
            #
            create_new_secret = True

        # Case 2.2. If service_certificate_secret parameter is provided, use
        #           that string asthe secret name and check if the secret
        #           exists.
        #
        else:
            certificate_secret_exists = check_secret_exists_with_retries(
                client.apis.kubernetes,
                cr.metadata.namespace,
                service_certificate_secret,
            )

            # Case 2.2.1. If secret does not exist, then create it.
            #
            if not certificate_secret_exists:
                # Set flag to create new secret.
                #
                create_new_secret = True

            # Case 2.2.2. If the secret exists, fail indicating that if the
            #             secret exists and the parameters for certificate
            #             files should not be provided.
            #
            else:
                raise ValueError(
                    CERT_ARGUMENT_ERROR_TEMPLATE.format(
                        service_certificate_secret
                    )
                )

    # Case 3. When both certificate_public_key_file and
    #         certificate_private_key_file are NOT provided.
    #
    if not certificate_public_key_file and not certificate_private_key_file:
        # Case 3.1. If service_certificate_secret parameter is NOT provided,
        #           do NOT use default value. User intends to use system
        #           generated certificate.
        #
        if not service_certificate_secret:
            pass

        # Case 3.2. If service_certificate_secret parameter is provided, use
        #           that string as the secret name and check if the secret
        #           already exists.
        #
        else:
            certificate_secret_exists = check_secret_exists_with_retries(
                client.apis.kubernetes,
                cr.metadata.namespace,
                service_certificate_secret,
            )

            # Case 3.2.1. If the secret exists, validate and use it.
            #
            if certificate_secret_exists:
                # Set flag to use existing secret.
                #
                use_existing_secret = True

            # Case 3.2.2. If the secret does not exist, fail.
            #
            else:
                raise ValueError(
                    "Kubernetes secret '{0}' does "
                    "not exist. If you intend to use a pre-existing "
                    "secret, please provide correct name of an existing "
                    "secret. If you intend to use a certificate from "
                    "public key and private key files, please provide "
                    "their paths in the parameters --cert-public-key-file "
                    "and --cert-private-key-file.".format(
                        service_certificate_secret
                    )
                )

    # If we decided to create a new secret, create it here.
    #
    if create_new_secret:
        # Validate and parse data from files.
        #
        public_key, private_key = parse_cert_files(
            certificate_public_key_file, certificate_private_key_file
        )

        # Create secret.
        #
        create_certificate_secret(
            client.apis.kubernetes,
            cr.metadata.namespace,
            service_certificate_secret,
            public_key,
            private_key,
        )

        # Set the secret name on custom resource spec to indicate to the
        # operator that we will use certificate from the Kubernetes secret.
        #
        if is_tde_protector:
            cr.spec.security.transparentDataEncryption.protectorSecret = (
                service_certificate_secret
            )
        else:
            cr.spec.security.serviceCertificateSecret = (
                service_certificate_secret
            )

    # If we decided to use an existing secret, validate it and pass on.
    #
    elif use_existing_secret:
        # Load secret and validate contents.
        #
        validate_certificate_secret(
            client.apis.kubernetes,
            cr.metadata.namespace,
            service_certificate_secret,
        )

        # Set the secret name on the custom resource spec to indicate to the
        # operator that a user provided certificate is available to use.
        #
        if is_tde_protector:
            cr.spec.security.transparentDataEncryption.protectorSecret = (
                service_certificate_secret
            )
        else:
            cr.spec.security.serviceCertificateSecret = (
                service_certificate_secret
            )
