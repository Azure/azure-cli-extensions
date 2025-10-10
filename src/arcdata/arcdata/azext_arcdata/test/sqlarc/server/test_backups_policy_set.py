# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

import os
import time

import pytest

VCR_RECORD_MODE = "once"  # options: None, once, all, rerecord

@pytest.mark.skip(reason="Skipping this entire test suite due to vc and urllib and how the testsare witten.")
@pytest.mark.usefixtures("setup")
class Tests_backups_set(object):
    @pytest.fixture
    def setup(self):
        os.environ["AZDATA_USERNAME"] = "username"
        os.environ["AZDATA_PASSWORD"] = "Placeholder001"

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, resource_group,str_retention_days , backup_days, diff_hours, tlog_mins",
        [
            ("ARCBOX-SQL", "aagonzalez-ci-test-mk6", 7, 7, 12, 5),
            # ("ARCBOX-SQL/MSSQLSERVER01", "aagonzalez-ci-test-mk6", 3, 2, 12, 5),
            ("ARCBOX-SQL", "aagonzalez-ci-test-mk6", 32, 7, 24, 15),
            ("ARCBOX-SQL", "aagonzalez-ci-test-mk6", 4, 4, 12, 5),
            # (
            #    "ARCBOX-SQL_MSSQLSERVER01",
            #    "aagonzalez-ci-test-mk6",
            #    2,
            #    3,
            #    12,
            #    55,
            # ),
            ("ARCBOX-SQL", "aagonzalez-ci-test-mk6", 0, 5, 24, 5),
        ],
    )
    def test_successful_inputs(
        self,
        name,
        resource_group,
        str_retention_days,
        backup_days,
        diff_hours,
        tlog_mins,
        az,
    ):
        result = az(
            "sql server-arc backups-policy set",
            name=name,
            resource_group=resource_group,
            retention_days=str_retention_days,
            full_backup_days=backup_days,
            diff_backup_hours=diff_hours,
            tlog_backup_mins=tlog_mins,
        )
        assert result.exit_code == 0
        assert (
            "The policy has successfully been sent to the Sql Server instance"
            in result.out
        )

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, resource_group",
        [
            ("ARCBOX-SQL", "aagonzalez-ci-test-mk6"),
        ],
    )
    def test_successful_inputs_default_policy(
        self,
        name,
        resource_group,
        az,
    ):
        result = az(
            "sql server-arc backups-policy set",
            name=name,
            resource_group=resource_group,
            default_policy="",
        )
        assert result.exit_code == 0
        assert (
            "The policy has successfully been sent to the Sql Server instance"
            in result.out
        )

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, resource_group,str_retention_days , backup_days, diff_hours, tlog_mins, def_policy, expected",
        [
            (
                "ARCBOX-SQL",
                "aagonzalez-ci-test-mk6",
                60,
                7,
                12,
                5,
                False,
                "Value Error: 60 is an invalid value for argument",
            ),
            (
                "ARCBOX-SQL",
                "aagonzalez-ci-test-mk6",
                -7,
                7,
                12,
                5,
                False,
                "Value Error: -7 is an invalid value for argument",
            ),
            (
                "ARCBOX-SQL",
                "aagonzalez-ci-test-mk6",
                None,
                7,
                None,
                None,
                True,
                "You can either do --default-policy to use the default policy or setup a custom policy",
            ),
            (
                "ARCBOX-SQL",
                "aagonzalez-ci-test-mk6",
                None,
                None,
                12,
                None,
                True,
                "You can either do --default-policy to use the default policy or setup a custom policy",
            ),
            (
                "ARCBOX-SQL",
                "aagonzalez-ci-test-mk6",
                None,
                None,
                None,
                5,
                True,
                "You can either do --default-policy to use the default policy or setup a custom policy",
            ),
            (
                "ARCBOX-SQL",
                "aagonzalez-ci-test-mk6",
                30,
                None,
                None,
                None,
                True,
                "You can either do --default-policy to use the default policy or setup a custom policy",
            ),
            (
                "ARCBOX-SQL",
                "aagonzalez-ci-test-mk6",
                None,
                7,
                12,
                5,
                False,
                "Please enter all the following parameter(s): ",
            ),
            (
                "ARCBOX-SQL",
                "aagonzalez-ci-test-mk6",
                30,
                None,
                12,
                5,
                False,
                "Please enter all the following parameter(s): ",
            ),
            (
                "ARCBOX-SQL",
                "aagonzalez-ci-test-mk6",
                30,
                7,
                None,
                5,
                False,
                "Please enter all the following parameter(s): ",
            ),
            (
                "ARCBOX-SQL",
                "aagonzalez-ci-test-mk6",
                30,
                7,
                12,
                None,
                False,
                "Please enter all the following parameter(s): ",
            ),
            (
                "ARCBOX-SQL",
                "aagonzalez-ci-test-mk6",
                None,
                None,
                None,
                None,
                False,
                "Please enter all the following parameter(s): ",
            ),
            (
                "ARCBOX-SQL",
                "aagonzalez-ci-test-mk6",
                30,
                None,
                None,
                None,
                False,
                "Please enter all the following parameter(s): ",
            ),
            (
                "ARCBOX-SQL",
                "lawynn-LTRHdack-rg",
                7,
                7,
                12,
                5,
                False,
                "Could not find resource group",
            ),
            (
                "ARCBOX-SQLasd",
                "aagonzalez-ci-test-mk6",
                10,
                7,
                12,
                5,
                False,
                "Could not find Sql Server instance",
            ),
        ],
    )
    def test_invalid_inputs(
        self,
        name,
        resource_group,
        str_retention_days,
        backup_days,
        diff_hours,
        tlog_mins,
        def_policy,
        expected,
        az,
    ):
        if def_policy:
            result = az(
                "sql server-arc backups-policy set",
                name=name,
                resource_group=resource_group,
                retention_days=str_retention_days,
                full_backup_days=backup_days,
                diff_backup_hours=diff_hours,
                tlog_backup_mins=tlog_mins,
                default_policy="",
                expect_failure=True,
            )
        else:
            result = az(
                "sql server-arc backups-policy set",
                name=name,
                resource_group=resource_group,
                retention_days=str_retention_days,
                full_backup_days=backup_days,
                diff_backup_hours=diff_hours,
                tlog_backup_mins=tlog_mins,
                expect_failure=True,
            )
        assert result.exit_code == 1 or result.exit_code == 2
        assert expected in str(result.err)

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, resource_group,str_retention_days , backup_days, diff_hours, tlog_mins, expected",
        [
            (
                "ARCBOX-SQL",
                "aagonzalez-ci-test-mk6",
                10,
                7,
                12,
                5,
                "not a valid license",
            ),
            (
                "ARCBOX-SQL/MSSQLSERVER01",
                "aagonzalez-ci-test-mk6",
                10,
                7,
                12,
                5,
                "not a valid license",
            ),
        ],
    )
    def test_invalid_license(
        self,
        name,
        resource_group,
        str_retention_days,
        backup_days,
        diff_hours,
        tlog_mins,
        expected,
        az,
    ):
        result = az(
            "sql server-arc backups-policy set",
            name=name,
            resource_group=resource_group,
            retention_days=str_retention_days,
            full_backup_days=backup_days,
            diff_backup_hours=diff_hours,
            tlog_backup_mins=tlog_mins,
        )
        assert result.exit_code == 1
        assert expected in str(result.err)
