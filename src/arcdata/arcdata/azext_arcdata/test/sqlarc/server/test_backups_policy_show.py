# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

import pytest
import os

VCR_RECORD_MODE = "once"  # options: None, once, all, rerecord


@pytest.mark.usefixtures("setup")
class Tests_backups_show(object):  # TODO CHANGE TO _backups_show
    @pytest.fixture
    def setup(self):
        os.environ["AZDATA_USERNAME"] = "username"
        os.environ["AZDATA_PASSWORD"] = "Placeholder001"

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, resource_group, expected",
        [
            (
                "DESKTOP-RRP62CV",
                "aagonzalez-easyup",
                "No backup policy has been set for this Sql Server instance",
            ),
            # (
            #    "DESKTOP-RRP62CV/FISCHERPRICE",
            #    "aagonzalez-easyup",
            #    "No backup policy has been set for this Sql Server instance",
            # ),
            (
                "DESKTOP-RRP62CV_FISCHERPRICE",
                "aagonzalez-easyup",
                "No backup policy has been set for this Sql Server instance",
            ),
        ],
    )
    def test_no_policy(self, name, resource_group, expected, az):
        result = az(
            "sql server-arc backups-policy show",
            name=name,
            resource_group=resource_group,
        )
        assert result.exit_code == 0
        assert expected in result.out

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, resource_group",
        [
            ("DESKTOP-RRP62CVss", "aagonzalez-easyup"),
            # ("DESKTOP-RRP62CV/FISCHERPRICEasd", "aagonzalez-easyup"),
            ("DESKTOP-RRP62CV_FISCHERPRICE", "aagonzalez-easyupasd"),
        ],
    )
    def test_invalid_inputs(self, name, resource_group, az):
        result = az(
            "sql server-arc backups-policy show",
            name=name,
            resource_group=resource_group,
        )
        assert result.exit_code == 1

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, resource_group, retention_days , full_backup_days, diff_backup_hours, tlog_backup_mins, instance_name",
        [
            (
                "DESKTOP-RRP62CV",
                "aagonzalez-easyup",
                7,
                7,
                12,
                5,
                "DESKTOP-RRP62CV",
            ),
            # (
            #    "DESKTOP-RRP62CV/FISCHERPRICE",
            #    "aagonzalez-easyup",
            #    3,
            #    2,
            #    12,
            #    5,
            #    "FISCHERPRICE",
            # ),
            (
                "DESKTOP-RRP62CV",
                "aagonzalez-easyup",
                32,
                7,
                24,
                15,
                "DESKTOP-RRP62CV",
            ),
            (
                "DESKTOP-RRP62CV",
                "aagonzalez-easyup",
                4,
                4,
                12,
                5,
                "DESKTOP-RRP62CV",
            ),
            (
                "DESKTOP-RRP62CV_FISCHERPRICE",
                "aagonzalez-easyup",
                2,
                3,
                12,
                55,
                "FISCHERPRICE",
            ),
            (
                "DESKTOP-RRP62CV",
                "aagonzalez-easyup",
                0,
                5,
                24,
                5,
                "DESKTOP-RRP62CV",
            ),
            (
                "DESKTOP-RRP62CV",
                "aagonzalez-easyup",
                7,
                7,
                24,
                5,
                "DESKTOP-RRP62CV",
            ),
        ],
    )
    def test_successful_inputs(
        self,
        name,
        resource_group,
        retention_days,
        full_backup_days,
        diff_backup_hours,
        tlog_backup_mins,
        instance_name,
        az,
    ):
        result = az(
            "sql server-arc backups-policy show",
            name=name,
            resource_group=resource_group,
        )
        assert result.exit_code == 0
        res = eval(result.out)
        assert diff_backup_hours == res["differentialBackupHours"]
        assert full_backup_days == res["fullBackupDays"]
        assert tlog_backup_mins == res["transactionLogBackupMinutes"]
        assert retention_days == res["retentionPeriodDays"]
        assert instance_name == res["instanceName"]

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, resource_group",
        [
            ("DESKTOP-RRP62CV", "aagonzalez-easyup"),
            # ("DESKTOP-RRP62CV/FISCHERPRICE", "aagonzalez-easyup"),
        ],
    )
    def test_invalid_licenses(self, name, resource_group, az):
        result = az(
            "sql server-arc backups-policy show",
            name=name,
            resource_group=resource_group,
        )
        assert result.exit_code == 1
