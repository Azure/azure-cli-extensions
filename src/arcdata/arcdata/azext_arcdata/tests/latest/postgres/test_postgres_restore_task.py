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
class TestPostgresRestoreTask(object):
    @pytest.fixture
    def setup(self, assets_path):
        os.environ["AZDATA_USERNAME"] = "username"
        os.environ["AZDATA_PASSWORD"] = "random-pwd"

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, expected",
        [("pg-ut00012", "created")],
    )
    def test_arc_postgres_restore(self, name, expected, az):
        result = az(
            f"postgres server-arc restore -n {name} -k {NAMESPACE} --source-server {name} --use-k8s --no-wait"
        )

        assert expected in result.out
