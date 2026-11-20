# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

import json
import os
import pytest

VCR_RECORD_MODE = "once"  # options: None, once, all, rerecord


@pytest.mark.usefixtures("setup")
class TestsHostPropertiesShow(object):
    @pytest.fixture
    def setup(self):
        os.environ["AZDATA_USERNAME"] = "username"
        os.environ["AZDATA_PASSWORD"] = "Placeholder001"

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "machine_name, resource_group",
        [
            (
                "ARCBOX-SQL",
                "arcee-test",
            ),
        ],
    )
    def test_successful_inputs(self, machine_name, resource_group, az):
        result = az(
            "sql server-arc extension show",
            resource_group=resource_group,
            machine_name=machine_name,
        )

        expected_output = (
            "{'ExcludedSqlInstances': ['', 'Testing', 'Instance1', ' Instance2'], 'SqlManagement': {'IsEnabled': True}, "
            "'LicenseType': 'Paid', 'enableExtendedSecurityUpdates': True, "
            "'esuLastUpdatedTimestamp': '2024-01-25T09:31:35.543Z', 'FeatureFlags': "
            "[{'Name': 'flightfeature', 'Enable': True}, {'Name': 'LeastPrivilege', "
            "'Enable': True}], 'cloudprovider': 'N/A'}\n"
        )
        assert result.exit_code == 0
        assert expected_output == result.out

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "machine_name, resource_group",
        [
            (
                "random-SQL",
                "arcee-test",
            ),
            (
                "ARCBOX-SQL",
                "random-rg",
            ),
        ],
    )
    def test_invalid_inputs(self, machine_name, resource_group, az):
        result = az(
            "sql server-arc extension show",
            resource_group=resource_group,
            machine_name=machine_name,
            expect_failure=True,
        )
        assert result.exit_code != 0
