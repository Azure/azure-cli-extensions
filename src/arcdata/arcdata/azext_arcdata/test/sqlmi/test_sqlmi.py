# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

import os
import time

import pytest
from azext_arcdata.kubernetes_sdk.models.custom_resource import CustomResource
from azext_arcdata.kubernetes_sdk.models.kube_quantity import KubeQuantity
from azext_arcdata.kubernetes_sdk.models.volume_claim import VolumeClaim
from azext_arcdata.sqlmi.models.sqlmi_cr_model import SqlmiCustomResource

VCR_RECORD_MODE = "once"  # options: None, once, all, rerecord
NAMESPACE = "test"
STORAGE_CLASS = "local-storage"


@pytest.mark.skip(reason="Testing library is broken.")
@pytest.mark.usefixtures("setup")
class TestSqlmi(object):
    @pytest.fixture
    def setup(self):
        os.environ["AZDATA_USERNAME"] = "username"
        os.environ["AZDATA_PASSWORD"] = "Placeholder001"

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, expected, storage_class",
        [("sqlmi1", "Deployed", STORAGE_CLASS)],
    )
    def test_arc_sql_mi_create(self, name, expected, storage_class, az):
        result = az(
            "sql mi-arc create --storage-class-data {2} "
            "--storage-class-logs {2} --no-wait -n {0} "
            "--k8s-namespace {1} --use-k8s".format(
                name, NAMESPACE, storage_class
            )
        )
        print(result.out)
        assert expected in result.out

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, expected, storage_class",
        [("sqlmibc1", "Deployed", STORAGE_CLASS)],
    )
    def test_arc_sql_mi_create_bc(self, name, expected, storage_class, az):
        result = az(
            "sql mi-arc create --storage-class-data {2} "
            "--storage-class-logs {2} --no-wait -n {0} "
            "--k8s-namespace {1} --tier bc --use-k8s".format(
                name, NAMESPACE, storage_class
            )
        )
        print(result.out)
        assert expected in result.out

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, expected, time_zone",
        [("sqlmi-tz", "Deployed", "America/New_York")],
    )
    def test_arc_sql_mi_create_time_zone(self, name, expected, time_zone, az):
        result = az(
            "sql mi-arc create --time-zone {2} "
            " --no-wait -n {0} --k8s-namespace {1} --use-k8s".format(
                name, NAMESPACE, time_zone
            )
        )
        print(result.out)
        assert expected in result.out

        # Clean up after test
        #
        az(
            "az sql mi-arc delete --use-k8s",
            name=name,
            k8s_namespace=NAMESPACE,
        )

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, expected, storage_class",
        [("sqlmi1", "exists", STORAGE_CLASS)],
    )
    def test_arc_sql_mi_create_conflict(
        self, name, expected, storage_class, az
    ):
        result = az(
            "sql mi-arc create --storage-class-data {2} "
            "--storage-class-logs {2} --no-wait -n {0} "
            "--k8s-namespace {1} --use-k8s".format(
                name, NAMESPACE, storage_class
            )
        )
        assert expected in str(result.err)

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, exp",
        [("sqlmi1", "Updated")],
    )
    def test_arc_sql_mi_edit(self, name, exp, az):
        time.sleep(10)
        result = az(
            "sql mi-arc update --memory-limit 10Gi --no-wait -n {0} "
            "--k8s-namespace {1} --use-k8s".format(name, NAMESPACE)
        )
        assert exp in result.out, str(result.err)

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, rd, expected", [("sqlmi1", "35", "Updated")]
    )
    def test_arc_sql_mi_edit_valid(self, name, rd, expected, az):
        time.sleep(10)
        result = az(
            "sql mi-arc update --no-wait -n {0} --k8s-namespace {1} --use-k8s"
            " --retention-days {2}".format(name, NAMESPACE, rd)
        )

        assert expected in str(result.out)

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, exp",
        [("foobar", "found")],
    )
    def test_arc_sql_mi_invalid_edit(self, name, exp, az):
        result = az(
            "sql mi-arc update --memory-limit 10Gi --no-wait -n {0} "
            "--k8s-namespace {1} --use-k8s".format(name, NAMESPACE)
        )
        assert exp in str(result.err)

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, rd",
        [("sqlmi1", "-1"), ("sqlmi1", "36")],
    )
    def test_arc_sql_mi_edit_rd_invalid(self, name, rd, az):
        try:
            az(
                "sql mi-arc update --no-wait -n {0} --k8s-namespace {1} --use-k8s --retention-days {2}".format(
                    name, NAMESPACE, rd
                )
            )
            assert False, "Error was not thrown as expected"
        except SystemExit:
            pass

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, expected",
        [("sqlmi1", "sqlmi1")],
    )
    def test_arc_sql_mi_show(self, name, expected, az):
        result = az(
            "sql mi-arc show -n {0} --k8s-namespace {1} --use-k8s".format(
                name, NAMESPACE
            )
        )
        assert expected in result.out

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, expected",
        [("sqlmi1", "sqlmi1")],
    )
    def test_arc_sql_mi_list_instance(self, name, expected, az):
        result = az(
            "sql mi-arc endpoint list -n {0} --k8s-namespace {1}"
            " --use-k8s".format(name, NAMESPACE)
        )
        print(type(result))
        assert expected in result.out

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "expected",
        ["sqlmi1"],
    )
    def test_arc_sql_mi_list(self, expected, az):
        result = az(
            "sql mi-arc list --k8s-namespace {0} --use-k8s".format(NAMESPACE)
        )
        print(result.out)
        assert expected in result.out

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "expected, storage_class",
        [(["sqlmi1", "sqlmi3"], STORAGE_CLASS)],
    )
    def test_arc_sql_mi_endpoint_list(self, expected, storage_class, az):
        result = az(
            "sql mi-arc create --storage-class-data {2} "
            "--storage-class-logs {2} --no-wait -n {0} "
            "--k8s-namespace {1} --use-k8s".format(
                expected[1], NAMESPACE, storage_class
            )
        )
        result = az(
            "sql mi-arc endpoint list --k8s-namespace {0} --use-k8s -o"
            " json".format(NAMESPACE)
        )
        for e in expected:
            assert e in result.out

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, expected",
        [("sqlmi1", "Deleted")],
    )
    def test_arc_sql_mi_delete(self, name, expected, az):
        result = az(
            "sql mi-arc delete -n {0} --k8s-namespace {1} --use-k8s".format(
                name, NAMESPACE
            )
        )
        print(result)
        assert expected in result.out

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, expected",
        [("sqlmiinvalid", "not found")],
    )
    def test_arc_sql_mi_delete_not_found(self, name, expected, az):
        result = az(
            "sql mi-arc delete -n {0} --k8s-namespace {1} --use-k8s".format(
                name, NAMESPACE
            )
        )
        assert expected in str(result.err)

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize("name, expected", [("sqlmi6", "does not exist")])
    def test_arc_sql_mi_create_storage_class_logs(self, name, expected, az):
        result = az(
            "sql mi-arc create --storage-class-logs DNE -n {0} "
            "--k8s-namespace {1} --use-k8s".format(name, NAMESPACE)
        )
        assert expected in str(result.err)

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize("name, expected", [("sqlmi6", "does not exist")])
    def test_arc_sql_mi_create_storage_class_data(self, name, expected, az):
        result = az(
            "sql mi-arc create --storage-class-data DNE -n {0} "
            "--k8s-namespace {1} --use-k8s".format(name, NAMESPACE)
        )
        assert expected in str(result.err)

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize("name, expected", [("sqlmi6", "does not exist")])
    def test_arc_sql_mi_create_storage_class_datalogs(self, name, expected, az):
        result = az(
            "sql mi-arc create --storage-class-data DNE -n {0} "
            "--storage-class-logs DNE --k8s-namespace {1} --use-k8s".format(
                name, NAMESPACE
            )
        )
        assert expected in str(result.err)

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, expected",
        [("".join(["a"] * 61), "exceeds 60 character length limit")],
    )
    def test_arc_sql_mi_create_name_length(self, name, expected, az):
        result = az(
            "sql mi-arc create -n {0} --k8s-namespace {1} --use-k8s".format(
                name, NAMESPACE
            )
        )
        assert name in str(result.err)
        assert expected in str(result.err)

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, rd",
        [("sqlmird", "36"), ("sqlmird", "-1")],
    )
    def test_arc_sql_mi_create_rd_invalid(self, name, rd, az):
        try:
            az(
                "sql mi-arc create -n {0} --k8s-namespace {1} --use-k8s --retention-days {2}".format(
                    name, NAMESPACE, rd
                )
            )
            assert False, "Error was not thrown as expected"
        except SystemExit:
            pass

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, rd, expected", [("sqlmivalid1", "1", "Deployed")]
    )
    def test_arc_sql_mi_create_valid(self, name, rd, expected, az):
        result = az(
            "sql mi-arc create --no-wait -n {0} --k8s-namespace {1} --use-k8s"
            " --retention-days {2}".format(name, NAMESPACE, rd)
        )

        assert expected in str(result.out)

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize("storage_class", [STORAGE_CLASS])
    def test_sql_mi_model(self, storage_class):
        sq1 = SqlmiCustomResource()
        # Custom Resource Fields
        sq1.apiversion = "sqlmi/v1"
        sq1.kind = "sqlmi"
        sq1.metadata.name = "sqlmi-test"
        sq1.metadata.namespace = "test"
        sq1.metadata.resourceVersion = "11225500"
        sq1.metadata.uid = "aaaaa-bbbbb-cccc-1234"
        sq1.status.state = "Ready"
        sq1.status.endpoints = SqlmiCustomResource.Status.EndpointsStatus()
        sq1.status.endpoints.primary = "endpoint.notreal.com/sqlmi"
        sq1.spec.dev = False
        sq1.spec.services.primary.port = 25565
        sq1.spec.services.primary.serviceType = "endpoint"
        sq1.spec.storage.data.volumes = [
            VolumeClaim(className=storage_class, size="50Gi")
        ]
        sq1.spec.storage.logs.volumes = [
            VolumeClaim(className=storage_class, size="50Gi")
        ]
        sq1.spec.storage.backups.volumes = [
            VolumeClaim(className=storage_class, size="50Gi")
        ]
        sq1.spec.docker.registry = "msft_test_reg.123"
        sq1.spec.docker.repository = "msft.test.github.cloud.com"
        sq1.spec.docker.imageTag = "ttttttaaagggg"
        sq1.spec.docker.imagePullPolicy = "always"
        sq1.spec.storage.volumeClaimMounts = [
            {"volumeClaimName": "test1", "volumeType": "type1"},
            {"volumeClaimName": "test2", "volumeType": "type2"},
        ]

        # Sqlmi
        sq1.spec.type = "svc1-sqlmi"
        sq1.spec.storage.datalogs.volumes = [
            VolumeClaim(className=storage_class, size="50Gi")
        ]
        sq1.spec.scheduling.default.resources.requests.memory = "2Gi"
        sq1.spec.scheduling.default.resources.requests.cpu = "3"
        sq1.spec.scheduling.default.resources.limits.memory = KubeQuantity(
            "2Gi"
        )
        sq1.spec.scheduling.default.resources.limits.cpu = KubeQuantity("5")
        sq1.status.roles.sql.readyReplicas = 10
        sq1.status.endpoints.secondary = "secondary.service.endpoint"
        sq1.spec.backup.retentionPeriodInDays = 4

        # Do the test
        sq1_encoding = sq1.encode()
        sq2 = CustomResource.decode(SqlmiCustomResource, sq1_encoding)
        sq2_encoding = sq2.encode()

        assert sq1_encoding == sq2_encoding

        sq1_str = sq1.encodes()
        sq3 = CustomResource.decodes(SqlmiCustomResource, sq1_str)
        sq3_encoding = sq3.encode()

        assert sq3_encoding == sq1_encoding

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, replicas, sync_secondary_commit, expected",
        [
            ("sync-sql", "3", "2", "Deployed"),
            ("sync-sql", "2", "1", "Deployed"),
            ("sync-sql", "1", "-1", "Deployed"),
        ],
    )
    def test_arc_sql_mi_sync_secondary_commit_valid(
        self, name, replicas, sync_secondary_commit, expected, az
    ):
        result = az(
            "az sql mi-arc create --no-wait --dev --use-k8s",
            name=name,
            k8s_namespace=NAMESPACE,
            sync_secondary_to_commit=sync_secondary_commit,
            replicas=replicas,
        )

        print(result)
        assert expected in result.out

        # Clean up after test
        #
        az(
            "az sql mi-arc delete --use-k8s",
            name=name,
            k8s_namespace=NAMESPACE,
        )

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, replicas, sync_secondary_commit, expected",
        [
            ("sync-sql", "1", "2", "Error"),
            ("sync-sql", "2", "2", "Error"),
            ("sync-sql", "1", "a", "Error"),
        ],
    )
    def test_arc_sql_mi_sync_secondary_commit_invalid(
        self, name, replicas, sync_secondary_commit, expected, az
    ):
        try:
            az(
                "az sql mi-arc create --no-wait --dev --use-k8s",
                name=name,
                k8s_namespace=NAMESPACE,
                sync_secondary_to_commit=sync_secondary_commit,
                replicas=replicas,
            )
            assert False, "Error was not thrown as expected"
        except SystemExit:
            pass

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, replicas, expected",
        [
            ("sync-sql", "1", "Deployed"),
            ("sync-sql", "2", "Deployed"),
            ("sync-sql", "3", "Deployed"),
            ("sync-sql", None, "Deployed"),
        ],
    )
    def test_arc_sql_mi_sync_replicas_valid(self, name, replicas, expected, az):
        result = az(
            "az sql mi-arc create --no-wait --dev --use-k8s",
            name=name,
            k8s_namespace=NAMESPACE,
            replicas=replicas,
        )

        print(result)
        assert expected in result.out

        # Clean up after test
        #
        az(
            "az sql mi-arc delete --use-k8s",
            name=name,
            k8s_namespace=NAMESPACE,
        )

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, replicas, expected",
        [
            ("sync-sql", "0", "Error"),
            ("sync-sql", "a", "Error"),
            ("sync-sql", "4", "Error"),
        ],
    )
    def test_arc_sql_mi_replicas_invalid(self, name, replicas, expected, az):
        try:
            az(
                "az sql mi-arc create --no-wait --dev --use-k8s",
                name=name,
                k8s_namespace=NAMESPACE,
                replicas=replicas,
            )
            assert False, "Error was not thrown as expected"
        except SystemExit:
            pass
