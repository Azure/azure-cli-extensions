# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# Disabled since logging statements were flagged as too long

from azext_load.vendored_sdks.loadtesting.models import (
    NotificationEventType,
    TestsNotificationRule,
    TestRunEndedNotificationEventFilter,
    TestRunStartedNotificationEventFilter,
    TriggerCompletedNotificationEventFilter,
    TriggerDisabledNotificationEventFilter,
    TestRunEndedEventCondition,
)
from azure.cli.core.azclierror import InvalidArgumentValueError
from knack.log import get_logger

logger = get_logger(__name__)


def get_notification_rule_create_body(
    action_groups=None,
    event=None,
    display_name=None,
    test_ids=None,
    all_tests=False,
    all_events=False,
):
    """
    This function creates a NotificationRule object with all the required fields for create request.
    """
    logger.debug("\nEvents provided: %s\n", event)
    if not all_tests and test_ids is None:
        raise InvalidArgumentValueError(
            "No tests provided for notification rule. Please provide specific tests using --test-ids option or provide --all-tests flag to select all tests."
        )

    # If all_tests is provided we ignore test_ids provided in command
    if all_tests:
        logger.debug("--all-tests option selected. Ignoring values in --test-ids if provided.")
        test_ids = None

    if not all_events and not event:
        raise InvalidArgumentValueError(
            "No events provided for notification rule. Please provide specific events using --event option or provide --all-events flag to select all events."
        )

    event_filters = None

    if all_events:
        logger.debug("--all-events option selected. Ignoring events provided in --event")
    elif event:
        event_filters = _maps_events_to_filters(event)

    return TestsNotificationRule(
        display_name=display_name,
        action_group_ids=action_groups,
        event_filters=event_filters,
        test_ids=test_ids,
    )


def get_notification_rule_update_body(
    existing_notification_rule,
    action_groups=None,
    add_event=None,
    remove_event=None,
    display_name=None,
    test_ids=None,
    all_tests=False,
):

    if not all_tests and not test_ids:
        # No change in existing test_ids
        test_ids = existing_notification_rule.get("testIds", None)

    # If all_tests is provided we ignore test_ids provided in command
    if all_tests:
        logger.debug("--all-tests option provided. Ignoring values in --test-ids if provided.")
        test_ids = None

    event_filters = existing_notification_rule.get("eventFilters", None)

    # Remove events from existing notification rule
    if remove_event:
        for event in remove_event:
            if not event["event-id"] in event_filters:
                msg = "Invalid --remove-event value. Event-id: %s does not exist existing event filters." % event.get(
                    "event-id"
                )
                raise InvalidArgumentValueError(msg)
            event_filters[event["event-id"]] = None

    if add_event:
        if event_filters is None:
            event_filters = _maps_events_to_filters(add_event)
        else:
            event_filters.update(_maps_events_to_filters(add_event))

    if not action_groups:
        action_groups = existing_notification_rule.get("actionGroupIds", None)

    return TestsNotificationRule(
        display_name=display_name,
        action_group_ids=action_groups,
        event_filters=event_filters,
        test_ids=test_ids,
    )


def _maps_events_to_filters(events):
    """
    This function creates a dictionary of event filters based on the event type.
    """
    if not events:
        return None
    event_filters = {}
    for event in events:
        logger.debug("Mapping event %s to filter", event)
        if event["type"] == NotificationEventType.TEST_RUN_STARTED:
            event_filters[event["event-id"]] = TestRunStartedNotificationEventFilter()
        elif event["type"] == NotificationEventType.TEST_RUN_ENDED:
            if event.get("result", None) is None and event.get("status", None) is None:
                event_filters[event["event-id"]] = TestRunEndedNotificationEventFilter()
            else:
                condition = TestRunEndedEventCondition(
                    test_run_results=event.get("result", None), test_run_statuses=event.get("status", None)
                )
                event_filters[event["event-id"]] = TestRunEndedNotificationEventFilter(
                    condition=condition
                )
        elif event["type"] == NotificationEventType.TRIGGER_COMPLETED:
            event_filters[event["event-id"]] = TriggerCompletedNotificationEventFilter()
        elif event["type"] == NotificationEventType.TRIGGER_DISABLED:
            event_filters[event["event-id"]] = TriggerDisabledNotificationEventFilter()
    return event_filters
