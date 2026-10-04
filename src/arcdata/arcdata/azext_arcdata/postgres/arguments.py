# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

from azext_arcdata.core.constants import USE_K8S_TEXT


def load_arguments(self, _):
    from knack.arguments import ArgumentsContext

    # -------------------------------------------------------------------------
    # Server Commands
    # -------------------------------------------------------------------------

    with ArgumentsContext(self, "postgres server-arc create") as arg_context:
        arg_context.argument(
            "path",
            options_list=["--path"],
            help="The path to the source json file for the Azure Arc enabled "
            "PostgreSQL server. This is optional.",
        )
        arg_context.argument(
            "name",
            options_list=["--name", "-n"],
            help="Name of the Azure Arc enabled PostgreSQL server.",
        )
        arg_context.argument(
            "namespace",
            options_list=["--k8s-namespace", "-k"],
            help="The Kubernetes namespace where the Azure Arc enabled "
            "PostgreSQL server is deployed. If no namespace is specified,"
            " then the namespace defined in the kubeconfig will be used.",
        )
        arg_context.argument(
            "admin-login-secret",
            options_list=["--admin-login-secret"],
            help="Name of the Kubernetes secret to generate that hosts or "
            "will host user admin login account credential.",
        )
        arg_context.argument(
            "certificate_public_key_file",
            options_list=["--cert-public-key-file"],
            help="Path to the file containing a PEM formatted certificate "
            "public key to be used for client SSL connections.",
        )
        arg_context.argument(
            "certificate_private_key_file",
            options_list=["--cert-private-key-file"],
            help="Path to the file containing a PEM formatted certificate "
            "private key to be used for client SSL connections.",
        )
        arg_context.argument(
            "cores_limit",
            options_list=["--cores-limit"],
            help="The maximum number of CPU cores that can be used for Azure "
            "Arc enabled PostgreSQL server.",
        )
        arg_context.argument(
            "cores_request",
            options_list=["--cores-request"],
            help="The minimum number of CPU cores that must be available per "
            "node to schedule the service.",
        )
        arg_context.argument(
            "log_level",
            options_list=["--log-level"],
            help="Sets the log_min_messages setting for the PostgreSQL engine."
            " Valid values are: DEBUG5, DEBUG4, DEBUG3, DEBUG2, DEBUG1, INFO, "
            "NOTICE, WARNING, ERROR, LOG, FATAL, PANIC.",
        )
        arg_context.argument(
            "memory_limit",
            options_list=["--memory-limit"],
            help="The memory limit of the Azure Arc enabled PostgreSQL server "
            "as a number followed by Ki (kilobytes), Mi (megabytes), or Gi "
            "(gigabytes).",
        )
        arg_context.argument(
            "memory_request",
            options_list=["--memory-request"],
            help="The memory request of the Azure Arc enabled PostgreSQL "
            "server as a number followed by Ki (kilobytes), Mi (megabytes), or"
            " Gi (gigabytes).",
        )
        arg_context.argument(
            "retention_days",
            options_list=["--retention-days"],
            type=int,
            help="Backup retention period, specified in days. "
            "Allowed values are 0 to 35. Default is 7. Setting "
            "the retention period to 0 will turn off automatic "
            "backups for Azure Arc enabled PostgreSql.",
        )
        arg_context.argument(
            "service-annotations",
            options_list=["--service-annotations"],
            help="Comma-separated list of annotations to apply to all "
            "external services.",
        )
        arg_context.argument(
            "service_certificate_secret",
            options_list=["--service-cert-secret"],
            help="Name of the Kubernetes secret to generate that hosts the SSL"
            " certificate.",
        )
        arg_context.argument(
            "service-labels",
            options_list=["--service-labels"],
            help="Comma-separated list of labels to apply to all external "
            "services.",
        )
        arg_context.argument(
            "storage_class_data",
            options_list=["--storage-class-data"],
            help="The storage class to be used for data persistent volumes.",
        )
        arg_context.argument(
            "storage_class_logs",
            options_list=["--storage-class-logs"],
            help="The storage class to be used for logs persistent volumes.",
        )
        arg_context.argument(
            "storage_class_backups",
            options_list=["--storage-class-backups"],
            help="The storage class to be used for backup persistent volumes.",
        )
        arg_context.argument(
            "volume_size_data",
            options_list=["--volume-size-data"],
            help="The size of the storage volume to be used for data as a "
            "positive number followed by Ki (kilobytes), Mi (megabytes), or "
            "Gi (gigabytes).",
        )
        arg_context.argument(
            "volume_size_logs",
            options_list=["--volume-size-logs"],
            help="The size of the storage volume to be used for logs as a "
            "positive number followed by Ki (kilobytes), Mi (megabytes), or "
            "Gi (gigabytes).",
        )
        arg_context.argument(
            "volume_size_backups",
            options_list=["--volume-size-backups"],
            help="The size of the storage volume to be used for backups as a "
            "positive number followed by Ki (kilobytes), Mi (megabytes), or "
            "Gi (gigabytes).",
        )
        arg_context.argument(
            "no_external_endpoint",
            options_list=["--no-external-endpoint"],
            action="store_true",
            help="If specified, no external service will be created. "
            "Otherwise, an external service will be created using either the "
            "type given with the --service-type argument or the same "
            "service type as the data controller.",
        )
        arg_context.argument(
            "use_k8s",
            options_list=("--use-k8s"),
            action="store_true",
            help=USE_K8S_TEXT,
        )
        arg_context.argument(
            "dev",
            options_list=["--dev"],
            action="store_true",
            help="If this is specified, then it is considered a dev instance "
            "and will not be billed for.",
        )
        arg_context.argument(
            "port",
            options_list=["--port"],
            help="The port number on which the primary service is exposed to "
            "the end-users.",
        )
        arg_context.argument(
            "nowait",
            options_list=["--no-wait"],
            action="store_true",
            help="Do not wait for deployment to be ready before returning.",
        )
        arg_context.argument(
            "extensions",
            options_list=["--extensions"],
            help="Comma seperated list of extensions to be enabled. "
            "Once enabled, extension can be installed via 'CREATE EXTENSION' command.",
        )
        # -- Active Directory --
        arg_context.argument(
            "ad_connector_name",
            options_list=["--ad-connector-name"],
            help="The name of the Active Directory Connector. This parameter "
            "indicates an intent to deploy with AD support.",
        )
        arg_context.argument(
            "ad_account_name",
            options_list=["--ad-account-name"],
            help="The Active Directory account name for this Azure Arc enabled "
            "PostgreSQL server. This account needs to be created prior to "
            "the deployment of this instance.",
        )
        arg_context.argument(
            "keytab_secret",
            options_list=["--keytab-secret"],
            help="The name of the Kubernetes secret that contains the keytab "
            "file for this Azure Arc enabled PostgreSQL server.",
        )
        arg_context.argument(
            "dns_name",
            options_list=["--dns-name"],
            help="The service DNS name exposed to the end-users to "
            "connect to this Azure Arc enabled PostgreSQL server (e.g. "
            "pginstancename.contoso.com).",
        )

    with ArgumentsContext(self, "postgres server-arc restore") as arg_context:
        arg_context.argument(
            "source-server",
            options_list=["--source-server"],
            help="Name of the source Azure Arc enabled PostgreSQL server "
            " from where the backups should be retrieved.",
        )
        arg_context.argument(
            "name",
            options_list=["--name", "-n"],
            help="Name of the Azure Arc enabled PostgreSQL server to be "
            "created.",
        )
        arg_context.argument(
            "time",
            options_list=["--time", "-t"],
            help="The point in time of the source server that will be "
            "restored to create the new Azure Arc enabled PostgreSQL server"
            ". Must be greater than or equal"
            " to the source database's earliest restore date/time value. "
            "Time should be in following format: 'YYYY-MM-DDTHH:MM:SSZ'. "
            "If no time is provided, the most recent backup will be restored.",
        )
        arg_context.argument(
            "namespace",
            options_list=["--k8s-namespace", "-k"],
            help="The Kubernetes namespace that contains the Azure Arc enabled "
            "PostgreSql. If no namespace is specified, then the "
            "namespace defined in the kubeconfig will be used.",
        )
        arg_context.argument(
            "storage_class_data",
            options_list=["--storage-class-data"],
            help="The storage class to be used for data persistent volumes.",
        )
        arg_context.argument(
            "storage_class_logs",
            options_list=["--storage-class-logs"],
            help="The storage class to be used for logs persistent volumes.",
        )
        arg_context.argument(
            "storage_class_backups",
            options_list=["--storage-class-backups"],
            help="The storage class to be used for backup persistent volumes.",
        )
        arg_context.argument(
            "volume_size_data",
            options_list=["--volume-size-data"],
            help="The size of the storage volume to be used for data as a "
            "positive number followed by Ki (kilobytes), Mi (megabytes), or "
            "Gi (gigabytes).",
        )
        arg_context.argument(
            "volume_size_logs",
            options_list=["--volume-size-logs"],
            help="The size of the storage volume to be used for logs as a "
            "positive number followed by Ki (kilobytes), Mi (megabytes), or "
            "Gi (gigabytes).",
        )
        arg_context.argument(
            "volume_size_backups",
            options_list=["--volume-size-backups"],
            help="The size of the storage volume to be used for backups as a "
            "positive number followed by Ki (kilobytes), Mi (megabytes), or "
            "Gi (gigabytes).",
        )
        arg_context.argument(
            "use_k8s",
            options_list=("--use-k8s"),
            action="store_true",
            help=USE_K8S_TEXT,
        )
        arg_context.argument(
            "nowait",
            options_list=["--no-wait"],
            action="store_true",
            help="Do not wait for deployment to be ready before returning.",
        )
        arg_context.argument(
            "dev",
            options_list=["--dev"],
            action="store_true",
            help="If this is specified, then it is considered a dev instance "
            "and will not be billed for.",
        )
        arg_context.argument(
            "dry_run",
            options_list=["--dry-run"],
            action="store_true",
            help="If set, validates the source and destination resources and "
            "the time, without performing the restore. The earliest and latest "
            "possible restore times are returned in the status of the restore "
            "task.",
        )

    with ArgumentsContext(self, "postgres server-arc update") as arg_context:
        arg_context.argument(
            "path",
            options_list=["--path"],
            help="The path to the source json file for the Azure Arc enabled "
            "PostgreSQL server. This is optional.",
        )
        arg_context.argument(
            "name",
            options_list=["--name", "-n"],
            help="Name of the Azure Arc enabled PostgreSQL server that is "
            "being updated. The name under which your instance is deployed "
            "cannot be changed.",
        )
        arg_context.argument(
            "namespace",
            options_list=["--k8s-namespace", "-k"],
            help="The Kubernetes namespace where the Azure Arc enabled "
            "PostgreSQL server is deployed. If no namespace is specified, "
            "then the namespace defined in the kubeconfig will be used.",
        )
        arg_context.argument(
            "certificate_public_key_file",
            options_list=["--cert-public-key-file"],
            help="Path to the file containing a PEM formatted certificate "
            "public key to be used for client SSL connections.",
        )
        arg_context.argument(
            "certificate_private_key_file",
            options_list=["--cert-private-key-file"],
            help="Path to the file containing a PEM formatted certificate "
            "private key to be used for client SSL connections.",
        )
        arg_context.argument(
            "cores_limit",
            options_list=["--cores-limit"],
            help="The maximum number of CPU cores for Azure Arc enabled "
            "PostgreSQL server that can be used per node. To remove the "
            "cores_limit, specify its value as empty string.",
        )
        arg_context.argument(
            "cores_request",
            options_list=["--cores-request"],
            help="The minimum number of CPU cores that must be available "
            "per node to schedule the service. To remove the cores_request, "
            "specify its value as empty string.",
        )
        arg_context.argument(
            "log_level",
            options_list=["--log-level"],
            help="Sets the log_min_messages setting for the PostgreSQL engine."
            " Valid values are: DEBUG5, DEBUG4, DEBUG3, DEBUG2, DEBUG1, INFO, "
            "NOTICE, WARNING, ERROR, LOG, FATAL, PANIC.",
        )
        arg_context.argument(
            "memory_limit",
            options_list=["--memory-limit"],
            help="The memory limit for Azure Arc enabled PostgreSQL server "
            "as a number followed by Ki (kilobytes), Mi (megabytes), or Gi "
            "(gigabytes). To remove the memory_limit, specify its value as "
            "empty string.",
        )
        arg_context.argument(
            "memory_request",
            options_list=["--memory-request"],
            help="The memory request for Azure Arc enabled PostgreSQL server "
            "as a number followed by Ki (kilobytes), Mi (megabytes), or Gi "
            "(gigabytes). To remove the memory_request, specify its value as "
            "empty string.",
        )
        arg_context.argument(
            "no_external_endpoint",
            options_list=["--no-external-endpoint"],
            action="store_true",
            help="If specified, no external service will be created. "
            "Otherwise, an external service will be created using either the "
            "type given with the --service-type argument or the same "
            "service type as the data controller.",
        )
        arg_context.argument(
            "retention_days",
            options_list=["--retention-days"],
            type=int,
            help="Backup retention period, specified in days. "
            "Allowed values are 0 to 35. Default is 7. Setting "
            "the retention period to 0 will turn off automatic "
            "backups for Azure Arc enabled PostgreSql.",
        )
        arg_context.argument(
            "service-annotations",
            options_list=["--service-annotations"],
            help="Comma-separated list of annotations to apply to all "
            "external services.",
        )
        arg_context.argument(
            "service_certificate_secret",
            options_list=["--service-cert-secret"],
            help="Name of the Kubernetes secret to generate that hosts the SSL"
            " certificate.",
        )
        arg_context.argument(
            "service-labels",
            options_list=["--service-labels"],
            help="Comma-separated list of labels to apply to all external "
            "services.",
        )
        arg_context.argument(
            "service-type",
            options_list=["--service-type"],
            help="The type for the primary service.",
        )
        arg_context.argument(
            "dev",
            options_list=["--dev"],
            action="store_true",
            help="If this is specified, then it is considered a dev instance "
            "and will not be billed for.",
        )
        arg_context.argument(
            "port",
            options_list=["--port"],
            help="The port number on which the primary service is exposed to "
            "the end-users.",
        )
        arg_context.argument(
            "nowait",
            options_list=["--no-wait"],
            action="store_true",
            help="Do not wait for deployment to be ready before returning.",
        )
        arg_context.argument(
            "use_k8s",
            options_list=["--use-k8s"],
            action="store_true",
            help=USE_K8S_TEXT,
        )
        arg_context.argument(
            "keytab_secret",
            options_list=["--keytab-secret"],
            help="The name of the Kubernetes secret that contains the keytab "
            "file for this Azure Arc enabled PostgreSQL server.",
        )
        arg_context.argument(
            "extensions",
            options_list=["--extensions"],
            help="Comma seperated list of extensions to be enabled. To Add "
            "or remove a new extension update the existing list of extensions. "
            "Once enabled, extension can be installed via 'CREATE EXTENSION' command.",
        )

    with ArgumentsContext(self, "postgres server-arc delete") as arg_context:
        arg_context.argument(
            "name",
            options_list=["--name", "-n"],
            help="Name of the Azure Arc enabled PostgreSQL server.",
        )
        arg_context.argument(
            "namespace",
            options_list=["--k8s-namespace", "-k"],
            help="The Kubernetes namespace where the Azure Arc enabled "
            "PostgreSQL server is deployed. If no namespace is specified, "
            "then the namespace defined in the kubeconfig will be used.",
        )
        arg_context.argument(
            "force",
            options_list=["--force", "-f"],
            action="store_true",
            help="Delete the Azure Arc enabled PostgreSQL server without confirmation.",
        )
        arg_context.argument(
            "use_k8s",
            options_list=["--use-k8s"],
            action="store_true",
            help=USE_K8S_TEXT,
        )

    with ArgumentsContext(self, "postgres server-arc show") as arg_context:
        arg_context.argument(
            "name",
            options_list=["--name", "-n"],
            help="Name of the Azure Arc enabled PostgreSQL server.",
        )
        arg_context.argument(
            "namespace",
            options_list=["--k8s-namespace", "-k"],
            help="The Kubernetes namespace where the Azure Arc enabled "
            "PostgreSQL server is deployed. If no namespace is specified, "
            "then the namespace defined in the kubeconfig will be used.",
        )
        arg_context.argument(
            "path",
            options_list=["--path"],
            help="A path where the full specification for the Azure Arc "
            "enabled PostgreSQL server should be written. If omitted, the "
            "specification will be written to standard output.",
        )
        arg_context.argument(
            "use_k8s",
            options_list=["--use-k8s"],
            action="store_true",
            help=USE_K8S_TEXT,
        )

    with ArgumentsContext(self, "postgres server-arc list") as arg_context:
        arg_context.argument(
            "namespace",
            options_list=["--k8s-namespace", "-k"],
            help="The Kubernetes namespace where the Azure Arc enabled "
            "PostgreSQL servers are deployed. If no namespace is specified, "
            "then the namespace defined in the kubeconfig will be used.",
        )
        arg_context.argument(
            "use_k8s",
            options_list=["--use-k8s"],
            action="store_true",
            help=USE_K8S_TEXT,
        )

    with ArgumentsContext(
        self, "postgres server-arc endpoint list"
    ) as arg_context:
        arg_context.argument(
            "name",
            options_list=["--name", "-n"],
            help="Name of the Azure Arc enabled PostgreSQL server.",
        )
        arg_context.argument(
            "namespace",
            options_list=["--k8s-namespace", "-k"],
            help="The Kubernetes namespace where the Azure Arc enabled "
            "PostgreSQL server is deployed. If no namespace is specified, "
            "then the namespace defined in the kubeconfig will be used.",
        )
        arg_context.argument(
            "use_k8s",
            options_list=["--use-k8s"],
            action="store_true",
            help=USE_K8S_TEXT,
        )
