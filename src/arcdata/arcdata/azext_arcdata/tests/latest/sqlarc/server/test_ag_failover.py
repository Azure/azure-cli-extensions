# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

import os
import sys
import pytest

VCR_RECORD_MODE = "once"  # options: None, once, all, rerecord


@pytest.mark.usefixtures("setup")
class TestsAvailabilityGroupFailover(object):
    @pytest.fixture
    def setup(self):
        os.environ["AZDATA_USERNAME"] = "username"
        os.environ["AZDATA_PASSWORD"] = "Placeholder001"

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "resource_group, server, availability_group ",
        [
            ("hh-arcee-test", "hh-sql-dev01", "hh_ag1"),
        ],
    )
    def test_unsuccessful_failover(
        self, resource_group, server, availability_group, az
    ):
        result = az(
            "sql server-arc availability-group failover "
            f"-n {availability_group} -g {resource_group} --server-name {server}",
        )
        assert result.exit_code != 0

    @pytest.mark.skipif(
        sys.version_info < (3, 10), reason="requires python3.10 or higher"
    )
    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "resource_group, server, availability_group ",
        [
            ("hh-arcee-test", "hh-sql-dev02", "hh_ag1"),
        ],
    )
    def test_successful_failover(
        self, resource_group, server, availability_group, az
    ):
        result = az(
            "sql server-arc availability-group failover "
            f"-n {availability_group} -g {resource_group} --server-name {server}",
        )
        assert result.exit_code == 0
        assert "Successfully requested availability group" in result.out
