# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

import pytest
import os

VCR_RECORD_MODE = "once"  # options: None, once, all, rerecord


@pytest.mark.usefixtures("setup")
class Tests_backups_delete(object):  # TODO CHANGE TO _backups_delete
    @pytest.fixture
    def setup(self):
        os.environ["AZDATA_USERNAME"] = "username"
        os.environ["AZDATA_PASSWORD"] = "Placeholder001"

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, resource_group",
        [
            ("ArcBox-SQL", "aagonzalez-CI-Test-mk6"),
            # ("ArcBox-SQL/MSSQLSERVER01", "aagonzalez-CI-Test-mk6"),
        ],
    )
    def test_no_policy(self, name, resource_group, az):
        result = az(
            "sql server-arc backups-policy delete",
            name=name,
            resource_group=resource_group,
            yes="",
        )
        assert result.exit_code == 0
        assert (
            "There is no policy currently active on this Sql Server instance."
            in result.out
        )

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, resource_group",
        [
            ("ArcBox-SQLss", "aagonzalez-CI-Test-mk6"),
            ("ArcBox-SQL/MSSQLSERVER01asd", "aagonzalez-CI-Test-mk6"),
            ("ArcBox-SQL_MSSQLSERVER01", "aagonzalez-CI-Test-mk6asd"),
        ],
    )
    def test_invalid_inputs(self, name, resource_group, az):
        result = az(
            "sql server-arc backups-policy delete",
            name=name,
            resource_group=resource_group,
            yes="",
        )
        assert result.exit_code == 1

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, resource_group",
        [
            (
                "ArcBox-SQL",
                "aagonzalez-CI-Test-mk6",
            ),
            # (
            #    "ArcBox-SQL/MSSQLSERVER01",
            #    "aagonzalez-CI-Test-mk6",
            # ),
        ],
    )
    def test_successful_inputs(
        self,
        name,
        resource_group,
        az,
    ):
        result = az(
            "sql server-arc backups-policy delete",
            name=name,
            resource_group=resource_group,
            yes="",
        )
        assert result.exit_code == 0

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, resource_group",
        [
            ("ArcBox-SQL", "aagonzalez-CI-Test-mk6"),
            ("ArcBox-SQL/MSSQLSERVER01", "aagonzalez-CI-Test-mk6"),
        ],
    )
    def test_invalid_licenses(self, name, resource_group, az):
        result = az(
            "sql server-arc backups-policy delete",
            name=name,
            resource_group=resource_group,
            yes="",
        )
        assert result.exit_code == 1
