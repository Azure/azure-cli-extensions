# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

import os
import pytest
import sys

VCR_RECORD_MODE = "once"  # options: None, once, all, rerecord

@pytest.mark.skipif(sys.version_info < (3, 10), reason="requires python3.10 or higher")
@pytest.mark.usefixtures("setup")
class Tests_host_feature_flag_set(object):
    @pytest.fixture
    def setup(self):
        os.environ["AZDATA_USERNAME"] = "username"
        os.environ["AZDATA_PASSWORD"] = "Placeholder001"

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "machine_name, resource_group, feature_name, flag_value, expected",
        [
            (
                "ARCBOX-SQL",
                "arcee-test",
                "LeastPrivilege",
                True,
                "LeastPrivilege feature flag successfully updated to True",
            ),
            (
                "ARCBOX-SQL",
                "arcee-test",
                "LeastPrivilege",
                False,
                "LeastPrivilege feature flag successfully updated to False",
            ),
        ],
    )
    def test_successful_inputs(
        self,
        machine_name,
        resource_group,
        feature_name,
        flag_value,
        expected,
        az,
    ):
        result = az(
            "sql server-arc extension feature-flag set",
            name=feature_name,
            enable=flag_value,
            resource_group=resource_group,
            machine_name=machine_name,
        )
        assert result.exit_code == 0
        assert expected in result.out

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "machine_name, resource_group, feature_name, flag_value",
        [
            (
                "random-SQL",
                "arcee-test",
                "LeastPrivilege",
                True,
            ),
            (
                "ARCBOX-SQL",
                "random-rg",
                "NewFeature",
                True,
            ),
        ],
    )
    def test_invalid_inputs(
        self,
        machine_name,
        resource_group,
        feature_name,
        flag_value,
        az,
    ):
        result = az(
            "sql server-arc extension feature-flag set",
            name=feature_name,
            enable=flag_value,
            resource_group=resource_group,
            machine_name=machine_name,
            expect_failure=True,
        )
        assert result.exit_code == 1 or result.exit_code == 2

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "machine_name, sql_server_arc_name, resource_group, feature_name, flag_value, exit_code",
        [
            (
                "ARCBOX-SQL",
                "ARCBOX-SQL",
                "arcee-test-1",
                "LeastPrivilege",
                True,
                0,
            ),
            (
                "ARCBOX_SQL-1",
                "ARCBOX-SQL",
                "arcee-test-1",
                "LeastPrivilege",
                True,
                1,
            ),
        ],
    )
    def test_feature_flag_set_with_both_machine_and_sql_server_name(
        self,
        machine_name,
        sql_server_arc_name,
        resource_group,
        feature_name,
        flag_value,
        exit_code,
        az,
    ):
        result = az(
            "sql server-arc extension feature-flag set",
            name=feature_name,
            enable=flag_value,
            sql_server_arc_name=sql_server_arc_name,
            machine_name=machine_name,
            resource_group=resource_group,
        )
        assert result.exit_code == exit_code

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "sql_server_arc_name, resource_group, feature_name, flag_value, exit_code",
        [
            (
                "ARCBOX-SQL",
                "arcee-test-1",
                "LeastPrivilege",
                True,
                0,
            ),
            (
                "ARCBOX-SQL-1",
                "arcee-test-1",
                "LeastPrivilege",
                True,
                1,
            ),
        ],
    )
    def test_feature_flag_set_with_only_sql_server_name(
        self,
        sql_server_arc_name,
        resource_group,
        feature_name,
        exit_code,
        flag_value,
        az,
    ):
        result = az(
            "sql server-arc extension feature-flag set",
            name=feature_name,
            enable=flag_value,
            sql_server_arc_name=sql_server_arc_name,
            resource_group=resource_group,
        )
        assert result.exit_code == exit_code
