import pydash as _
import re
import sys
from azext_arcdata.core.util import retry
from azext_arcdata.sqlmi.constants import (
    API_GROUP,
    RESOURCE_KIND_PLURAL,
)
from azext_arcdata.vendored_sdks.kubernetes_sdk.models.custom_resource import CustomResource
from src.arcdata.arcdata.azext_arcdata.vendored_sdks.kubernetes_sdk.models.sqlmi_cr_model import SqlmiCustomResource
from azext_arcdata.vendored_sdks.kubernetes_sdk.client import (
    CONNECTION_RETRY_ATTEMPTS,
    RETRY_INTERVAL,
    KubernetesClient,
    KubernetesError,
    K8sApiException,
    http_status_codes,
)
from azext_arcdata.vendored_sdks.kubernetes_sdk.dc.constants import SQLMI_CRD_NAME
from azext_arcdata.vendored_sdks.kubernetes_sdk.arc_docker_image_service import (
    ArcDataImageService,
)
from urllib3.exceptions import MaxRetryError, NewConnectionError


def upgrade_sqlmi_instances(
    namespace,
    name=None,
    field_filter=None,
    label_filter=None,
    desired_version=None,
    dry_run=None,
    use_k8s=None,
):
    KubernetesClient.assert_use_k8s(use_k8s)
    instances = resolve_sqlmi_instances(
        namespace, name, field_filter, label_filter
    )

    (datacontroller, _) = KubernetesClient.get_arc_datacontroller(
        namespace, use_k8s
    )
    datacontrollerVersion = _.get(datacontroller, "spec.docker.imageTag")

    if not desired_version:
        desired_version = datacontrollerVersion

    _validate_upgrade_sqlmi_args(
        name, namespace, instances, desired_version, datacontrollerVersion)

    # - Filter to find instances that can upgrade to desired_version
    upgrade_instances = []
    for sqlmi in instances:
        sqlmi_name = sqlmi.metadata.name
        sqlmiVersion = sqlmi.status.runningVersion
        auto_upgrade_setting = sqlmi.spec.update.desiredVersion

        if desired_version == "auto":
            if not auto_upgrade_setting or auto_upgrade_setting != "auto":
                upgrade_instances.append(sqlmi)
            else:
                if name and name == sqlmi_name:
                    print(
                        "Auto-upgrade is already enabled for Arc-enabled SQL managed instance '{0}'.".format(
                            sqlmi_name
                        )
                    )
                    return
            continue

        val = ArcDataImageService.compare_version_tag(
            desired_version, sqlmiVersion, ignore_label=True
        )

        # In alignment with CustomResourceStateMachine.cs, upgrades to Controller version is allowed,
        # provided runningVersion imageTag is not same as desiredVersion
        if (desired_version == datacontrollerVersion) and (
            sqlmiVersion != desired_version
        ):
            upgrade_instances.append(sqlmi)
            continue

        # SemVer of desiredVersion is lower than runningVersion
        # No upgrade
        if val == -1:
            if name and name == sqlmi_name:
                raise ValueError(
                    "Arc-enabled SQL managed instance '{0}' cannot be downgraded below the current version {1}".format(
                        sqlmi_name, sqlmiVersion
                    )
                )
        # SemVer of desiredVersion is same as runningVersion and imageTag is same
        # No upgrade
        elif (val == 0) and (sqlmiVersion == desired_version):
            if auto_upgrade_setting and auto_upgrade_setting == "auto":
                # Disabling auto-upgrade by replacing auto with current version
                upgrade_instances.append(sqlmi)
                continue
            if name and name == sqlmi_name:
                raise ValueError(
                    "Arc-enabled SQL managed instance '{0}' is already running version {1}".format(
                        sqlmi_name, desired_version
                    )
                )
        # Allow upgrades in all other cases
        else:
            upgrade_instances.append(sqlmi)

    if dry_run:
        sys.stdout.write("****Dry Run****\n")

        sys.stdout.write(
            "{0} instance(s) would be upgraded by this command. \n".format(
                len(upgrade_instances)
            )
        )

        for ss in upgrade_instances:
            # todo: use running version if available post ga+1
            if desired_version == "auto":
                sys.stdout.write(
                    "{0} would continually be upgraded automatically to the latest valid version.\n".format(
                        ss.metadata.name
                    )
                )
            else:
                sys.stdout.write(
                    "{0} would be upgraded to {1}.\n".format(
                        ss.metadata.name, desired_version
                    )
                )
        return upgrade_instances

    # upgrade instances

    patch = {"spec": {"update": {"desiredVersion": desired_version}}}

    for ss in upgrade_instances:
        if desired_version == "auto":
            sys.stdout.write(
                "Enabling auto-upgrade for Arc-enabled SQL managed instance {0} \n".format(
                    ss.metadata.name
                )
            )
        else:
            sys.stdout.write(
                "Upgrading {0} to {1}.\n".format(
                    ss.metadata.name, desired_version
                )
            )

    patch_all_namespaced_objects(upgrade_instances, namespace, patch)

    return upgrade_instances


def resolve_sqlmi_instances(
    namespace,
    name=None,
    field_filter=None,
    label_filter=None,
) -> list:

    client = KubernetesClient.resolve_k8s_client().CustomObjectsApi()

    response = client.list_namespaced_custom_object(
        namespace=namespace,
        field_selector=field_filter,
        label_selector=label_filter,
        group=API_GROUP,
        version=KubernetesClient.get_crd_version(SQLMI_CRD_NAME),
        plural=RESOURCE_KIND_PLURAL,
    )

    items = response.get("items")

    instances = _.map_(
        items, lambda cr: CustomResource.decode(SqlmiCustomResource, cr)
    )

    if name is not None:
        instances = _.filter_(
            instances, lambda i: re.match(name, i.metadata.name)
        )

    return instances


def patch_all_namespaced_objects(instances: list, namespace, body):
    for instance in instances:
        KubernetesClient.merge_namespaced_custom_object(
            name=instance.metadata.name,
            namespace=namespace,
            body=body,
            group=API_GROUP,
            version=KubernetesClient.get_crd_version(SQLMI_CRD_NAME),
            plural=RESOURCE_KIND_PLURAL,
        )


def get_sqlmi_custom_resource(client, name, namespace):
    """
    Queries the kubernetes cluster and returns the custom resource for a SQL Instancewith the given name in
    the specified namespace
    :param client: KubernetesClient
    :param name: The name of the SQL Managed Instance
    :param namespace: Namespace where the SQL Managed Instance is deployed.
    :return: The k8s custom resource if one is found. An error will be raised if the instance is not found.
    """

    try:
        response = retry(
            lambda: client.get_namespaced_custom_object(
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
        cr = CustomResource.decode(SqlmiCustomResource, response)
        cr.metadata.namespace = namespace
        return cr

    except K8sApiException as e:
        if e.status == http_status_codes.not_found:
            raise ValueError(
                "Arc-enabled SQL Managed Instance `{}` was not found in namespace `{}`.".format(
                    name, namespace
                )
            )


def _validate_upgrade_sqlmi_args(name, namespace, instances, desired_version, datacontrollerVersion):
    if name and not instances:
        raise ValueError(
            "Instance {0} does not exist in namespace {1}.".format(
                name, namespace
            )
        )

    if (
        desired_version != "auto"
        and ArcDataImageService.compare_version_tag(
            desired_version, datacontrollerVersion, ignore_label=True
        )
        == 1
    ):
        raise ValueError(
            "Arc-enabled SQL managed instance(s) cannot be upgraded beyond the data controller version {}".format(
                datacontrollerVersion
            )
        )
