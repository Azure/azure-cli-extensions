# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

"""Command definitions for `data control`."""

import base64
import os
import time
from azext_arcdata.core.env import Env
from azext_arcdata.kubernetes_sdk.models.docker_spec import DockerSpec
from azext_arcdata.sqlmi.util import resolve_old_dag_items
import azext_arcdata.core.kubernetes as kubernetes_util
import pydash as _
import yaml
import sys
from azext_arcdata.core.constants import (
    ARC_GROUP,
    AZDATA_PASSWORD,
    AZDATA_USERNAME,
    CERT_ARGUMENT_ERROR_TEMPLATE,
    DATA_CONTROLLER_PLURAL,
    DEFAULT_IMAGE_POLICY,
    DEFAULT_IMAGE_TAG,
    DEFAULT_REGISTRY,
    DEFAULT_REPOSITORY,
    DOCKER_PASSWORD,
    DOCKER_USERNAME,
    LOGSUI_PASSWORD,
    LOGSUI_USERNAME,
    METRICSUI_PASSWORD,
    METRICSUI_USERNAME,
    REGISTRY_PASSWORD,
    REGISTRY_USERNAME,
    DEFAULT_LOGSUI_CERT_SECRET_NAME,
    DEFAULT_METRICSUI_CERT_SECRET_NAME,
)
from azext_arcdata.core.kubernetes import create_namespace_with_retry

# TODO: Refactor out
from azext_arcdata.core.prompt import (
    prompt_for_choice,
    prompt,
    prompt_pass,
    prompt_y_n,
)
from azext_arcdata.core.util import (
    BOOLEAN_STATES,
    check_and_set_kubectl_context,
    check_missing,
    control_config_check,
    display,
    get_config_from_template,
    parse_cert_files,
    parse_labels,
    read_config,
    env_vars_are_set,
    is_set,
    is_windows,
    retry,
    retry_method,
    time_ns,
    validate_creds_from_env,
    get_yaml_from_template,
)
from azext_arcdata.kubernetes_sdk.client import (
    KubernetesClient,
    KubernetesError,
    http_status_codes,
)
from azext_arcdata.kubernetes_sdk.util import (
    check_secret_exists_with_retries,
    create_certificate_secret,
)
from azext_arcdata.kubernetes_sdk.dc.common_util import (
    get_kubernetes_infra,
    validate_dc_create_params,
    validate_infrastructure_value,
    write_file,
    write_output_file,
)
from azext_arcdata.kubernetes_sdk.dc.constants import (
    CONFIG_DIR,
    CONNECTION_MODE,
    CONTROL_CONFIG_FILENAME,
    CONTROLLER_LABEL,
    CONTROLLER_LOGIN_SECRET_NAME,
    CONTROLLER_SVC,
    DATA_CONTROLLER_CRD_NAME,
    DIRECT,
    DISPLAY_NAME,
    EXPORT_COMPLETED_STATE,
    EXPORT_TASK_CRD_NAME,
    EXPORT_TASK_CRD_VERSION,
    EXPORT_TASK_RESOURCE_KIND_PLURAL,
    HELP_DIR,
    INDIRECT,
    INFRASTRUCTURE_CR_ALLOWED_VALUES,
    KAFKA_CRD_NAME,
    LAST_BILLING_USAGE_FILE,
    LOCATION,
    LOGSUI_LOGIN_SECRET_NAME,
    MAX_POLLING_ATTEMPTS,
    METRICSUI_LOGIN_SECRET_NAME,
    MINIMUM_IMAGE_VERSION_SUPPORTED,
    MONITOR_CRD_NAME,
    MONITOR_CRD_VERSION,
    MONITOR_PLURAL,
    MONITOR_RESOURCE,
    TELEMETRY_COLLECTOR_CRD,
    TELEMETRY_COLLECTOR_CRD_NAME,
    TELEMETRY_COLLECTOR_CRD_VERSION,
    OTEL_COLLECTOR_PLURAL,
    OTEL_COLLECTOR_RESOURCE,
    POSTGRES_CRD_NAME,
    RESOURCE_GROUP,
    RESOURCE_KIND_DATA_CONTROLLER,
    SQLMI_CRD_NAME,
    SUBSCRIPTION,
    TASK_API_GROUP,
    TEMPLATE_DIR,
    BOOTSTRAP_TEMPLATES,
    INFRASTRUCTURE_AUTO,
    CRD_SUPPORTED_IMAGE_VERSIONS,
)
from azext_arcdata.kubernetes_sdk.dc.dc_utilities import (
    patch_data_controller,
    resolve_valid_target_version,
    upgrade_arc_control_plane,
    is_v1,
)
from azext_arcdata.kubernetes_sdk.dc.export_util import (
    ExportType,
    add_last_upload_flag,
    generate_export_file_name,
    get_export_timestamp,
)
from azext_arcdata.kubernetes_sdk.models import (
    CustomResourceDefinition,
    MonitorCustomResource,
)
from azext_arcdata.kubernetes_sdk.models.data_controller_custom_resource import (
    CustomResource,
    DataControllerCustomResource,
)
from azext_arcdata.kubernetes_sdk.models.export_task_custom_resource import (
    ExportTaskCustomResource,
)
from azext_arcdata.kubernetes_sdk.arc_docker_image_service import (
    ArcDataImageService,
)
from humanfriendly.terminal.spinners import AutomaticSpinner
from azure.cli.core.azclierror import ArgumentUsageError
from knack.log import get_logger
from knack.prompting import NoTTYException
from knack.cli import CLIError
from kubernetes import client as k8sClient
from kubernetes.client.rest import ApiException as K8sApiException
from urllib3.exceptions import MaxRetryError, NewConnectionError
from http import HTTPStatus
from requests.exceptions import SSLError
from types import SimpleNamespace
from typing import List, Tuple

from azext_arcdata.postgres.postgres_utilities import resolve_postgres_instances
from azext_arcdata.sqlmi.sqlmi_utilities import resolve_sqlmi_instances
from azext_arcdata.sqlmi.constants import (
    SQLMI_TIER_BUSINESS_CRITICAL,
    SQLMI_TIER_BUSINESS_CRITICAL_SHORT,
)


__all__ = ["DataControllerClient"]

CONNECTION_RETRY_ATTEMPTS = 12
DELETE_CLUSTER_TIMEOUT_SECONDS = 300
RETRY_INTERVAL = 5
UPDATE_INTERVAL = (15 * 60) / RETRY_INTERVAL
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
logger = get_logger(__name__)


# ============================================================================ #
# ============================================================================ #
# ============================================================================ #


class JobNotCompleteException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# ============================================================================ #
# ============================================================================ #
# ============================================================================ #


class DataControllerClient(object):
    def __init__(self, stdout, stderr):
        check_and_set_kubectl_context()
        self._client = KubernetesClient
        # for now all methods in the KubernetesClient are marked static.  We
        # may need to change them to instance methods going forward.
        self.stdout = stdout
        self.stderr = stderr

    # ------------------------------------------------------------------------ #
    # DC Create
    # ------------------------------------------------------------------------ #

    def create(
        self,
        subscription,
        namespace,
        name,
        resource_group,
        location,
        config_profile,
        storage_class=None,
        infrastructure=None,
        image_tag=None,
        labels=None,
        annotations=None,
        service_annotations=None,
        service_labels=None,
        storage_labels=None,
        storage_annotations=None,
        logs_ui_public_key_file=None,
        logs_ui_private_key_file=None,
        metrics_ui_public_key_file=None,
        metrics_ui_private_key_file=None,
    ):
        """
        If an argument is not provided, the user will be prompted for the needed
        values NoTTY Scenario: provide a config_profile, profile_name
        """
        args = {
            "namespace": namespace,
            "name": name,
            "connectivity_mode": INDIRECT,
            "resource_group": resource_group,
            "location": location,
            "storage_class": storage_class,
            "infrastructure": infrastructure,
            "labels": labels,
            "annotations": annotations,
            "service_annotations": service_annotations,
            "service_labels": service_labels,
            "storage_labels": storage_labels,
            "storage_annotations": storage_annotations,
            "subscription": subscription,
            "logs_ui_public_key_file": logs_ui_public_key_file,
            "logs_ui_private_key_file": logs_ui_private_key_file,
            "metrics_ui_public_key_file": metrics_ui_public_key_file,
            "metrics_ui_private_key_file": metrics_ui_private_key_file,
        }

        client = self._client
        stdout = self.stdout

        # subscription = client.subscription or prompt_assert("Subscription: ")
        # stdout("\nUsing subscription '{}'.".format(subscription))

        # -- Check Kubectl Context --
        # check_and_set_kubectl_context()
        # namespace = namespace or client.namespace

        # Validate params
        validate_dc_create_params(
            name,
            namespace,
            subscription,
            location,
            resource_group,
            # connectivity_mode,
            infrastructure,
            # profile_name,
            # path,
            logs_ui_public_key_file,
            logs_ui_private_key_file,
            metrics_ui_public_key_file,
            metrics_ui_private_key_file,
        )

        # Sets up credential environment variables needed for login
        # credential secret creation
        #
        self._setup_env_vars()

        logsui_public_key, logsui_private_key = None, None
        metricsui_public_key, metricsui_private_key = None, None

        logsui_secret_exists = check_secret_exists_with_retries(
            client, namespace, DEFAULT_LOGSUI_CERT_SECRET_NAME
        )
        if logsui_secret_exists and (
            logs_ui_public_key_file or logs_ui_private_key_file
        ):
            raise ArgumentUsageError(
                CERT_ARGUMENT_ERROR_TEMPLATE.format(
                    DEFAULT_LOGSUI_CERT_SECRET_NAME
                )
            )
        elif not logsui_secret_exists:
            # Fetches and validates the public/private key file params
            #
            (
                logsui_public_key,
                logsui_private_key,
            ) = self._validate_and_fetch_monitoring_keys(
                logs_ui_public_key_file, logs_ui_private_key_file
            )

        metricsui_secret_exists = check_secret_exists_with_retries(
            client, namespace, DEFAULT_METRICSUI_CERT_SECRET_NAME
        )
        if metricsui_secret_exists and (
            metrics_ui_public_key_file or metrics_ui_private_key_file
        ):
            raise ArgumentUsageError(
                CERT_ARGUMENT_ERROR_TEMPLATE.format(
                    DEFAULT_METRICSUI_CERT_SECRET_NAME
                )
            )
        elif not metricsui_secret_exists:
            # Fetches and validates the public/private key file params
            #
            (
                metricsui_public_key,
                metricsui_private_key,
            ) = self._validate_and_fetch_monitoring_keys(
                metrics_ui_public_key_file, metrics_ui_private_key_file
            )

        # Get infrastructure if needed.

        if infrastructure == INFRASTRUCTURE_AUTO:
            infrastructure = self._detect_or_prompt_infrastructure()

        #  -- User entered an existing configuration type

        # if config_profile is just a name, join with base-config-dir
        if not os.path.isdir(config_profile):
            config_profile = os.path.join(CONFIG_DIR, config_profile)
        if not os.path.isdir(config_profile):
            raise ValueError(
                "Profile name {0} does not exist.".format(
                    os.path.basename(config_profile)
                )
            )

        if labels:
            try:
                stdout("labels set {}", labels)
                parse_labels(labels)
            except ValueError as e:
                raise ValueError("Labels invalid: {}", e)

        if annotations:
            try:
                stdout("annotations set {}", annotations)
                parse_labels(annotations)
            except ValueError as e:
                raise ValueError("Annotations invalid: {}", e)

        if service_labels:
            try:
                parse_labels(service_labels)
            except ValueError as e:
                raise ValueError("Service labels invalid: {}", e)

        if service_annotations:
            try:
                parse_labels(service_annotations)
            except ValueError as e:
                raise ValueError("Service annotations invalid: {}", e)

        if storage_labels:
            try:
                parse_labels(storage_labels)
            except ValueError as e:
                raise ValueError("Storage labels invalid: {}", e)

        if storage_annotations:
            try:
                parse_labels(storage_annotations)
            except ValueError as e:
                raise ValueError("Storage annotations invalid: {}", e)

        # -- Read json into python dictionary --
        # config_object = read_config(path, CONTROL_CONFIG_FILENAME)
        config_object = read_config(config_profile, CONTROL_CONFIG_FILENAME)
        dc_cr = CustomResource.decode(
            DataControllerCustomResource, config_object
        )

        dc_api_version = dc_cr.apiVersion.split("/")[1]

        if dc_api_version not in CRD_SUPPORTED_IMAGE_VERSIONS:
            raise ValueError(
                "The configuration profile has an unsupported API version '{"
                "}' in DataController spec.".format(dc_cr.apiVersion)
            )

        registry = (
            Env.get("DOCKER_REGISTRY")
            or dc_cr.spec.docker.registry
            or DEFAULT_REGISTRY
        )
        repository = (
            Env.get("DOCKER_REPOSITORY")
            or dc_cr.spec.docker.repository
            or DEFAULT_REPOSITORY
        )
        image_tag = (
            image_tag
            or Env.get("DOCKER_IMAGE_TAG")
            or dc_cr.spec.docker.imageTag
            or DEFAULT_IMAGE_TAG
        )
        image_pull_policy = (
            Env.get("DOCKER_IMAGE_POLICY")
            or dc_cr.spec.docker.imagePullPolicy
            or DEFAULT_IMAGE_POLICY
        )
        dc_cr.spec.docker = DockerSpec(
            registry=registry,
            repository=repository,
            imageTag=image_tag,
            imagePullPolicy=image_pull_policy,
        )
        stdout("Using image: {}/{}:{}".format(registry, repository, image_tag))

        image_version = dc_cr.spec.docker.imageTag.split("_")[0]

        if image_version not in CRD_SUPPORTED_IMAGE_VERSIONS[dc_api_version]:
            raise ValueError(
                "The configuration profile has an image tag '{}' which is not supported "
                "in {} DataController spec.".format(
                    dc_cr.spec.docker.imageTag, dc_cr.apiVersion
                )
            )

        if (
            ArcDataImageService.compare_version_tag(
                dc_cr.spec.docker.imageTag,
                MINIMUM_IMAGE_VERSION_SUPPORTED,
                ignore_label=True,
            )
            < 0
        ):
            raise ValueError(
                "Deployment of version older than {} is not supported in this version of arcdata Azure CLI extension.\n".format(
                    MINIMUM_IMAGE_VERSION_SUPPORTED
                )
                + "Please install the arcdata Azure CLI extension from the corresponding release.\n"
                + "See: https://docs.microsoft.com/azure/azure-arc/data/version-log"
            )

        # Sets up credential environment variables needed for login
        # credential secret creation
        #
        self._setup_env_vars()

        # Get infrastructure if needed.
        #
        if infrastructure == INFRASTRUCTURE_AUTO:
            infrastructure = self._detect_or_prompt_infrastructure()

        # If no infrastructure parameter was provided, try to get it from
        # the file
        if infrastructure is None:
            infrastructure = self._get_infrastructure_from_file_or_auto(
                config_object
            )

        # this is dangerous
        # args = locals()
        dc_cr.apply_args(**args)

        dc_encoding = dc_cr.encode()
        # -- Get help documentation for missing values --
        help_object = read_config(HELP_DIR, CONTROL_CONFIG_FILENAME)
        # -- Check for missing values in the config object --
        check_missing(
            stdout, False, dc_encoding, help_object, CONTROL_CONFIG_FILENAME
        )
        # -- Check if dc config is valid
        control_config_check(dc_encoding)

        # Rehydrate from config object which might have been updated from
        # prompts by check_missing
        dc_cr = CustomResource.decode(DataControllerCustomResource, dc_encoding)

        annotations = {
            "openshift.io/sa.scc.supplemental-groups": "1000700001/10000",
            "openshift.io/sa.scc.uid-range": "1000700001/10000",
        }

        # prepare the namespace
        create_namespace_with_retry(
            dc_cr.metadata.namespace, annotations=annotations
        )

        # -- attempt to create cluster --
        stdout("")
        stdout("Deploying data controller")
        stdout("")
        stdout(
            "NOTE: Data controller creation can take a significant amount "
            "of time depending on"
        )
        stdout(
            "configuration, network speed, and the number of nodes in the "
            "cluster."
        )
        stdout("")

        if logsui_public_key and logsui_private_key:
            create_certificate_secret(
                client,
                dc_cr.metadata.namespace,
                DEFAULT_LOGSUI_CERT_SECRET_NAME,
                logsui_public_key,
                logsui_private_key,
            )

        if metricsui_public_key and metricsui_private_key:
            create_certificate_secret(
                client,
                dc_cr.metadata.namespace,
                DEFAULT_METRICSUI_CERT_SECRET_NAME,
                metricsui_public_key,
                metricsui_private_key,
            )

        self._create_monitoring_secrets(dc_cr)
        response = self._dc_create(dc_cr)
        deployed_cr = CustomResource.decode(
            DataControllerCustomResource, response
        )

        self._await_dc_ready(namespace)

        stdout("Data controller successfully deployed.")

        return deployed_cr.encode()

    def _dc_create(self, cr: DataControllerCustomResource):
        """
        Create a data controller
        """
        # Set up the private registry if the docker environment variables set
        #
        if (
            os.environ.get(DOCKER_USERNAME) and os.environ.get(DOCKER_PASSWORD)
        ) or (
            os.environ.get(REGISTRY_USERNAME)
            and os.environ.get(REGISTRY_PASSWORD)
        ):
            retry(
                lambda: kubernetes_util.setup_private_registry(
                    cr.metadata.namespace,
                    cr.spec.docker.registry,
                    secret_name=cr.spec.credentials.dockerRegistry,
                    ignore_conflict=True,
                ),
                retry_count=CONNECTION_RETRY_ATTEMPTS,
                retry_delay=RETRY_INTERVAL,
                retry_method="set up docker private registry",
                retry_on_exceptions=(NewConnectionError, MaxRetryError),
            )

        # Create deployer service acocunts
        self.create_deployer_service_account(cr.metadata.namespace)

        # Bootstrap the deployment with a job to run helm install
        self.bootstrap_create(cr.metadata.namespace, cr)

        # Set up secrets
        #
        try:
            model = dict()
            model["namespace"] = cr.metadata.namespace
            ns = cr.metadata.namespace

            connectivity_mode = cr.spec.settings["azure"][
                CONNECTION_MODE
            ].lower()

            if connectivity_mode == DIRECT and not self._client.secret_exists(
                ns, "upload-service-principal-secret"
            ):
                model["SPN_CLIENT_ID"] = base64.b64encode(
                    bytes(os.environ["SPN_CLIENT_ID"], "utf-8")
                ).decode("utf-8")
                # [SuppressMessage("Microsoft.Security", "CS002:SecretInNextLine", Justification="False positive. The next line is the name of an env variable, not a secret.")
                spn_env = "SPN_CLIENT_SECRET"
                model[spn_env] = base64.b64encode(
                    bytes(os.environ[spn_env], "utf-8")
                ).decode("utf-8")
                model["SPN_TENANT_ID"] = base64.b64encode(
                    bytes(os.environ["SPN_TENANT_ID"], "utf-8")
                ).decode("utf-8")
                model["SPN_AUTHORITY"] = base64.b64encode(
                    bytes(os.environ["SPN_AUTHORITY"], "utf-8")
                ).decode("utf-8")
                config = get_config_from_template(
                    os.path.join(
                        TEMPLATE_DIR,
                        "secret-upload-service-principal.yaml.tmpl",
                    ),
                    model,
                )
                secret = yaml.safe_load(config)
                self._client.create_secret(ns, secret)

        except K8sApiException as e:
            raise KubernetesError(e)

        # Create DataController custom resource
        #
        retry(
            lambda: self._client.create_namespaced_custom_object(
                cr=cr, plural=DATA_CONTROLLER_PLURAL, ignore_conflict=True
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

        i = 0

        # Check if the external controller service exists
        #
        while not retry(
            lambda: self._client.service_ready(
                cr.metadata.namespace, CONTROLLER_SVC
            ),
            retry_count=CONNECTION_RETRY_ATTEMPTS,
            retry_delay=RETRY_INTERVAL,
            retry_method="service ready",
            retry_on_exceptions=(NewConnectionError, MaxRetryError),
        ):
            # Log to console once every 5 minutes if controller service is
            # not ready
            #
            if i != 0 and i % 60 == 0:
                display(
                    "Waiting for data controller service to be ready after %d "
                    "minutes." % ((i * RETRY_INTERVAL) / 60)
                )

            time.sleep(RETRY_INTERVAL)
            i = i + 1

        # Check if controller is running
        #
        while not retry(
            lambda: self._client.pod_is_running(
                cr.metadata.namespace, CONTROLLER_LABEL
            ),
            retry_count=CONNECTION_RETRY_ATTEMPTS,
            retry_delay=RETRY_INTERVAL,
            retry_method="pod is running",
            retry_on_exceptions=(
                NewConnectionError,
                MaxRetryError,
                K8sApiException,
            ),
        ):
            # Log to console once every 5 minutes if controller is not running
            #
            if i != 0 and i % 60 == 0:
                display(
                    "Waiting for data controller to be running after %d "
                    "minutes." % ((i * RETRY_INTERVAL) / 60)
                )

            time.sleep(RETRY_INTERVAL)
            i = i + 1

        service = retry(
            lambda: self._client.get_service(
                cr.metadata.namespace, CONTROLLER_SVC
            ),
            retry_count=CONNECTION_RETRY_ATTEMPTS,
            retry_delay=RETRY_INTERVAL,
            retry_method="get service",
            retry_on_exceptions=(
                NewConnectionError,
                MaxRetryError,
                K8sApiException,
            ),
        )

        controller_endpoint = retry(
            lambda: self._client.get_service_endpoint(
                cr.metadata.namespace, service
            ),
            retry_count=CONNECTION_RETRY_ATTEMPTS,
            retry_delay=RETRY_INTERVAL,
            retry_method="get service endpoint",
            retry_on_exceptions=(
                NewConnectionError,
                MaxRetryError,
                K8sApiException,
            ),
        )

        ip_endpoint = retry(
            lambda: self._client.get_service_endpoint(
                cr.metadata.namespace, service, True
            ),
            retry_count=CONNECTION_RETRY_ATTEMPTS,
            retry_delay=RETRY_INTERVAL,
            retry_method="get service endpoint",
            retry_on_exceptions=(
                NewConnectionError,
                MaxRetryError,
                K8sApiException,
            ),
        )

        if controller_endpoint == ip_endpoint:
            endpoint_str = controller_endpoint
        else:
            endpoint_str = controller_endpoint + ", " + ip_endpoint

        display(
            "Data controller endpoint is available at {}".format(endpoint_str)
        )

        response = retry(
            lambda: self._client.get_namespaced_custom_object(
                cr.metadata.name,
                cr.metadata.namespace,
                group=ARC_GROUP,
                version=KubernetesClient.get_crd_version(
                    DATA_CONTROLLER_CRD_NAME
                ),
                plural=DATA_CONTROLLER_PLURAL,
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

        return response

    def _await_dc_ready(self, namespace):
        while not self.is_dc_ready(namespace):
            time.sleep(5)
            logger.info("Data controller is not ready yet.")

    def _setup_env_vars(self) -> None:
        """
        Validates and ensures that two of the three following sets of
        environment
        variables are set (or just AZDATA_USERNAME and AZDATA_PASSWORD):
            (AZDATA_USERNAME, AZDATA_PASSWORD)
            (LOGSUI_USERNAME, LOGSUI_PASSWORD)
            (METRICSUI_USERNAME, METRICSUI_PASSWORD)
        """

        def set_credential_vars(vars: List[str], msg: str):
            """
            Prompts the user to enter values for the given vars. Expecting
            a username var to be first in the list and password second.
            """
            if not is_set(vars[0]):
                os.environ[vars[0]] = prompt(msg.strip() + " username:").strip()
            if not is_set(vars[1]):
                os.environ[vars[1]] = prompt_pass(
                    msg.strip() + " password:", True
                ).strip()

        def raise_error(vars: List[str]):
            raise ValueError(
                "Missing environment variables."
                " Please set either {0} and {1} or {2} and {3}".format(
                    AZDATA_USERNAME, AZDATA_PASSWORD, vars[0], vars[1]
                )
            )

        # Raise error if only one part of a credential is set
        #
        logs_vars = [LOGSUI_USERNAME, LOGSUI_PASSWORD]
        metrics_vars = [METRICSUI_USERNAME, METRICSUI_PASSWORD]
        default_vars = [AZDATA_USERNAME, AZDATA_PASSWORD]
        validate_creds_from_env(logs_vars[0], logs_vars[1])
        validate_creds_from_env(metrics_vars[0], metrics_vars[1])
        if not (env_vars_are_set(logs_vars) and env_vars_are_set(metrics_vars)):
            if env_vars_are_set(metrics_vars):
                if not env_vars_are_set(default_vars):
                    if sys.stdin.isatty():
                        set_credential_vars(logs_vars, "Logs administrator")
                    else:
                        raise_error(logs_vars)
            elif env_vars_are_set(logs_vars):
                if not env_vars_are_set(default_vars):
                    if sys.stdin.isatty():
                        set_credential_vars(
                            metrics_vars, "Metrics administrator"
                        )
                    else:
                        raise_error(metrics_vars)
            else:
                if not env_vars_are_set(default_vars):
                    if sys.stdin.isatty():
                        set_credential_vars(
                            default_vars, "Monitoring administrator"
                        )
                    else:
                        raise ValueError(
                            "Missing environment variables. Please set {0} "
                            "and {1}".format(AZDATA_USERNAME, AZDATA_PASSWORD)
                        )
                validate_creds_from_env(default_vars[0], default_vars[1])

    def _validate_and_fetch_monitoring_keys(
        self, public_key_file: str, private_key_file: str
    ) -> Tuple[str, str]:

        if public_key_file and not private_key_file:
            raise ArgumentUsageError(
                "Please specify both the monitoring public and "
                "private key files. Only public key file specified."
            )

        if private_key_file and not public_key_file:
            raise ArgumentUsageError(
                "Please specify both the monitoring public and "
                "private key files. Only private key file specified."
            )

        if not private_key_file and not public_key_file:
            return None, None

        return parse_cert_files(public_key_file, private_key_file)

    def get_data_controller(self, cluster_name):
        """
        Get data control
        """
        # self.cluster_name = cluster_name

        data_controller_list = retry(
            lambda: self._client.list_namespaced_custom_object(
                namespace=cluster_name,
                group=ARC_GROUP,
                version=self._client.get_crd_version(DATA_CONTROLLER_CRD_NAME),
                plural=DATA_CONTROLLER_PLURAL,
            ),
            retry_count=CONNECTION_RETRY_ATTEMPTS,
            retry_delay=RETRY_INTERVAL,
            retry_method="get namespaced custom object",
            retry_on_exceptions=(NewConnectionError, MaxRetryError),
        )

        data_controller_cr = None

        # Kubernetes will not block the creation of more than one datacontroller
        # in a namespace. To prevent multiple datacontrollers from being
        # deployed in the same namespace, we update the state for any
        # datacontrollers deployed after the first to state "duplicateerror". To
        # avoid using the incorrect datacontroller custom resource, search for
        # the instance that is not in an error state.
        for data_controller in data_controller_list["items"]:
            if (
                data_controller["status"]["state"] != ""
                and data_controller["status"]["state"].lower()
                != "duplicateerror"
            ):
                data_controller_cr = data_controller
                break

        dc_settings = data_controller_cr["spec"]["settings"]

        return {
            "instanceName": dc_settings["controller"][DISPLAY_NAME],
            "instanceNamespace": cluster_name,
            "kind": RESOURCE_KIND_DATA_CONTROLLER,
            "subscriptionId": dc_settings["azure"][SUBSCRIPTION],
            "resourceGroupName": dc_settings["azure"][RESOURCE_GROUP],
            "location": dc_settings["azure"][LOCATION],
            "connectionMode": dc_settings["azure"][CONNECTION_MODE],
            "infrastructure": data_controller_cr["spec"]["infrastructure"],
            "publicKey": "",
            "k8sRaw": data_controller_cr,
            "infrastructure": _.get(data_controller_cr, "spec.infrastructure"),
        }

    # ------------------------------------------------------------------------ #
    # Misc
    # ------------------------------------------------------------------------ #

    def get_config(self, namespace):
        (_, config) = self._client.get_arc_datacontroller(namespace)
        return config

    def get_status(self, namespace=None):
        """
        Return the status of the data controller custom resource.
        """

        (cr, config) = self._client.get_arc_datacontroller(namespace)

        state = cr.status.state
        if state:
            # client.stdout(state.lower().capitalize())
            return state.lower().capitalize()
        else:
            raise ValueError(
                "Status unavailable for data controller `{0}` in Kubernetes "
                "namespace `{1}`.".format(cr.metadata.name, namespace)
            )

    def is_dc_ready(self, namespace):
        (cr, config) = self._client.get_arc_datacontroller(namespace)
        if str(cr.metadata.generation) != str(cr.status.observed_generation):
            return False

        state = cr.status.state
        if state:
            # client.stdout(state.lower().capitalize())
            return state.lower().capitalize().strip() == "Ready"
        else:
            raise ValueError(
                "Status unavailable for data controller `{0}` in Kubernetes "
                "namespace `{1}`.".format(cr.metadata.name, namespace)
            )

    def get_controller_endpoint(self, namespace):
        check_and_set_kubectl_context()
        service = retry(
            lambda: self._client.get_service(namespace, CONTROLLER_SVC),
            retry_count=CONNECTION_RETRY_ATTEMPTS,
            retry_delay=RETRY_INTERVAL,
            retry_method="get service",
            retry_on_exceptions=(
                NewConnectionError,
                MaxRetryError,
                K8sApiException,
            ),
        )
        logger.debug(service)

        endpoint = retry(
            lambda: self._client.get_service_endpoint(namespace, service),
            retry_count=CONNECTION_RETRY_ATTEMPTS,
            retry_delay=RETRY_INTERVAL,
            retry_method="get service endpoint",
            retry_on_exceptions=(
                NewConnectionError,
                MaxRetryError,
                K8sApiException,
            ),
        )
        logger.debug("Controller Endpoint: %s", endpoint)

        return endpoint

    def _get_infrastructure_from_file_or_auto(self, config_object):
        """
        Get and validate infrastructure form config_object. If missing,
        detect or
        prompt for it.
        """

        def _get_infrastructure_from_file(config_obj):
            """
            Get infrastructure from the confg file. If no
            "spec.infrastructure" was
            provided, return None. Otherwise validate it and raise an error
            if not
            valid.
            """

            logger.debug("Looking for infrastructure in control.json")

            try:
                infra = config_obj["spec"]["infrastructure"]
                logger.debug("Found infrastructure in control.json: %s", infra)
                validate_infrastructure_value(infra)
                return infra
            except KeyError:
                return None

        # try to get infrastructure from file
        infrastructure = _get_infrastructure_from_file(config_object)

        # detect or prompt for it
        if infrastructure is None:
            infrastructure = self._detect_or_prompt_infrastructure()

        return infrastructure

    def _detect_or_prompt_infrastructure(self):
        """
        Try to detect the infrastructure from the node's
        spec.provider_id. If not
        possible prompt for it / fail (based on TTY).
        """

        logger.debug("Trying to detect infrastructure.")

        try:
            nodes = self._client.list_node()
            return get_kubernetes_infra(nodes)
        except Exception as e:
            try:
                logger.info(
                    "Unable to detect infrastructure: %s. Will try to "
                    "prompt for it.",
                    e,
                )
                self.stdout(
                    "Please select the infrastructure for the data "
                    "controller:"
                )
                return prompt_for_choice(INFRASTRUCTURE_CR_ALLOWED_VALUES)
            except NoTTYException:
                raise Exception(
                    "Unable to determine the infrastructure for the data "
                    "controller. Please provide an '--infrastructure' "
                    "value other than 'auto'."
                )

    # ------------------------------------------------------------------------ #
    # DC Export
    # ------------------------------------------------------------------------ #

    def export(self, namespace, export_type, path):
        """
        Export metrics, logs or usage to a file.
        """
        from datetime import datetime, timedelta

        stdout = self.stdout
        cluster_name = namespace

        info_msg = (
            'This option exports {} of all instances in "{}" to the file: "{}".'
        )

        # -- Check Kubectl Context --
        # check_and_set_kubectl_context()

        """
        if not use_k8s:
        raise ValueError(USE_K8S_EXCEPTION_TEXT)

        if export_type.lower() not in ExportType.list():
            raise ValueError(
            "{} is not a supported type. "
                    "Please specify one of the following: {}".format(
                        export_type, ExportType.list()
                    )
                )
        """

        # path = _check_prompt_export_output_file(path, force)
        # Get DC CR after export task executed.
        connection_mode = self.get_data_controller(namespace).get(
            "connectionMode"
        )
        if connection_mode == DIRECT:
            raise Exception(
                "Performing this action from az is only allowed using indirect mode."
            )

        content = {
            "exportType": export_type,
            "dataTimestamp": datetime.now().isoformat(
                sep=" ", timespec="milliseconds"
            ),
            "instances": [],
            "data": [],
        }

        # Create export custom resource
        # Get startTime and endTime of export
        end_time = datetime.utcnow()
        start_time = get_export_timestamp(export_type)
        export_cr_name = "export-{}-{}".format(
            export_type,
            end_time.strftime("%Y-%m-%d-%H-%M-%S")
            + "-"
            + str(time_ns() // 1000000),
        )

        crd = CustomResourceDefinition(
            self._client.get_crd(EXPORT_TASK_CRD_NAME)
        )

        spec_object = {
            "apiVersion": crd.group + "/" + crd.stored_version,
            "kind": crd.kind,
            "metadata": {
                "name": export_cr_name,
                "namespace": cluster_name,
            },
            "spec": {
                "exportType": export_type,
                "startTime": start_time,
                "endTime": end_time,
            },
        }

        cr = CustomResource.decode(ExportTaskCustomResource, spec_object)
        # cr.validate(client.apis.kubernetes)  # >>>>> ?????

        response = retry(
            lambda: self._client.create_namespaced_custom_object_with_body(
                spec_object, cr=cr, plural=crd.plural, ignore_conflict=True
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

        if response:
            stdout(
                "Export custom resource: {} is created.".format(export_cr_name)
            )
        else:
            raise Exception(
                "Failed to create export custom resource: {}".format(
                    export_cr_name
                )
            )

        index_file_path = self._get_export_task_file_path(
            export_cr_name, namespace
        )

        if index_file_path == "No data are exported" or index_file_path is None:
            raise Exception("No data are exported.")

        controller_endpoint = self.get_controller_endpoint(namespace)

        # Get download path
        index_file = retry(
            self.get_export_file_path,
            index_file_path,
            controller_endpoint,
            retry_count=CONNECTION_RETRY_ATTEMPTS,
            retry_delay=RETRY_INTERVAL,
            retry_method="download index file",
            retry_on_exceptions=(NewConnectionError, MaxRetryError),
        )

        index_file_json = index_file

        data_controller = self.get_data_controller(cluster_name)
        data_controller["publicKey"] = index_file_json[
            "publicSigningCertificate"
        ]
        content["dataController"] = data_controller
        content["dataTimestamp"] = index_file_json["endTime"]

        instances = self.list_all_custom_resource_instances(cluster_name)
        content["instances"] = instances

        active_instances = dict.fromkeys(
            map(
                lambda x: "{}/{}.{}".format(
                    x["kind"], x["instanceName"], x["instanceNamespace"]
                ),
                instances,
            )
        )

        deleted_instances = index_file_json["customResourceDeletionList"]

        # Ignored instances which were deleted but subsequently
        # recreated,
        # as their will be updated
        content["deletedInstances"] = list(
            filter(
                lambda x: "{}/{}.{}".format(
                    x["kind"], x["instanceName"], x["instanceNamespace"]
                )
                not in active_instances.keys(),
                deleted_instances,
            )
        )

        stdout(info_msg.format(export_type, cluster_name, path))

        if (
            export_type.lower() == ExportType.metrics.value
            or export_type.lower() == ExportType.usage.value
        ):
            file = retry(
                self.get_export_file_path,
                index_file_json["dataFilePathList"][0],
                controller_endpoint,
                retry_count=CONNECTION_RETRY_ATTEMPTS,
                retry_delay=RETRY_INTERVAL,
                retry_method="download data file",
                retry_on_exceptions=(NewConnectionError, MaxRetryError),
            )

            if file:
                content["data"] = file
                write_output_file(path, content)
                stdout("{0} are exported to {1}".format(export_type, path))
            else:
                allowNodeMetricsCollection = content["dataController"][
                    "k8sRaw"
                ]["spec"]["security"]["allowNodeMetricsCollection"]
                allowPodMetricsCollection = content["dataController"]["k8sRaw"][
                    "spec"
                ]["security"]["allowPodMetricsCollection"]
                if (
                    not allowNodeMetricsCollection
                    or not allowPodMetricsCollection
                ):
                    raise Exception(
                        "There are no metrics available for export. "
                        "Please follow the documentation to ensure "
                        "that "
                        "allowNodeMetricsCollection and/or "
                        "allowPodMetricsCollection are set to true to "
                        "collect metrics and then export them."
                    )
                else:
                    raise Exception(
                        "Failed to get metrics. "
                        "Please ensure you connect to the correct "
                        "cluster "
                        "and the instances have metrics."
                    )
        elif export_type.lower() == ExportType.logs.value:
            file_index = 0
            data_files = []
            for data_file_path in index_file_json["dataFilePathList"]:
                file = retry(
                    self.get_export_file_path,
                    data_file_path,
                    controller_endpoint,
                    retry_count=CONNECTION_RETRY_ATTEMPTS,
                    retry_delay=RETRY_INTERVAL,
                    retry_method="download data file",
                    retry_on_exceptions=(NewConnectionError, MaxRetryError),
                )

                if file:
                    data = file
                    file_path = generate_export_file_name(path, file_index)
                    write_file(
                        file_path,
                        data,
                        export_type,
                        index_file_json["endTime"],
                    )
                    file_index += 1
                    data_files.append(file_path)

            if len(data_files) > 0:
                content["data"] = data_files
                write_output_file(path, content)
                stdout("{0} are exported to {1}".format(export_type, path))
            else:
                stdout("No log is exported.")

    @staticmethod
    def get_export_file_path(file_path, controller_endpoint):
        import json
        import requests
        from urllib3 import disable_warnings, exceptions

        def _get_export_file_path(verify=True):

            uri = "{endpoint}/api/v{version}/export/{file_path}".format(
                endpoint=controller_endpoint, version=1, file_path=file_path
            )
            logger.debug("EXPORT FILE PATH URI: %s", uri)
            logger.debug("SSL certificate verification: %s", verify)

            disable_warnings(exceptions.InsecureRequestWarning)
            return json.loads(requests.get(uri, verify=verify).text)

        verify_ssl = os.environ.get("AZDATA_VERIFY_SSL")
        logger.debug("AZDATA_VERIFY_SSL: %s", verify_ssl)

        if verify_ssl is None:
            try:
                return _get_export_file_path()
            except SSLError as e:
                logger.debug(e)

                try:
                    bypass = prompt_y_n("Bypass server certificate check?")
                except NoTTYException:
                    raise CLIError(
                        "Specify environment variable "
                        "'AZDATA_VERIFY_SSL=yes|no' for "
                        "non-interactive mode."
                    )

                if not bypass:
                    logger.debug(
                        "You have opted to require the server "
                        "certificate check, aborting."
                    )
                    raise CLIError(e)

                logger.warn(
                    "You have opted to bypass the server certificate check."
                )

                # Set the VERIFY_SSL flag for subsequent calls
                os.environ["AZDATA_VERIFY_SSL"] = "no"

                return _get_export_file_path(verify=False)

        else:
            return _get_export_file_path(verify=BOOLEAN_STATES(verify_ssl))

    def list_all_custom_resource_instances(self, cluster_name):
        """
        list all custom resource instances
        """
        result = []
        crd_names = [POSTGRES_CRD_NAME, SQLMI_CRD_NAME]

        for crd_name in crd_names:
            # Create the control plane CRD if it doesn't already exist
            crd = CustomResourceDefinition(self._client.get_crd(crd_name))

            try:
                response = self._client.list_namespaced_custom_object(
                    cluster_name, crd=crd
                )
            except K8sApiException as e:
                if e.status == http_status_codes.not_found:
                    # CRD has not been applied yet, because no custom
                    # resource of this kind has been created yet
                    continue
                else:
                    raise e

            for item in response["items"]:
                spec = item["spec"]
                status = item["status"] if "status" in item else None

                if (
                    status
                    and "state" in status
                    and status["state"].lower() == "ready"
                ):
                    result.append(
                        {
                            "kind": item["kind"],
                            "instanceName": item["metadata"]["name"],
                            "instanceNamespace": item["metadata"]["namespace"],
                            "creationTimestamp": item["metadata"][
                                "creationTimestamp"
                            ],
                            "externalEndpoint": status["externalEndpoint"]
                            if "externalEndpoint" in status
                            else "-",
                            "vcores": str(spec["limits"]["vcores"])
                            if "limits" in spec and "vcores" in spec["limits"]
                            else "-",
                            "k8sRaw": item,
                        }
                    )

        return result

    def _get_export_task_file_path(self, name, namespace):
        import time

        retry_count = 0

        while retry_count < MAX_POLLING_ATTEMPTS:
            export_task = retry(
                lambda: self._client.get_namespaced_custom_object(
                    name=name,
                    namespace=namespace,
                    group=TASK_API_GROUP,
                    version=EXPORT_TASK_CRD_VERSION,
                    plural=EXPORT_TASK_RESOURCE_KIND_PLURAL,
                ),
                retry_count=CONNECTION_RETRY_ATTEMPTS,
                retry_delay=RETRY_INTERVAL,
                retry_method="get namespaced custom object",
                retry_on_exceptions=(NewConnectionError, MaxRetryError),
            )

            state = export_task.get("status", {}).get("state")
            if state is None:
                retry_count += 1
                time.sleep(20)
            else:
                self.stdout(
                    "Export custom resource: {0} state is {1}".format(
                        name, state
                    )
                )
                if state == EXPORT_COMPLETED_STATE:
                    logger.debug(export_task)
                    return export_task.get("status", {}).get("path")
                else:
                    time.sleep(20)

        raise Exception("Export custom resource:{0} is not ready.".format(name))

    def _create_monitoring_secrets(self, cr: CustomResource) -> None:
        """
        Creates the logsui and metricsui admin secrets based on
        environment variable values.
        """

        def to_b64_string(s: str):
            """
            Base 64 encodes the byte representation of
            a string. Useful for creating the values of
            k8s secrets.
            """
            return base64.b64encode(bytes(s, "utf-8")).decode("utf-8")

        def create_login_secret(model: any):
            """
            Creates a login secret from a model. Expected
            to have the following fields:
                - name
                - username
                - password
            """
            secret_body = get_config_from_template(
                os.path.join(
                    TEMPLATE_DIR,
                    "login-secret.yaml.tmpl",
                ),
                model,
            )

            retry(
                lambda: self._client.create_secret(
                    cr.metadata.namespace, yaml.safe_load(secret_body)
                ),
                retry_count=CONNECTION_RETRY_ATTEMPTS,
                retry_delay=RETRY_INTERVAL,
                retry_method="create secret",
                retry_on_exceptions=(
                    NewConnectionError,
                    MaxRetryError,
                    KubernetesError,
                ),
            )

        def create_login(name: str, username_var: str, password_var: str):
            """
            Determines the appropriate login credential values based on
            environment variables and creates the login secret.

            Throws an exception if only one of username or password
            are provided.

            Defaults to AZDATA_USERNAME and AZDATA_PASSWORD if neither
            part of the credential is provided.
            """
            validate_creds_from_env(username_var, password_var)
            username = os.environ.get(username_var)
            password = os.environ.get(password_var)
            if username and password:
                create_login_secret(
                    SimpleNamespace(
                        name=name,
                        username=to_b64_string(username),
                        password=to_b64_string(password),
                    )
                )
            else:
                validate_creds_from_env(AZDATA_USERNAME, AZDATA_PASSWORD)
                create_login_secret(
                    SimpleNamespace(
                        name=name,
                        username=to_b64_string(os.environ[AZDATA_USERNAME]),
                        password=to_b64_string(os.environ[AZDATA_PASSWORD]),
                    )
                )

        if is_v1(cr):
            create_login(
                CONTROLLER_LOGIN_SECRET_NAME, AZDATA_USERNAME, AZDATA_PASSWORD
            )

        create_login(LOGSUI_LOGIN_SECRET_NAME, LOGSUI_USERNAME, LOGSUI_PASSWORD)
        create_login(
            METRICSUI_LOGIN_SECRET_NAME, METRICSUI_USERNAME, METRICSUI_PASSWORD
        )

    def monitor_endpoint_list(self, namespace, endpoint_name=None):
        """
        List endpoints for the Monitor CR.
        """
        try:
            check_and_set_kubectl_context()

            # namespace = client.profile.active_context.namespace

            response = self._client.get_namespaced_custom_object(
                MONITOR_RESOURCE,
                namespace,
                group=ARC_GROUP,
                version=MONITOR_CRD_VERSION,
                plural=MONITOR_PLURAL,
            )
            cr = CustomResource.decode(MonitorCustomResource, response)
            if cr is None:
                raise Exception("Monitor custom resource not found.")

            endpoints = []

            if cr.status:
                descrip_str = "description"
                endpoint_str = "endpoint"
                name_str = "name"
                protocol_str = "protocol"

                # Logs
                logs_endpoint = {
                    descrip_str: "Log Search Dashboard",
                    endpoint_str: cr.status.log_search_dashboard,
                    name_str: "logsui",
                    protocol_str: "https",
                }

                # Metrics
                metrics_endpoint = {
                    descrip_str: "Metrics Dashboard",
                    endpoint_str: cr.status.metrics_dashboard,
                    name_str: "metricsui",
                    protocol_str: "https",
                }

                if endpoint_name is None:
                    endpoints.append(logs_endpoint)
                    endpoints.append(metrics_endpoint)
                    return endpoints
                elif endpoint_name.lower().startswith("metricsui"):
                    return metrics_endpoint
                else:
                    return logs_endpoint
        except KubernetesError as e:
            raise Exception(e.message)
        except Exception as e:
            raise Exception(e)

    # ------------------------------------------------------------------------ #
    # Delete DC
    # ------------------------------------------------------------------------ #

    def delete(self, name, namespace, force=None):
        """
        Deletes the data controller - requires kube config and env var
        """

        stdout = self.stdout

        # -- Check existence of data controller --
        if not self._client.namespaced_custom_object_exists(
            name,
            namespace,
            group=ARC_GROUP,
            version=self._client.get_crd_version(
                "datacontrollers.arcdata.microsoft.com"
            ),
            plural=DATA_CONTROLLER_PLURAL,
        ):
            raise ValueError(
                "Data controller `{}` does not exist in "
                "Kubernetes namespace `{}`.".format(name, namespace)
            )

        # -- Check that connectivity mode is indirect --
        connection_mode = self.get_data_controller(namespace).get(
            "connectionMode"
        )

        self.is_valid_connectivity_mode(connection_mode)

        # -- Calculate usage at time of deletion --
        # self.calculate_usage(namespace=namespace, exclude_curr_period=False)

        # -- Check existence of data services --
        crd_names = [POSTGRES_CRD_NAME, SQLMI_CRD_NAME]

        for crd_name in crd_names:
            crd = CustomResourceDefinition(self._client.get_crd(crd_name))

            cr_list = self._client.list_namespaced_custom_object(
                namespace, crd=crd
            )
            if cr_list["items"]:
                if not force:
                    raise Exception(
                        "Instances of `{}` are deployed. Cannot delete "
                        "data controller `{}`. Please delete these "
                        "instances before deleting the data "
                        "controller or "
                        "use --force.".format(crd.kind, name)
                    )
                else:
                    stdout("Deleting instances of `{}`.".format(crd.kind))

                    for item in cr_list["items"]:
                        cr_name = item["metadata"]["name"]
                        self._client.delete_namespaced_custom_object(
                            name=cr_name, namespace=namespace, crd=crd
                        )
                    stdout("`{}` deleted.".format(cr_name))

        stdout("Exporting the remaining resource usage information...")

        usage_file_name = LAST_BILLING_USAGE_FILE.format(name)
        # TODO: dc_export(client, "usage", usage_file_name, namespace,
        # force=True)

        usage_file_created = os.path.exists(usage_file_name)

        if usage_file_created:
            add_last_upload_flag(usage_file_name)
            stdout(
                "Please run 'az arcdata arc dc upload -p {}' to complete "
                "the "
                "deletion of data controller {}.".format(usage_file_name, name)
            )

        # -- attempt to delete the upgrade job if it exists --
        self.delete_bootstrap_job(namespace)

        stdout("Deleting data controller `{}`.".format(name))

        # Create deployer service acocunts
        self.create_deployer_service_account(namespace)

        # Bootstrap a job to run helm uninstall
        if not retry(
            lambda: self.bootstrap_uninstall(namespace),
            retry_count=CONNECTION_RETRY_ATTEMPTS,
            retry_delay=RETRY_INTERVAL,
            retry_method="uninstall",
            retry_on_exceptions=(NewConnectionError, MaxRetryError),
        ):
            display("Failed to uninstall bootstrapper chart.")

        # Delete the monitor and control plane CRD
        #
        crd_names = [
            MONITOR_CRD_NAME,
            KAFKA_CRD_NAME,
            TELEMETRY_COLLECTOR_CRD_NAME,
            DATA_CONTROLLER_CRD_NAME,
        ]

        for crd_name in crd_names:
            crd = CustomResourceDefinition(self._client.get_crd(crd_name))
            self._client.delete_custom_resource_definition(crd)

        # Delete the remaining resources which are not part of the helm chart
        #
        self._delete_cluster(namespace)

    @staticmethod
    def _delete_cluster(namespace):
        if not retry(
            kubernetes_util.namespace_exists,
            namespace,
            retry_count=CONNECTION_RETRY_ATTEMPTS,
            retry_delay=RETRY_INTERVAL,
            retry_method="check if namespace exists",
            retry_on_exceptions=(NewConnectionError, MaxRetryError),
        ):
            display("Namespace '%s' doesn't exist" % namespace)
            return

        # Try to delete the cluster
        #
        i = 1
        resources_are_deleted = False
        cluster_is_empty = False
        while not cluster_is_empty:
            time.sleep(RETRY_INTERVAL)

            if not resources_are_deleted:
                # Try to delete the remaining resources which are not part of the helm chart
                #
                (resources_are_deleted, http_status) = retry(
                    kubernetes_util.delete_cluster_resources,
                    namespace,
                    retry_count=CONNECTION_RETRY_ATTEMPTS,
                    retry_delay=RETRY_INTERVAL,
                    retry_method="delete cluster resources",
                    retry_on_exceptions=(NewConnectionError, MaxRetryError),
                )

                if http_status == HTTPStatus.FORBIDDEN:
                    break

            # Check if the cluster is empty
            #
            cluster_is_empty = retry(
                kubernetes_util.namespace_is_empty,
                namespace,
                retry_count=CONNECTION_RETRY_ATTEMPTS,
                retry_delay=RETRY_INTERVAL,
                retry_method="namespace is empty",
                retry_on_exceptions=(NewConnectionError, MaxRetryError),
            )

            if i * RETRY_INTERVAL > DELETE_CLUSTER_TIMEOUT_SECONDS:
                logger.warn(
                    "Data controller is not empty after %d minutes."
                    % (DELETE_CLUSTER_TIMEOUT_SECONDS / 60)
                )
                break

            i = i + 1
            time.sleep(RETRY_INTERVAL)

        if not cluster_is_empty:
            raise Exception("Failed to delete data controller.")

    # ------------------------------------------------------------------------ #
    # Bootstrapper
    # ------------------------------------------------------------------------ #

    def create_bootstrap_job(self, namespace, job_spec):
        """
        Create boostrap job for deployment or upgrade.
        """
        # Delete job if exists.
        self.delete_bootstrap_job(namespace)
        self.await_bootstrap_job_deletion(namespace)

        # Create job
        self._client.create_namespaced_job(namespace, job_spec)

    def bootstrap_create(self, namespace, dc: DataControllerCustomResource):
        """
        Creates the bootstrap job that will be used to install the bootstrapper chart.
        """
        docker_spec = dc.spec.docker
        job_model = SimpleNamespace(
            jobName=BOOTSTRAP_TEMPLATES.JOB_NAME,
            jobOperation="bootstrap",
            imagePullSecret=dc.spec.credentials.dockerRegistry,
            imagePullPolicy=docker_spec.imagePullPolicy,
            bootstrapper=ArcDataImageService.format_image_uri(
                docker_spec.registry,
                docker_spec.repository,
                BOOTSTRAP_TEMPLATES.BOOTSTRAPPER_IMAGE_NAME,
                docker_spec.imageTag,
            ),
            namespace=namespace,
            serviceAccountName=BOOTSTRAP_TEMPLATES.SERVICE_ACCOUNT_NAME,
        )

        logger.debug(
            "Creating bootstrap job {0} for installation.".format(
                job_model.jobName
            )
        )

        job_spec = get_yaml_from_template(BOOTSTRAP_TEMPLATES.JOB, job_model)

        self.create_bootstrap_job(namespace, job_spec)
        self.await_bootstrap_job_completion(namespace)

    def bootstrap_uninstall(self, namespace):
        """
        Creates the bootstrap job that will be used to uninstall the bootstrapper chart.
        """
        (dc, _) = self._client.get_arc_datacontroller(namespace, True)
        docker_spec = dc.spec.docker

        job_model = SimpleNamespace(
            jobName=BOOTSTRAP_TEMPLATES.JOB_NAME,
            jobOperation="uninstall",
            imagePullSecret=dc.spec.credentials.dockerRegistry,
            imagePullPolicy=docker_spec.imagePullPolicy,
            bootstrapper=ArcDataImageService.format_image_uri(
                docker_spec.registry,
                docker_spec.repository,
                BOOTSTRAP_TEMPLATES.BOOTSTRAPPER_IMAGE_NAME,
                docker_spec.imageTag,
            ),
            namespace=namespace,
            serviceAccountName=BOOTSTRAP_TEMPLATES.SERVICE_ACCOUNT_NAME,
        )

        logger.debug(
            "Creating bootstrap job {0} for uninstalling.".format(
                job_model.jobName
            )
        )

        job_spec = get_yaml_from_template(BOOTSTRAP_TEMPLATES.JOB, job_model)

        self.create_bootstrap_job(namespace, job_spec)
        self.await_bootstrap_job_completion(namespace)
        self.delete_bootstrap_job(namespace)

    def bootstrap_upgrade(self, namespace, target_version=None):
        """
        Creates the bootstrap job that will be used to update
        versions and perform cluster level operations.
        """
        (dc, _) = self._client.get_arc_datacontroller(namespace, True)

        if target_version is None:
            target_version = ArcDataImageService.get_latest_image_version(
                namespace, True
            )
            self.stdout(
                "Target version not specified, using latest published version "
                "{0}".format(target_version)
            )

        # ArcDataImageService.validate_image_tag(target_version)

        docker_spec = dc.spec.docker
        template_body = SimpleNamespace(
            jobName=BOOTSTRAP_TEMPLATES.JOB_NAME,
            jobOperation="bootstrap",
            imagePullSecret=dc.spec.credentials.dockerRegistry,
            imagePullPolicy=docker_spec.imagePullPolicy,
            bootstrapper=ArcDataImageService.format_image_uri(
                docker_spec.registry,
                docker_spec.repository,
                BOOTSTRAP_TEMPLATES.BOOTSTRAPPER_IMAGE_NAME,
                target_version,
            ),
            namespace=namespace,
            serviceAccountName=BOOTSTRAP_TEMPLATES.SERVICE_ACCOUNT_NAME,
        )

        logger.debug(
            "Creating upgrade bootstrap job {0} for upgrading.".format(
                template_body.jobName
            )
        )

        job_spec = get_yaml_from_template(
            BOOTSTRAP_TEMPLATES.JOB, template_body
        )

        self.create_bootstrap_job(namespace, job_spec)
        self.await_bootstrap_job_completion(namespace)

    def delete_bootstrap_job(self, namespace):
        api = k8sClient.BatchV1Api()
        job_name = BOOTSTRAP_TEMPLATES.JOB_NAME
        try:
            api.delete_namespaced_job(name=job_name, namespace=namespace)
        except K8sApiException as e:
            if e.status == HTTPStatus.NOT_FOUND:
                # already deleted
                pass
            else:
                logger.error(
                    "Could not delete bootstrap job {0} "
                    "in namespace {1}.  Please delete manually.".format(
                        job_name, namespace
                    )
                )
                raise

    @retry_method(
        12, 10, "await bootstrapper job deletion", (JobNotCompleteException)
    )
    def await_bootstrap_job_deletion(self, namespace):
        """
        Waits up to 2 minutes for the preexisting bootstrap job to terminate.
        """

        try:
            jobList = (
                k8sClient.BatchV1Api()
                .list_namespaced_job(
                    field_selector="metadata.name={0}".format(
                        BOOTSTRAP_TEMPLATES.JOB_NAME
                    ),
                    namespace=namespace,
                )
                .items
            )

            if len(jobList) == 0:
                return

        except Exception as e:
            raise JobNotCompleteException(e)

        raise JobNotCompleteException("Job not deleted")

    @staticmethod
    def read_namespaced_job_log(namespace, job_name, job_uid):
        job_pods = k8sClient.CoreV1Api().list_namespaced_pod(
            namespace=namespace,
            label_selector="job-name={},controller-uid={}".format(
                job_name, job_uid
            ),
        )
        job_pod_log = k8sClient.CoreV1Api().read_namespaced_pod_log(
            name=job_pods.items[0].metadata.name, namespace=namespace
        )
        return job_pod_log

    def _output_error_log(self, log):
        for line in log.splitlines():
            if line.startswith("ERROR") or line.startswith("FATAL"):
                self.stderr(line)

    def _dump_pre_upgrade_validation_job_log(self, namespace):
        jobs = (
            k8sClient.BatchV1Api()
            .list_namespaced_job(
                field_selector="metadata.name=upgrade-validation-job",
                namespace=namespace,
            )
            .items
        )

        if jobs:
            self._output_error_log(
                self.read_namespaced_job_log(
                    namespace, jobs[0].metadata.name, jobs[0].metadata.uid
                )
            )

    @retry_method(
        36, 10, "await bootstrap job completion", (JobNotCompleteException)
    )
    def await_bootstrap_job_completion(self, namespace):
        """
        Waits up to 6 minutes for the job to complete, then fails. Several factors
        can contribute to longer execution times for the job, including:

        1. Kubernetes Distribution
        2. Image Pull bandwidth
        3. Number of Custom Resources and CRD versions deployed
        4. Client side throttling (e.g. OpenShift can throttle arc-bootstrapper-job
           during helm upgrade as the number of APIServer calls increases).

        TODO: Poll until definite job outcome (success or failure), rather than
        awaiting constant duration.
        """

        try:
            job = (
                k8sClient.BatchV1Api()
                .list_namespaced_job(
                    field_selector="metadata.name={0}".format(
                        BOOTSTRAP_TEMPLATES.JOB_NAME
                    ),
                    namespace=namespace,
                )
                .items[0]
            )

        except Exception as e:
            raise JobNotCompleteException(e)

        status = _.get(job, "status")

        if status.active:
            raise JobNotCompleteException("Job Still Active")

        if status.succeeded == 1:
            return

        if status.failed == 1:
            self._output_error_log(
                self.read_namespaced_job_log(
                    namespace, job.metadata.name, job.metadata.uid
                )
            )
            self._dump_pre_upgrade_validation_job_log(namespace)
            raise Exception("Bootstrap job failed.")

        raise JobNotCompleteException("Job Still Active")

    def validate_no_pg_bc(self, namespace):
        """
        Temporary validation for GA to GA+1 upgrades to ensure the cluster does not have any postgres or sql business critical preview instances
        Will raise an exception if any exist.
        """
        postgres_instances = resolve_postgres_instances(namespace)
        if len(postgres_instances) > 0:
            raise Exception(
                "One or more postgres preview instances exist in the cluster and must be deleted prior to upgrading the data controller."
            )

    def validate_no_old_dag(self, namespace):
        """
        Valid old dag items before this release. User has to remove dag before the upgrade.
        """
        dag_items = resolve_old_dag_items(namespace)
        if len(dag_items) > 0:
            raise Exception(
                "One or more Dag preview instances exist in the cluster and must be deleted prior to upgrading the data controller."
            )

    def validate_dc_child_mi_versions(self, namespace, datacontrollerVersion):
        """
        Validates that all Arc-enabled SQL Managed Instances in the cluster
        are aligned to the same image version as the data controller.
        """
        instances = resolve_sqlmi_instances(namespace)

        for sqlmi in instances:
            sqlmiVersion = sqlmi.status.runningVersion
            if sqlmiVersion and sqlmiVersion != datacontrollerVersion:
                raise Exception(
                    "All Arc-enabled SQL Managed Instances in the cluster must first be "
                    "aligned to the same image version as the data controller ({0}) "
                    "before the data controller can be upgraded.".format(
                        datacontrollerVersion
                    )
                )

    # ------------------------------------------------------------------------ #
    # Upgrade
    # ------------------------------------------------------------------------ #

    def upgrade(self, namespace, target, dry_run=None, no_wait=False):
        try:

            self.validate_no_pg_bc(namespace=namespace)
            self.validate_no_old_dag(namespace=namespace)

            (dc, config) = self._client.get_arc_datacontroller(namespace)
            connection_mode = _.get(dc, "spec.settings.azure.connectionMode")
            self.is_valid_connectivity_mode(connection_mode)

            datacontrollerVersion = _.get(dc, "spec.docker.imageTag")
            self.validate_dc_child_mi_versions(namespace, datacontrollerVersion)

            target = resolve_valid_target_version(namespace, target)

            self.stdout(
                "Upgrading data controller to version {0}.".format(target)
            )

            upgrade_arc_control_plane(self, namespace, target, dry_run)

        except Exception as e:
            raise CLIError(e)

        if no_wait:
            self.stdout(
                "Data controller upgrade in progress.\n"
                "Please use `az arcdata dc status show --use-k8s "
                "--k8s-namespace {0}` to check its status.".format(namespace)
            )
        else:
            # Wait for the CR to reflect new state
            time.sleep(5)

            if not is_windows():
                with AutomaticSpinner(
                    "Running",
                    show_time=True,
                ):
                    self._await_dc_ready(namespace)
            else:
                self._await_dc_ready(namespace)
            self.stdout("Data controller successfully upgraded.")

    def update(
        self,
        namespace=None,
        no_wait=False,
        desired_version=None,
        maintenance_start=None,
        maintenance_duration=None,
        maintenance_recurrence=None,
        maintenance_time_zone=None,
        maintenance_enabled=None,
    ):
        """
        Updates the maintenance window for the given namespace's data controller.  This is a patch operation and as such will only alter parameters that are present
        """
        # Apply the upgrade first if specified
        if desired_version:
            self.upgrade(
                namespace=namespace, target=desired_version, no_wait=no_wait
            )

        patchBody = {}
        if maintenance_start is not None:
            patchBody["start"] = maintenance_start

        if maintenance_duration is not None:
            patchBody["duration"] = maintenance_duration

        if maintenance_recurrence is not None:
            patchBody["recurrence"] = maintenance_recurrence

        if maintenance_time_zone is not None:
            patchBody["timeZone"] = maintenance_time_zone

        if maintenance_enabled is not None:
            patchBody["enabled"] = maintenance_enabled

        patch = {"spec": {"settings": {"maintenance": patchBody}}}

        try:
            patch_data_controller(namespace, patch)
        except Exception as e:
            raise CLIError(e)

        if no_wait:
            self.stdout(
                "Data controller update in progress.\n"
                "Please use `az arcdata dc status show --use-k8s "
                "--k8s-namespace {0}` to check its status.".format(namespace)
            )
        else:
            # Wait for the CR to reflect new state
            time.sleep(5)

            if not is_windows():
                with AutomaticSpinner("Running", show_time=True):
                    self._await_dc_ready(namespace)
            else:
                self._await_dc_ready(namespace)
            self.stdout("Data controller successfully updated.")

    def list_upgrades(self, namespace):
        from azext_arcdata.kubernetes_sdk.arc_docker_image_service import (
            ArcDataImageService,
        )

        """
        Returns a list of all available upgrades from the docker registry defined by the data controller
        """
        versions = ArcDataImageService.get_available_image_versions(namespace)
        (dc, config) = self._client.get_arc_datacontroller(namespace)

        current_version = _.get(dc, "spec.docker.imageTag")

        return current_version, versions

    def create_deployer_service_account(self, namespace):
        """
        Create service account for deployment and upgrade bootstrap job.
        """

        service_account_name = BOOTSTRAP_TEMPLATES.SERVICE_ACCOUNT_NAME
        cluster_role_name = BOOTSTRAP_TEMPLATES.get_cluster_role_name(namespace)
        cluster_role_binding_name = (
            BOOTSTRAP_TEMPLATES.get_cluster_role_binding_name(namespace)
        )

        cluster_role_binding_model = {
            "namespace": namespace,
            "serviceAccountName": service_account_name,
            "clusterRoleBindingName": cluster_role_binding_name,
            "clusterRoleName": cluster_role_name,
        }

        deployer_role_name = "role-deployer"
        deployer_role_binding_name = "rb-deployer"
        bootstrapper_role_name = "role-bootstrapper"
        deployer_bootstrapper_role_binding_name = "rb-deployer-bootstrapper"

        deployer_role_binding_model = {
            "namespace": namespace,
            "serviceAccountName": service_account_name,
            "roleBindingName": deployer_role_binding_name,
            "roleName": deployer_role_name,
        }

        deployer_bootstrapper_role_binding_model = {
            "namespace": namespace,
            "serviceAccountName": service_account_name,
            "roleBindingName": deployer_bootstrapper_role_binding_name,
            "roleName": bootstrapper_role_name,
        }

        try:
            logger.debug(
                "Creating service account: {0}".format(cluster_role_name)
            )
            # Creating Service Account
            service_account_body = get_yaml_from_template(
                BOOTSTRAP_TEMPLATES.SERVICE_ACCOUNT,
                cluster_role_binding_model,
            )
            kubernetes_util.update_service_account(
                namespace, service_account_name, service_account_body
            )

            logger.debug(
                "Service account {0} has been created successfully.".format(
                    service_account_name
                )
            )

            logger.debug("Creating cluster role: {0}".format(cluster_role_name))
            # Creating Cluster Role
            cluster_role_body = get_yaml_from_template(
                BOOTSTRAP_TEMPLATES.CLUSTER_ROLE,
                cluster_role_binding_model,
            )
            kubernetes_util.update_cluster_role(
                cluster_role_name, cluster_role_body
            )

            logger.debug(
                "Cluster role: {0} created successfully.".format(
                    cluster_role_name
                )
            )

            logger.debug(
                "Creating cluster role binding: {0}".format(
                    cluster_role_binding_name
                )
            )

            # Creating Cluster Role Binding
            cluster_role_binding_body = get_yaml_from_template(
                BOOTSTRAP_TEMPLATES.CLUSTER_ROLE_BINDING,
                cluster_role_binding_model,
            )

            kubernetes_util.update_cluster_role_binding(
                cluster_role_binding_name, cluster_role_binding_body
            )

            logger.debug(
                "Cluster role binding: {0} created successfully.".format(
                    cluster_role_binding_name
                )
            )

            # Creating Deployer Role
            logger.debug("Creating role: {0}".format(deployer_role_name))

            role_spec = yaml.safe_load(
                get_config_from_template(
                    BOOTSTRAP_TEMPLATES.DEPLOYER_ROLE,
                    deployer_role_binding_model,
                )
            )

            kubernetes_util.update_namespaced_role(
                namespace=namespace,
                role_name=deployer_role_name,
                role_body=role_spec,
            )

            logger.debug(
                "Role: {0} created successfully.".format(deployer_role_name)
            )

            # Creating Deployer Role Binding
            if not self._client.namespaced_role_binding_exists(
                namespace, deployer_role_binding_name
            ):
                role_binding_spec = yaml.safe_load(
                    get_config_from_template(
                        BOOTSTRAP_TEMPLATES.ROLE_BINDING,
                        deployer_role_binding_model,
                    )
                )
                self._client.create_namespaced_role_binding(
                    namespace, role_binding_spec
                )

                logger.debug(
                    "Role binding: {0} created successfully.".format(
                        deployer_role_binding_name
                    )
                )

            # Update Bootstrapper Role
            logger.debug("Updating role: {0}".format(bootstrapper_role_name))

            role_spec = yaml.safe_load(
                get_config_from_template(
                    BOOTSTRAP_TEMPLATES.BOOTSTRAPPER_ROLE,
                    {"namespace": namespace},
                )
            )

            kubernetes_util.update_namespaced_role(
                namespace=namespace,
                role_name=bootstrapper_role_name,
                role_body=role_spec,
            )

            logger.debug(
                "Role: {0} updated successfully.".format(bootstrapper_role_name)
            )

            # Creating Deployer Bootstrapper Role Binding
            if not self._client.namespaced_role_binding_exists(
                namespace, deployer_bootstrapper_role_binding_name
            ):
                role_binding_spec = yaml.safe_load(
                    get_config_from_template(
                        BOOTSTRAP_TEMPLATES.ROLE_BINDING,
                        deployer_bootstrapper_role_binding_model,
                    )
                )
                self._client.create_namespaced_role_binding(
                    namespace, role_binding_spec
                )

                logger.debug(
                    "Role binding: {0} created successfully.".format(
                        deployer_bootstrapper_role_binding_name
                    )
                )

        except K8sApiException as e:
            logger.warning(e.body)

            if e.status == HTTPStatus.FORBIDDEN:
                logger.error(
                    "The current user may not not have sufficient permissions to "
                    "create '%s' Service Account and grant necessary permissions."
                    "If these resources already exist, please ignore this "
                    "warning. Otherwise please ask your cluster administrator "
                    "to manually create them."
                    "More details: "
                    "https://aka.ms/arcdata_k8s_native",
                    service_account_name,
                )

            raise

    def delete_deployer_service_account(self, namespace):
        """
        Deletes the deployer service account and RBAC.
        """
        service_account_name = BOOTSTRAP_TEMPLATES.SERVICE_ACCOUNT_NAME
        cluster_role_name = BOOTSTRAP_TEMPLATES.get_cluster_role_name(namespace)
        cluster_role_binding_name = (
            BOOTSTRAP_TEMPLATES.get_cluster_role_binding_name(namespace)
        )

        kubernetes_util.delete_cluster_role_binding(
            cluster_role_binding_name=cluster_role_binding_name
        )
        kubernetes_util.delete_service_account(
            name=service_account_name, namespace=namespace
        )
        kubernetes_util.delete_cluster_role(cluster_role_name=cluster_role_name)

    @retry_method(
        12,
        10,
        "await datacontroller update complete",
        (JobNotCompleteException),
    )
    def await_dc_replicaset_update_completion(self, namespace, target_version):
        """
        Waits up to 2 minutes for the datacontroller replicaset to be
        updated, then fails, this process should never take more than 2 minutes.
        """

        try:
            pods = k8sClient.CoreV1Api().list_namespaced_pod(
                label_selector="app=controller", namespace=namespace
            )

        except Exception as e:
            raise JobNotCompleteException(e)

        for pod in pods.items:
            tag = _.get(pod.spec.containers[0], "image")

            if not tag.endswith(target_version):
                raise JobNotCompleteException("Job Still Active")

    def is_valid_connectivity_mode(self, connection_mode):
        if connection_mode == DIRECT:
            raise Exception(
                "Performing this action from az using the --use-k8s parameter "
                "is only allowed using indirect mode. Please use the Azure "
                "Portal to perform this action in direct connectivity mode. "
                "Or use --resource-group "
            )
