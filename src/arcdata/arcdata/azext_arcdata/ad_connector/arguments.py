# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from azext_arcdata.core.constants import (
    USE_K8S_TEXT,
    CLI_ARG_GROUP_DIRECT_TEXT,
    CLI_ARG_GROUP_INDIRECT_TEXT,
)


def load_arguments(self, _):
    from knack.arguments import ArgumentsContext

    with ArgumentsContext(self, "arcdata ad-connector create") as arg_context:
        # -- indirect --
        arg_context.argument(
            "namespace",
            options_list=["--k8s-namespace", "-k"],
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            help="The Kubernetes namespace to deploy the Active Directory connector.",
        )
        arg_context.argument(
            "use_k8s",
            options_list=("--use-k8s"),
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            action="store_true",
            help=USE_K8S_TEXT,
        )
        # -- direct --
        arg_context.argument(
            "data_controller_name",
            options_list=["--data-controller-name"],
            arg_group=CLI_ARG_GROUP_DIRECT_TEXT,
            help="The name of the Arc data controller associated with this Active Directory connector.",
        )
        arg_context.argument(
            "resource_group",
            options_list=["--resource-group", "-g"],
            arg_group=CLI_ARG_GROUP_DIRECT_TEXT,
            help="The Azure resource group of the Arc data controller associated with this Active Directory connector.",
        )
        # -- common ---
        arg_context.argument(
            "name",
            options_list=["--name", "-n"],
            help="The name of the Active Directory connector.",
        )
        arg_context.argument(
            "account_provisioning",
            options_list=["--account-provisioning"],
            help="Value indicating whether service account provisioning for data services should be automatic or manual. Allowed values are: 'manual' or 'automatic'",
        )
        arg_context.argument(
            "realm",
            options_list=["--realm"],
            help="The name of the Active Directory domain in uppercase (e.g CONTOSO.LOCAL).",
        )
        arg_context.argument(
            "nameserver_addresses",
            options_list=["--nameserver-addresses"],
            help="List of Active Directory DNS server IP addresses separated by ',' (e.g. 10.10.10.11,10.10.10.12,10.10.10.13)",
        )
        arg_context.argument(
            "primary_domain_controller",
            options_list=["--primary-ad-dc-hostname"],
            help="The hostname of the primary AD domain controller.",
        )
        arg_context.argument(
            "secondary_domain_controllers",
            options_list=["--secondary-ad-dc-hostnames"],
            help="List of the hostnames of the secondary Active Directory domain controller separated by ','"
            "(e.g. azdc02.contoso.local,azdc03.contoso.local)",
        )
        arg_context.argument(
            "netbios_domain_name",
            options_list=["--netbios-domain-name"],
            help="The NETBIOS name of the Active Directory domain (e.g. CONTOSO).",
        )
        arg_context.argument(
            "dns_domain_name",
            options_list=["--dns-domain-name"],
            help="The DNS domain name (e.g. contoso.com)",
        )
        arg_context.argument(
            "num_dns_replicas",
            options_list=["--dns-replicas"],
            help="The number of copies for DNS proxy service.",
        )
        arg_context.argument(
            "prefer_k8s_dns",
            options_list=["--prefer-k8s-dns"],
            help="Use Kubernetes DNS Server responses over the Active Directory DNS server responses for IP address lookup. Allowed values are 'true' or 'false'",
        )
        arg_context.argument(
            "ou_distinguished_name",
            options_list=["--ou-distinguished-name"],
            help="The distinguished name of the pre-created Organizational Unit (OU) in the Active Directory domain. (e.g. OU=arcou,DC=contoso,DC=com).",
        )
        arg_context.argument(
            "domain_service_account_secret",
            options_list=["--domain-service-account-secret"],
            help="The name of the Kubernetes secret containing the credentials for the pre-created Active Directory account with permissions to create and manage accounts in the given OU. Alternatively, setting the 'DOMAIN_SERVICE_ACCOUNT_USERNAME' and 'DOMAIN_SERVICE_ACCOUNT_PASSWORD' env variables will create this secret automatically.",
        )

    with ArgumentsContext(self, "arcdata ad-connector update") as arg_context:
        # -- indirect --
        arg_context.argument(
            "namespace",
            options_list=["--k8s-namespace", "-k"],
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            help="The Kubernetes namespace containing Active Directory connector.",
        )
        arg_context.argument(
            "use_k8s",
            options_list=("--use-k8s"),
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            action="store_true",
            help=USE_K8S_TEXT,
        )
        # -- direct --
        arg_context.argument(
            "data_controller_name",
            options_list=["--data-controller-name"],
            arg_group=CLI_ARG_GROUP_DIRECT_TEXT,
            help="The name of the Arc data controller associated with this Active Directory connector.",
        )
        arg_context.argument(
            "resource_group",
            options_list=["--resource-group", "-g"],
            arg_group=CLI_ARG_GROUP_DIRECT_TEXT,
            help="The Azure resource group of the Arc data controller associated with this Active Directory connector.",
        )
        # -- common ---
        arg_context.argument(
            "name",
            options_list=["--name", "-n"],
            help="The name of the Active Directory connector.",
        )
        arg_context.argument(
            "nameserver_addresses",
            options_list=["--nameserver-addresses"],
            help="List of Active Directory DNS server IP addresses separated by ',' (e.g. 10.10.10.11,10.10.10.12,10.10.10.13)",
        )
        arg_context.argument(
            "primary_domain_controller",
            options_list=["--primary-ad-dc-hostname"],
            help="The hostname of the primary AD domain controller.",
        )
        arg_context.argument(
            "secondary_domain_controllers",
            options_list=["--secondary-ad-dc-hostnames"],
            help="List of the hostnames of the secondary Active Directory domain controller separated by ','"
            "(e.g. azdc02.contoso.local,azdc03.contoso.local)",
        )
        arg_context.argument(
            "num_dns_replicas",
            options_list=["--dns-replicas"],
            help="The number of copies for DNS proxy service.",
        )
        arg_context.argument(
            "prefer_k8s_dns",
            options_list=["--prefer-k8s-dns"],
            help="Use Kubernetes DNS Server responses over the Active Directory DNS server responses for IP address lookup. Allowed values are 'true' or 'false'",
        )
        arg_context.argument(
            "domain_service_account_secret",
            options_list=["--domain-service-account-secret"],
            help="The name of the Kubernetes secret containing the credentials for the pre-created Active Directory account with permissions to create and manage accounts in the given OU.",
        )

    with ArgumentsContext(self, "arcdata ad-connector delete") as arg_context:
        # -- indirect --
        arg_context.argument(
            "namespace",
            options_list=["--k8s-namespace", "-k"],
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            help="The Kubernetes namespace containing the Active Directory connector.",
        )
        arg_context.argument(
            "use_k8s",
            options_list=("--use-k8s"),
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            action="store_true",
            help=USE_K8S_TEXT,
        )
        # -- direct --
        arg_context.argument(
            "data_controller_name",
            options_list=["--data-controller-name"],
            arg_group=CLI_ARG_GROUP_DIRECT_TEXT,
            help="The name of the Arc data controller "
            "associated with this Active Directory connector.",
        )
        arg_context.argument(
            "resource_group",
            options_list=["--resource-group", "-g"],
            arg_group=CLI_ARG_GROUP_DIRECT_TEXT,
            help="The Azure resource group of the Arc data controller "
            "associated with this Active Directory connector.",
        )
        # -- common ---
        arg_context.argument(
            "name",
            options_list=["--name", "-n"],
            help="The name of the Active Directory connector.",
        )

    with ArgumentsContext(self, "arcdata ad-connector show") as arg_context:
        # -- indirect --
        arg_context.argument(
            "namespace",
            options_list=["--k8s-namespace", "-k"],
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            help="The Kubernetes namespace containing the Active Directory connector.",
        )
        arg_context.argument(
            "use_k8s",
            options_list=("--use-k8s"),
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            action="store_true",
            help=USE_K8S_TEXT,
        )
        # -- direct --
        arg_context.argument(
            "data_controller_name",
            options_list=["--data-controller-name"],
            arg_group=CLI_ARG_GROUP_DIRECT_TEXT,
            help="The name of the Arc data controller "
            "associated with this Active Directory connector.",
        )
        arg_context.argument(
            "resource_group",
            options_list=["--resource-group", "-g"],
            arg_group=CLI_ARG_GROUP_DIRECT_TEXT,
            help="The Azure resource group of the Arc data controller "
            "associated with this Active Directory connector.",
        )
        # -- common ---
        arg_context.argument(
            "name",
            options_list=["--name", "-n"],
            help="The name of the Active Directory connector.",
        )

    with ArgumentsContext(self, "arcdata ad-connector list") as arg_context:
        # -- indirect --
        arg_context.argument(
            "namespace",
            options_list=["--k8s-namespace", "-k"],
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            help="The Kubernetes namespace containing the Active Directory connectors.",
        )
        arg_context.argument(
            "use_k8s",
            options_list=("--use-k8s"),
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            action="store_true",
            help=USE_K8S_TEXT,
        )
        # -- direct --
        arg_context.argument(
            "data_controller_name",
            options_list=["--data-controller-name"],
            arg_group=CLI_ARG_GROUP_DIRECT_TEXT,
            help="The name of the Arc data controller "
            "associated with the Active Directory connectors.",
        )
        arg_context.argument(
            "resource_group",
            options_list=["--resource-group", "-g"],
            arg_group=CLI_ARG_GROUP_DIRECT_TEXT,
            help="The Azure resource group containing the Active Directory connectors.",
        )
