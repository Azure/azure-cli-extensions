# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

import os
import pytest

VCR_RECORD_MODE = "once"  # options: None, once, all, rerecord

# Due to Paramtization making cassettes with invalid names we had to switch from paramterized unit tests singular unit tests
@pytest.mark.usefixtures("setup")
class Tests_backups_set(object):
    @pytest.fixture
    def setup(self):
        os.environ["AZDATA_USERNAME"] = "username"
        os.environ["AZDATA_PASSWORD"] = "Placeholder001"

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    def test_invalid_input_no_double_dash(
        self,
        az,
    ):
        self._invalid_test_helper(
            "lawynn-dotnet8Upgrade",
            "LAPTOP-OIUS4TO4",
            "MyDatabase",
            "両--佣1",
            None,
            'The database name "両--佣1" is invalid.',
            az,
        )

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    def test_invalid_input_no_slashes(
        self,
        az,
    ):
        self._invalid_test_helper(
            "lawynn-dotnet8Upgrade",
            "LAPTOP-OIUS4TO4",
            "MyDatabase",
            "This/is/Illegal1",
            None,
            'The database name "This/is/Illegal1" is invalid.',
            az,
        )

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    def test_invalid_input_no_random_unicode(
        self,
        az,
    ):
        self._invalid_test_helper(
            "lawynn-dotnet8Upgrade",
            "LAPTOP-OIUS4TO4",
            "MyDatabase",
            "NoEmojisAllowed😊1",
            None,
            'The database name "NoEmojisAllowed😊1" is invalid.',
            az,
        )

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    def test_invalid_inputs_no_resource_group_found(
        self,
        az,
    ):
        self._invalid_test_helper(
            "NoResourceFoundByThisName",
            "LAPTOP-OIUS4TO4",
            "MyDatabase",
            "uNIQUE",
            None,
            'Could not find resource group "NoResourceFoundByThisName".',
            az,
        )

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    def test_invalid_input_no_source_database_found(
        self,
        az,
    ):
        self._invalid_test_helper(
            "lawynn-dotnet8Upgrade",
            "LAPTOP-OIUS4TO4",
            "NoDatabasefound",
            "DONOTMAKE11",
            None,
            'Could not find a database called "NoDatabasefound" in the Sql Server Instance "LAPTOP-OIUS4TO4" in the resource group "lawynn-dotnet8Upgrade". For more details please go to https://aka.ms/ARMResourceNotFoundFix',
            az,
        )

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    def test_invalid_input_no_server_found(
        self,
        az,
    ):
        self._invalid_test_helper(
            "lawynn-dotnet8Upgrade",
            "NoServerFound",
            "MyDatabase",
            "DONOTMAKE21",
            None,
            'Could not find Sql Server instance "NoServerFound" in the resource group "lawynn-dotnet8Upgrade". For more details please go to https://aka.ms/ARMResourceNotFoundFix',
            az,
        )

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    def test_invalid_input_time_selected_in_future(
        self,
        az,
    ):
        self._invalid_test_helper(
            "lawynn-dotnet8Upgrade",
            "LAPTOP-OIUS4TO4",
            "MyDatabase",
            "DONOTMAKE31",
            "5134-10-15T23:48:44Z",
            "The selected time is invalid as it is currently set for the future. Given time: '5134-10-15 23:48:44+00:00' Current time:",
            az,
        )

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    def test_invalid_input_time_selected_older_than_backups(
        self,
        az,
    ):
        self._invalid_test_helper(
            "lawynn-dotnet8Upgrade",
            "LAPTOP-OIUS4TO4",
            "MyDatabase",
            "DONOTMAKE34",
            "2020-10-15T23:48:44Z",
            "The selected time is invalid as it is prior to the Last Full Backup. Given time: '2020-10-15 23:48:44+00:00' Last Full Backup time: ",
            az,
        )

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    def test_invalid_input_backups_disabled(
        self,
        az,
    ):
        self._invalid_test_helper(
            "lawynn-dotnet8Upgrade",
            "LAPTOP-OIUS4TO4",
            "MyDatabase",
            "DONOTMAKE234",
            None,
            "The backups policy is currently disabled on this SQL database.",
            az,
        )

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    def test_invalid_input_invalid_license(
        self,
        az,
    ):
        self._invalid_test_helper(
            "lawynn-dotnet8Upgrade",
            "LAPTOP-OIUS4TO4",
            "MyDatabase",
            "DONOTMAKE43",
            None,
            "not a valid license",
            az,
        )

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    def test_successful_inputs_time_unentered(
        self,
        az,
    ):
        result = az(
            "sql db-arc restore",
            name="MyDatabase",
            resource_group="lawynn-dotnet8Upgrade",
            server="LAPTOP-OIUS4TO4",
            dest_name="AA_G-d_te_st2e321tt",
            expect_failure=False,
        )
        assert result.exit_code == 0
        assert (
            "The restore request has successfully been sent to the Sql Database."
            in result.out
        )

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    def test_successful_inputs_unicode(
        self,
        az,
    ):
        result = az(
            "sql db-arc restore",
            name="MyDatabase",
            resource_group="lawynn-dotnet8Upgrade",
            server="LAPTOP-OIUS4TO4",
            dest_name="894t3両佣12t",
            time="2024-02-09T21:11:26Z",
            expect_failure=False,
        )
        assert result.exit_code == 0
        assert (
            "The restore request has successfully been sent to the Sql Database."
            in result.out
        )

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    def test_successful_inputs_time_entered(
        self,
        az,
    ):

        result = az(
            "sql db-arc restore",
            name="MyDatabase",
            resource_group="lawynn-dotnet8Upgrade",
            server="LAPTOP-OIUS4TO4",
            dest_name="anOriginalDatabaseName2",
            time="2024-02-09T21:11:26Z",
            expect_failure=False,
        )
        assert result.exit_code == 0
        assert (
            "The restore request has successfully been sent to the Sql Database."
            in result.out
        )

    def _invalid_test_helper(
        self, resource_group, server, source_db, dest_db, time, expected, az
    ):
        if time:
            result = az(
                "sql db-arc restore",
                name=source_db,
                resource_group=resource_group,
                server=server,
                dest_name=dest_db,
                time=time,
                expect_failure=True,
            )
        else:
            result = az(
                "sql db-arc restore",
                name=source_db,
                resource_group=resource_group,
                server=server,
                dest_name=dest_db,
                expect_failure=True,
            )
        assert result.exit_code == 1 or result.exit_code == 2
        assert expected in str(result.err)
