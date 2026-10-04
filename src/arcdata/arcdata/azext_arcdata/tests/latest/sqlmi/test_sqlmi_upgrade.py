from azext_arcdata.vendored_sdks.kubernetes_sdk.client import KubernetesError
from azext_arcdata.vendored_sdks.kubernetes_sdk.errors.K8sAdmissionReviewError import (
    K8sAdmissionReviewError,
)
from azext_arcdata.sqlmi.sqlmi_utilities import upgrade_sqlmi_instances
from azext_arcdata.vendored_sdks.kubernetes_sdk.client import KubernetesClient
import os
import pytest
from pytest_az import VCRState, RECORD_MODES

import time

# todo: these are integration tests used for debugging early,  we need to create recordings and wire these up for unit testing.

VCR_RECORD_MODE = "once"  # options: None, once, all, rerecord
NAMESPACE = "test"
STORAGE_CLASS = "local-storage"
SQLMI_NAME = "sqlmi3"


@pytest.mark.skip(reason="Testing library is broken.")
@pytest.mark.usefixtures("setup")
class TestSqlMiUpgrade:
    @pytest.fixture
    def setup(self, az_vcr_cassette, mock_kube_config):
        st = VCRState()
        if st.record_mode != RECORD_MODES["rerecord"] and st.cassette_exists:
            mock_kube_config()

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "namespace, name",
        [(NAMESPACE, SQLMI_NAME)],
    )
    def test_upgrade_dryrun(self, namespace, name):
        upgrade_sqlmi_instances(
            namespace,
            name=name,
            desired_version="v1.14.0_upgrade-test",
            dry_run=True,
            use_k8s=True,
        )

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "namespace, expected_sql_instance",
        [(NAMESPACE, SQLMI_NAME)],
    )
    def test_upgrade_pre_dc_upgrade(self, namespace, expected_sql_instance, az):
        results = az(
            "az sql mi-arc upgrade --k8s-namespace {0} -n {1} --dry-run --use-k8s".format(
                namespace, expected_sql_instance
            )
        )
        assert expected_sql_instance in results.out

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "namespace, name, desired_version",
        [(NAMESPACE, "sqlmi100", "v1.2.0_2021-12-15")],
    )
    def test_upgrade_with_instance_not_exists(
        self, namespace, name, desired_version
    ):
        with pytest.raises(
            ValueError, match=r"Instance sqlmi100 does not exist."
        ):
            upgrade_sqlmi_instances(
                namespace,
                name=name,
                desired_version=desired_version,
                use_k8s=True,
            )

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "namespace, name, desired_version",
        [(NAMESPACE, SQLMI_NAME, "20211026.5_master")],
    )
    def test_upgrade_to_unsupported_version(
        self, namespace, name, desired_version
    ):
        with pytest.raises(ValueError):
            upgrade_sqlmi_instances(
                namespace,
                name=name,
                desired_version=desired_version,
                use_k8s=True,
            )

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "namespace, name, desired_version",
        [(NAMESPACE, SQLMI_NAME, "v1.14.0_upgrade-test2")],
    )
    def test_upgrade_with_name(self, namespace, name, desired_version):
        upgraded_instances = upgrade_sqlmi_instances(
            namespace, name=name, desired_version=desired_version, use_k8s=True
        )
        assert len(upgraded_instances) == 1

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "namespace, desired_version",
        [(NAMESPACE, "v1.14.0_upgrade-test2")],
    )
    def test_upgrade_with_name_wildcard(self, namespace, desired_version):
        upgraded_instances = upgrade_sqlmi_instances(
            namespace,
            name="sqlmi*",
            desired_version=desired_version,
            use_k8s=True,
            dry_run=True,
        )
        assert len(upgraded_instances) == 3

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "namespace, name",
        [(NAMESPACE, SQLMI_NAME)],
    )
    def test_upgrade(self, namespace, name):
        upgrade_sqlmi_instances(namespace, use_k8s=True)

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    def test_upgrade_fails_beyond_dc_version(self, az):
        results = az(
            "az sql mi-arc upgrade -k {0} --use-k8s -v v13.7.0_test -d -n {1}".format(
                NAMESPACE, SQLMI_NAME
            )
        )

        assert (
            results.exit_code == 1
        ), "Upgrade request beyond the dc version should have failed, but did not."
        assert (
            "Arc-enabled SQL managed instance(s) cannot be upgraded beyond the data controller version"
            in str(results.err)
        ), "Upgrade was blocked, but improper exception text was returned."
