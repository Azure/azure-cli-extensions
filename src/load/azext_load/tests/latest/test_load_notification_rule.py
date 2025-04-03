# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_load.tests.latest.preparers import LoadTestResourcePreparer, ActionGroupPreparer
from azure.cli.testsdk import (
    JMESPathCheck,
    ResourceGroupPreparer,
    ScenarioTest,
    JMESPathCheckExists,
)
from knack.log import get_logger
from azure.cli.core.azclierror import InvalidArgumentValueError
import time

logger = get_logger(__name__)

rg_params = {
    "name_prefix": "clitest-notification-",
    "location": "eastus",
    "key": "resource_group",
    "parameter_name": "rg",
    "random_name_length": 30,
}
load_params = {
    "name_prefix": "clitest-notification-",
    "location": "eastus",
    "key": "load_test_resource",
    "parameter_name": "load",
    "resource_group_key": "resource_group",
    "random_name_length": 30,
}
ag_params = {
    "name_prefix": "clitest-notification-",
    "resource_group_key": "resource_group",
    "key": "action_group",
    "parameter_name": "action_group",
    "random_name_length": 30,
    "location": "eastus",
}

class LoadTestScenarioNotificationRule(ScenarioTest):
    def __init__(self, *args, **kwargs):
        super(LoadTestScenarioNotificationRule, self).__init__(*args, **kwargs)
        self.kwargs.update({"subscription_id": self.get_subscription_id()})

    def create_notification_rule(self, notification_rule_id, load_test_resource, resource_group, action_groups, display_name=None, test_ids=None, event_filters=None, all_tests=False, all_events=False):
        """
        Create a notification rule with the specified parameters.
        """
        cmd = [
            'az load notification-rule create',
            f'--load-test-resource {load_test_resource}',
            f'--resource-group {resource_group}',
            f'--action-groups {action_groups}',
            f'--notification-rule-id {notification_rule_id}'
        ]
        if display_name:
            cmd.append(f'--display-name {display_name}')
        if test_ids:
            cmd.append(f'--test-ids {" ".join(test_ids)}')
        if event_filters:
                for event in event_filters:
                # Handle both formats for --add-event
                    event_cmd = f'--event event-id={event["event_id"]} type={event["type"]}'
                    if "status" in event and "result" in event:
                        event_cmd += f' status={event["status"]} result={event["result"]}'
                    cmd.append(event_cmd)
        if all_tests:
            cmd.append('--all-tests')
        if all_events:
            cmd.append('--all-events')

        cmd.append('--debug')
        logger.debug("Creating notification rule with command: %s", ' '.join(cmd))  
        self.cmd(' '.join(cmd))

    def verify_notification_rule(self, notification_rule_id, load_test_resource, resource_group, expected_action_groups, expected_display_name=None, expected_test_ids=None, expected_event_filters=None, all_tests=False, all_events=False):
        """
        Verify the details of a notification rule.
        """
        # Determine if the test is running in live mode or recording mode
        is_live = self.is_live  # `self.is_live` is True in live mode, False in recording/playback mode

        if not is_live:
            expected_action_groups = None  # Allow any value in playback mode

        checks = [
            JMESPathCheck("notificationRuleId", notification_rule_id),
        ]

        # Add a conditional check for actionGroupIds[0]
        if expected_action_groups:
            checks.append(JMESPathCheck("actionGroupIds[0]", expected_action_groups))
        else:
            checks.append(JMESPathCheckExists("actionGroupIds[0]"))  # Ensure the key exists

        if expected_display_name:
            checks.append(JMESPathCheck("displayName", expected_display_name))
        if expected_test_ids:
            for i, test_id in enumerate(expected_test_ids):
                checks.append(JMESPathCheck(f"testIds[{i}]", test_id))
        if expected_event_filters:
            for expected_event in expected_event_filters:
                event_id = expected_event["event_id"]
                checks.append(JMESPathCheck(f"eventFilters.{event_id}.kind", expected_event["type"]))
                if "status" in expected_event:
                    checks.append(JMESPathCheck(f"eventFilters.{event_id}.condition.testRunStatuses[0]", expected_event["status"]))
                if "result" in expected_event:
                    checks.append(JMESPathCheck(f"eventFilters.{event_id}.condition.testRunResults[0]", expected_event["result"]))
        if all_tests:
            checks.append(JMESPathCheck("testIds", None))
        if all_events:
            checks.append(JMESPathCheck("eventFilters", None))

        self.cmd(
            f'az load notification-rule show '
            f'--load-test-resource {load_test_resource} '
            f'--resource-group {resource_group} '
            f'--notification-rule-id {notification_rule_id}',
            checks=checks
        )

    def update_notification_rule(self, notification_rule_id, load_test_resource, resource_group, action_groups=None, add_events=None, remove_events=None, test_ids=None, all_tests=None, all_events=None):
        """
        Update a notification rule with the specified parameters.
        """
        cmd = [
            'az load notification-rule update',
            f'--load-test-resource {load_test_resource}',
            f'--resource-group {resource_group}',
            f'--notification-rule-id {notification_rule_id}'
        ]
        if action_groups:
            cmd.append(f'--action-groups {action_groups}')
        if add_events:
            for event in add_events:
                # Handle both formats for --add-event
                event_cmd = f'--add-event event-id={event["event_id"]} type={event["type"]}'
                if "status" in event and "result" in event:
                    event_cmd += f' status={event["status"]} result={event["result"]}'
                cmd.append(event_cmd)
        if remove_events:
            for event_id in remove_events:
                cmd.append(f'--remove-event event-id={event_id}')
        if test_ids:
            cmd.append(f'--test-ids {" ".join(test_ids)}')
        if all_tests is not None:
            cmd.append('--all-tests')
        if all_events is not None:
            cmd.append('--all-events')

        self.cmd(' '.join(cmd))
    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    @ActionGroupPreparer(**ag_params)
    def test_create_notification_rule(self, rg, load, action_group):
        """
        Test cases for creating notification rules.
        """
        self.cmd(
            "az load test create "
            "--test-id test1 "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        )

        self.cmd(
            "az load test create "
            "--test-id test2 "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        )

        # Test case 1: Create a notification rule with specific events
        self.create_notification_rule(
            notification_rule_id="nri-test",
            load_test_resource=load,
            resource_group=rg,
            action_groups=action_group,
            event_filters=[
                {"event_id": "event1", "type": "TestRunEnded", "status": "DONE", "result": "FAILED"}
            ],
            test_ids=["test1"],
            display_name="NotificationRule1"
        )
        self.verify_notification_rule(
            notification_rule_id="nri-test",
            load_test_resource=load,
            resource_group=rg,
            expected_action_groups=action_group,
            expected_event_filters=[
                {"event_id": "event1", "type": "TestRunEnded", "status": "DONE", "result": "FAILED"}
            ],
            expected_test_ids=["test1"],
            expected_display_name="NotificationRule1"
        )

        # Test case 2: Create a notification rule for all events
        self.create_notification_rule(
            notification_rule_id="nri-all-events",
            load_test_resource=load,
            resource_group=rg,
            action_groups=action_group,
            all_tests=True,
            all_events=True
        )
        self.verify_notification_rule(
            notification_rule_id="nri-all-events",
            load_test_resource=load,
            resource_group=rg,
            expected_action_groups=action_group,
            all_tests=True,
            all_events=True
        )

        # Test case 3: Create a notification rule for specific tests
        self.create_notification_rule(
            notification_rule_id="nri-specific-tests",
            load_test_resource=load,
            resource_group=rg,
            action_groups=action_group,
            test_ids=["test1", "test2"],
            all_events=True
        )
        self.verify_notification_rule(
            notification_rule_id="nri-specific-tests",
            load_test_resource=load,
            resource_group=rg,
            expected_action_groups=action_group,
            expected_test_ids=["test1", "test2"],
            all_events=True
        )

        # Test case 4: Create a notification rule with multiple events
        self.create_notification_rule(
            notification_rule_id="nri-multiple-events",
            load_test_resource=load,
            resource_group=rg,
            action_groups=action_group,
            event_filters=[
                {"event_id": "event1", "type": "TestRunEnded", "status": "DONE", "result": "FAILED"},
                {"event_id": "event2", "type": "TestRunStarted"}
            ],
            test_ids=["test1", "test2"],
            display_name="NotificationRuleMultipleEvents"
        )
        self.verify_notification_rule(
            notification_rule_id="nri-multiple-events",
            load_test_resource=load,
            resource_group=rg,
            expected_action_groups=action_group,
            expected_event_filters=[
                {"event_id": "event1", "type": "TestRunEnded", "status": "DONE", "result": "FAILED"},
                {"event_id": "event2", "type": "TestRunStarted"}
            ],
            expected_test_ids=["test1", "test2"],
            expected_display_name="NotificationRuleMultipleEvents"
        )

        # Test case 5: Verify the created notification rules
        self.cmd(
            "az load notification-rule list "
            f"--load-test-resource {load} "
            f"--resource-group {rg}",
            checks=[
                JMESPathCheck("length(@)", 4),  # Ensure 4 notification rules are created
            ]
        )

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    @ActionGroupPreparer(**ag_params)
    def test_update_notification_rule(self, rg, load, action_group):
        """
        Test cases for updating notification rules.
        """
        self.cmd(
            "az load test create "
            "--test-id test1 "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        )

        self.cmd(
            "az load test create "
            "--test-id test2 "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        )

        # Step 1: Create a notification rule to update later
        self.create_notification_rule(
            notification_rule_id="nri-update-test",
            load_test_resource=load,
            resource_group=rg,
            action_groups=action_group,
            event_filters=[
                {"event_id": "event1", "type": "TestRunEnded", "status": "DONE", "result": "FAILED"}
            ],
            test_ids=["test1"]
        )
        self.verify_notification_rule(
            notification_rule_id="nri-update-test",
            load_test_resource=load,
            resource_group=rg,
            expected_action_groups=action_group,
            expected_event_filters=[
                {"event_id": "event1", "type": "TestRunEnded", "status": "DONE", "result": "FAILED"}
            ],
            expected_test_ids=["test1"]
        )

        # Step 2: Update the notification rule to add new events
        self.update_notification_rule(
            notification_rule_id="nri-update-test",
            load_test_resource=load,
            resource_group=rg,
            add_events=[
                {"event_id": "event2", "type": "TestRunStarted"}
            ]
        )
        self.verify_notification_rule(
            notification_rule_id="nri-update-test",
            load_test_resource=load,
            resource_group=rg,
            expected_action_groups=action_group,
            expected_event_filters=[
                {"event_id": "event1", "type": "TestRunEnded", "status": "DONE", "result": "FAILED"},
                {"event_id": "event2", "type": "TestRunStarted"}
            ],
            expected_test_ids=["test1"]
        )

        # Step 3: Update the notification rule to remove an event
        self.update_notification_rule(
            notification_rule_id="nri-update-test",
            load_test_resource=load,
            resource_group=rg,
            remove_events=["event1"]
        )
        self.verify_notification_rule(
            notification_rule_id="nri-update-test",
            load_test_resource=load,
            resource_group=rg,
            expected_action_groups=action_group,
            expected_event_filters=[
                {"event_id": "event2", "type": "TestRunStarted"}
            ],
            expected_test_ids=["test1"]
        )

        # Step 4: Update the notification rule to modify test IDs
        self.update_notification_rule(
            notification_rule_id="nri-update-test",
            load_test_resource=load,
            resource_group=rg,
            test_ids=["test2"]
        )
        self.verify_notification_rule(
            notification_rule_id="nri-update-test",
            load_test_resource=load,
            resource_group=rg,
            expected_action_groups=action_group,
            expected_event_filters=[
                {"event_id": "event2", "type": "TestRunStarted"}
            ],
            expected_test_ids=["test2"]
        )
        
        self.update_notification_rule(
            notification_rule_id="nri-update-test",
            load_test_resource=load,
            resource_group=rg,
            add_events=[
                {"event_id": "event3", "type": "TestRunEnded", "status": "DONE", "result": "PASSED"},
                {"event_id": "event4", "type": "TestRunStarted"}
            ]
        )
        self.verify_notification_rule(
            notification_rule_id="nri-update-test",
            load_test_resource=load,
            resource_group=rg,
            expected_action_groups=action_group,
            expected_event_filters=[
                {"event_id": "event2", "type": "TestRunStarted"},
                {"event_id": "event3", "type": "TestRunEnded", "status": "DONE", "result": "PASSED"},
                {"event_id": "event4", "type": "TestRunStarted"}
            ]
        )

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    @ActionGroupPreparer(**ag_params)
    def test_list_notification_rule(self, rg, load, action_group):
        self.cmd(
            "az load test create "
            "--test-id test1 "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        )

        self.cmd(
            "az load test create "
            "--test-id test2 "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        )
        
        # Step 1: Create multiple notification rules
        self.create_notification_rule(
            notification_rule_id="nri-list-test-1",
            load_test_resource=load,
            resource_group=rg,
            action_groups=action_group,
            all_tests=True,
            event_filters=[
                {"event_id": "event1", "type": "TestRunEnded", "status": "DONE", "result": "FAILED"}
            ]
        )
        self.create_notification_rule(
            notification_rule_id="nri-list-test-2",
            load_test_resource=load,
            resource_group=rg,
            action_groups=action_group,
            all_tests=True,
            all_events=True
        )
        self.create_notification_rule(
            notification_rule_id="nri-list-test-3",
            load_test_resource=load,
            resource_group=rg,
            action_groups=action_group,
            test_ids=["test1"],
            all_events=True
        )
        self.create_notification_rule(
            notification_rule_id="nri-list-test-4",
            load_test_resource=load,
            resource_group=rg,
            action_groups=action_group,
            test_ids=["test2"],
            all_events=True
        )
        # Step 2: List all notification rules and verify the count
        self.cmd(
            f"az load notification-rule list --load-test-resource {load} --resource-group {rg}",
            checks=[
                JMESPathCheck("length(@)", 4),  # Ensure 3 notification rules are created
            ]
        )

        # Step 3: Verify filtering by notification rule ID
        self.cmd(
            f"az load notification-rule list --load-test-resource {load} --resource-group {rg} --test-ids test1",
            checks=[
                JMESPathCheck("length(@)", 3),  # Ensure 3 notification rules, all except test 2
            ]
        )

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    @ActionGroupPreparer(**ag_params)
    def test_delete_notification_rule(self, rg, load, action_group):
        """
        Test cases for deleting notification rules.
        """
        
        self.cmd(
            "az load test create "
            "--test-id test1 "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        )

        # Step 1: Create a notification rule to delete later
        self.create_notification_rule(
            notification_rule_id="nri-delete-test",
            load_test_resource=load,
            resource_group=rg,
            action_groups=action_group,
            event_filters=[
                {"event_id": "event1", "type": "TestRunEnded", "status": "DONE", "result": "FAILED"}
            ],
            test_ids=["test1"]
        )
        self.verify_notification_rule(
            notification_rule_id="nri-delete-test",
            load_test_resource=load,
            resource_group=rg,
            expected_action_groups=action_group,
            expected_event_filters=[
                {"event_id": "event1", "type": "TestRunEnded", "status": "DONE", "result": "FAILED"}
            ],
            expected_test_ids=["test1"]
        )

        # Step 2: Delete the notification rule
        self.cmd(
            f"az load notification-rule delete --load-test-resource {load} --resource-group {rg} --notification-rule-id nri-delete-test --yes"
        )

        time.sleep(5)

        # Step 3: Verify the notification rule is deleted
        self.cmd(
            f"az load notification-rule list --load-test-resource {load} --resource-group {rg}",
            checks=[
                JMESPathCheck("length(@)", 0)  # Ensure no notification rules exist
            ]
        ) 
    
    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_create_notification_invalid_cases(self, rg, load):
        """
        Test cases for invalid scenarios in creating notification rules.
        """
        # Invalid action group, test id not existing are taken care in backend. Not testing here.
        # Providing both `--test-ids` and `--all-tests` is not an error scenario. 
        # Providing both `--event` and `--all-events` is not an error scenario.

        # Case 1: Missing required arguments (no `--test-ids` or `--all-tests`)
        with self.assertRaises(InvalidArgumentValueError) as ex:
            self.create_notification_rule(
                notification_rule_id="nri-invalid-case-1",
                load_test_resource=load,
                resource_group=rg,
                action_groups="/subscriptions/<subscription-id>/resourceGroups/<rg-name>/providers/microsoft.insights/actionGroups/<action-group-name>",
                event_filters=[
                    {"event_id": "event1", "type": "TestRunEnded", "status": "DONE", "result": "FAILED"}
                ]
            )
        self.assertIn("No tests provided for notification rule", str(ex.exception))

        # Case 2: Missing required arguments (no `--event` or `--all-events`)
        with self.assertRaises(InvalidArgumentValueError) as ex:
            self.create_notification_rule(
                notification_rule_id="nri-invalid-case-2",
                load_test_resource=load,
                resource_group=rg,
                action_groups="/subscriptions/<subscription-id>/resourceGroups/<rg-name>/providers/microsoft.insights/actionGroups/<action-group-name>",
                test_ids=["test1"]
            )
        self.assertIn("No events provided for notification rule", str(ex.exception))

        # Case 3: Invalid `--event` format
        with self.assertRaises(InvalidArgumentValueError) as ex:
            self.create_notification_rule(
                notification_rule_id="nri-invalid-case-3",
                load_test_resource=load,
                resource_group=rg,
                action_groups="/subscriptions/<subscription-id>/resourceGroups/<rg-name>/providers/microsoft.insights/actionGroups/<action-group-name>",
                test_ids=["test1"],
                event_filters=[
                    {"event_id": "event1", "type": "InvalidEventType"}  # Invalid event type
                ]
            )
        self.assertIn("Invalid event type", str(ex.exception))

        # Case 4: Invalid `--event` with extra fields for non-`TestRunEnded` type
        with self.assertRaises(InvalidArgumentValueError) as ex:
            self.cmd(
                "az load notification-rule create "
                "--notification-rule-id nri-invalid-case-4 "
                "--action-groups /subscriptions/<subscription-id>/resourceGroups/<rg-name>/providers/microsoft.insights/actionGroups/<action-group-name> "
                "--event event-id=event1 type=TestRunStarted result=DONE "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                "--test-ids test1 "
            )
        self.assertIn("Event type 'TestRunStarted' should not have status and result fields.", str(ex.exception))

        # Case 5: Invalid `--test-ids` format
        with self.assertRaises(InvalidArgumentValueError) as ex:
            self.create_notification_rule(
                notification_rule_id="nri-invalid-case-5",
                load_test_resource=load,
                resource_group=rg,
                action_groups="/subscriptions/<subscription-id>/resourceGroups/<rg-name>/providers/microsoft.insights/actionGroups/<action-group-name>",
                test_ids=["InvalidID"],  # Invalid test ID format
                event_filters=[
                    {"event_id": "event1", "type": "TestRunEnded", "status": "DONE", "result": "FAILED"}
                ]
            )
        self.assertIn("Invalid test-id value", str(ex.exception))
        
        # Case 6: Duplicate event ids in `--event`
        with self.assertRaises(InvalidArgumentValueError) as ex:
            self.create_notification_rule(
                notification_rule_id="nri-invalid-case-6",
                load_test_resource=load,
                resource_group=rg,
                action_groups="/subscriptions/<subscription-id>/resourceGroups/<rg-name>/providers/microsoft.insights/actionGroups/<action-group-name>",
                test_ids=["test1"],
                event_filters=[
                    {"event_id": "event1", "type": "TestRunEnded", "status": "DONE", "result": "FAILED"},
                    {"event_id": "event1", "type": "TestRunStarted"}  # Duplicate event ID
                ]
            )
        self.assertIn("Duplicate event-id: event1 found in the event list.", str(ex.exception))


    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    @ActionGroupPreparer(**ag_params)
    def test_update_notification_invalid_cases(self, rg, load, action_group):
        """
        Test cases for invalid scenarios in updating notification rules.
        """
        self.cmd(
            "az load test create "
            "--test-id test1 "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        )
        # Step 1: Create a notification rule to update later
        self.create_notification_rule(
            notification_rule_id="nri-update-invalid-test",
            load_test_resource=load,
            resource_group=rg,
            action_groups=action_group,
            event_filters=[
                {"event_id": "event1", "type": "TestRunEnded", "status": "DONE", "result": "FAILED"}
            ],
            test_ids=["test1"]
        )

        # Case 3: Invalid `--add-event` format
        with self.assertRaises(InvalidArgumentValueError) as ex:
            self.update_notification_rule(
                notification_rule_id="nri-update-invalid-test",
                load_test_resource=load,
                resource_group=rg,
                add_events=[
                    {"event_id": "event2", "type": "InvalidEventType"}  # Invalid event type
                ]
            )
        self.assertIn("Invalid event type", str(ex.exception))

        # Case 4: Invalid `--remove-event` value
        with self.assertRaises(InvalidArgumentValueError) as ex:
            self.update_notification_rule(
                notification_rule_id="nri-update-invalid-test",
                load_test_resource=load,
                resource_group=rg,
                remove_events=["event2"]  # Event ID not present in existing rule
            )
        self.assertIn("Invalid --remove-event value. Event-id: event2 does not exist existing event filters.", str(ex.exception))

        # Case 5: Duplicate event ids in `--add-event`
        with self.assertRaises(InvalidArgumentValueError) as ex:
            self.update_notification_rule(
                notification_rule_id="nri-update-duplicate-events",
                load_test_resource=load,
                resource_group=rg,
                add_events=[
                    {"event_id": "event1", "type": "TestRunEnded"},
                    {"event_id": "event1", "type": "TestRunStarted"}
                ]
            )
        self.assertIn("Duplicate event-id: event1 found in the event list.", str(ex.exception))

        # Case 6: Invalid `--test-ids` format
        with self.assertRaises(InvalidArgumentValueError) as ex:
            self.update_notification_rule(
                notification_rule_id="nri-update-invalid-test",
                load_test_resource=load,
                resource_group=rg,
                test_ids=["Invalid"],  # Invalid test ID format
            )
        self.assertIn("Invalid test-id value", str(ex.exception))

        # Case 7: Invalid event type in `--add-event`
        with self.assertRaises(InvalidArgumentValueError) as ex:
            self.update_notification_rule(
                notification_rule_id="nri-update-invalid-test",
                load_test_resource=load,
                resource_group=rg,
                add_events=[
                    {"event_id": "event5", "type": "InvalidEventType"}
                ]
            )
        self.assertIn("Invalid event type", str(ex.exception))

        # Case 8: Providing non-existing event id in `--remove-event`
        with self.assertRaises(InvalidArgumentValueError) as ex:
            self.update_notification_rule(
                notification_rule_id="nri-update-invalid-test",
                load_test_resource=load,
                resource_group=rg,
                remove_events=["nonexistent-event"]
            )
        self.assertIn("Invalid --remove-event value. Event-id: nonexistent-event does not exist existing event filters.", str(ex.exception))

        # Case 9: Adding an event with extra fields for non-`TestRunEnded` type
        with self.assertRaises(InvalidArgumentValueError) as ex:
            self.cmd(
                "az load notification-rule update "
                "--notification-rule-id nri-invalid-case-9 "
                "--action-groups /subscriptions/<subscription-id>/resourceGroups/<rg-name>/providers/microsoft.insights/actionGroups/<action-group-name> "
                "--add-event event-id=event1 type=TestRunStarted result=DONE "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                "--test-ids test1 "
            )
        self.assertIn("Event type 'TestRunStarted' should not have status and result fields.", str(ex.exception))