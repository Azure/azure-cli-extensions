# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements

from azure.cli.core.commands.validators import get_default_location_from_resource_group
from azure.cli.core.commands.parameters import (
    get_enum_type,
    get_three_state_flag,
    tags_type,
)
from .validators import (
    validate_configuration_name,
    validate_fluxconfig_name,
    validate_namespace,
)

from .action import (
    KustomizationAddAction,
)
from . import consts


def load_arguments(self, _):
    with self.argument_context("k8s-configuration") as c:
        c.argument("tags", tags_type)
        c.argument("location", validator=get_default_location_from_resource_group)
        c.argument(
            "cluster_name",
            options_list=["--cluster-name", "-c"],
            help="Name of the Kubernetes cluster",
        )
        c.argument(
            "cluster_type",
            options_list=["--cluster-type", "-t"],
            arg_type=get_enum_type(["connectedClusters", "managedClusters", "provisionedClusters"]),
            help="Specify Arc connected clusters or AKS managed clusters or provisioned clusters.",
        )

    with self.argument_context("k8s-configuration flux") as c:
        c.argument(
            "cluster_resource_provider",
            options_list=['--cluster-resource-provider', '--cluster-rp'],
            help='Cluster Resource Provider name for this clusterType (Required for provisionedClusters)'
        )
        c.argument(
            "name",
            options_list=["--name", "-n"],
            help="Name of the flux configuration",
            validator=validate_fluxconfig_name,
        )
        c.argument(
            "scope",
            options_list=["--scope", "-s"],
            arg_type=get_enum_type(["namespace", "cluster"]),
            help="Specify scope of the operator to be 'namespace' or 'cluster'",
        )
        c.argument(
            "namespace",
            help="Namespace to deploy the configuration",
            options_list=["--namespace", "--ns"],
            validator=validate_namespace,
        )
        c.argument(
            "kind",
            arg_type=get_enum_type([consts.GIT, consts.BUCKET, consts.AZBLOB]),
            help="Source kind to reconcile",
        )
        c.argument(
            "url", options_list=["--url", "-u"], help="URL of the source to reconcile"
        )
        c.argument(
            "timeout", help="Maximum time to reconcile the source before timing out"
        )
        c.argument(
            "sync_interval",
            options_list=["--interval", "--sync-interval"],
            help="Time between reconciliations of the source on the cluster",
        )
        c.argument(
            "branch",
            arg_group="Git Repo Ref",
            help="Branch within the git source to reconcile with the cluster",
        )
        c.argument(
            "tag",
            arg_group="Git Repo Ref",
            help="Tag within the git source to reconcile with the cluster",
        )
        c.argument(
            "semver",
            arg_group="Git Repo Ref",
            help="Semver range within the git source to reconcile with the cluster",
        )
        c.argument(
            "commit",
            arg_group="Git Repo Ref",
            help="Commit within the git source to reconcile with the cluster",
        )
        c.argument(
            "ssh_private_key",
            arg_group="Git Auth",
            help="Base64-encoded private ssh key for private repository sync",
        )
        c.argument(
            "ssh_private_key_file",
            arg_group="Git Auth",
            help="File path to private ssh key for private repository sync",
        )
        c.argument(
            "https_user",
            arg_group="Git Auth",
            help="HTTPS username for private repository sync",
        )
        c.argument(
            "https_key",
            arg_group="Git Auth",
            help="HTTPS token/password for private repository sync",
        )
        c.argument(
            "https_ca_cert",
            arg_group="Git Auth",
            help="Base64-encoded HTTPS CA certificate for TLS communication with private repository sync",
        )
        c.argument(
            "https_ca_cert_file",
            arg_group="Git Auth",
            help="File path to HTTPS CA certificate file for TLS communication with private repository sync",
        )
        c.argument(
            "known_hosts",
            arg_group="Git Auth",
            help="Base64-encoded known_hosts data containing public SSH keys required to access private Git instances",
        )
        c.argument(
            "known_hosts_file",
            arg_group="Git Auth",
            help="File path to known_hosts contents containing public SSH keys required to access private Git instances",
        )
        c.argument(
            "bucket_access_key",
            arg_group="Bucket Auth",
            help="Access Key ID used to authenticate with the bucket",
        )
        c.argument(
            "bucket_secret_key",
            arg_group="Bucket Auth",
            help="Secret Key used to authenticate with the bucket",
        )
        c.argument(
            "bucket_name",
            help="Name of the S3 bucket to sync",
        )
        c.argument(
            "bucket_insecure",
            arg_type=get_three_state_flag(),
            help="Communicate with a bucket without TLS",
        )
        c.argument(
            "local_auth_ref",
            arg_group="Auth",
            options_list=["--local-auth-ref", "--local-ref"],
            help="Local reference to a kubernetes secret in the configuration namespace to use for communication to the source",
        )
        c.argument(
            "suspend",
            arg_type=get_three_state_flag(),
            help="Suspend the reconciliation of the source and kustomizations associated with this configuration",
        )
        c.argument(
            "kustomization",
            action=KustomizationAddAction,
            options_list=["--kustomization", "-k"],
            help="Define kustomizations to sync sources with parameters ['name', 'path', 'depends_on', 'timeout', 'sync_interval', 'retry_interval', 'prune', 'force', 'disable_health_check']",
            nargs="+",
        )
        c.argument(
            "container_name",
            help="Name of the Azure Blob Storage container to sync",
        )
        c.argument(
            "sp_client_id",
            arg_group="Azure Blob Auth",
            options_list=["--sp-client-id", "--service-principal-client-id"],
            help="The client ID for authenticating a service principal with Azure Blob, required for this authentication method",
        )
        c.argument(
            "sp_tenant_id",
            arg_group="Azure Blob Auth",
            options_list=["--sp-tenant-id", "--service-principal-tenant-id"],
            help="The tenant ID for authenticating a service principal with Azure Blob, required for this authentication method",
        )
        c.argument(
            "sp_client_secret",
            arg_group="Azure Blob Auth",
            options_list=["--sp-client-secret", "--service-principal-client-secret"],
            help="The client secret for authenticating a service principal with Azure Blob",
        )
        c.argument(
            "sp_client_cert",
            arg_group="Azure Blob Auth",
            options_list=["--sp-client-cert", "--service-principal-client-certificate"],
            help="The Base64 encoded client certificate for authenticating a service principal with Azure Blob",
        )
        c.argument(
            "sp_client_cert_password",
            arg_group="Azure Blob Auth",
            options_list=["--sp-cert-password", "--service-principal-client-certificate-password"],
            help="The password for the client certificate used to authenticate a service principal with Azure Blob",
        )
        c.argument(
            "sp_client_cert_send_chain",
            arg_group="Azure Blob Auth",
            options_list=["--sp-cert-send-chain", "--service-principal-client-certificate-send-chain"],
            help="Specify whether to include x5c header in client claims when acquiring a token to enable subject name / issuer based authentication for the client certificate",
        )
        c.argument(
            "account_key",
            arg_group="Azure Blob Auth",
            help="The Azure Blob Shared Key for authentication ",
        )
        c.argument(
            "sas_token",
            arg_group="Azure Blob Auth",
            help="The Azure Blob SAS Token for authentication ",
        )
        c.argument(
            "mi_client_id",
            arg_group="Azure Blob Auth",
            options_list=["--mi-client-id", "--managed-identity-client-id"],
            help="The client ID of the managed identity for authentication with Azure Blob",
        )

    with self.argument_context("k8s-configuration flux update") as c:
        c.argument(
            "yes", options_list=["--yes", "-y"], help="Do not prompt for confirmation"
        )

    with self.argument_context("k8s-configuration flux delete") as c:
        c.argument(
            "force",
            arg_type=get_three_state_flag(),
            help="Force delete the flux configuration from the cluster.",
        )
        c.argument(
            "yes", options_list=["--yes", "-y"], help="Do not prompt for confirmation"
        )

    with self.argument_context("k8s-configuration flux deployed-object show") as c:
        c.argument(
            "object_name",
            help="Name of the object deployed by the configuration on the cluster.",
        )
        c.argument(
            "object_namespace",
            help="Namespace of the object deployed by the configuration on the cluster.",
        )
        c.argument(
            "object_kind",
            arg_type=get_enum_type(
                [
                    "GitRepository",
                    "Bucket",
                    "HelmRepository",
                    "HelmChart",
                    "HelmRelease",
                    "Kustomization",
                ]
            ),
            help="Kind of the object deployed by the configuration on the cluster.",
        )

    with self.argument_context("k8s-configuration") as c:
        c.argument(
            "name",
            options_list=["--name", "-n"],
            help="Name of the configuration",
            validator=validate_configuration_name,
        )

    with self.argument_context("k8s-configuration flux kustomization") as c:
        c.argument(
            "kustomization_name",
            options_list=["--kustomization-name", "-k"],
            help="Specify the name of the kustomization to target",
        )
        c.argument(
            "path",
            help="Specify the path in the source that the kustomization should apply",
        )
        c.argument(
            "dependencies",
            options_list=["--depends", "--dependencies", "--depends-on"],
            help="Comma-separated list of kustomization dependencies",
        )
        c.argument(
            "timeout",
            help="Maximum time to reconcile the kustomization before timing out",
        )
        c.argument(
            "sync_interval",
            options_list=["--interval", "--sync-interval"],
            help="Time between reconciliations of the kustomization on the cluster",
        )
        c.argument(
            "retry_interval",
            help="Time between reconciliations of the kustomization on the cluster on failures, defaults to --sync-interval",
        )
        c.argument(
            "prune",
            arg_type=get_three_state_flag(),
            help="Garbage collect resources deployed by the kustomization on the cluster",
        )
        c.argument(
            "force",
            arg_type=get_three_state_flag(),
            help="Re-create resources that cannot be updated on the cluster (i.e. jobs)",
        )
        c.argument(
            "disable_health_check",
            arg_type=get_three_state_flag(),
            help="Disable health checks for kustomizations applied to the cluster."
        )

    with self.argument_context("k8s-configuration flux kustomization delete") as c:
        c.argument(
            "yes", options_list=["--yes", "-y"], help="Do not prompt for confirmation"
        )
