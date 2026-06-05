# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

import json
import os
from sys import stdout
import pytest

VCR_RECORD_MODE = "once"  # options: None, once, all, rerecord


@pytest.mark.usefixtures("setup")
class TestsHostPropertiesSet(object):
    @pytest.fixture
    def setup(self):
        os.environ["AZDATA_USERNAME"] = "username"
        os.environ["AZDATA_PASSWORD"] = "Placeholder001"

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "machine_name, resource_group, value, exit_code",
        [
            ("ARCBOX-SQL", "arcee-test", "PAYG", 0),
            ("ARCBOX-SQL", "arcee-test", "Random", 1),
        ],
    )
    def test_license_type_host_property(
        self, machine_name, resource_group, value, exit_code, az
    ):
        result = az(
            "sql server-arc extension set",
            resource_group=resource_group,
            machine_name=machine_name,
            license_type=value,
        )

        assert result.exit_code == exit_code

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "machine_name, resource_group, value, exit_code",
        [
            ("ARCBOX-SQL", "arcee-test", "False", 0),
            ("ARCBOX-SQL", "arcee-test", "Random", 1),
        ],
    )
    def test_esu_type_host_property(
        self, machine_name, resource_group, value, exit_code, az
    ):
        result = az(
            "sql server-arc extension set",
            resource_group=resource_group,
            machine_name=machine_name,
            esu_enabled=value,
        )

        assert result.exit_code == exit_code

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "machine_name, resource_group, license_type, esu_enabled",
        [
            (
                "ARCBOX-SQL",
                "arcee-test",
                "LicenseOnly",
                "True",
            ),
        ],
    )
    def test_licenseType_esu_compatibilty(
        self, machine_name, resource_group, license_type, esu_enabled, az
    ):
        result = az(
            "sql server-arc extension set",
            resource_group=resource_group,
            machine_name=machine_name,
            license_type=license_type,
            esu_enabled=esu_enabled,
        )

        assert result.exit_code != 0
