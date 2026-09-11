# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Argument-surface tests for `monitor health-models arrange`.

Pins the option names and shapes callers script against. Help wording is left to `azdev linter`,
except the one claim that must not overstate what the layout does.
"""

import unittest
from unittest.mock import MagicMock

from azext_health_models._params import load_arguments


def _arrange_arguments():
    """Every argument registered for `monitor health-models arrange`, keyed by name."""
    mock_loader = MagicMock()
    load_arguments(mock_loader, None)
    entered = mock_loader.argument_context.return_value.__enter__.return_value
    return {call.args[0]: call.kwargs for call in entered.argument.call_args_list}


class TestArrangeArgumentSurface(unittest.TestCase):

    def test_optional_arguments_are_registered_with_the_expected_option_names(self):
        arguments = _arrange_arguments()

        self.assertEqual(arguments['entity_name']['options_list'], ['--entity-name'])
        self.assertEqual(arguments['yes']['options_list'], ['--yes', '-y'])
        self.assertEqual(arguments['yes']['action'], 'store_true')
        self.assertEqual(arguments['priority']['nargs'], '+')

        # `-n`/`--name` already belong to `health_model_name` on this command.
        self.assertEqual(
            set(arguments['entity_name']['options_list']) & set(arguments['health_model_name']['options_list']),
            set(),
        )
        for name in ('entity_name', 'priority', 'yes'):
            self.assertNotIn('required', arguments[name])

    def test_priority_help_promises_best_effort_rather_than_a_guarantee(self):
        help_text = _arrange_arguments()['priority'].get('help', '').lower()
        self.assertIn('best effort', help_text)
        self.assertNotIn('must appear', help_text)


if __name__ == "__main__":
    unittest.main()
