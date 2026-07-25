# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

import pytest
import os
import json
import sys

VCR_RECORD_MODE = "once"  # options: None, once, all, rerecord


@pytest.mark.skipif(
    sys.version_info < (3, 10), reason="requires python3.10 or higher"
)
@pytest.mark.usefixtures("setup")
class Tests_host_feature_flag_show(object):
    @pytest.fixture
    def setup(self):
        os.environ["AZDATA_USERNAME"] = "username"
        os.environ["AZDATA_PASSWORD"] = "Placeholder001"

    """ (
                "ARCBOX-SQL",
                "arcee-test",
                None,
                "No feature flags are set for this machine.",
            ),"""

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "machine_name, resource_group, feature_name, expected",
        [
            (
                "ARCBOX-SQL",
                "arcee-test",
                "LeastPrivilege",
                "Feature",
                # "Feature flag not found for LeastPrivilege.",
            ),
        ],
    )
    def test_feature_flag_show_no_ff_added(
        self, machine_name, resource_group, feature_name, expected, az
    ):
        if feature_name is not None:
            result = az(
                "sql server-arc extension feature-flag show",
                name=feature_name,
                resource_group=resource_group,
                machine_name=machine_name,
            )
        else:
            result = az(
                "sql server-arc extension feature-flag show",
                machine_name=machine_name,
                resource_group=resource_group,
            )
        assert result.exit_code == 0
        assert expected in result.out

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "machine_name, resource_group, feature_name",
        [
            (
                "ARCBOX-SQL",
                "arcee-test",
                "LeastPrivilege",
            ),
            (
                "ARCBOX-SQL",
                "arcee-test",
                None,
            ),
            (
                "ARCBOX-SQL",
                "arcee-test",
                "randomFeature",
            ),
        ],
    )
    def test_feature_flag_show_ff_added(
        self, machine_name, resource_group, feature_name, az
    ):

        if feature_name is not None:
            result = az(
                "sql server-arc extension feature-flag show",
                name=feature_name,
                resource_group=resource_group,
                machine_name=machine_name,
            )
        else:
            result = az(
                "sql server-arc extension feature-flag show",
                machine_name=machine_name,
                resource_group=resource_group,
            )
        assert result.exit_code == 0

        if isinstance(result.out, str) is False:
            expected = "Feature flag not found for {0}."
            assert expected.format(feature_name) in result.out
        else:
            if feature_name is not None:
                assert feature_name.lower() in result.out.lower()
            else:
                actual = json.loads(result.out)
                assert len(actual) == 2

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "machine_name, sql_server_arc_name, resource_group, feature_name, exit_code",
        [
            (
                "ARCBOX-SQL",
                "ARCBOX-SQL",
                "arcee-test",
                "RandomFeature",
                0,
            ),
            (
                "ARCBOX_SQL-1",
                "ARCBOX-SQL",
                "arcee-test",
                "RandomFeature",
                1,
            ),
        ],
    )
    def test_feature_flag_show_with_both_machine_and_sql_server_name(
        self,
        machine_name,
        sql_server_arc_name,
        resource_group,
        feature_name,
        exit_code,
        az,
    ):
        result = az(
            "sql server-arc extension feature-flag show",
            name=feature_name,
            sql_server_arc_name=sql_server_arc_name,
            machine_name=machine_name,
            resource_group=resource_group,
        )
        assert result.exit_code == exit_code

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "sql_server_arc_name, resource_group, feature_name, exit_code",
        [
            (
                "ARCBOX-SQL",
                "arcee-test",
                "RandomFeature",
                0,
            ),
            (
                "ARCBOX-SQL-1",
                "arcee-test",
                "RandomFeature",
                1,
            ),
        ],
    )
    def test_feature_flag_show_with_only_sql_server_name(
        self,
        sql_server_arc_name,
        resource_group,
        feature_name,
        exit_code,
        az,
    ):
        result = az(
            "sql server-arc extension feature-flag show",
            name=feature_name,
            sql_server_arc_name=sql_server_arc_name,
            resource_group=resource_group,
        )
        assert result.exit_code == exit_code
