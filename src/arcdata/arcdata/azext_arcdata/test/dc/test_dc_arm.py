# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

import json
import os
import pytest

VCR_RECORD_MODE = "once"  # options: None, once, all, rerecord


@pytest.mark.usefixtures("setup")
@pytest.mark.skip(reason="Long running")
class TestDataControllerARM(object):
    @pytest.fixture
    def setup(
        self,
        credentials,
        cluster_name,
        resource_group,
        custom_location,
        dc_name,
        subscription,
    ):
        os.environ["AZDATA_USERNAME"] = credentials[0]
        os.environ["AZDATA_PASSWORD"] = credentials[1]
        self.cluster_name = cluster_name
        self.resource_group = resource_group
        self.custom_location = custom_location
        self.dc_name = dc_name
        self.subscription = subscription

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "profile",
        [("azure-arc-aks-default-storage")],
    )
    def test_arcdata_dc_create_no_wait(self, az, profile):
        result = az(
            "az arcdata dc create --connectivity-mode direct --no-wait",
            profile=profile,
            name=self.dc_name,
            cluster_name=self.cluster_name,
            resource_group=self.resource_group,
            custom_location=self.custom_location,
            subscription=self.subscription,
        )

        assert result.exit_code == 0
        assert (
            f"The data controller '{self.dc_name}' "
            f"is being created" in result.out
        ), "Did not find output."

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    def test_arcdata_dc_status_show(self, az):
        result = az(
            "az arcdata dc status show",
            name=self.dc_name,
            resource_group=self.resource_group,
        )
        assert result.exit_code == 0
        result = json.loads(result.out)
        assert result["name"] == self.dc_name

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    def test_arcdata_dc_delete(self, az):
        result = az(
            "az arcdata dc delete --yes",
            name=self.dc_name,
            resource_group=self.resource_group,
        )
        assert result.exit_code == 0

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    def test_arcdata_dc_upgrade_hydrationrule(self, az):
        result = az(
            "az arcdata dc upgrade -v v1.8.0_2022-06-14",
            name=self.dc_name,
            resource_group=self.resource_group,
        )
        assert result.exit_code == 0
