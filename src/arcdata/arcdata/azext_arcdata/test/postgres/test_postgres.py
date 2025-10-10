# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

import os
import pytest

VCR_RECORD_MODE = "once"  # options: once, rerecord, replay
NAMESPACE = "test"
STORAGE_CLASS = "local-storage"


def normalize_path(path, *paths):
    """
    Windows needs this sometimes when running the e2e tests from the
    `build unit-tests` task-runner. This can be slightly different than running
    from PyCharm/editor.
    """
    path = os.path.join(path, *paths)
    return path.replace("\\", "/")


@pytest.mark.usefixtures("setup")
class TestPostgres(object):
    @pytest.fixture
    def setup(self, assets_path):
        os.environ["AZDATA_USERNAME"] = "username"
        os.environ["AZDATA_PASSWORD"] = "random-pwd"

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, expected",
        [("pg-ut00001", "Deployed")],
    )
    def test_arc_postgres_server_create(self, name, expected, az):
        result = az(
            f"postgres server-arc create --storage-class-data {STORAGE_CLASS} "
            f"--storage-class-logs {STORAGE_CLASS} --no-wait -n {name} "
            f"--k8s-namespace {NAMESPACE} --use-k8s"
        )

        assert expected in result.out

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, expected",
        [("pg-ut00001", "exists")],
    )
    def test_arc_postgres_server_create_conflict(self, name, expected, az):
        result = az(
            f"postgres server-arc create --storage-class-data {STORAGE_CLASS} "
            f"--storage-class-logs {STORAGE_CLASS} --no-wait -n {name} "
            f"--k8s-namespace {NAMESPACE} --use-k8s"
        )
        print(result.err)
        print("#############################")
        assert expected in str(result.err)

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, exp",
        [("pg-ut00001", "Updated")],
    )
    def test_arc_postgres_server_update(self, name, exp, az):
        result = az(
            "postgres server-arc update --memory-limit 10Gi --no-wait -n "
            f"{name} --k8s-namespace {NAMESPACE} --use-k8s"
        )
        assert exp in result.out

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, exp",
        [("pg-ut00003", "found")],
    )
    def test_arc_postgres_server_invalid_update(self, name, exp, az):
        result = az(
            "postgres server-arc update --memory-limit 10Gi --no-wait "
            f"-n {name} --k8s-namespace {NAMESPACE} --use-k8s"
        )
        assert exp in str(result.err)

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, expected",
        [("pg-ut00001", "pg-ut00001")],
    )
    def test_arc_postgres_server_show(self, name, expected, az):
        result = az(
            f"postgres server-arc show --k8s-namespace {NAMESPACE} --use-k8s",
            name=name,
        )
        assert expected in result.out

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "expected",
        [("pg-ut00001")],
    )
    def test_arc_postgres_server_list(self, expected, az):
        result = az(
            f"postgres server-arc list --k8s-namespace {NAMESPACE} --use-k8s"
        )
        assert "primaryEndpoint" in result.out
        assert "replicas" in result.out
        assert "desiredVersion" in result.out
        assert "runningVersion" in result.out
        assert "state" in result.out
        assert expected in result.out

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, expected",
        [("pg-ut00001", "pg-ut00001")],
    )
    def test_arc_postgres_server_endpoint_list(self, name, expected, az):
        result = az(
            f"postgres server-arc endpoint list -n {name} "
            f"--k8s-namespace {NAMESPACE} --use-k8s"
        )
        assert "instances" in result.out
        assert expected in result.out

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, expected",
        [("pg-ut00001", "Deleted")],
    )
    def test_arc_postgres_server_delete(self, name, expected, az):
        result = az(
            f"postgres server-arc delete --force -n {name} --k8s-namespace "
            f"{NAMESPACE} --use-k8s"
        )
        assert expected in result.out

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, expected",
        [("pg-ut00004", "found")],
    )
    def test_arc_postgres_server_delete_not_found(self, name, expected, az):
        result = az(
            f"postgres server-arc delete --force -n {name} --k8s-namespace "
            f"{NAMESPACE} --use-k8s"
        )
        assert expected in str(result.err)

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize("name, expected", [("pg-ut00005", "exceed")])
    def test_arc_postgres_server_create_cores_exceed_limit(
        self, name, expected, az
    ):
        result = az(
            "postgres server-arc create --cores-request 2 --cores-limit 1 "
            f"-n {name} --k8s-namespace {NAMESPACE} --use-k8s"
        )
        assert expected in str(result.err)

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize("name, expected", [("pg-ut00006", "at least")])
    def test_arc_postgres_server_create_mr_too_low(self, name, expected, az):
        result = az(
            f"postgres server-arc create --memory-request 255Mi -n {name} "
            f"--k8s-namespace {NAMESPACE} --use-k8s"
        )
        assert expected in str(result.err)

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize("name, expected", [("pg-ut00007", "at least")])
    def test_arc_postgres_server_create_ml_too_low(self, name, expected, az):
        result = az(
            f"postgres server-arc create --memory-limit 255Mi -n {name} "
            f"--k8s-namespace {NAMESPACE} --use-k8s"
        )
        assert expected in str(result.err)

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize("name, expected", [("pg-ut00008", "exceed")])
    def test_arc_postgres_server_create_mr_exceeds_ml(self, name, expected, az):
        result = az(
            "postgres server-arc create --memory-limit 2Gi --memory-request 3Gi"
            f" -n {name} --k8s-namespace {NAMESPACE} --use-k8s"
        )
        assert expected in str(result.err)

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, expected", [("ppg-ut00009", "does not exist")]
    )
    def test_arc_postgres_server_create_storage_class_logs(
        self, name, expected, az
    ):
        result = az(
            f"postgres server-arc create --storage-class-logs DNE -n {name} "
            f"--k8s-namespace {NAMESPACE} --use-k8s"
        )
        assert expected in str(result.err)

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, expected", [("pg-ut00010", "does not exist")]
    )
    def test_arc_postgres_server_create_storage_class_data(
        self, name, expected, az
    ):
        result = az(
            f"postgres server-arc create --storage-class-data DNE -n {name} "
            f"--k8s-namespace {NAMESPACE} --use-k8s"
        )
        assert expected in str(result.err)

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, expected",
        [
            (
                "waytoolonganameforthis",
                "'waytoolonganameforthis' exceeds 13 character length limit",
            )
        ],
    )
    def test_arc_postgres_server_create_name_length(self, name, expected, az):
        result = az(
            f"postgres server-arc create -n {name} "
            f"--k8s-namespace {NAMESPACE} --use-k8s"
        )
        assert expected in str(result.err)

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, expected",
        [("!nv@l!d", "name '!nv@l!d' does not follow DNS requirements")],
    )
    def test_arc_postgres_server_create_invalid_name(self, name, expected, az):
        result = az(
            f"postgres server-arc create -n {name} "
            f"--k8s-namespace {NAMESPACE} --use-k8s"
        )
        assert expected in str(result.err)

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, volume_size, expected",
        [("pg-ut00011", "not_a_size", "Invalid number format")],
    )
    def test_arc_postgres_server_create_invalid_logs_volume_size(
        self, name, volume_size, expected, az
    ):
        result = az(
            f"postgres server-arc create -n {name} --volume-size-logs "
            f"{volume_size} --k8s-namespace {NAMESPACE} --use-k8s"
        )
        assert expected + ": " + volume_size in str(result.err)

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, volume_size, expected",
        [("pg-ut00011", "5W", "Invalid number format")],
    )
    def test_arc_postgres_server_create_invalid_data_volume_size(
        self, name, volume_size, expected, az
    ):
        result = az(
            f"postgres server-arc create -n {name} --volume-size-data "
            f"{volume_size} --k8s-namespace {NAMESPACE} --use-k8s"
        )
        assert expected + ": " + volume_size in str(result.err)
