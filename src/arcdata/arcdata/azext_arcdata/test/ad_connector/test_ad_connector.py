# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------


import os
from azext_arcdata.ad_connector.constants import (
    ACCOUNT_PROVISIONING_MODE_AUTOMATIC,
    ACCOUNT_PROVISIONING_MODE_MANUAL,
)

import pytest

VCR_RECORD_MODE = "once"  # options: None, once, all, rerecord

NAME = "arcadc"
AUTO_NAME = "arcadcauto"
NAMESPACE = "test"
REALM = "BDC.ARIS.LOCAL"
NAMESERVER_ADDRESSES = "10.91.136.121,10.91.136.203"
PRIMARY_DOMAIN_CONTROLLER = "aris-win2016-dc.bdc.aris.local"
SECONDARY_DOMAIN_CONTROLLERS = "bdcarislocal2.bdc.aris.local"
NETBIOS_DOMAIN_NAME = "BDC"
DNS_DOMAIN_NAME = "bdc.aris.local"
NUM_DNS_REPLICAS = 2
PREFER_K8S_DNS = "false"
OU_DISTINGUISHED_NAME = "OU=arcou,DC=bdc,DC=aris,DC=local"
DOMAIN_SERVICE_ACCOUNT_SECRET = "arcadc-domain-service-account-secret"

# Pytest error codes
ARGUMENT_REQUIRED_ERROR = 2


@pytest.mark.skip(
    reason="Due to new controller-side validations, "
    "no longer able to run these locally."
)
@pytest.mark.usefixtures("setup")
class TestADConnector(object):
    @pytest.fixture
    def setup(self):
        os.environ["DOMAIN_SERVICE_ACCOUNT_USERNAME"] = "username"
        os.environ["DOMAIN_SERVICE_ACCOUNT_PASSWORD"] = "Placeholder001"

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "expected",
        ["is being created"],
    )
    def test_ad_connector_create_manual_required_args(self, expected, az):
        result = az(
            "az arcdata ad-connector create --use-k8s --no-wait",
            name=NAME,
            k8s_namespace=NAMESPACE,
            realm=REALM,
            account_provisioning=ACCOUNT_PROVISIONING_MODE_MANUAL,
            nameserver_addresses=NAMESERVER_ADDRESSES,
        )

        print(result)
        assert expected in result.out

        # Clean up after test
        #
        az(
            "az arcdata ad-connector delete --use-k8s",
            name=NAME,
            k8s_namespace=NAMESPACE,
        )

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "expected",
        ["is being created"],
    )
    def test_ad_connector_create_automatic_required_args(self, expected, az):
        result = az(
            "az arcdata ad-connector create --use-k8s --no-wait",
            name=AUTO_NAME,
            k8s_namespace=NAMESPACE,
            realm=REALM,
            nameserver_addresses=NAMESERVER_ADDRESSES,
            account_provisioning=ACCOUNT_PROVISIONING_MODE_AUTOMATIC,
            ou_distinguished_name=OU_DISTINGUISHED_NAME,
            domain_service_account_secret=DOMAIN_SERVICE_ACCOUNT_SECRET,
        )
        print(result)
        assert expected in result.out

        # Clean up after test
        #
        az(
            "az arcdata ad-connector delete --use-k8s",
            name=AUTO_NAME,
            k8s_namespace=NAMESPACE,
        )

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "expected",
        ["is being created"],
    )
    def test_ad_connector_create_manual_all_args(self, expected, az):
        result = az(
            "az arcdata ad-connector create --use-k8s --no-wait",
            name=NAME,
            k8s_namespace=NAMESPACE,
            realm=REALM,
            account_provisioning=ACCOUNT_PROVISIONING_MODE_MANUAL,
            nameserver_addresses=NAMESERVER_ADDRESSES,
            primary_ad_dc_hostname=PRIMARY_DOMAIN_CONTROLLER,
            secondary_ad_dc_hostnames=SECONDARY_DOMAIN_CONTROLLERS,
            netbios_domain_name=NETBIOS_DOMAIN_NAME,
            dns_domain_name=DNS_DOMAIN_NAME,
            dns_replicas=NUM_DNS_REPLICAS,
            prefer_k8s_dns=PREFER_K8S_DNS,
        )
        print(result)
        assert expected in result.out

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "expected",
        ["is being created"],
    )
    def test_ad_connector_create_automatic_all_args(self, expected, az):
        result = az(
            "az arcdata ad-connector create --use-k8s --no-wait",
            name=AUTO_NAME,
            k8s_namespace=NAMESPACE,
            realm=REALM,
            nameserver_addresses=NAMESERVER_ADDRESSES,
            account_provisioning=ACCOUNT_PROVISIONING_MODE_AUTOMATIC,
            ou_distinguished_name=OU_DISTINGUISHED_NAME,
            domain_service_account_secret=DOMAIN_SERVICE_ACCOUNT_SECRET,
            primary_ad_dc_hostname=PRIMARY_DOMAIN_CONTROLLER,
            secondary_ad_dc_hostnames=SECONDARY_DOMAIN_CONTROLLERS,
            netbios_domain_name=NETBIOS_DOMAIN_NAME,
            dns_domain_name=DNS_DOMAIN_NAME,
            dns_replicas=NUM_DNS_REPLICAS,
            prefer_k8s_dns=PREFER_K8S_DNS,
        )
        print(result)
        assert expected in result.out

    @pytest.mark.parametrize(
        "name, expected",
        [
            (
                "123adc",
                "does not follow DNS requirements",
            ),
            (
                "arc@adc",
                "does not follow DNS requirements",
            ),
            (
                "arc.adc",
                "does not follow DNS requirements",
            ),
        ],
    )
    def test_ad_connector_create_name(self, name, expected, az):
        result = az(
            "az arcdata ad-connector create --use-k8s --no-wait",
            name=name,
            k8s_namespace=NAMESPACE,
            realm=REALM,
            account_provisioning=ACCOUNT_PROVISIONING_MODE_MANUAL,
            nameserver_addresses=NAMESERVER_ADDRESSES,
            expect_failure=True,
        )
        print(result)
        assert result.exit_code == ARGUMENT_REQUIRED_ERROR
        # assert expected in str(result.err)

        result = az(
            "az arcdata ad-connector create --use-k8s --no-wait",
            name=name,
            k8s_namespace=NAMESPACE,
            realm=REALM,
            nameserver_addresses=NAMESERVER_ADDRESSES,
            account_provisioning=ACCOUNT_PROVISIONING_MODE_AUTOMATIC,
            ou_distinguished_name=OU_DISTINGUISHED_NAME,
            domain_service_account_secret=DOMAIN_SERVICE_ACCOUNT_SECRET,
            expect_failure=True,
        )
        print(result)
        assert result.exit_code == ARGUMENT_REQUIRED_ERROR
        # assert expected in str(result.err)

    @pytest.mark.parametrize(
        "realm, expected",
        [
            ("A", "The given realm 'A' is invalid"),
            (".CONTOSO.LOCAL", "The given realm '.CONTOSO.LOCAL' is invalid"),
        ],
    )
    def test_ad_connector_create_realm(self, realm, expected, az):
        result = az(
            "az arcdata ad-connector create --use-k8s --no-wait",
            name=AUTO_NAME,
            k8s_namespace=NAMESPACE,
            realm=realm,
            nameserver_addresses=NAMESERVER_ADDRESSES,
            account_provisioning=ACCOUNT_PROVISIONING_MODE_AUTOMATIC,
            ou_distinguished_name=OU_DISTINGUISHED_NAME,
            domain_service_account_secret=DOMAIN_SERVICE_ACCOUNT_SECRET,
            expect_failure=True,
        )
        print(result)
        assert result.exit_code == ARGUMENT_REQUIRED_ERROR
        # assert expected in str(result.err)

    @pytest.mark.parametrize(
        "account_provisioning, expected",
        [
            (
                "default",
                "The allowed values for --account-provisioning are 'manual' and 'automatic'",
            )
        ],
    )
    def test_ad_connector_create_account_provisioning(
        self, account_provisioning, expected, az
    ):
        result = az(
            "az arcdata ad-connector create --use-k8s --no-wait",
            name=AUTO_NAME,
            k8s_namespace=NAMESPACE,
            realm=REALM,
            nameserver_addresses=NAMESERVER_ADDRESSES,
            account_provisioning=account_provisioning,
            ou_distinguished_name=OU_DISTINGUISHED_NAME,
            domain_service_account_secret=DOMAIN_SERVICE_ACCOUNT_SECRET,
            expect_failure=True,
        )
        print(result)
        assert result.exit_code == ARGUMENT_REQUIRED_ERROR
        # assert expected in str(result.err)

    @pytest.mark.parametrize(
        "nameserver_addresses, expected",
        [
            (
                ",",
                "One or more Active Directory DNS server IP addresses are invalid.",
            ),
            (
                "11.11.111.111,22.22.222.333",
                "One or more Active Directory DNS server IP addresses are invalid.",
            ),
        ],
    )
    def test_ad_connector_create_nameserver_addresses(
        self, nameserver_addresses, expected, az
    ):
        result = result = az(
            "az arcdata ad-connector create --use-k8s --no-wait",
            name=NAME,
            k8s_namespace=NAMESPACE,
            realm=REALM,
            account_provisioning=ACCOUNT_PROVISIONING_MODE_MANUAL,
            nameserver_addresses=nameserver_addresses,
            expect_failure=True,
        )
        print(result)
        assert result.exit_code == ARGUMENT_REQUIRED_ERROR
        # assert expected in str(result.err)

        result = az(
            "az arcdata ad-connector create --use-k8s --no-wait",
            name=AUTO_NAME,
            k8s_namespace=NAMESPACE,
            realm=REALM,
            nameserver_addresses=nameserver_addresses,
            account_provisioning=ACCOUNT_PROVISIONING_MODE_AUTOMATIC,
            ou_distinguished_name=OU_DISTINGUISHED_NAME,
            domain_service_account_secret=DOMAIN_SERVICE_ACCOUNT_SECRET,
            expect_failure=True,
        )
        print(result)
        assert result.exit_code == ARGUMENT_REQUIRED_ERROR
        # assert expected in str(result.err)

    @pytest.mark.parametrize(
        "dns_replicas, expected",
        [
            (
                0,
                "Invalid number of DNS replicas. --dns-replicas must be 1 or greater.",
            ),
            (
                True,
                "Invalid number of DNS replicas. --dns-replicas must be 1 or greater.",
            ),
        ],
    )
    def test_ad_connector_create_dns_replicas(self, dns_replicas, expected, az):
        result = az(
            "az arcdata ad-connector create --use-k8s --no-wait",
            name=AUTO_NAME,
            k8s_namespace=NAMESPACE,
            realm=REALM,
            nameserver_addresses=NAMESERVER_ADDRESSES,
            account_provisioning=ACCOUNT_PROVISIONING_MODE_AUTOMATIC,
            ou_distinguished_name=OU_DISTINGUISHED_NAME,
            domain_service_account_secret=DOMAIN_SERVICE_ACCOUNT_SECRET,
            dns_replicas=dns_replicas,
            expect_failure=True,
        )
        print(result)
        assert result.exit_code == ARGUMENT_REQUIRED_ERROR
        # assert expected in str(result.err)

    @pytest.mark.parametrize(
        "netbios_domain_name, expected",
        [("CONTOSO*LOCAL", "is invalid")],
    )
    def test_ad_connector_create_netbios_name(
        self, netbios_domain_name, expected, az
    ):
        result = result = az(
            "az arcdata ad-connector create --use-k8s --no-wait",
            name=NAME,
            k8s_namespace=NAMESPACE,
            realm=REALM,
            account_provisioning=ACCOUNT_PROVISIONING_MODE_MANUAL,
            nameserver_addresses=NAMESERVER_ADDRESSES,
            netbios_domain_name=netbios_domain_name,
            expect_failure=True,
        )
        print(result)
        assert result.exit_code == ARGUMENT_REQUIRED_ERROR
        # assert expected in str(result.err)

    @pytest.mark.parametrize(
        "dns_domain_name, expected",
        [("contoso_local", "is invalid")],
    )
    def test_ad_connector_create_dns_domain_name(
        self, dns_domain_name, expected, az
    ):
        result = result = az(
            "az arcdata ad-connector create --use-k8s --no-wait",
            name=NAME,
            k8s_namespace=NAMESPACE,
            realm=REALM,
            account_provisioning=ACCOUNT_PROVISIONING_MODE_MANUAL,
            nameserver_addresses=NAMESERVER_ADDRESSES,
            dns_domain_name=dns_domain_name,
            expect_failure=True,
        )
        print(result)
        assert result.exit_code == ARGUMENT_REQUIRED_ERROR
        # assert expected in str(result.err)

    @pytest.mark.parametrize(
        "prefer_k8s_dns, expected",
        [
            (
                "no",
                "The allowed values for --prefer-k8s-dns are 'true' or 'false'",
            )
        ],
    )
    def test_ad_connector_create_k8s_dns(self, prefer_k8s_dns, expected, az):
        result = result = az(
            "az arcdata ad-connector create --use-k8s --no-wait",
            name=prefer_k8s_dns,
            k8s_namespace=NAMESPACE,
            realm=REALM,
            account_provisioning=ACCOUNT_PROVISIONING_MODE_MANUAL,
            nameserver_addresses=NAMESERVER_ADDRESSES,
            prefer_k8s_dns=prefer_k8s_dns,
            expect_failure=True,
        )
        print(result)
        assert result.exit_code == ARGUMENT_REQUIRED_ERROR
        # assert expected in str(result.err)

    @pytest.mark.parametrize(
        "ou_distinguished_name, expected",
        [
            (
                "DC=contoso,DC=local",
                "Invalid distinguished name of AD Organizational Unit (OU)",
            )
        ],
    )
    def test_ad_connector_create_ou_distinguished_name(
        self, ou_distinguished_name, expected, az
    ):
        result = az(
            "az arcdata ad-connector create --use-k8s --no-wait",
            name=AUTO_NAME,
            k8s_namespace=NAMESPACE,
            realm=REALM,
            nameserver_addresses=NAMESERVER_ADDRESSES,
            account_provisioning=ACCOUNT_PROVISIONING_MODE_AUTOMATIC,
            ou_distinguished_name=ou_distinguished_name,
            domain_service_account_secret=DOMAIN_SERVICE_ACCOUNT_SECRET,
            expect_failure=True,
        )
        print(result)
        assert result.exit_code == ARGUMENT_REQUIRED_ERROR
        # assert expected in str(result.err)

    @pytest.mark.parametrize(
        "primary_domain_controller, expected",
        [
            (
                "newdc_contoso.local",
                "The given primary domain controller hostname 'newdc_contoso.local' is invalid.",
            )
        ],
    )
    def test_ad_connector_update_primary_dc_invalid(
        self, primary_domain_controller, expected, az
    ):
        result = az(
            "az arcdata ad-connector update --use-k8s --no-wait",
            name=AUTO_NAME,
            k8s_namespace=NAMESPACE,
            primary_ad_dc_hostname=primary_domain_controller,
            expect_failure=True,
        )
        print(result)
        assert result.exit_code == ARGUMENT_REQUIRED_ERROR
        # assert expected in str(result.err)

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "primary_domain_controller, expected",
        [("newdc.contoso.local", "is being updated")],
    )
    def test_ad_connector_update_primary_dc_valid(
        self, primary_domain_controller, expected, az
    ):
        result = az(
            "az arcdata ad-connector update --use-k8s --no-wait",
            name=AUTO_NAME,
            k8s_namespace=NAMESPACE,
            primary_ad_dc_hostname=primary_domain_controller,
            domain_service_account_secret=DOMAIN_SERVICE_ACCOUNT_SECRET,
        )
        print(result)
        assert expected in result.out

    @pytest.mark.parametrize(
        "secondary_domain_controllers, expected",
        [
            (
                "newdc1.contoso.local,new#dc2.contoso.local",
                "One or more secondary domain controller hostnames is invalid.",
            )
        ],
    )
    def test_ad_connector_update_secondary_dc_invalid(
        self, secondary_domain_controllers, expected, az
    ):
        result = az(
            "az arcdata ad-connector update --use-k8s --no-wait",
            name=AUTO_NAME,
            k8s_namespace=NAMESPACE,
            secondary_ad_dc_hostnames=secondary_domain_controllers,
            expect_failure=True,
        )
        print(result)
        assert result.exit_code == ARGUMENT_REQUIRED_ERROR
        # assert expected in str(result.err)

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, expected",
        [(NAME, NAME), (AUTO_NAME, AUTO_NAME)],
    )
    def test_ad_connector_show(self, name, expected, az):
        result = az(
            "az arcdata ad-connector show --use-k8s",
            name=name,
            k8s_namespace=NAMESPACE,
        )
        print(result.out)
        assert expected in result.out

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, expected",
        [
            (NAME, "Deleted Active Directory connector"),
            (AUTO_NAME, "Deleted Active Directory connector"),
        ],
    )
    def test_ad_connector_delete(self, name, expected, az):
        result = az(
            "az arcdata ad-connector delete --use-k8s",
            name=name,
            k8s_namespace=NAMESPACE,
        )
        print(result)
        assert expected in result.out
