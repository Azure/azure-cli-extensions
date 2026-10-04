# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

import datetime
import os
import time

import pytest
from azext_arcdata.vendored_sdks.kubernetes_sdk.models.custom_resource import CustomResource
from azext_arcdata.sqlmidb.constants import TASK_API_VERSION
from src.arcdata.arcdata.azext_arcdata.vendored_sdks.kubernetes_sdk.models.restore_cr_model import (
    SqlmiRestoreTaskCustomResource,
)

VCR_RECORD_MODE = "once"  # options: None, once, all, rerecord
NAMESPACE = "test"


@pytest.mark.usefixtures("setup")
class TestSqlmidb(object):
    @pytest.fixture
    def setup(self):
        os.environ["AZDATA_USERNAME"] = "username"
        os.environ["AZDATA_PASSWORD"] = "Placeholder001"

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, expected",
        [("sqlmi2", "")],
    )
    def test_arc_sql_midb_restore_backup(self, name, expected, az):
        az(
            "sql mi-arc create -n {0} --k8s-namespace {1} --use-k8s "
            "--no-wait".format(name, NAMESPACE)
        )
        result = az(
            "sql midb-arc restore --name {0} --managed-instance {1} "
            "--dest-name {2} --k8s-namespace {3} --use-k8s --no-wait".format(
                "test_database", name, "dest_database", NAMESPACE
            )
        )
        assert expected in str(result.out)
        az(
            "sql mi-arc delete -n {0} --k8s-namespace {1} --use-k8s".format(
                name, NAMESPACE
            )
        )

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, expected",
        [("sqlmi1", "'restorePoint' has invalid value")],
    )
    def test_arc_sql_midb_restore_time(self, name, expected, az):
        result = az(
            "sql midb-arc restore --name {0} --managed-instance {1}"
            " --dest-name {2} --k8s-namespace {3} --use-k8s --time '{4}'".format(
                "test_database",
                name,
                "dest_database",
                NAMESPACE,
                datetime.datetime.now().ctime(),
            )
        )
        assert expected in str(result.err)

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    def test_sql_mi_restore_task_model(self):
        sq1 = SqlmiRestoreTaskCustomResource()
        # Custom Resource Fields
        sq1.apiversion = "tasks.sql.arcdata.microsoft.com/" + TASK_API_VERSION
        sq1.kind = "SqlManagedInstanceRestoreTask"
        sq1.metadata.name = "sql01-restore-test"
        sq1.metadata.namespace = "test"
        sq1.spec.dev = False
        sq1.spec.source.name = "from-server"
        sq1.spec.source.database = "from-db"
        sq1.spec.destination.name = "to-server"
        sq1.spec.destination.database = "to-db"
        sq1.spec.restorePoint = "2021-08-24T019:00:00Z"
        sq1.spec.services.primary.serviceType = "endpoint"

        # Do the test
        sq1_encoding = sq1.encode()
        sq2 = CustomResource.decode(
            SqlmiRestoreTaskCustomResource, sq1_encoding
        )
        sq2_encoding = sq2.encode()

        assert sq1_encoding == sq2_encoding
        sq1_str = sq1.encodes()
        sq3 = CustomResource.decodes(SqlmiRestoreTaskCustomResource, sq1_str)
        sq3_encoding = sq3.encode()

        assert sq3_encoding == sq1_encoding
