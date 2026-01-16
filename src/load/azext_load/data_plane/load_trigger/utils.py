# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# Disabled since logging statements were flagged as too long

from datetime import datetime
from azext_load.vendored_sdks.loadtesting.models import _models as models
from azext_load.vendored_sdks.loadtesting.models import _enums as enums
from knack.log import get_logger
from azure.cli.core.azclierror import InvalidArgumentValueError

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


def _handle_daily_recurrence(recurrence_interval, recurrence_end_body, **kwargs):
    if recurrence_interval is None:
        raise InvalidArgumentValueError("Recurrence interval is required for daily recurrence.")
    if any(kwargs.values()):
        raise InvalidArgumentValueError("Only recurrence interval is a valid input for daily recurrence.")
    return models.DailyRecurrence(
        interval=recurrence_interval,
        recurrence_end=recurrence_end_body
    )


def _handle_weekly_recurrence(recurrence_interval, recurrence_week_days, recurrence_end_body, **kwargs):
    if recurrence_interval is None:
        raise InvalidArgumentValueError("Recurrence interval is required for weekly recurrence.")
    if recurrence_week_days is None or len(recurrence_week_days) == 0:
        raise InvalidArgumentValueError("Recurrence week days are required for weekly recurrence.")
    if any(kwargs.values()):
        raise InvalidArgumentValueError("Only recurrence interval and week days are valid inputs for weekly recurrence.")
    return models.WeeklyRecurrence(
        interval=recurrence_interval,
        days_of_week=recurrence_week_days,
        recurrence_end=recurrence_end_body
    )


def _handle_hourly_recurrence(recurrence_interval, recurrence_end_body, **kwargs):
    if recurrence_interval is None:
        raise InvalidArgumentValueError("Recurrence interval is required for hourly recurrence.")
    if any(kwargs.values()):
        raise InvalidArgumentValueError("Only recurrence interval is a valid input for hourly recurrence.")
    return models.HourlyRecurrence(
        interval=recurrence_interval,
        recurrence_end=recurrence_end_body
    )


def _handle_monthly_by_dates_recurrence(recurrence_interval, recurrence_dates_in_month, recurrence_end_body, **kwargs):
    if recurrence_interval is None:
        raise InvalidArgumentValueError("Recurrence interval is required for monthly by dates recurrence.")
    if recurrence_dates_in_month is None or len(recurrence_dates_in_month) == 0:
        raise InvalidArgumentValueError("Recurrence dates in month are required for monthly by dates recurrence.")
    if any(kwargs.values()):
        raise InvalidArgumentValueError("Only recurrence interval and dates in month are valid input for monthly by dates recurrence.")
    return models.MonthlyRecurrenceByDates(
        interval=recurrence_interval,
        dates_in_month=recurrence_dates_in_month,
        recurrence_end=recurrence_end_body
    )


def _handle_monthly_by_days_recurrence(recurrence_interval, recurrence_week_days, recurrence_index, recurrence_end_body, **kwargs):
    if recurrence_interval is None:
        raise InvalidArgumentValueError("Recurrence interval is required for monthly by days recurrence.")
    if recurrence_week_days is None or len(recurrence_week_days) == 0:
        raise InvalidArgumentValueError("Recurrence week days are required for monthly by days recurrence.")
    if recurrence_index not in range(1, 6):
        raise InvalidArgumentValueError("Recurrence index should be between 1 and 5 for monthly by days recurrence.")
    if any(kwargs.values()):
        raise InvalidArgumentValueError("Only recurrence interval, week days, and index are valid input for monthly by days recurrence.")
    return models.MonthlyRecurrenceByWeekDays(
        interval=recurrence_interval,
        week_days_in_month=recurrence_week_days,
        index=recurrence_index,
        recurrence_end=recurrence_end_body
    )


def _handle_cron_recurrence(recurrence_cron_expression, recurrence_end_body, **kwargs):
    if recurrence_cron_expression is None:
        raise InvalidArgumentValueError("Recurrence cron expression is required for cron recurrence.")
    if any(kwargs.values()):
        raise InvalidArgumentValueError("Only recurrence cron expression is valid input for cron recurrence.")
    return models.RecurrenceWithCron(
        cron_expression=recurrence_cron_expression,
        recurrence_end=recurrence_end_body
    )


recurrence_handlers = {
    enums.Frequency.DAILY: _handle_daily_recurrence,
    enums.Frequency.WEEKLY: _handle_weekly_recurrence,
    enums.Frequency.HOURLY: _handle_hourly_recurrence,
    enums.Frequency.MONTHLY_BY_DATES: _handle_monthly_by_dates_recurrence,
    enums.Frequency.MONTHLY_BY_DAYS: _handle_monthly_by_days_recurrence,
    enums.Frequency.CRON: _handle_cron_recurrence,
}


def get_recurrence_body(
    recurrence_type,
    recurrence_interval,
    recurrence_index,
    recurrence_cron_expression,
    recurrence_dates_in_month,
    recurrence_week_days,
    recurrence_end_body,
):
    if recurrence_type is None:
        if any([recurrence_interval, recurrence_index, recurrence_cron_expression, recurrence_dates_in_month, recurrence_week_days]):
            raise InvalidArgumentValueError("Recurrence type is required.")
        logger.debug("Recurrence type not provided. Treating it as one-time trigger.")
        return None

    handler = recurrence_handlers.get(recurrence_type)
    if handler:
        return handler(
            recurrence_interval=recurrence_interval,
            recurrence_index=recurrence_index,
            recurrence_cron_expression=recurrence_cron_expression,
            recurrence_dates_in_month=recurrence_dates_in_month,
            recurrence_week_days=recurrence_week_days,
            recurrence_end_body=recurrence_end_body
        )
    return None


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

    return get_recurrence_body(
        recurrence_type,
        recurrence_interval,
        recurrence_index,
        recurrence_cron_expression,
        recurrence_dates_in_month,
        recurrence_week_days,
        recurrence_end_body
    )
