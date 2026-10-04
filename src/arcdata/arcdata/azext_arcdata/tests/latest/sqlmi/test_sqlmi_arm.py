# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

import json
import os
import pytest

VCR_RECORD_MODE = "once"  # options: None, once, all, rerecord


@pytest.mark.usefixtures("setup")
@pytest.mark.skip(reason="Long running")
class TestSqlmiARM(object):
    @pytest.fixture
    def setup(
        self,
        credentials,
        resource_group,
        custom_location,
        location,
        mi_name,
        subscription,
    ):
        os.environ["AZDATA_USERNAME"] = credentials[0]
        os.environ["AZDATA_PASSWORD"] = credentials[1]
        self.resource_group = resource_group
        self.custom_location = custom_location
        self.location = location
        self.mi_name = mi_name
        self.mi_name_wait = f"{mi_name}w"
        self.subscription = subscription

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.slow
    def _test_sql_mi_arc_create(self, az):
        result = az(
            "az sql mi-arc create",
            name=self.mi_name_wait,
            resource_group=self.resource_group,
            custom_location=self.custom_location,
            location=self.location,
            subscription=self.subscription,
        )
        assert result.exit_code == 0
        mi = json.loads(result.out)
        assert mi["name"] == self.mi_name_wait

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.slow
    @pytest.mark.parametrize(
        "cores_request, cores_limit",
        [(1, 2)],
    )
    def _test_sql_mi_arc_update(self, az, cores_request, cores_limit):
        result = az(
            "az sql mi-arc update",
            name=self.mi_name_wait,
            cores_request=cores_request,
            cores_limit=cores_limit,
            resource_group=self.resource_group,
            subscription=self.subscription,
        )
        assert result.exit_code == 0
        mi = json.loads(result.out)
        assert mi["name"] == self.mi_name_wait

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    def test_sql_mi_arc_list(self, az):
        result = az(
            "az sql mi-arc list",
            resource_group=self.resource_group,
            subscription=self.subscription,
        )
        assert result.exit_code == 0
        result = json.loads(result.out)
        assert len(result) > 0
        found = False
        for mi in result:
            if mi["name"] == self.mi_name:
                found = True
                assert mi["properties"]["k8SRaw"]["status"]["state"] == "Ready"
        assert found

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    def test_sql_mi_arc_show(self, az):
        result = az(
            "az sql mi-arc show",
            name=self.mi_name,
            resource_group=self.resource_group,
            subscription=self.subscription,
        )
        assert result.exit_code == 0
        mi = json.loads(result.out)
        assert mi["properties"]["k8_s_raw"]["status"]["state"] == "Ready"

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    def test_sql_mi_arc_delete(self, az):
        result = az(
            "az sql mi-arc delete",
            name=self.mi_name,
            resource_group=self.resource_group,
            subscription=self.subscription,
        )
        assert result.exit_code == 0

    # --------------------------------------------------------------------------
    # Faster running tests for gci with the `--no-wait` argument
    # NOTE:
    # Since `--no-wait` returns right away you will have to first wait until
    # the state in `test_sql_mi_arc_create_no_wait` is "Ready" before recording:
    # - test_sql_mi_arc_update_no_wait
    # - test_sql_mi_arc_delete_no_wait
    # --------------------------------------------------------------------------

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    def test_sql_mi_arc_create_no_wait(self, az):
        result = az(
            "az sql mi-arc create --no-wait",
            name=self.mi_name,
            resource_group=self.resource_group,
            custom_location=self.custom_location,
            location=self.location,
            subscription=self.subscription,
        )
        assert result.exit_code == 0
        assert (
            f"The managed instance '{self.mi_name}' "
            f"is being created" in result.out
        ), "Did not find output."

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "cores_request, cores_limit",
        [(1, 2)],
    )
    def test_sql_mi_arc_update_no_wait(self, az, cores_request, cores_limit):
        result = az(
            "az sql mi-arc update --no-wait",
            name=self.mi_name,
            cores_request=cores_request,
            cores_limit=cores_limit,
            resource_group=self.resource_group,
            subscription=self.subscription,
        )
        assert result.exit_code == 0
        assert (
            f"The managed instance '{self.mi_name}' "
            f"is being updated" in result.out
        ), "Did not find output."
