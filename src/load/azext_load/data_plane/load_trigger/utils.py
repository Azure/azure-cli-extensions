# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from datetime import datetime
from azext_load.vendored_sdks.loadtesting.models import _models as models
from azext_load.vendored_sdks.loadtesting.models import _enums as enums
from knack.log import get_logger
from azure.cli.core.azclierror import InvalidArgumentValueError, FileOperationError

logger = get_logger(__name__)

def parse_datetime_in_utc(value):
    try:
        parsed_date_time = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
        return parsed_date_time
    except ValueError:
        raise InvalidArgumentValueError("Invalid datetime format. Please provide datetime in UTC format (YYYY-MM-DDTHH:MM:SSZ).")

def get_recurrence_end_body(end_after_occurrence, end_after_date_time, existing_recurrence_end=None):
    if end_after_occurrence is not None and end_after_date_time is not None:
        raise InvalidArgumentValueError("Specify either end_after_occurrence or end_after_date_time, not both.")
    
    if end_after_occurrence is not None:
        return models.RecurrenceEnd(number_of_occurrences=end_after_occurrence)
    
    if end_after_date_time is not None:
        return models.RecurrenceEnd(end_date_time=end_after_date_time)
    
    return existing_recurrence_end

def get_recurrence_body(
    recurrence_type,
    recurrence_interval,
    recurrence_index,
    recurrence_cron_expression,
    recurrence_dates_in_month,
    recurrence_week_days,
    recurrence_end_body,
):
    validate_recurrence_input(recurrence_type,
    recurrence_interval,
    recurrence_index,
    recurrence_cron_expression,
    recurrence_dates_in_month,
    recurrence_week_days)

    if recurrence_type == enums.Frequency.DAILY:
        return models.DailyRecurrence(
            interval=recurrence_interval,
            recurrence_end=recurrence_end_body
        )
    elif recurrence_type == enums.Frequency.WEEKLY:
        return models.WeeklyRecurrence(
            interval=recurrence_interval,
            days_of_week=recurrence_week_days,
            recurrence_end=recurrence_end_body
        )
    elif recurrence_type == enums.Frequency.HOURLY:
        return models.HourlyRecurrence(
            interval=recurrence_interval,
            recurrence_end=recurrence_end_body
        )
    elif recurrence_type == enums.Frequency.MONTHLY_BY_DATES:
        return models.MonthlyRecurrenceByDates(
            interval=recurrence_interval,
            dates_in_month=recurrence_dates_in_month,
            recurrence_end=recurrence_end_body
        )
    elif recurrence_type == enums.Frequency.MONTHLY_BY_DAYS:
        return models.MonthlyRecurrenceByWeekDays(
            interval=recurrence_interval,
            week_days_in_month=recurrence_week_days,
            index=recurrence_index,
            recurrence_end=recurrence_end_body
        )
    elif recurrence_type == enums.Frequency.CRON:
        return models.RecurrenceWithCron(
            cron_expression=recurrence_cron_expression,
            recurrence_end=recurrence_end_body
        )
    else:
        return None


def validate_recurrence_input(
    recurrence_type,
    recurrence_interval,
    recurrence_index,
    recurrence_cron_expression,
    recurrence_dates_in_month,
    recurrence_week_days,
):
    if recurrence_type is None:
        if any([recurrence_interval, recurrence_index, recurrence_cron_expression, recurrence_dates_in_month, recurrence_week_days]):
            raise InvalidArgumentValueError("Recurrence type is required.")
        logger.debug("Recurrence type not provided. Treating it as one-time trigger.")
        return
    
    if recurrence_type == enums.Frequency.DAILY:
        if recurrence_interval is None:
            raise InvalidArgumentValueError("Recurrence interval is required for daily recurrence.")
        
        # Ensure other arguments are not provided
        if any([recurrence_index, recurrence_cron_expression, recurrence_dates_in_month, recurrence_week_days]):
            raise InvalidArgumentValueError("Only recurrence interval should be provided for daily recurrence.")
    
    if recurrence_type == enums.Frequency.WEEKLY:
        if recurrence_interval is None:
            raise InvalidArgumentValueError("Recurrence interval is required for weekly recurrence.")
        if recurrence_week_days is None or len(recurrence_week_days) == 0:
            raise InvalidArgumentValueError("Recurrence week days are required for weekly recurrence.")
        # Ensure other arguments are not provided
        if any([recurrence_index, recurrence_cron_expression, recurrence_dates_in_month]):
            raise InvalidArgumentValueError("Only recurrence interval and week days should be provided for weekly recurrence.")
    
    if recurrence_type == enums.Frequency.HOURLY:
        if recurrence_interval is None:
            raise InvalidArgumentValueError("Recurrence interval is required for hourly recurrence.")
        # Ensure other arguments are not provided
        if any([recurrence_index, recurrence_cron_expression, recurrence_dates_in_month, recurrence_week_days]):
            raise InvalidArgumentValueError("Only recurrence interval should be provided for hourly recurrence.")
    
    if recurrence_type == enums.Frequency.MONTHLY_BY_DATES:
        if recurrence_interval is None:
            raise InvalidArgumentValueError("Recurrence interval is required for monthly by dates recurrence.")
        if recurrence_dates_in_month is None or len(recurrence_dates_in_month) == 0:
            raise InvalidArgumentValueError("Recurrence dates in month are required for monthly by dates recurrence.")
        # Ensure other arguments are not provided
        if any([recurrence_index, recurrence_cron_expression, recurrence_week_days]):
            raise InvalidArgumentValueError("Only recurrence interval and dates in month should be provided for monthly by dates recurrence.")
    
    if recurrence_type == enums.Frequency.MONTHLY_BY_DAYS:
        if recurrence_interval is None:
            raise InvalidArgumentValueError("Recurrence interval is required for monthly by days recurrence.")
        if recurrence_week_days is None or len(recurrence_week_days) == 0:
            raise InvalidArgumentValueError("Recurrence week days are required for monthly by days recurrence.")
        if recurrence_index not in range(1, 6):
            raise InvalidArgumentValueError("Recurrence index should be between 1 and 5 for monthly by days recurrence.")
        # Ensure other arguments are not provided
        if any([recurrence_cron_expression, recurrence_dates_in_month]):
            raise InvalidArgumentValueError("Only recurrence interval, week days, and index should be provided for monthly by days recurrence.")
    
    if recurrence_type == enums.Frequency.CRON:
        if recurrence_cron_expression is None:
            raise InvalidArgumentValueError("Recurrence cron expression is required for cron recurrence.")
        
        # Ensure other arguments are not provided
        if any([recurrence_interval, recurrence_index, recurrence_dates_in_month, recurrence_week_days]):
            raise InvalidArgumentValueError("Only recurrence cron expression should be provided for cron recurrence.")
        
def get_schedule_trigger_body_for_update(
    existing_trigger_schedule,
    recurrence_body,
    display_name,
    description,
    trigger_start_date_time,
    test_ids,
):
    new_trigger_body = models.ScheduleTestsTrigger(
        test_ids=test_ids,
        recurrence=recurrence_body,
        start_date_time=trigger_start_date_time,
        display_name=display_name,
        description=description,
    )

    if test_ids is None:
        new_trigger_body.test_ids = existing_trigger_schedule.test_ids
    
    if trigger_start_date_time is None:
        new_trigger_body.start_date_time = existing_trigger_schedule.start_date_time
    
    if display_name is None:
        new_trigger_body.display_name = existing_trigger_schedule.display_name

    if description is None:
        new_trigger_body.description = existing_trigger_schedule.description

    if recurrence_body is None:
        new_trigger_body.recurrence = existing_trigger_schedule.recurrence
    
    return new_trigger_body


def get_recurrence_body_for_update(
    recurrence_type,
    recurrence_interval,
    recurrence_index,
    recurrence_cron_expression,
    recurrence_dates_in_month,
    recurrence_week_days,
    recurrence_end_body,
    existing_recurrence,
):
    # No recurrence type provided means update in existing recurrence
    # Prioritize new values, but fallback to existing values if new values are not provided
    if recurrence_type is None:
        if existing_recurrence is None:
            if any([recurrence_interval, recurrence_index, recurrence_cron_expression, recurrence_dates_in_month, recurrence_week_days]):
                raise InvalidArgumentValueError("Updating recurrence properties of a non recurring schedule requires recurrence type.")
            logger.debug("Recurrence type not provided. Treating it as one-time trigger.")
            return None
        recurrence_type = existing_recurrence.frequency
        if recurrence_type == enums.Frequency.CRON:
            recurrence_cron_expression = recurrence_cron_expression or existing_recurrence.cron_expression
        elif recurrence_type == enums.Frequency.DAILY:
            recurrence_interval = recurrence_interval or existing_recurrence.interval
        elif recurrence_type == enums.Frequency.WEEKLY:
            recurrence_interval = recurrence_interval or existing_recurrence.interval
            recurrence_week_days = recurrence_week_days or existing_recurrence.days_of_week
        elif recurrence_type == enums.Frequency.HOURLY:
            recurrence_interval = recurrence_interval or existing_recurrence.interval
        elif recurrence_type == enums.Frequency.MONTHLY_BY_DATES:
            recurrence_interval = recurrence_interval or existing_recurrence.interval
            recurrence_dates_in_month = recurrence_dates_in_month or existing_recurrence.days_of_month
        elif recurrence_type == enums.Frequency.MONTHLY_BY_DAYS:
            recurrence_interval = recurrence_interval or existing_recurrence.interval
            recurrence_week_days = recurrence_week_days or existing_recurrence.days_of_week
            recurrence_index = recurrence_index or existing_recurrence.index
    
    # if recurrence type is provided, override existing recurrence body with new values
    return get_recurrence_body(
        recurrence_type,
        recurrence_interval,
        recurrence_index,
        recurrence_cron_expression,
        recurrence_dates_in_month,
        recurrence_week_days,
        recurrence_end_body
    )
        
    