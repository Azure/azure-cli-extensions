# --------------------------------------------------------------------------------------------
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

    def create_trigger_schedule(self, trigger_id, description, display_name, start_date_time, test_ids, recurrence_type=None, recurrence_interval=None, recurrence_week_days=None, recurrence_dates_in_month=None, recurrence_index=None, recurrence_cron_expression=None):
        cmd = [
            'az load trigger schedule create',
            '--name {load_test_resource}',
            '--resource-group {resource_group}',
            f'--trigger-id {trigger_id}',
            f'--description "{description}"',
            f'--display-name "{display_name}"',
            f'--start-date-time {start_date_time}',
            f'--test-ids {test_ids}'
        ]
        if recurrence_type:
            cmd.append(f'--recurrence-type {recurrence_type}')
        if recurrence_interval:
            cmd.append(f'--recurrence-interval {recurrence_interval}')
        if recurrence_week_days:
            cmd.append(f'--recurrence-week-days {recurrence_week_days}')
        if recurrence_dates_in_month:
            cmd.append(f'--recurrence-dates-in-month {recurrence_dates_in_month}')
        if recurrence_index:
            cmd.append(f'--recurrence-index {recurrence_index}')
        if recurrence_cron_expression:
            cmd.append(f'--recurrence-cron-exp "{recurrence_cron_expression}"')

        self.cmd(' '.join(cmd))

    def verify_trigger_schedule(self, trigger_id, description, display_name, start_date_time, test_ids, recurrence_type=None, recurrence_interval=None, recurrence_week_days=None, recurrence_dates_in_month=None, recurrence_index=None, recurrence_cron_expression=None):
        checks = [
            JMESPathCheck("description", description),
            JMESPathCheck("displayName", display_name),
            JMESPathCheck("startDateTime", start_date_time),
            JMESPathCheck("testIds[0]", test_ids),
        ]
        if recurrence_type:
            checks.append(JMESPathCheck("recurrence.frequency", recurrence_type))
        if recurrence_interval:
            checks.append(JMESPathCheck("recurrence.interval", recurrence_interval))
        if recurrence_week_days:
            week_days = recurrence_week_days.split()
            if recurrence_type == "Weekly":
                for i, day in enumerate(week_days):
                    checks.append(JMESPathCheck(f"recurrence.daysOfWeek[{i}]", day))
            else:
                for i, day in enumerate(week_days):
                    checks.append(JMESPathCheck(f"recurrence.weekDaysInMonth[{i}]", day))
        if recurrence_dates_in_month:
            dates_in_month = recurrence_dates_in_month.split()
            for i, date in enumerate(dates_in_month):
                checks.append(JMESPathCheck(f"recurrence.datesInMonth[{i}]", int(date)))
        if recurrence_index:
            checks.append(JMESPathCheck("recurrence.index", recurrence_index))
        if recurrence_cron_expression:
            checks.append(JMESPathCheck("recurrence.cronExpression", recurrence_cron_expression))

        self.cmd(
            'az load trigger schedule show '
            '--name {load_test_resource} '
            '--resource-group {resource_group} '
            f'--trigger-id {trigger_id}',
            checks=checks
        )

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_create_and_verify_trigger_schedules(self, rg, load):
        # Test Daily Recurrence
        self.create_trigger_schedule(
            trigger_id="test-trigger-id-daily",
            description="Test trigger schedule daily",
            display_name="Test Trigger Daily",
            start_date_time="2025-03-31T23:59:59Z",
            recurrence_type="Daily",
            recurrence_interval=1,
            test_ids="test-id-daily"
        )
        self.verify_trigger_schedule(
            trigger_id="test-trigger-id-daily",
            description="Test trigger schedule daily",
            display_name="Test Trigger Daily",
            start_date_time="2025-03-31T23:59:59Z",
            recurrence_type="Daily",
            recurrence_interval=1,
            test_ids="test-id-daily"
        )

        # Test Weekly Recurrence
        self.create_trigger_schedule(
            trigger_id="test-trigger-id-weekly",
            description="Test trigger schedule weekly",
            display_name="Test Trigger Weekly",
            start_date_time="2025-03-31T23:59:59Z",
            recurrence_type="Weekly",
            recurrence_interval=1,
            recurrence_week_days="Monday Tuesday",
            test_ids="test-id-weekly"
        )
        self.verify_trigger_schedule(
            trigger_id="test-trigger-id-weekly",
            description="Test trigger schedule weekly",
            display_name="Test Trigger Weekly",
            start_date_time="2025-03-31T23:59:59Z",
            recurrence_type="Weekly",
            recurrence_interval=1,
            recurrence_week_days="Monday Tuesday",
            test_ids="test-id-weekly"
        )

        # Test Monthly By Dates Recurrence
        self.create_trigger_schedule(
            trigger_id="test-trigger-id-monthly-dates",
            description="Test trigger schedule monthly by dates",
            display_name="Test Trigger Monthly By Dates",
            start_date_time="2025-03-31T23:59:59Z",
            recurrence_type="MonthlyByDates",
            recurrence_interval=1,
            recurrence_dates_in_month="1 15",
            test_ids="test-id-monthly-dates"
        )
        self.verify_trigger_schedule(
            trigger_id="test-trigger-id-monthly-dates",
            description="Test trigger schedule monthly by dates",
            display_name="Test Trigger Monthly By Dates",
            start_date_time="2025-03-31T23:59:59Z",
            recurrence_type="MonthlyByDates",
            recurrence_interval=1,
            recurrence_dates_in_month="1 15",
            test_ids="test-id-monthly-dates"
        )

        # Test Monthly By Days Recurrence
        self.create_trigger_schedule(
            trigger_id="test-trigger-id-monthly-days",
            description="Test trigger schedule monthly by days",
            display_name="Test Trigger Monthly By Days",
            start_date_time="2025-03-31T23:59:59Z",
            recurrence_type="MonthlyByDays",
            recurrence_interval=1,
            recurrence_week_days="Monday",
            recurrence_index=1,
            test_ids="test-id-monthly-days"
        )
        self.verify_trigger_schedule(
            trigger_id="test-trigger-id-monthly-days",
            description="Test trigger schedule monthly by days",
            display_name="Test Trigger Monthly By Days",
            start_date_time="2025-03-31T23:59:59Z",
            recurrence_type="MonthlyByDays",
            recurrence_interval=1,
            recurrence_week_days="Monday",
            recurrence_index=1,
            test_ids="test-id-monthly-days"
        )

        # Test Cron Recurrence
        self.create_trigger_schedule(
            trigger_id="test-trigger-id-cron",
            description="Test trigger schedule cron",
            display_name="Test Trigger Cron",
            start_date_time="2025-03-31T23:59:59Z",
            recurrence_type="Cron",
            recurrence_cron_expression="0 0 12 * *",
            test_ids="test-id-cron"
        )
        self.verify_trigger_schedule(
            trigger_id="test-trigger-id-cron",
            description="Test trigger schedule cron",
            display_name="Test Trigger Cron",
            start_date_time="2025-03-31T23:59:59Z",
            recurrence_type="Cron",
            recurrence_cron_expression="0 0 12 * *",
            test_ids="test-id-cron"
        )

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_update_trigger_schedule(self, rg, load):
        self.create_trigger_schedule(
            trigger_id="test-trigger-id",
            description="Initial description",
            display_name="Initial Display Name",
            start_date_time="2025-03-31T23:59:59Z",
            recurrence_type="Daily",
            recurrence_interval=1,
            test_ids="test-id-update"
        )

        self.kwargs.update({
            "trigger_id": "test-trigger-id",
            "description": "Updated test trigger schedule",
            "display_name": "Updated Test Trigger",
            "start_date_time": "2025-04-01T00:00:00Z",
            "recurrence_type": "Weekly",
            "recurrence_interval": 2,
            "recurrence_week_days": "Monday",
            "test_ids": "test-id-update"
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
        self.create_trigger_schedule(
            trigger_id="test-trigger-id",
            description="Test trigger schedule",
            display_name="Test Trigger",
            start_date_time="2025-03-31T23:59:59Z",
            recurrence_type="Daily",
            recurrence_interval=1,
            test_ids="test-id-list"
        )

        self.kwargs.update({
            "description": "Test trigger schedule",
            "display_name": "Test Trigger",
            "start_date_time": "2025-03-31T23:59:59Z",
            "recurrence_type": "Daily",
            "recurrence_interval": 1,
            "test_ids": "test-id-list"
        })

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
        self.create_trigger_schedule(
            trigger_id="test-trigger-id",
            description="Test trigger schedule",
            display_name="Test Trigger",
            start_date_time="2025-03-31T23:59:59Z",
            recurrence_type="Daily",
            recurrence_interval=1,
            test_ids="test-id-delete"
        )

        self.kwargs.update({
            "trigger_id": "test-trigger-id"
        })


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
        self.create_trigger_schedule(
            trigger_id="test-trigger-id",
            description="Test trigger schedule",
            display_name="Test Trigger",
            start_date_time="2025-03-31T23:59:59Z",
            recurrence_type="Daily",
            recurrence_interval=1,
            test_ids="test-id-pause"
        )

        self.kwargs.update({
            "trigger_id": "test-trigger-id"
        })

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
        self.create_trigger_schedule(
            trigger_id="test-trigger-id",
            description="Test trigger schedule",
            display_name="Test Trigger",
            start_date_time="2025-03-31T23:59:59Z",
            recurrence_type="Daily",
            recurrence_interval=1,
            test_ids="test-id-enable"
        )

        self.kwargs.update({
            "trigger_id": "test-trigger-id"
        })

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