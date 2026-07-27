# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Tests at the CLI help/argument boundary for `monitor health-models arrange`'s
`--node-width`/`--node-height` help text: the wording must be exactly as strong as the
underlying evidence. Width is an exact, stable, verified CSS match - the portal's
`.react-flow__node { width: 200px; }` rule (see `_designer-blade.scss`). Height has no
fixed CSS rule; the human-adjudicated correction (blueprint Decisions/User feedback:
"Use Portal seed 200x81 (Recommended)") instead sources it from `ModelActionsSlice.ts`'s
`measured: { width: 200, height: 81 }` initial seed applied to every V2/V3 health entity -
this SUPERSEDES the prior "no height constant anywhere" framing (that claim was true only
for a fixed *CSS* rule, not for the portal's runtime *measured-seed* value). The help text
must therefore cite 81 as the portal's seed while explicitly not claiming it is a fixed or
guaranteed-final rendered height (ReactFlow may replace it once content is measured). See
blueprint 2026-07-24-portal-health-card-sizes.blueprint.md.
"""

import unittest
from unittest.mock import MagicMock

from azext_health_models._params import load_arguments


def _arrange_argument_help():
    """Capture the `help=` text registered for every `monitor health-models arrange`
    argument, keyed by argument name, by driving `load_arguments` with a lightweight
    loader double (no real `AzCommandsLoader` required) - mirrors this repo's
    `azext_chaos.tests.latest.test_command_registration.TestParamsLoadable` convention
    of exercising `load_arguments` directly.
    """
    mock_loader = MagicMock()
    load_arguments(mock_loader, None)
    entered_context = mock_loader.argument_context.return_value.__enter__.return_value
    return {call.args[0]: call.kwargs.get('help', '') for call in entered_context.argument.call_args_list}


def _arrange_argument_kwargs():
    """Same driving mechanism as `_arrange_argument_help`, but returns each argument's full
    `**kwargs` (not just `help`) keyed by argument name - needed to assert on `options_list`
    for the new `--entity-name` selector, specifically that it carries no `-n`/`--name` alias
    (those already belong to `health_model_name` on this same command).
    """
    mock_loader = MagicMock()
    load_arguments(mock_loader, None)
    entered_context = mock_loader.argument_context.return_value.__enter__.return_value
    return {call.args[0]: call.kwargs for call in entered_context.argument.call_args_list}


class TestArrangeEntityNameArgument(unittest.TestCase):

    def test_entity_name_argument_is_registered_and_optional(self):
        kwargs_by_arg = _arrange_argument_kwargs()
        self.assertIn('entity_name', kwargs_by_arg)
        # Omitted selector must preserve full-model behavior - i.e. the argument must not be
        # `required`, unlike `health_model_name`/`resource_group` on this same command.
        self.assertNotIn('required', kwargs_by_arg['entity_name'])

    def test_entity_name_uses_bare_entity_name_option_with_no_dash_n_or_dash_dash_name_alias(self):
        # `-n`/`--name` are already `health_model_name`'s aliases on this exact command
        # (see `health_model_name`'s own `options_list`); the new selector must avoid that
        # collision even though the repo-wide convention for "select one entity" elsewhere
        # (`entity show`/`create`/...) also includes `-n`/`--name`.
        kwargs_by_arg = _arrange_argument_kwargs()
        options_list = kwargs_by_arg['entity_name']['options_list']
        self.assertEqual(options_list, ['--entity-name'])
        self.assertNotIn('-n', options_list)
        self.assertNotIn('--name', options_list)

        health_model_name_options = kwargs_by_arg['health_model_name']['options_list']
        self.assertEqual(set(options_list) & set(health_model_name_options), set())

    def test_entity_name_help_documents_subtree_scope_and_untouched_outside_entities(self):
        help_text = _arrange_argument_help()['entity_name'].lower()
        self.assertIn('subtree', help_text)
        self.assertIn('descendant', help_text)
        self.assertIn('unchanged', help_text)


class TestArrangeNodeSizeHelpText(unittest.TestCase):

    def test_node_width_help_cites_the_portal_exact_fixed_200px_card_width(self):
        help_text = _arrange_argument_help()['node_width']
        self.assertIn('200', help_text)
        self.assertIn('portal', help_text.lower())
        # The old "explicit approximation" framing no longer applies to width now that
        # it is a verified, exact match - only height should still carry it.
        self.assertNotIn('approximation', help_text.lower())

    def test_node_height_help_cites_the_portal_measured_seed_81_without_claiming_it_is_final(self):
        help_text = _arrange_argument_help()['node_height']
        lowered = help_text.lower()
        # Corrected: the portal DOES seed a height value (81) onto every V2/V3 entity - it
        # is the CLI's claim of "no height constant anywhere" that was overturned by the
        # human-adjudicated correction, not the portal's actual initial state. Cite it.
        self.assertIn('81', help_text)
        self.assertIn('portal', lowered)
        self.assertIn('seed', lowered)
        # Must not claim this seed is a fixed CSS rule or a guaranteed final rendered
        # height - ReactFlow may later replace it with a live DOM measurement, which the
        # headless CLI cannot obtain or predict.
        self.assertNotIn('fixed', lowered)
        self.assertNotIn('final', lowered)
        self.assertNotIn('guaranteed', lowered)
        self.assertIn('override', lowered)


if __name__ == "__main__":
    unittest.main()
