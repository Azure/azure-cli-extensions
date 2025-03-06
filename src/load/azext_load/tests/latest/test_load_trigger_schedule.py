# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_load.tests.latest.constants import LoadTestConstants
from azext_load.tests.latest.preparers import LoadTestResourcePreparer
from azure.cli.testsdk import (
    JMESPathCheck,
    ResourceGroupPreparer,
    ScenarioTest,
)
from knack.log import get_logger

logger = get_logger(__name__)

rg_params = {
    "name_prefix": "clitest-schedule-",
    "location": "eastus",
    "key": "resource_group",
    "parameter_name": "rg",
    "random_name_length": 30,
}
load_params = {
    "name_prefix": "clitest-schedule-",
    "location": "eastus",
    "key": "load_test_resource",
    "parameter_name": "load",
    "resource_group_key": "resource_group",
    "random_name_length": 30,
}

class LoadTestScenarioTriggerSchedule(ScenarioTest):
    def __init__(self, *args, **kwargs):
        super(LoadTestScenarioTriggerSchedule, self).__init__(*args, **kwargs)
        self.kwargs.update({"subscription_id": self.get_subscription_id()})
    
    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_create_trigger_schedule(self, rg, load):
        self.kwargs.update({
            "trigger_id": "test-trigger-id",
            "description": "Test trigger schedule",
            "display_name": "Test Trigger",
            "start_date_time": "2025-03-31T23:59:59Z",
            "recurrence_type": "Daily",
            "recurrence_interval": 1,
            "test_ids": "test-id-1"
        })

        checks = [
            JMESPathCheck("description", self.kwargs["description"]),
            JMESPathCheck("displayName", self.kwargs["display_name"]),
            JMESPathCheck("startDateTime", self.kwargs["start_date_time"]),
            JMESPathCheck("recurrence.frequency", self.kwargs["recurrence_type"]),
            JMESPathCheck("recurrence.interval", self.kwargs["recurrence_interval"]),
            JMESPathCheck("testIds[0]", self.kwargs["test_ids"]),
        ]

        self.cmd(
            'az load trigger schedule create '
            '--name {load_test_resource} '
            '--resource-group {resource_group} '
            '--trigger-id {trigger_id} '
            '--description "{description}" '
            '--display-name "{display_name}" '
            '--start-date-time {start_date_time} '
            '--recurrence-type {recurrence_type} '
            '--recurrence-interval {recurrence_interval} '
            '--test-ids {test_ids}',
            checks=checks,
        )

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_update_trigger_schedule(self, rg, load):
        self.kwargs.update({
            "trigger_id": "test-trigger-id",
            "description": "Updated test trigger schedule",
            "display_name": "Updated Test Trigger",
            "start_date_time": "2025-04-01T00:00:00Z",
            "recurrence_type": "Daily",
            "recurrence_interval": 2,
            "recurrence_week_days": "Monday",
            "test_ids": "test-id-1"
        })

        # Create initial trigger schedule
        self.cmd(
            'az load trigger schedule create '
            '--name {load_test_resource} '
            '--resource-group {resource_group} '
            '--trigger-id {trigger_id} '
            '--description "Initial description" '
            '--display-name "Initial Display Name" '
            '--start-date-time "2025-03-31T23:59:59Z" '
            '--recurrence-type {recurrence_type} '
            '--recurrence-interval 1 '
            '--test-ids {test_ids}'
        )

        self.kwargs.update({
            "recurrence_type": "Weekly",
            "recurrence_week_days": "Monday",
        })

        checks = [
            JMESPathCheck("description", self.kwargs["description"]),
            JMESPathCheck("displayName", self.kwargs["display_name"]),
            JMESPathCheck("startDateTime", self.kwargs["start_date_time"]),
            JMESPathCheck("recurrence.frequency", self.kwargs["recurrence_type"]),
            JMESPathCheck("recurrence.interval", self.kwargs["recurrence_interval"]),
            JMESPathCheck("recurrence.daysOfWeek[0]", self.kwargs["recurrence_week_days"]),
            JMESPathCheck("testIds[0]", self.kwargs["test_ids"]),
        ]

        self.cmd(
            'az load trigger schedule update '
            '--name {load_test_resource} '
            '--resource-group {resource_group} '
            '--trigger-id {trigger_id} '
            '--description "{description}" '
            '--display-name "{display_name}" '
            '--start-date-time {start_date_time} '
            '--recurrence-type {recurrence_type} '
            '--recurrence-interval {recurrence_interval} '
            '--recurrence-week-days {recurrence_week_days} '
            '--test-ids {test_ids}',
            checks=checks,
        )

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_list_trigger_schedules(self, rg, load):
        self.kwargs.update({
            "trigger_id": "test-trigger-id",
            "description": "Test trigger schedule",
            "display_name": "Test Trigger",
            "start_date_time": "2025-03-31T23:59:59Z",
            "recurrence_type": "Daily",
            "recurrence_interval": 1,
            "test_ids": "test-id-1"
        })

        # Create a trigger schedule
        self.cmd(
            'az load trigger schedule create '
            '--name {load_test_resource} '
            '--resource-group {resource_group} '
            '--trigger-id {trigger_id} '
            '--description "{description}" '
            '--display-name "{display_name}" '
            '--start-date-time {start_date_time} '
            '--recurrence-type {recurrence_type} '
            '--recurrence-interval {recurrence_interval} '
            '--test-ids {test_ids}'
        )

        checks = [
            JMESPathCheck("length(@)", 1),
            JMESPathCheck("[0].description", self.kwargs["description"]),
            JMESPathCheck("[0].displayName", self.kwargs["display_name"]),
            JMESPathCheck("[0].startDateTime", self.kwargs["start_date_time"]),
            JMESPathCheck("[0].recurrence.frequency", self.kwargs["recurrence_type"]),
            JMESPathCheck("[0].recurrence.interval", self.kwargs["recurrence_interval"]),
            JMESPathCheck("[0].testIds[0]", self.kwargs["test_ids"]),
        ]

        self.cmd(
            'az load trigger schedule list '
            '--name {load_test_resource} '
            '--resource-group {resource_group}',
            checks=checks,
        )

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_delete_trigger_schedule(self, rg, load):
        self.kwargs.update({
            "trigger_id": "test-trigger-id",
            "description": "Test trigger schedule",
            "display_name": "Test Trigger",
            "start_date_time": "2025-03-31T23:59:59Z",
            "recurrence_type": "Daily",
            "recurrence_interval": 1,
            "test_ids": "test-id-1"
        })

        # Create a trigger schedule
        self.cmd(
            'az load trigger schedule create '
            '--name {load_test_resource} '
            '--resource-group {resource_group} '
            '--trigger-id {trigger_id} '
            '--description "{description}" '
            '--display-name "{display_name}" '
            '--start-date-time {start_date_time} '
            '--recurrence-type {recurrence_type} '
            '--recurrence-interval {recurrence_interval} '
            '--test-ids {test_ids}'
        )

        # Delete the trigger schedule
        self.cmd(
            'az load trigger schedule delete '
            '--name {load_test_resource} '
            '--resource-group {resource_group} '
            '--trigger-id {trigger_id} '
            '--yes'
        )

        checks = [
            JMESPathCheck("length(@)", 0)
        ]

        self.cmd(
            'az load trigger schedule list '
            '--name {load_test_resource} '
            '--resource-group {resource_group}',
            checks=checks,
        )

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_pause_trigger_schedule(self, rg, load):
        self.kwargs.update({
            "trigger_id": "test-trigger-id",
            "description": "Test trigger schedule",
            "display_name": "Test Trigger",
            "start_date_time": "2025-03-31T23:59:59Z",
            "recurrence_type": "Daily",
            "recurrence_interval": 1,
            "test_ids": "test-id-1"
        })

        # Create a trigger schedule
        self.cmd(
            'az load trigger schedule create '
            '--name {load_test_resource} '
            '--resource-group {resource_group} '
            '--trigger-id {trigger_id} '
            '--description "{description}" '
            '--display-name "{display_name}" '
            '--start-date-time {start_date_time} '
            '--recurrence-type {recurrence_type} '
            '--recurrence-interval {recurrence_interval} '
            '--test-ids {test_ids}'
        )

        # Pause the trigger schedule
        self.cmd(
            'az load trigger schedule pause '
            '--name {load_test_resource} '
            '--resource-group {resource_group} '
            '--trigger-id {trigger_id}'
        )

        checks = [
            JMESPathCheck("state", "Paused")
        ]

        self.cmd(
            'az load trigger schedule show '
            '--name {load_test_resource} '
            '--resource-group {resource_group} '
            '--trigger-id {trigger_id}',
            checks=checks,
        )

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_enable_trigger_schedule(self, rg, load):
        self.kwargs.update({
            "trigger_id": "test-trigger-id",
            "description": "Test trigger schedule",
            "display_name": "Test Trigger",
            "start_date_time": "2025-03-31T23:59:59Z",
            "recurrence_type": "Daily",
            "recurrence_interval": 1,
            "test_ids": "test-id-1"
        })

        # Create a trigger schedule
        self.cmd(
            'az load trigger schedule create '
            '--name {load_test_resource} '
            '--resource-group {resource_group} '
            '--trigger-id {trigger_id} '
            '--description "{description}" '
            '--display-name "{display_name}" '
            '--start-date-time {start_date_time} '
            '--recurrence-type {recurrence_type} '
            '--recurrence-interval {recurrence_interval} '
            '--test-ids {test_ids}'
        )

        # Pause the trigger schedule
        self.cmd(
            'az load trigger schedule pause '
            '--name {load_test_resource} '
            '--resource-group {resource_group} '
            '--trigger-id {trigger_id}'
        )

        # Enable the trigger schedule
        self.cmd(
            'az load trigger schedule enable '
            '--name {load_test_resource} '
            '--resource-group {resource_group} '
            '--trigger-id {trigger_id}'
        )

        checks = [
            JMESPathCheck("state", "Active")
        ]

        self.cmd(
            'az load trigger schedule show '
            '--name {load_test_resource} '
            '--resource-group {resource_group} '
            '--trigger-id {trigger_id}',
            checks=checks,
        )