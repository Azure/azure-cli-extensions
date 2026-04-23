# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

import pytest
import os

VCR_RECORD_MODE = "once"  # options: None, once, all, rerecord


@pytest.mark.usefixtures("setup")
class Tests_str_show(object):
    @pytest.fixture
    def setup(self):
        os.environ["AZDATA_USERNAME"] = "username"
        os.environ["AZDATA_PASSWORD"] = "Placeholder001"

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name,server, resource_group",
        [
            ("MyDatabase", "LAPTOP-OIUS4TO4", "lawynn-dotnet8upgrade"),
        ],
    )
    def test_no_policy(self, name, server, resource_group, az):
        result = az(
            "sql db-arc backups-policy show",
            name=name,
            server=server,
            resource_group=resource_group,
        )
        assert result.exit_code == 0
        assert "No backup policy" in result.out

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, server, resource_group",
        [
            ("MyDatabase", "LAPTOP-OIUS4TO4S", "lawynn-dotnet8upgrade"),
            ("MyDatabase", "LAPTOP-OIUS4TO4", "aagonasdfzalasdez-easasdafyup"),
        ],
    )
    def test_invalid_inputs(self, name, server, resource_group, az):
        result = az(
            "sql db-arc backups-policy show",
            name=name,
            server=server,
            resource_group=resource_group,
        )
        assert result.exit_code == 1

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name,server, resource_group, retention_days, full_backup_days, diff_backup_hours, tlog_backup_mins, instance_name, database_name",
        [
            (
                "MyDatabase",
                "LAPTOP-OIUS4TO4",
                "lawynn-dotnet8upgrade",
                7,
                7,
                12,
                5,
                "LAPTOP-OIUS4TO4",
                "MyDatabase",
            )
        ],
    )
    def test_successful_inputs(
        self,
        name,
        server,
        resource_group,
        diff_backup_hours,
        tlog_backup_mins,
        full_backup_days,
        retention_days,
        instance_name,
        database_name,
        az,
    ):
        result = az(
            "sql db-arc backups-policy show",
            name=name,
            server=server,
            resource_group=resource_group,
        )
        assert result.exit_code == 0
        res = eval(result.out)
        assert diff_backup_hours == res["differentialBackupHours"]
        assert tlog_backup_mins == res["transactionLogBackupMinutes"]
        assert full_backup_days == res["fullBackupDays"]
        assert retention_days == res["retentionPeriodDays"]
        assert instance_name == res["instanceName"]
        assert database_name == res["databaseName"]
