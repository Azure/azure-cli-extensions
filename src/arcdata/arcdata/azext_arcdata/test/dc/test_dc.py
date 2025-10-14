# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from collections import namedtuple
from multiprocessing.sharedctypes import Value
from azext_arcdata.kubernetes_sdk.arc_docker_image_service import (
    ArcDataImageService,
)
from azext_arcdata.kubernetes_sdk.dc.dc_utilities import (
    get_bootstrapper_deployment,
    resolve_valid_target_version,
)
from azext_arcdata.kubernetes_sdk.client import KubernetesClient

from pytest_az import VCRState, RECORD_MODES
import azext_arcdata.dc.validators
import os
import pytest
import random
import re
import string

VCR_RECORD_MODE = "once"  # options: None, once, all, rerecord
PG_NAME = "pg1"
NAMESPACE = "test"
RESOURCE_GROUP = "chachan-eastus-rg"
CONTROLLER_NAME = "dc-ipp"
TEST_PASSWORD = (
    "a"
    + "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
    + "aB1"
)


@pytest.mark.usefixtures("setup")
class TestDC(object):
    @pytest.fixture
    def setup(self, az_vcr_cassette, mock_kube_config):
        os.environ["AZDATA_USERNAME"] = "username"
        os.environ["AZDATA_PASSWORD"] = "random-pwd"
        st = VCRState()
        if st.record_mode != RECORD_MODES["rerecord"] and st.cassette_exists:
            mock_kube_config()

    @pytest.mark.skip(
        reason="This is a particularly flakey test, and the functionality"
        "is now being duplicated by the n-x to n CI upgrade tests."
    )
    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "namespace, version",
        [
            (
                NAMESPACE,
                "v1.12.0_ubuntu2004-ravpate",  # locally retaggged images
            )
        ],
    )
    def test_full_dc_upgrade(self, namespace, version, az):
        result = az(
            "arcdata dc upgrade --use-k8s --no-wait",
            k8s_namespace=namespace,
            desired_version=version,
        )

        assert result.exit_code == 0

        dc, dc_config = KubernetesClient.get_arc_datacontroller(namespace, True)
        bsr = get_bootstrapper_deployment(namespace, use_k8s=True)
        assert bsr.spec.template.spec.containers[0].image.endswith(version)
        assert dc.spec.docker.imageTag == version

    @pytest.mark.skip(
        reason="The export generates unique urls which breaks the cassette on "
        "subsequent runs.  Should be run locally."
    )
    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "namespace",
        [NAMESPACE],
    )
    def test_export(self, namespace, az):
        result = az(
            "arcdata dc export -t metrics -p m.json --use-k8s --force",
            k8s_namespace=namespace,
        )

        # todo: need to re-enable when all images are properly published.
        assert result.exit_code == 0

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "namespace",
        [NAMESPACE],
    )
    def test_target_version_validation_default(self, namespace):
        target = resolve_valid_target_version(namespace, use_k8s=True)
        assert target is not None

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "namespace",
        [NAMESPACE],
    )
    def test_list_versions(self, namespace, az):
        results = az(
            "arcdata dc list-upgrades --use-k8s",
            k8s_namespace=namespace,
        )
        assert results.exit_code == 0

        versions = results.out.split("\n")
        assert len(versions) > 0

        # Valid version could be 'v1.1.23' or 'v9.50.35'
        version_prefix_regex = re.compile(r"v\d+\.\d+\.\d+")
        assert version_prefix_regex.search(
            versions[0]
        ), "Expected current version did not match vX.XX.XX."

        version_result_regex = re.compile(
            r"Found \d+ valid versions.\s+The current datacontroller version is v\d+\.\d+\.\d+"
        )
        assert version_result_regex.search(
            versions[0]
        ), "Expected initial message not found in results."

        assert (
            "latest" not in versions
        ), "'latest' version found but not expected in results."

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "namespace",
        [NAMESPACE],
    )
    def _test_dry_run_upgrade_indirect(self, namespace, az):
        (
            cMajor,
            cMinor,
            cRevision,
            cTag,
        ) = ArcDataImageService.get_config_image_tag()
        nextVersion = f"{cMajor}.{cMinor}.{cRevision+1}_{cTag}"
        results = az(
            f"arcdata dc upgrade --use-k8s --target {nextVersion} --dry-run",
            k8s_namespace=namespace,
        )
        assert results.exit_code == 0

        dryrun_results = results.out.split("\n")
        assert "****Dry Run****" in dryrun_results
        assert (
            f"Data controller would be upgraded to: {nextVersion}"
            in dryrun_results
        )

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "resource_group, controller_name",
        [(RESOURCE_GROUP, CONTROLLER_NAME)],
    )
    @pytest.mark.skip(
        "Skipping as it may be that ARM calls are not recorded by the VCR"
    )  # Skipping as it may be that ARM calls are not recorded by the VCR
    def test_dry_run_upgrade_direct(self, resource_group, controller_name, az):
        results = az(
            "arcdata dc upgrade --desired-version 20210928.13 --dry-run",
            resource_group=resource_group,
            name=controller_name,
        )
        assert results.exit_code == 0

        dryrun_results = results.out.split("\n")
        assert "****Dry Run****" in dryrun_results
        assert (
            "Data controller would be upgraded: 20210928.13" in dryrun_results
        )

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "namespace",
        [NAMESPACE],
    )
    def test_upgrade_fails_when_pg_present(self, namespace, az):
        az(
            "postgres server-arc create -n {0} --no-wait --k8s-namespace {1} --use-k8s".format(
                PG_NAME, NAMESPACE
            )
        )

        results = az(
            "arcdata dc upgrade --use-k8s --desired-version 1.7.0_test --dry-run",
            k8s_namespace=namespace,
        )

        dryrun_results = results.err
        assert (
            "One or more postgres preview instances exist in the cluster "
            "and must be deleted prior to upgrading the data controller."
            in str(dryrun_results)
        )

        az(
            "postgres server-arc delete -n {0} --force --k8s-namespace {1} --use-k8s".format(
                PG_NAME, NAMESPACE
            )
        )

    @pytest.mark.skip(
        "Skipping for now until we can get the recordings working correctly"
    )
    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "namespace",
        [NAMESPACE],
    )
    def test_delete_dc(self, namespace, az):
        results = az(
            "arcdata dc delete -n arcdc -y -f --use-k8s",
            k8s_namespace=namespace,
        )

        assert results.exit_code == 0

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "namespace",
        [NAMESPACE],
    )
    def test_update_maintenance_window(self, namespace, az):
        results = az(
            'arcdata dc update --use-k8s --maintenance-start "2022-01-01T23:00" --maintenance-duration 3:00 --maintenance-recurrence Saturday --maintenance-time-zone US/Pacific',
            k8s_namespace=namespace,
        )
        assert (
            results.exit_code == 0
        ), "az command line failed when calling arcdata dc update."

    @pytest.mark.skip(
        "Skipping for now until we can get the recordings working correctly"
    )
    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "resource_group, controller_name",
        [(RESOURCE_GROUP, CONTROLLER_NAME)],
    )
    def test_update_arm_log_upload(self, resource_group, controller_name, az):
        results = az(
            "arcdata dc update --auto-upload-logs true",
            name=controller_name,
            resource_group=RESOURCE_GROUP,
        )
        assert (
            results.exit_code == 0
        ), "az command line failed when calling arcdata dc update."

    @pytest.mark.skip(
        "Skipping for now until we can get the recordings working correctly"
    )
    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "resource_group, controller_name",
        [(RESOURCE_GROUP, CONTROLLER_NAME)],
    )
    def test_update_arm_metrics_upload(
        self, resource_group, controller_name, az
    ):
        results = az(
            "arcdata dc update --auto-upload-metrics true",
            name=controller_name,
            resource_group=RESOURCE_GROUP,
        )
        assert (
            results.exit_code == 0
        ), "az command line failed when calling arcdata dc update."

    def test_upgrade_version_validation_success(self):
        from azext_arcdata.dc.validators import (
            validate_client_version_for_upgrade,
        )

        major, minor, release, tag = ArcDataImageService.get_config_image_tag()
        command_values = namedtuple("command_values", ["desired_version"])
        command_values.desired_version = f"{major}.{minor}.{release}"

        validate_client_version_for_upgrade(command_values)

    def test_upgrade_version_validation_success_release_tag(self):
        from azext_arcdata.dc.validators import (
            validate_client_version_for_upgrade,
        )

        major, minor, release, tag = ArcDataImageService.get_config_image_tag()
        command_values = namedtuple("command_values", ["desired_version"])
        command_values.desired_version = f"{major}.{minor}.{release + 1}_zzz"

        validate_client_version_for_upgrade(command_values)

    def test_upgrade_version_validation_fail_major(self):
        from azext_arcdata.dc.validators import (
            validate_client_version_for_upgrade,
        )

        major, minor, release, tag = ArcDataImageService.get_config_image_tag()
        command_values = namedtuple("command_values", ["desired_version"])
        command_values.desired_version = f"{major + 1}.{minor}.{release}"
        with pytest.raises(ValueError):
            validate_client_version_for_upgrade(command_values)

    def test_upgrade_version_validation_fail_minor(self):
        from azext_arcdata.dc.validators import (
            validate_client_version_for_upgrade,
        )

        major, minor, release, tag = ArcDataImageService.get_config_image_tag()
        command_values = namedtuple("command_values", ["desired_version"])
        command_values.desired_version = f"{major}.{minor + 1}.{release}"
        with pytest.raises(ValueError):
            validate_client_version_for_upgrade(command_values)

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    def test_downgrade_fails_on_dry_run(self, az):
        results = az(
            "az arcdata dc upgrade -ktest --use-k8s --dry-run --desired-version v1.1.0_2021-11-02"
        )
        assert (
            results.exit_code == 1
        ), "Dry-Run did not fail when attempting downgrade."
