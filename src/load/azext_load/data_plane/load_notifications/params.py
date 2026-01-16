# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=line-too-long

from azext_load.data_plane.utils import argtypes


def load_arguments(self, _):
    # Load Trigger Schedule
    with self.argument_context("load notification-rule") as c:
        c.argument("load_test_resource", argtypes.load_test_resource)
        c.argument("resource_group_name", argtypes.resource_group)

    # Load notification-rule create
    with self.argument_context("load notification-rule create") as c:
        c.argument("display_name", argtypes.notification_display_name)
        c.argument("notification_rule_id", argtypes.notification_rule_id)
        c.argument("test_ids", argtypes.notification_rule_test_ids)
        c.argument("event", argtypes.notification_rule_event)
        c.argument("action_groups", argtypes.action_groups)
        c.argument("all_tests", argtypes.notification_all_tests)
        c.argument("all_events", argtypes.notification_all_events)

    # Load notification-rule update
    with self.argument_context("load notification-rule update") as c:
        c.argument("display_name", argtypes.notification_display_name)
        c.argument("notification_rule_id", argtypes.notification_rule_id)
        c.argument("test_ids", argtypes.notification_rule_test_ids)
        c.argument("add_event", argtypes.notification_rule_add_event)
        c.argument("remove_event", argtypes.notification_rule_remove_event)
        c.argument("action_groups", argtypes.action_groups)
        c.argument("all_tests", argtypes.notification_all_tests)

    # Load notification-rule list
    with self.argument_context("load notification-rule list") as c:
        c.argument("test_ids", argtypes.notification_rule_test_ids)

    # Load notification-rule show
    with self.argument_context("load notification-rule show") as c:
        c.argument("notification_rule_id", argtypes.notification_rule_id)

    # Load notification-rule delete
    with self.argument_context("load notification-rule delete") as c:
        c.argument("notification_rule_id", argtypes.notification_rule_id)
