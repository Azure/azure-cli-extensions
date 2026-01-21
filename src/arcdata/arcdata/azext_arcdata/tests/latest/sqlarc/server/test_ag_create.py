# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

import os
import pytest

from azext_arcdata.vendored_sdks.arm_sdk.swagger.swagger_latest.models import (
    SqlServerAvailabilityGroupResource,
    SqlAvailabilityGroupReplicaResourceProperties,
)

VCR_RECORD_MODE = "once"  # options: None, once, all, rerecord


@pytest.mark.usefixtures("setup")
class TestsAvailabilityGroupCreate(object):
    @pytest.fixture
    def setup(self):
        os.environ["AZDATA_USERNAME"] = "username"
        os.environ["AZDATA_PASSWORD"] = "Placeholder001"

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "resource_group, availability_group ",
        [
            ("hh-sqldev01-rg", "ag1"),
        ],
    )
    def test_create_single_replica_ag(
        self, resource_group, availability_group, az
    ):
        replica_id = "/subscriptions/a5082b19-8a6e-4bc5-8fdd-8ef39dfebc39/resourceGroups/hh-sqldev01-rg/providers/Microsoft.AzureArcData/SqlServerInstances/sql01"
        mirroring_port = 5022
        database_name = "appdb01"

        result = az(
            "sql server-arc availability-group create ",
            name=availability_group,
            resource_group=resource_group,
            replica_ids=replica_id,
            databases=database_name,
            mirroring_port=mirroring_port,
        )

        assert result.exit_code == 0
        assert (
            result.out
            == f"Successfully created/altered availability group {availability_group}.\n"
        )

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "resource_group, availability_group ",
        [
            ("hh-sqldev01-rg", "ag1"),
        ],
    )
    def test_create_ag_with_listener(
        self, resource_group, availability_group, az
    ):
        replica_id = "/subscriptions/a5082b19-8a6e-4bc5-8fdd-8ef39dfebc39/resourceGroups/hh-sqldev01-rg/providers/Microsoft.AzureArcData/sqlServerInstances/sql01"
        mirroring_port = 5022
        database_name = "appdb01"
        listener_name = "test-listener"
        listener_port = 7777
        listener_ipv4_addresses = "192.168.0.50"
        listener_ipv4_masks = "255.255.255.0"

        result = az(
            "sql server-arc availability-group create ",
            name=availability_group,
            resource_group=resource_group,
            replica_ids=replica_id,
            databases=database_name,
            mirroring_port=mirroring_port,
            listener_name=listener_name,
            listener_port=listener_port,
            listener_ipv4_addresses=listener_ipv4_addresses,
            listener_ipv4_masks=listener_ipv4_masks,
        )

        assert result.exit_code == 0
        assert (
            result.out
            == f"Successfully created/altered availability group {availability_group}.\n"
        )

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "resource_group, availability_group ",
        [
            ("hh-sqldev01-rg", "ag1"),
        ],
    )
    def test_create_single_replica_ag_no_db(
        self, resource_group, availability_group, az
    ):
        replica_id = "/subscriptions/a5082b19-8a6e-4bc5-8fdd-8ef39dfebc39/resourceGroups/hh-sqldev01-rg/providers/Microsoft.AzureArcData/sqlServerInstances/sql01"
        mirroring_port = 5022

        result = az(
            "sql server-arc availability-group create ",
            name=availability_group,
            resource_group=resource_group,
            replica_ids=replica_id,
            mirroring_port=mirroring_port,
        )

        assert result.exit_code == 0
        assert (
            result.out
            == f"Successfully created/altered availability group {availability_group}.\n"
        )

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "resource_group, availability_group ",
        [
            ("hh-sqldev01-rg", "ag1"),
        ],
    )
    def test_create_ag_all_args(self, resource_group, availability_group, az):
        # all args except for endpoint login and cluster type, we have bugs that needs fixing
        # in the extension
        replica_id = "/subscriptions/a5082b19-8a6e-4bc5-8fdd-8ef39dfebc39/resourceGroups/hh-sqldev01-rg/providers/Microsoft.AzureArcData/sqlServerInstances/sql01"
        mirroring_port = 5022
        database_name = "appdb01"
        listener_name = "test-listener"
        listener_port = 9999
        listener_ipv4_addresses = "192.168.0.51"
        listener_ipv4_masks = "255.255.255.0"
        availability_mode = "ASYNCHRONOUS_COMMIT"
        failover_mode = "MANUAL"
        seeding_mode = "MANUAL"
        automated_backup_preference = "PRIMARY"
        failure_condition_level = 1
        health_check_timeout = 35000
        db_failover = "ON"
        dtc_support = "PER_DB"

        result = az(
            "sql server-arc availability-group create ",
            name=availability_group,
            resource_group=resource_group,
            replica_ids=replica_id,
            mirroring_port=mirroring_port,
            databases=database_name,
            listener_name=listener_name,
            listener_port=listener_port,
            listener_ipv4_addresses=listener_ipv4_addresses,
            listener_ipv4_masks=listener_ipv4_masks,
            availability_mode=availability_mode,
            failover_mode=failover_mode,
            seeding_mode=seeding_mode,
            automated_backup_preference=automated_backup_preference,
            failure_condition_level=failure_condition_level,
            health_check_timeout=health_check_timeout,
            db_failover=db_failover,
            dtc_support=dtc_support,
        )

        assert result.exit_code == 0
        assert (
            result.out
            == f"Successfully created/altered availability group {availability_group}.\n"
        )

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "resource_group, availability_group ",
        [
            ("hh-sqldev01-rg", "ag1"),
        ],
    )
    def test_create_ag_invalid_replica_id(
        self, resource_group, availability_group, az
    ):
        result = az(
            "sql server-arc availability-group create ",
            name=availability_group,
            resource_group=resource_group,
            replica_ids="/subscriptions/a5082b19-8a6e-4bc5-8fdd-8ef39dfebc39/resourceGroups/hh-sqldev01-rg/providers/Microsoft.AzureArcData/sqlServerInstances/sql3000",
            databases="appdb01",
            mirroring_port=5022,
            endpoint_login="FG\\Administrator",
            endpoint_auth_mode="WINDOWS_NEGOTIATE",
        )

        assert result.exit_code == 1
        assert "ResourceNotFound" in result.err.args[0].exc_msg

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "resource_group, availability_group ",
        [
            ("hh-sqldev01-rg", "ag1"),
        ],
    )
    def test_create_ag_invalid_login(
        self, resource_group, availability_group, az
    ):
        result = az(
            "sql server-arc availability-group create ",
            name=availability_group,
            resource_group=resource_group,
            replica_ids="/subscriptions/a5082b19-8a6e-4bc5-8fdd-8ef39dfebc39/resourceGroups/hh-sqldev01-rg/providers/Microsoft.AzureArcData/sqlServerInstances/sql01",
            databases="appdb01",
            mirroring_port=5022,
            endpoint_login="foo",
            endpoint_auth_mode="WINDOWS_NEGOTIATE",
        )

        assert result.exit_code == 1
        assert (
            "Failed to grant connect on endpoint" in result.err.args[0].exc_msg
        )

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "resource_group, availability_group ",
        [
            ("hh-sqldev01-rg", "ag1"),
        ],
    )
    def test_create_ag_db_already_in_ag(
        self, resource_group, availability_group, az
    ):
        result = az(
            "sql server-arc availability-group create ",
            name=availability_group,
            resource_group=resource_group,
            replica_ids="/subscriptions/a5082b19-8a6e-4bc5-8fdd-8ef39dfebc39/resourceGroups/hh-sqldev01-rg/providers/Microsoft.AzureArcData/sqlServerInstances/sql01",
            databases="db01",
            mirroring_port=5022,
        )

        assert result.exit_code == 1
        assert (
            "Failed to create availability group" in result.err.args[0].exc_msg
        )
