# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_load.tests.latest.constants import LoadTestTriggerConstants
from azext_load.tests.latest.preparers import LoadTestResourcePreparer
from azure.cli.testsdk import (
    JMESPathCheck,
    ResourceGroupPreparer,
    ScenarioTest,
)
from knack.log import get_logger
from azure.cli.core.azclierror import InvalidArgumentValueError

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
            cmd.append(f'--recurrence-dates {recurrence_dates_in_month}')
        if recurrence_index:
            cmd.append(f'--recurrence-index {recurrence_index}')
        if recurrence_cron_expression:
            cmd.append(f'--recurrence-cron-exp "{recurrence_cron_expression}"')

        self.cmd(' '.join(cmd))

    def verify_trigger_schedule(self, trigger_id, description, display_name, test_ids, start_date_time=None, recurrence_type=None, recurrence_interval=None, recurrence_week_days=None, recurrence_dates_in_month=None, recurrence_index=None, recurrence_cron_expression=None):
        checks = [
            JMESPathCheck("description", description),
            JMESPathCheck("displayName", display_name),
            JMESPathCheck("testIds[0]", test_ids),
        ]
        if recurrence_type:
            checks.append(JMESPathCheck("recurrence.frequency", recurrence_type))
        if recurrence_interval:
            checks.append(JMESPathCheck("recurrence.interval", recurrence_interval))
        if start_date_time:
            checks.append(JMESPathCheck("startDateTime", start_date_time))
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
            trigger_id=LoadTestTriggerConstants.DAILY_TRIGGER_ID,
            description=LoadTestTriggerConstants.DAILY_DESCRIPTION,
            display_name=LoadTestTriggerConstants.DAILY_DISPLAY_NAME,
            start_date_time=LoadTestTriggerConstants.CURRENT_DATE_TIME,
            recurrence_type=LoadTestTriggerConstants.DAILY_RECURRENCE_TYPE,
            recurrence_interval=LoadTestTriggerConstants.DAILY_RECURRENCE_INTERVAL,
            test_ids=LoadTestTriggerConstants.DAILY_TEST_IDS
        )
        self.verify_trigger_schedule(
            trigger_id=LoadTestTriggerConstants.DAILY_TRIGGER_ID,
            description=LoadTestTriggerConstants.DAILY_DESCRIPTION,
            display_name=LoadTestTriggerConstants.DAILY_DISPLAY_NAME,
            recurrence_type=LoadTestTriggerConstants.DAILY_RECURRENCE_TYPE,
            recurrence_interval=LoadTestTriggerConstants.DAILY_RECURRENCE_INTERVAL,
            test_ids=LoadTestTriggerConstants.DAILY_TEST_IDS
        )

        # Test Weekly Recurrence
        self.create_trigger_schedule(
            trigger_id=LoadTestTriggerConstants.WEEKLY_TRIGGER_ID,
            description=LoadTestTriggerConstants.WEEKLY_DESCRIPTION,
            display_name=LoadTestTriggerConstants.WEEKLY_DISPLAY_NAME,
            start_date_time=LoadTestTriggerConstants.CURRENT_DATE_TIME,
            recurrence_type=LoadTestTriggerConstants.WEEKLY_RECURRENCE_TYPE,
            recurrence_interval=LoadTestTriggerConstants.WEEKLY_RECURRENCE_INTERVAL,
            recurrence_week_days=LoadTestTriggerConstants.WEEKLY_RECURRENCE_DAYS,
            test_ids=LoadTestTriggerConstants.WEEKLY_TEST_IDS
        )
        self.verify_trigger_schedule(
            trigger_id=LoadTestTriggerConstants.WEEKLY_TRIGGER_ID,
            description=LoadTestTriggerConstants.WEEKLY_DESCRIPTION,
            display_name=LoadTestTriggerConstants.WEEKLY_DISPLAY_NAME,
            recurrence_type=LoadTestTriggerConstants.WEEKLY_RECURRENCE_TYPE,
            recurrence_interval=LoadTestTriggerConstants.WEEKLY_RECURRENCE_INTERVAL,
            recurrence_week_days=LoadTestTriggerConstants.WEEKLY_RECURRENCE_DAYS,
            test_ids=LoadTestTriggerConstants.WEEKLY_TEST_IDS
        )

        # Test Monthly By Dates Recurrence
        self.create_trigger_schedule(
            trigger_id=LoadTestTriggerConstants.MONTHLY_DATES_TRIGGER_ID,
            description=LoadTestTriggerConstants.MONTHLY_DATES_DESCRIPTION,
            display_name=LoadTestTriggerConstants.MONTHLY_DATES_DISPLAY_NAME,
            start_date_time=LoadTestTriggerConstants.CURRENT_DATE_TIME,
            recurrence_type=LoadTestTriggerConstants.MONTHLY_DATES_RECURRENCE_TYPE,
            recurrence_interval=LoadTestTriggerConstants.MONTHLY_DATES_RECURRENCE_INTERVAL,
            recurrence_dates_in_month=LoadTestTriggerConstants.MONTHLY_DATES_RECURRENCE_DATES_IN_MONTH,
            test_ids=LoadTestTriggerConstants.MONTHLY_DATES_TEST_IDS
        )
        self.verify_trigger_schedule(
            trigger_id=LoadTestTriggerConstants.MONTHLY_DATES_TRIGGER_ID,
            description=LoadTestTriggerConstants.MONTHLY_DATES_DESCRIPTION,
            display_name=LoadTestTriggerConstants.MONTHLY_DATES_DISPLAY_NAME,
            recurrence_type=LoadTestTriggerConstants.MONTHLY_DATES_RECURRENCE_TYPE,
            recurrence_interval=LoadTestTriggerConstants.MONTHLY_DATES_RECURRENCE_INTERVAL,
            recurrence_dates_in_month=LoadTestTriggerConstants.MONTHLY_DATES_RECURRENCE_DATES_IN_MONTH,
            test_ids=LoadTestTriggerConstants.MONTHLY_DATES_TEST_IDS
        )

        # Test Monthly By Days Recurrence
        self.create_trigger_schedule(
            trigger_id=LoadTestTriggerConstants.MONTHLY_DAYS_TRIGGER_ID,
            description=LoadTestTriggerConstants.MONTHLY_DAYS_DESCRIPTION,
            display_name=LoadTestTriggerConstants.MONTHLY_DAYS_DISPLAY_NAME,
            start_date_time=LoadTestTriggerConstants.CURRENT_DATE_TIME,
            recurrence_type=LoadTestTriggerConstants.MONTHLY_DAYS_RECURRENCE_TYPE,
            recurrence_interval=LoadTestTriggerConstants.MONTHLY_DAYS_RECURRENCE_INTERVAL,
            recurrence_week_days=LoadTestTriggerConstants.MONTHLY_DAYS_RECURRENCE_WEEK_DAYS,
            recurrence_index=LoadTestTriggerConstants.MONTHLY_DAYS_RECURRENCE_INDEX,
            test_ids=LoadTestTriggerConstants.MONTHLY_DAYS_TEST_IDS
        )
        self.verify_trigger_schedule(
            trigger_id=LoadTestTriggerConstants.MONTHLY_DAYS_TRIGGER_ID,
            description=LoadTestTriggerConstants.MONTHLY_DAYS_DESCRIPTION,
            display_name=LoadTestTriggerConstants.MONTHLY_DAYS_DISPLAY_NAME,
            recurrence_type=LoadTestTriggerConstants.MONTHLY_DAYS_RECURRENCE_TYPE,
            recurrence_interval=LoadTestTriggerConstants.MONTHLY_DAYS_RECURRENCE_INTERVAL,
            recurrence_week_days=LoadTestTriggerConstants.MONTHLY_DAYS_RECURRENCE_WEEK_DAYS,
            recurrence_index=LoadTestTriggerConstants.MONTHLY_DAYS_RECURRENCE_INDEX,
            test_ids=LoadTestTriggerConstants.MONTHLY_DAYS_TEST_IDS
        )

        # Test Cron Recurrence
        self.create_trigger_schedule(
            trigger_id=LoadTestTriggerConstants.CRON_TRIGGER_ID,
            description=LoadTestTriggerConstants.CRON_DESCRIPTION,
            display_name=LoadTestTriggerConstants.CRON_DISPLAY_NAME,
            start_date_time=LoadTestTriggerConstants.CURRENT_DATE_TIME,
            recurrence_type=LoadTestTriggerConstants.CRON_RECURRENCE_TYPE,
            recurrence_cron_expression=LoadTestTriggerConstants.CRON_RECURRENCE_CRON_EXPRESSION,
            test_ids=LoadTestTriggerConstants.CRON_TEST_IDS
        )
        self.verify_trigger_schedule(
            trigger_id=LoadTestTriggerConstants.CRON_TRIGGER_ID,
            description=LoadTestTriggerConstants.CRON_DESCRIPTION,
            display_name=LoadTestTriggerConstants.CRON_DISPLAY_NAME,
            recurrence_type=LoadTestTriggerConstants.CRON_RECURRENCE_TYPE,
            recurrence_cron_expression=LoadTestTriggerConstants.CRON_RECURRENCE_CRON_EXPRESSION,
            test_ids=LoadTestTriggerConstants.CRON_TEST_IDS
        )

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_update_trigger_schedule(self, rg, load):
        # Create the trigger schedule with Daily recurrence
        self.create_trigger_schedule(
            trigger_id=LoadTestTriggerConstants.UPDATE_TRIGGER_ID,
            description=LoadTestTriggerConstants.UPDATE_DESCRIPTION,
            display_name=LoadTestTriggerConstants.UPDATE_DISPLAY_NAME,
            start_date_time=LoadTestTriggerConstants.CURRENT_DATE_TIME,
            recurrence_type=LoadTestTriggerConstants.DAILY_RECURRENCE_TYPE,
            recurrence_interval=LoadTestTriggerConstants.RECURRENCE_INTERVAL_ONE,
            test_ids=LoadTestTriggerConstants.UPDATE_TEST_IDS
        )

        self.kwargs.update({
            "trigger_id": LoadTestTriggerConstants.UPDATE_TRIGGER_ID,
            "description": LoadTestTriggerConstants.UPDATE_DESCRIPTION,
            "display_name": LoadTestTriggerConstants.UPDATE_DISPLAY_NAME,
            "start_date_time": LoadTestTriggerConstants.CURRENT_DATE_TIME,
            "recurrence_type": LoadTestTriggerConstants.WEEKLY_RECURRENCE_TYPE,
            "recurrence_interval": LoadTestTriggerConstants.WEEKLY_RECURRENCE_INTERVAL,
            "recurrence_week_days": LoadTestTriggerConstants.WEEKLY_RECURRENCE_DAYS,
            "test_ids": LoadTestTriggerConstants.UPDATE_TEST_IDS
        })

        checks = [
            JMESPathCheck("description", self.kwargs["description"]),
            JMESPathCheck("displayName", self.kwargs["display_name"]),
            JMESPathCheck("recurrence.frequency", self.kwargs["recurrence_type"]),
            JMESPathCheck("recurrence.interval", self.kwargs["recurrence_interval"]),
            JMESPathCheck("recurrence.daysOfWeek[0]", self.kwargs["recurrence_week_days"]),
            JMESPathCheck("testIds[0]", self.kwargs["test_ids"]),
        ]

        # Update the trigger schedule to weekly recurrence
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
            trigger_id=LoadTestTriggerConstants.LIST_TRIGGER_ID,
            description=LoadTestTriggerConstants.LIST_DESCRIPTION,
            display_name=LoadTestTriggerConstants.LIST_DISPLAY_NAME,
            start_date_time=LoadTestTriggerConstants.CURRENT_DATE_TIME,
            recurrence_type=LoadTestTriggerConstants.DAILY_RECURRENCE_TYPE,
            recurrence_interval=LoadTestTriggerConstants.RECURRENCE_INTERVAL_ONE,
            test_ids=LoadTestTriggerConstants.LIST_TEST_IDS
        )

        self.kwargs.update({
            "description": LoadTestTriggerConstants.LIST_DESCRIPTION,
            "display_name": LoadTestTriggerConstants.LIST_DISPLAY_NAME,
            "recurrence_type": LoadTestTriggerConstants.DAILY_RECURRENCE_TYPE,
            "recurrence_interval": LoadTestTriggerConstants.RECURRENCE_INTERVAL_ONE,
            "test_ids": LoadTestTriggerConstants.LIST_TEST_IDS
        })

        checks = [
            JMESPathCheck("length(@)", 1),
            JMESPathCheck("[0].description", self.kwargs["description"]),
            JMESPathCheck("[0].displayName", self.kwargs["display_name"]),
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
            trigger_id=LoadTestTriggerConstants.DELETE_TRIGGER_ID,
            description=LoadTestTriggerConstants.DELETE_DESCRIPTION,
            display_name=LoadTestTriggerConstants.DELETE_DISPLAY_NAME,
            start_date_time=LoadTestTriggerConstants.CURRENT_DATE_TIME,
            recurrence_type=LoadTestTriggerConstants.DAILY_RECURRENCE_TYPE,
            recurrence_interval=LoadTestTriggerConstants.RECURRENCE_INTERVAL_ONE,
            test_ids=LoadTestTriggerConstants.DELETE_TEST_IDS
        )

        self.kwargs.update({
            "trigger_id": LoadTestTriggerConstants.DELETE_TRIGGER_ID
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
            trigger_id=LoadTestTriggerConstants.PAUSE_TRIGGER_ID,
            description=LoadTestTriggerConstants.PAUSE_DESCRIPTION,
            display_name=LoadTestTriggerConstants.PAUSE_DISPLAY_NAME,
            start_date_time=LoadTestTriggerConstants.CURRENT_DATE_TIME,
            recurrence_type=LoadTestTriggerConstants.DAILY_RECURRENCE_TYPE,
            recurrence_interval=LoadTestTriggerConstants.RECURRENCE_INTERVAL_ONE,
            test_ids=LoadTestTriggerConstants.PAUSE_TEST_IDS
        )

        self.kwargs.update({
            "trigger_id": LoadTestTriggerConstants.PAUSE_TRIGGER_ID
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
            trigger_id=LoadTestTriggerConstants.ENABLE_TRIGGER_ID,
            description=LoadTestTriggerConstants.ENABLE_DESCRIPTION,
            display_name=LoadTestTriggerConstants.ENABLE_DISPLAY_NAME,
            start_date_time=LoadTestTriggerConstants.CURRENT_DATE_TIME,
            recurrence_type=LoadTestTriggerConstants.DAILY_RECURRENCE_TYPE,
            recurrence_interval=LoadTestTriggerConstants.RECURRENCE_INTERVAL_ONE,
            test_ids=LoadTestTriggerConstants.ENABLE_TEST_IDS
        )

        self.kwargs.update({
            "trigger_id": LoadTestTriggerConstants.ENABLE_TRIGGER_ID
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


    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_create_trigger_schedule_invalid_cases(self, rg, load):
        # Test invalid daily recurrence with extra parameters
        with self.assertRaises(InvalidArgumentValueError):
            self.create_trigger_schedule(
                trigger_id=LoadTestTriggerConstants.INVALID_DAILY_TRIGGER_ID,
                description=LoadTestTriggerConstants.DAILY_DESCRIPTION,
                display_name=LoadTestTriggerConstants.DAILY_DISPLAY_NAME,
                start_date_time=LoadTestTriggerConstants.CURRENT_DATE_TIME,
                recurrence_type=LoadTestTriggerConstants.DAILY_RECURRENCE_TYPE,
                recurrence_interval=LoadTestTriggerConstants.RECURRENCE_INTERVAL_ONE,
                recurrence_week_days=LoadTestTriggerConstants.WEEKLY_RECURRENCE_DAYS,  # Invalid parameter for daily recurrence
                test_ids=LoadTestTriggerConstants.DAILY_TEST_IDS
            )

        # Test invalid weekly recurrence without required parameters
        with self.assertRaises(InvalidArgumentValueError):
            self.create_trigger_schedule(
                trigger_id=LoadTestTriggerConstants.INVALID_WEEKLY_TRIGGER_ID,
                description=LoadTestTriggerConstants.WEEKLY_DESCRIPTION,
                display_name=LoadTestTriggerConstants.WEEKLY_DISPLAY_NAME,
                start_date_time=LoadTestTriggerConstants.CURRENT_DATE_TIME,
                recurrence_type=LoadTestTriggerConstants.WEEKLY_RECURRENCE_TYPE,
                recurrence_interval=LoadTestTriggerConstants.WEEKLY_RECURRENCE_INTERVAL,
                test_ids=LoadTestTriggerConstants.WEEKLY_TEST_IDS
            )

        # Test invalid monthly by dates recurrence with extra parameters
        with self.assertRaises(InvalidArgumentValueError):
            self.create_trigger_schedule(
                trigger_id=LoadTestTriggerConstants.INVALID_MONTHLY_DATES_TRIGGER_ID,
                description=LoadTestTriggerConstants.MONTHLY_DATES_DESCRIPTION,
                display_name=LoadTestTriggerConstants.MONTHLY_DATES_DISPLAY_NAME,
                start_date_time=LoadTestTriggerConstants.CURRENT_DATE_TIME,
                recurrence_type=LoadTestTriggerConstants.MONTHLY_DATES_RECURRENCE_TYPE,
                recurrence_interval=LoadTestTriggerConstants.MONTHLY_DATES_RECURRENCE_INTERVAL,
                recurrence_dates_in_month=LoadTestTriggerConstants.MONTHLY_DATES_RECURRENCE_DATES_IN_MONTH,
                recurrence_week_days=LoadTestTriggerConstants.MONTHLY_DAYS_RECURRENCE_WEEK_DAYS,  # Invalid parameter for monthly by dates recurrence
                test_ids=LoadTestTriggerConstants.MONTHLY_DATES_TEST_IDS
            )

        # Test invalid monthly by days recurrence without required parameters
        with self.assertRaises(InvalidArgumentValueError):
            self.create_trigger_schedule(
                trigger_id=LoadTestTriggerConstants.INVALID_MONTHLY_DAYS_TRIGGER_ID,
                description=LoadTestTriggerConstants.MONTHLY_DAYS_DESCRIPTION,
                display_name=LoadTestTriggerConstants.MONTHLY_DAYS_DISPLAY_NAME,
                start_date_time=LoadTestTriggerConstants.CURRENT_DATE_TIME,
                recurrence_type=LoadTestTriggerConstants.MONTHLY_DAYS_RECURRENCE_TYPE,
                recurrence_interval=LoadTestTriggerConstants.MONTHLY_DAYS_RECURRENCE_INTERVAL,
                recurrence_week_days=LoadTestTriggerConstants.MONTHLY_DAYS_RECURRENCE_WEEK_DAYS,
                test_ids=LoadTestTriggerConstants.MONTHLY_DAYS_TEST_IDS
            )

        # Test invalid cron recurrence with extra parameters
        with self.assertRaises(InvalidArgumentValueError):
            self.create_trigger_schedule(
                trigger_id=LoadTestTriggerConstants.INVALID_CRON_TRIGGER_ID,
                description=LoadTestTriggerConstants.CRON_DESCRIPTION,
                display_name=LoadTestTriggerConstants.CRON_DISPLAY_NAME,
                start_date_time=LoadTestTriggerConstants.CURRENT_DATE_TIME,
                recurrence_type=LoadTestTriggerConstants.CRON_RECURRENCE_TYPE,
                recurrence_cron_expression=LoadTestTriggerConstants.CRON_RECURRENCE_CRON_EXPRESSION,
                recurrence_interval=LoadTestTriggerConstants.RECURRENCE_INTERVAL_ONE,  # Invalid parameter for cron recurrence
                test_ids=LoadTestTriggerConstants.CRON_TEST_IDS
            )

        # Test invalid date-time format
        with self.assertRaises(InvalidArgumentValueError):
            self.create_trigger_schedule(
                trigger_id=LoadTestTriggerConstants.INVALID_DAILY_TRIGGER_ID,
                description=LoadTestTriggerConstants.DAILY_DESCRIPTION,
                display_name=LoadTestTriggerConstants.DAILY_DISPLAY_NAME,
                start_date_time="2025-02-04T14:20:31",  # Invalid date-time format, not utc format
                recurrence_type=LoadTestTriggerConstants.DAILY_RECURRENCE_TYPE,
                recurrence_interval=LoadTestTriggerConstants.RECURRENCE_INTERVAL_ONE,
                test_ids=LoadTestTriggerConstants.DAILY_TEST_IDS
            )

        # Test invalid recurrence interval
        with self.assertRaises(SystemExit):  # Use SystemExit to catch argument parser errors
            self.create_trigger_schedule(
                trigger_id=LoadTestTriggerConstants.INVALID_DAILY_TRIGGER_ID,
                description=LoadTestTriggerConstants.DAILY_DESCRIPTION,
                display_name=LoadTestTriggerConstants.DAILY_DISPLAY_NAME,
                start_date_time=LoadTestTriggerConstants.CURRENT_DATE_TIME,
                recurrence_type=LoadTestTriggerConstants.DAILY_RECURRENCE_TYPE,
                recurrence_interval="invalid-interval",  # Invalid recurrence interval
                test_ids=LoadTestTriggerConstants.DAILY_TEST_IDS
            )

        # Test invalid recurrence dates in month
        with self.assertRaises(SystemExit):  # Use SystemExit to catch argument parser errors
            self.create_trigger_schedule(
                trigger_id=LoadTestTriggerConstants.INVALID_MONTHLY_DATES_TRIGGER_ID,
                description=LoadTestTriggerConstants.MONTHLY_DATES_DESCRIPTION,
                display_name=LoadTestTriggerConstants.MONTHLY_DATES_DISPLAY_NAME,
                start_date_time=LoadTestTriggerConstants.CURRENT_DATE_TIME,
                recurrence_type=LoadTestTriggerConstants.MONTHLY_DATES_RECURRENCE_TYPE,
                recurrence_interval=LoadTestTriggerConstants.MONTHLY_DATES_RECURRENCE_INTERVAL,
                recurrence_dates_in_month="invalid-dates-in-month",  # Invalid dates in month
                test_ids=LoadTestTriggerConstants.MONTHLY_DATES_TEST_IDS
            )

        # Test invalid recurrence week days
        with self.assertRaises(SystemExit):
            self.create_trigger_schedule(
                trigger_id=LoadTestTriggerConstants.INVALID_WEEKLY_TRIGGER_ID,
                description=LoadTestTriggerConstants.WEEKLY_DESCRIPTION,
                display_name=LoadTestTriggerConstants.WEEKLY_DISPLAY_NAME,
                start_date_time=LoadTestTriggerConstants.CURRENT_DATE_TIME,
                recurrence_type=LoadTestTriggerConstants.WEEKLY_RECURRENCE_TYPE,
                recurrence_interval=LoadTestTriggerConstants.WEEKLY_RECURRENCE_INTERVAL,
                recurrence_week_days="invalid-week-days",  # Invalid week days
                test_ids=LoadTestTriggerConstants.WEEKLY_TEST_IDS
            )

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_update_trigger_schedule_invalid_cases(self, rg, load):
        self.create_trigger_schedule(
            trigger_id=LoadTestTriggerConstants.INVALID_UPDATE_TRIGGER_ID,
            description=LoadTestTriggerConstants.UPDATE_DESCRIPTION,
            display_name=LoadTestTriggerConstants.UPDATE_DISPLAY_NAME,
            start_date_time=LoadTestTriggerConstants.CURRENT_DATE_TIME,
            recurrence_type=LoadTestTriggerConstants.DAILY_RECURRENCE_TYPE,
            recurrence_interval=LoadTestTriggerConstants.RECURRENCE_INTERVAL_ONE,
            test_ids=LoadTestTriggerConstants.UPDATE_TEST_IDS
        )

        # Test invalid update to daily recurrence with extra parameters
        with self.assertRaises(InvalidArgumentValueError):
            self.cmd(
                'az load trigger schedule update '
                '--name {load_test_resource} '
                '--resource-group {resource_group} '
                f'--trigger-id {LoadTestTriggerConstants.INVALID_UPDATE_TRIGGER_ID} '
                f'--recurrence-type {LoadTestTriggerConstants.DAILY_RECURRENCE_TYPE} '
                f'--recurrence-interval {LoadTestTriggerConstants.DAILY_RECURRENCE_INTERVAL} '
                f'--recurrence-week-days {LoadTestTriggerConstants.WEEKLY_RECURRENCE_DAYS} '  # Invalid parameter for daily recurrence
            )

        # Test invalid update to weekly recurrence without required parameter (recurrence-interval)
        with self.assertRaises(InvalidArgumentValueError):
            self.cmd(
                'az load trigger schedule update '
                '--name {load_test_resource} '
                '--resource-group {resource_group} '
                f'--trigger-id {LoadTestTriggerConstants.INVALID_UPDATE_TRIGGER_ID} '
                f'--recurrence-type {LoadTestTriggerConstants.WEEKLY_RECURRENCE_TYPE} '
                f'--recurrence-week-days {LoadTestTriggerConstants.WEEKLY_RECURRENCE_DAYS} '
            )

        # Test invalid update to monthly by dates recurrence with extra parameters
        with self.assertRaises(InvalidArgumentValueError):
            self.cmd(
                'az load trigger schedule update '
                '--name {load_test_resource} '
                '--resource-group {resource_group} '
                f'--trigger-id {LoadTestTriggerConstants.INVALID_UPDATE_TRIGGER_ID} '
                f'--recurrence-type {LoadTestTriggerConstants.MONTHLY_DATES_RECURRENCE_TYPE} '
                f'--recurrence-interval {LoadTestTriggerConstants.MONTHLY_DATES_RECURRENCE_INTERVAL} '
                f'--recurrence-week-days {LoadTestTriggerConstants.MONTHLY_DAYS_RECURRENCE_WEEK_DAYS} '  # Invalid parameter for monthly by dates recurrence
                f'--recurrence-dates {LoadTestTriggerConstants.MONTHLY_DATES_RECURRENCE_DATES_IN_MONTH} '
            )

        # Test invalid update to monthly by days recurrence without required parameters
        with self.assertRaises(InvalidArgumentValueError):
            self.cmd(
                'az load trigger schedule update '
                '--name {load_test_resource} '
                '--resource-group {resource_group} '
                f'--trigger-id {LoadTestTriggerConstants.INVALID_UPDATE_TRIGGER_ID} '
                f'--recurrence-type {LoadTestTriggerConstants.MONTHLY_DAYS_RECURRENCE_TYPE} '
                f'--recurrence-interval {LoadTestTriggerConstants.MONTHLY_DAYS_RECURRENCE_INTERVAL} '
                f'--recurrence-week-days {LoadTestTriggerConstants.MONTHLY_DAYS_RECURRENCE_WEEK_DAYS} '
            )

        # Test invalid update to cron recurrence with extra parameters
        with self.assertRaises(InvalidArgumentValueError):
            self.cmd(
                'az load trigger schedule update '
                '--name {load_test_resource} '
                '--resource-group {resource_group} '
                f'--trigger-id {LoadTestTriggerConstants.INVALID_UPDATE_TRIGGER_ID} '
                f'--recurrence-cron-exp "{LoadTestTriggerConstants.CRON_RECURRENCE_CRON_EXPRESSION}" '
                f'--recurrence-interval {LoadTestTriggerConstants.RECURRENCE_INTERVAL_ONE} '  # Invalid parameter for cron recurrence
                f'--recurrence-type {LoadTestTriggerConstants.CRON_RECURRENCE_TYPE} '
            )