# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

import os
import time

import pytest

VCR_RECORD_MODE = "once"  # options: None, once, all, rerecord


@pytest.mark.usefixtures("setup")
class Tests_str_set(object):
    @pytest.fixture
    def setup(self):
        os.environ["AZDATA_USERNAME"] = "username"
        os.environ["AZDATA_PASSWORD"] = "Placeholder001"

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name,server, resource_group,str_retention_days , backup_days, diff_hours, tlog_mins",
        [
            (
                "MyDatabase",
                "LAPTOP-OIUS4TO4",
                "lawynn-dotnet8Upgrade",
                7,
                7,
                12,
                5,
            ),
            (
                "MyDatabase",
                "LAPTOP-OIUS4TO4",
                "lawynn-dotnet8Upgrade",
                0,
                5,
                24,
                5,
            ),
        ],
    )
    def test_successful_inputs(
        self,
        name,
        server,
        resource_group,
        str_retention_days,
        backup_days,
        diff_hours,
        tlog_mins,
        az,
    ):
        result = az(
            "sql db-arc backups-policy set",
            name=name,
            server=server,
            resource_group=resource_group,
            retention_days=str_retention_days,
            full_backup_days=backup_days,
            diff_backup_hours=diff_hours,
            tlog_backup_mins=tlog_mins,
        )
        assert result.exit_code == 0
        assert "The policy has successfully been sent to the Sql" in result.out

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, server, resource_group",
        [
            ("MyDatabase", "LAPTOP-OIUS4TO4", "lawynn-dotnet8Upgrade"),
        ],
    )
    def test_successful_inputs_default_policy(
        self,
        name,
        server,
        resource_group,
        az,
    ):
        result = az(
            "sql db-arc backups-policy set",
            name=name,
            server=server,
            resource_group=resource_group,
            default_policy="",
        )
        assert result.exit_code == 0
        assert "The policy has successfully been sent to the Sql" in result.out

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "name, server, resource_group,str_retention_days , backup_days, diff_hours, tlog_mins, def_policy, expected",
        [
            (
                "MyDatabase",
                "LAPTOP-OIUS4TO4",
                "lawynn-dotnet8Upgrade",
                60,
                7,
                12,
                5,
                False,
                "Value Error: 60 is an invalid value for argument",
            ),
            (
                "MyDatabase",
                "LAPTOP-OIUS4TO4",
                "lawynn-dotnet8Upgrade",
                -7,
                7,
                12,
                5,
                False,
                "Value Error: -7 is an invalid value for argument",
            ),
            (
                "MyDatabase",
                "LAPTOP-OIUS4TO4",
                "lawynn-dotnet8Upgrade",
                None,
                7,
                None,
                None,
                True,
                "You can either do --default-policy to use the default policy or setup a custom policy",
            ),
            (
                "MyDatabase",
                "LAPTOP-OIUS4TO4",
                "lawynn-dotnet8Upgrade",
                None,
                None,
                12,
                None,
                True,
                "You can either do --default-policy to use the default policy or setup a custom policy",
            ),
            (
                "MyDatabase",
                "LAPTOP-OIUS4TO4",
                "lawynn-dotnet8Upgrade",
                None,
                None,
                None,
                5,
                True,
                "You can either do --default-policy to use the default policy or setup a custom policy",
            ),
            (
                "MyDatabase",
                "LAPTOP-OIUS4TO4",
                "lawynn-dotnet8Upgrade",
                30,
                None,
                None,
                None,
                True,
                "You can either do --default-policy to use the default policy or setup a custom policy",
            ),
            (
                "MyDatabase",
                "LAPTOP-OIUS4TO4",
                "lawynn-dotnet8Upgrade",
                None,
                7,
                12,
                5,
                False,
                "Please enter all the following parameter(s): ",
            ),
            (
                "MyDatabase",
                "LAPTOP-OIUS4TO4",
                "lawynn-dotnet8Upgrade",
                30,
                None,
                12,
                5,
                False,
                "Please enter all the following parameter(s): ",
            ),
            (
                "MyDatabase",
                "LAPTOP-OIUS4TO4",
                "lawynn-dotnet8Upgrade",
                30,
                7,
                None,
                5,
                False,
                "Please enter all the following parameter(s): ",
            ),
            (
                "MyDatabase",
                "LAPTOP-OIUS4TO4",
                "lawynn-dotnet8Upgrade",
                30,
                7,
                12,
                None,
                False,
                "Please enter all the following parameter(s): ",
            ),
            (
                "MyDatabase",
                "LAPTOP-OIUS4TO4",
                "lawynn-dotnet8Upgrade",
                None,
                None,
                None,
                None,
                False,
                "Please enter all the following parameter(s): ",
            ),
            (
                "MyDatabase",
                "LAPTOP-OIUS4TO4",
                "lawynn-dotnet8Upgrade",
                30,
                None,
                None,
                None,
                False,
                "Please enter all the following parameter(s): ",
            ),
            (
                "MyDatabase",
                "LAPTOP-OIUS4TO4",
                "lawynn-LTRHdack-rg",
                7,
                7,
                12,
                5,
                False,
                "Could not find resource group",
            ),
            (
                "MyDatabase",
                "LAPTOP-OIUS4TO4asd",
                "lawynn-dotnet8Upgrade",
                10,
                7,
                12,
                5,
                False,
                "Could not find Sql Server instance",
            ),
            (
                "MyDatabaseash",
                "LAPTOP-OIUS4TO4",
                "lawynn-dotnet8Upgrade",
                10,
                7,
                12,
                5,
                False,
                "Could not find a database called",
            ),
        ],
    )
    def test_invalid_inputs(
        self,
        name,
        server,
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
                "sql db-arc backups-policy set",
                name=name,
                server=server,
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
                "sql db-arc backups-policy set",
                name=name,
                server=server,
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
        "name, server, resource_group, str_retention_days , backup_days, diff_hours, tlog_mins, expected",
        [
            (
                "MyDatabase",
                "LAPTOP-OIUS4TO4",
                "lawynn-dotnet8Upgrade",
                10,
                7,
                12,
                5,
                "not a valid license",
            )
        ],
    )
    def test_invalid_license(
        self,
        name,
        server,
        resource_group,
        str_retention_days,
        backup_days,
        diff_hours,
        tlog_mins,
        expected,
        az,
    ):
        result = az(
            "sql db-arc backups-policy set",
            name=name,
            server=server,
            resource_group=resource_group,
            retention_days=str_retention_days,
            full_backup_days=backup_days,
            diff_backup_hours=diff_hours,
            tlog_backup_mins=tlog_mins,
        )
        assert result.exit_code == 1
        assert expected in str(result.err)
