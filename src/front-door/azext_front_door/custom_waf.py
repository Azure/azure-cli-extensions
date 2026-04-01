# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=protected-access
from azure.cli.core.aaz import AAZBoolArg, AAZStrArg
from azure.cli.core.azclierror import RequiredArgumentMissingError, ResourceNotFoundError
from azext_front_door.aaz.latest.network.front_door.waf_policy import Create as _WafPolicyCreate, \
    Update as _WafPolicyUpdate, Show as _WafPolicyShow


class WafPolicyCreate(_WafPolicyCreate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.disabled = AAZBoolArg(
            options=['--disabled'],
            help='Create in a disabled state.',
            default=False,
            blank=True,
        )
        args_schema.enabled_state._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.location = 'global'
        if args.disabled.to_serialized_data():
            args.enabled_state = 'Disabled'
        else:
            args.enabled_state = 'Enabled'
        # Normalize mode to be case-insensitive
        if hasattr(args, 'mode') and args.mode:
            mode_value = args.mode.to_serialized_data()
            if mode_value:
                mode_lower = mode_value.lower()
                if mode_lower == 'prevention':
                    args.mode = 'Prevention'
                elif mode_lower == 'detection':
                    args.mode = 'Detection'


class WafPolicyUpdate(_WafPolicyUpdate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.disabled = AAZBoolArg(
            options=['--disabled'],
            help='Create in a disabled state.',
            default=False,
            blank=True,
        )
        args_schema.enabled_state._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.location = 'global'
        if args.disabled.to_serialized_data():
            args.enabled_state = 'Disabled'
        else:
            args.enabled_state = 'Enabled'
        # Normalize mode to be case-insensitive
        if hasattr(args, 'mode') and args.mode:
            mode_value = args.mode.to_serialized_data()
            if mode_value:
                mode_lower = mode_value.lower()
                if mode_lower == 'prevention':
                    args.mode = 'Prevention'
                elif mode_lower == 'detection':
                    args.mode = 'Detection'


class AddExclusionAzureManagedRuleSet(_WafPolicyUpdate):
    """Add an exclusion to an Azure managed rule set for a WAF policy."""

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)

        # Add custom arguments for exclusion
        args_schema.rule_set_type = AAZStrArg(
            options=['--type'],
            help='The type of the managed rule set.',
            required=True,
        )
        args_schema.match_variable = AAZStrArg(
            options=['--match-variable'],
            help='The variable type to be excluded.',
            required=True,
            enum={
                'QueryStringArgNames': 'QueryStringArgNames',
                'RequestBodyJsonArgNames': 'RequestBodyJsonArgNames',
                'RequestBodyPostArgNames': 'RequestBodyPostArgNames',
                'RequestCookieNames': 'RequestCookieNames',
                'RequestHeaderNames': 'RequestHeaderNames'
            },
        )
        args_schema.operator = AAZStrArg(
            options=['--operator'],
            help='Comparison operator to apply to the selector.',
            required=True,
            enum={
                'Contains': 'Contains',
                'EndsWith': 'EndsWith',
                'Equals': 'Equals',
                'EqualsAny': 'EqualsAny',
                'StartsWith': 'StartsWith'
            },
        )
        args_schema.value = AAZStrArg(
            options=['--value'],
            help='Selector value for which elements in the collection this exclusion applies to.',
            required=True,
        )
        args_schema.rule_group_id = AAZStrArg(
            options=['--rule-group-id'],
            help='The managed rule group ID.',
        )
        args_schema.rule_id = AAZStrArg(
            options=['--rule-id'],
            help='The managed rule ID.',
        )

        # Hide the managed_rules argument as we will build it programmatically
        args_schema.managed_rules._registered = False
        args_schema.custom_rules._registered = False
        args_schema.enabled_state._registered = False
        args_schema.mode._registered = False
        args_schema.redirect_url._registered = False
        args_schema.request_body_check._registered = False
        args_schema.custom_block_response_body._registered = False
        args_schema.custom_block_response_status_code._registered = False
        args_schema.log_scrubbing._registered = False
        args_schema.sku._registered = False
        args_schema.tags._registered = False
        args_schema.etag._registered = False
        args_schema.location._registered = False
        args_schema.captcha_expiration_in_minutes._registered = False
        args_schema.javascript_challenge_expiration_in_minutes._registered = False

        return args_schema

    def pre_operations(self):
        args = self.ctx.args

        # Validate rule_id requires rule_group_id
        rule_id = (args.rule_id.to_serialized_data()
                   if hasattr(args, 'rule_id') and args.rule_id else None)
        rule_group_id = (args.rule_group_id.to_serialized_data()
                         if hasattr(args, 'rule_group_id') and args.rule_group_id else None)

        if rule_id and not rule_group_id:
            raise RequiredArgumentMissingError("Must specify --rule-group-id when you specify --rule-id")

    # pylint: disable=too-many-branches
    def pre_instance_update(self, instance):
        args = self.ctx.args

        rule_set_type = args.rule_set_type.to_serialized_data()
        match_variable = args.match_variable.to_serialized_data()
        operator = args.operator.to_serialized_data()
        value = args.value.to_serialized_data()
        rule_group_id = (args.rule_group_id.to_serialized_data()
                         if hasattr(args, 'rule_group_id') and args.rule_group_id else None)
        rule_id = (args.rule_id.to_serialized_data()
                   if hasattr(args, 'rule_id') and args.rule_id else None)

        exclusion = {
            'matchVariable': match_variable,
            'selectorMatchOperator': operator,
            'selector': value
        }

        # Get managed_rules from instance
        managed_rules = instance.properties.managed_rules
        if managed_rules is None:
            raise ResourceNotFoundError("No managed rules found in policy")

        managed_rule_sets = managed_rules.managed_rule_sets
        if managed_rule_sets is None:
            managed_rule_sets = []

        # Find the matching rule set
        rule_set_obj = None
        for rule_set in managed_rule_sets:
            if rule_set.rule_set_type.to_serialized_data().upper() == rule_set_type.upper():
                rule_set_obj = rule_set
                break

        if rule_set_obj is None:
            raise ResourceNotFoundError(f"Rule set type '{rule_set_type}' not found")

        # Determine where to add the exclusion
        if rule_group_id is None:
            # Add exclusion at rule set level
            if rule_set_obj.exclusions is None:
                rule_set_obj.exclusions = []
            rule_set_obj.exclusions.append(exclusion)
        else:
            # Find or create rule group override
            if rule_set_obj.rule_group_overrides is None:
                rule_set_obj.rule_group_overrides = []

            rule_group_override = None
            for rg in rule_set_obj.rule_group_overrides:
                if rg.rule_group_name.to_serialized_data().upper() == rule_group_id.upper():
                    rule_group_override = rg
                    break

            if rule_group_override is None:
                # Create new rule group override
                rule_group_override = {
                    'ruleGroupName': rule_group_id,
                    'exclusions': [],
                    'rules': []
                }
                rule_set_obj.rule_group_overrides.append(rule_group_override)
                # Re-find it as we just appended a dict
                for rg in rule_set_obj.rule_group_overrides:
                    rg_name = rg.rule_group_name if hasattr(rg, 'rule_group_name') else rg.get('ruleGroupName', '')
                    rg_name_val = rg_name.to_serialized_data() if hasattr(rg_name, 'to_serialized_data') else rg_name
                    if rg_name_val.upper() == rule_group_id.upper():
                        rule_group_override = rg
                        break

            if rule_id is None:
                # Add exclusion at rule group level
                if rule_group_override.exclusions is None:
                    rule_group_override.exclusions = []
                rule_group_override.exclusions.append(exclusion)
            else:
                # Find or create rule override
                if rule_group_override.rules is None:
                    rule_group_override.rules = []

                rule_override = None
                for rule in rule_group_override.rules:
                    rule_id_val = (rule.rule_id if hasattr(rule, 'rule_id')
                                   else rule.get('ruleId', ''))
                    rule_id_str = (rule_id_val.to_serialized_data()
                                   if hasattr(rule_id_val, 'to_serialized_data') else rule_id_val)
                    if rule_id_str.upper() == rule_id.upper():
                        rule_override = rule
                        break

                if rule_override is None:
                    # Create new rule override
                    rule_override = {
                        'ruleId': rule_id,
                        'exclusions': []
                    }
                    rule_group_override.rules.append(rule_override)
                    # Re-find it
                    for rule in rule_group_override.rules:
                        rule_id_val = (rule.rule_id if hasattr(rule, 'rule_id')
                                       else rule.get('ruleId', ''))
                        rule_id_str = (rule_id_val.to_serialized_data()
                                       if hasattr(rule_id_val, 'to_serialized_data') else rule_id_val)
                        if rule_id_str.upper() == rule_id.upper():
                            rule_override = rule
                            break

                # Add exclusion at rule level
                if rule_override.exclusions is None:
                    rule_override.exclusions = []
                rule_override.exclusions.append(exclusion)


class RemoveExclusionAzureManagedRuleSet(_WafPolicyUpdate):
    """Remove an exclusion from an Azure managed rule set for a WAF policy."""

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)

        args_schema.rule_set_type = AAZStrArg(
            options=['--type'],
            help='The type of the managed rule set.',
            required=True,
        )
        args_schema.match_variable = AAZStrArg(
            options=['--match-variable'],
            help='The variable type to be excluded.',
            required=True,
            enum={
                'QueryStringArgNames': 'QueryStringArgNames',
                'RequestBodyJsonArgNames': 'RequestBodyJsonArgNames',
                'RequestBodyPostArgNames': 'RequestBodyPostArgNames',
                'RequestCookieNames': 'RequestCookieNames',
                'RequestHeaderNames': 'RequestHeaderNames'
            },
        )
        args_schema.operator = AAZStrArg(
            options=['--operator'],
            help='Comparison operator to apply to the selector.',
            required=True,
            enum={
                'Contains': 'Contains',
                'EndsWith': 'EndsWith',
                'Equals': 'Equals',
                'EqualsAny': 'EqualsAny',
                'StartsWith': 'StartsWith'
            },
        )
        args_schema.value = AAZStrArg(
            options=['--value'],
            help='Selector value for which elements in the collection this exclusion applies to.',
            required=True,
        )
        args_schema.rule_group_id = AAZStrArg(
            options=['--rule-group-id'],
            help='The managed rule group ID.',
        )
        args_schema.rule_id = AAZStrArg(
            options=['--rule-id'],
            help='The managed rule ID.',
        )

        # Hide unrelated arguments
        args_schema.managed_rules._registered = False
        args_schema.custom_rules._registered = False
        args_schema.enabled_state._registered = False
        args_schema.mode._registered = False
        args_schema.redirect_url._registered = False
        args_schema.request_body_check._registered = False
        args_schema.custom_block_response_body._registered = False
        args_schema.custom_block_response_status_code._registered = False
        args_schema.log_scrubbing._registered = False
        args_schema.sku._registered = False
        args_schema.tags._registered = False
        args_schema.etag._registered = False
        args_schema.location._registered = False
        args_schema.captcha_expiration_in_minutes._registered = False
        args_schema.javascript_challenge_expiration_in_minutes._registered = False

        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        rule_id = (args.rule_id.to_serialized_data()
                   if hasattr(args, 'rule_id') and args.rule_id else None)
        rule_group_id = (args.rule_group_id.to_serialized_data()
                         if hasattr(args, 'rule_group_id') and args.rule_group_id else None)

        if rule_id and not rule_group_id:
            raise RequiredArgumentMissingError("Must specify --rule-group-id when you specify --rule-id")

    def pre_instance_update(self, instance):
        args = self.ctx.args

        rule_set_type = args.rule_set_type.to_serialized_data()
        match_variable = args.match_variable.to_serialized_data()
        operator = args.operator.to_serialized_data()
        value = args.value.to_serialized_data()
        rule_group_id = (args.rule_group_id.to_serialized_data()
                         if hasattr(args, 'rule_group_id') and args.rule_group_id else None)
        rule_id = (args.rule_id.to_serialized_data()
                   if hasattr(args, 'rule_id') and args.rule_id else None)

        managed_rules = instance.properties.managed_rules
        if managed_rules is None or managed_rules.managed_rule_sets is None:
            raise ResourceNotFoundError("Exclusion not found")

        rule_set_obj = None
        for rule_set in managed_rules.managed_rule_sets:
            if rule_set.rule_set_type.to_serialized_data().upper() == rule_set_type.upper():
                rule_set_obj = rule_set
                break

        if rule_set_obj is None:
            raise ResourceNotFoundError(f"Rule set type '{rule_set_type}' not found")

        exclusions = None
        if rule_group_id is None:
            exclusions = rule_set_obj.exclusions
        else:
            if rule_set_obj.rule_group_overrides is None:
                raise ResourceNotFoundError("Exclusion not found")

            rule_group_override = None
            for rg in rule_set_obj.rule_group_overrides:
                if rg.rule_group_name.to_serialized_data().upper() == rule_group_id.upper():
                    rule_group_override = rg
                    break

            if rule_group_override is None:
                raise ResourceNotFoundError(f"Rule group '{rule_group_id}' not found")

            if rule_id is None:
                exclusions = rule_group_override.exclusions
            else:
                if rule_group_override.rules is None:
                    raise ResourceNotFoundError("Exclusion not found")

                for rule in rule_group_override.rules:
                    if rule.rule_id.to_serialized_data().upper() == rule_id.upper():
                        exclusions = rule.exclusions
                        break

                if exclusions is None:
                    raise ResourceNotFoundError(f"Rule '{rule_id}' not found")

        if exclusions is None:
            raise ResourceNotFoundError("Exclusion not found")

        # Find and remove the matching exclusion
        for i, exclusion in enumerate(exclusions):
            exc_match_var = (exclusion.match_variable.to_serialized_data()
                             if hasattr(exclusion.match_variable, 'to_serialized_data')
                             else exclusion.get('matchVariable', ''))
            exc_operator = (exclusion.selector_match_operator.to_serialized_data()
                            if hasattr(exclusion.selector_match_operator, 'to_serialized_data')
                            else exclusion.get('selectorMatchOperator', ''))
            exc_selector = (exclusion.selector.to_serialized_data()
                            if hasattr(exclusion.selector, 'to_serialized_data')
                            else exclusion.get('selector', ''))

            if (exc_match_var == match_variable and exc_operator == operator
                    and exc_selector == value):
                del exclusions[i]
                return

        raise ResourceNotFoundError("Exclusion not found")


class ListExclusionAzureManagedRuleSet(_WafPolicyShow):
    """List exclusions for an Azure managed rule set in a WAF policy."""

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)

        # Disable --ids for list command
        args_schema.policy_name._id_part = None

        args_schema.rule_set_type = AAZStrArg(
            options=['--type'],
            help='The type of the managed rule set.',
            required=True,
        )
        args_schema.rule_group_id = AAZStrArg(
            options=['--rule-group-id'],
            help='The managed rule group ID.',
        )
        args_schema.rule_id = AAZStrArg(
            options=['--rule-id'],
            help='The managed rule ID.',
        )

        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        rule_id = (args.rule_id.to_serialized_data()
                   if hasattr(args, 'rule_id') and args.rule_id else None)
        rule_group_id = (args.rule_group_id.to_serialized_data()
                         if hasattr(args, 'rule_group_id') and args.rule_group_id else None)

        if rule_id and not rule_group_id:
            raise RequiredArgumentMissingError("Must specify --rule-group-id when you specify --rule-id")

    def _output(self, *args, **kwargs):
        result = self.deserialize_output(self.ctx.vars.instance, client_flatten=True)
        ctx_args = self.ctx.args

        rule_set_type = ctx_args.rule_set_type.to_serialized_data()
        rule_group_id = (ctx_args.rule_group_id.to_serialized_data()
                         if hasattr(ctx_args, 'rule_group_id') and ctx_args.rule_group_id else None)
        rule_id = (ctx_args.rule_id.to_serialized_data()
                   if hasattr(ctx_args, 'rule_id') and ctx_args.rule_id else None)

        managed_rule_sets = result.get('managedRules', {}).get('managedRuleSets', [])
        if not managed_rule_sets:
            raise ResourceNotFoundError(f"Rule set '{rule_set_type}' not found")

        rule_set_obj = None
        for rule_set in managed_rule_sets:
            if rule_set.get('ruleSetType', '').upper() == rule_set_type.upper():
                rule_set_obj = rule_set
                break

        if rule_set_obj is None:
            raise ResourceNotFoundError(f"Rule set '{rule_set_type}' not found")

        if rule_group_id is None:
            return rule_set_obj.get('exclusions', [])

        rule_group_overrides = rule_set_obj.get('ruleGroupOverrides', [])
        if not rule_group_overrides:
            raise ResourceNotFoundError(f"Rule group '{rule_group_id}' not found")

        rule_group_override = None
        for rg in rule_group_overrides:
            if rg.get('ruleGroupName', '').upper() == rule_group_id.upper():
                rule_group_override = rg
                break

        if rule_group_override is None:
            raise ResourceNotFoundError(f"Rule group '{rule_group_id}' not found")

        if rule_id is None:
            return rule_group_override.get('exclusions', [])

        rules = rule_group_override.get('rules', [])
        for rule in rules:
            if rule.get('ruleId', '').upper() == rule_id.upper():
                return rule.get('exclusions', [])

        raise ResourceNotFoundError(f"Rule '{rule_id}' not found")


class AddAzureManagedRuleSet(_WafPolicyUpdate):
    """Add a managed rule set to a WAF policy."""

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)

        args_schema.rule_set_type = AAZStrArg(
            options=['--type'],
            help='The type of the managed rule set.',
            required=True,
        )
        args_schema.version = AAZStrArg(
            options=['--version'],
            help='The version of the managed rule set.',
            required=True,
        )
        args_schema.rule_set_action = AAZStrArg(
            options=['--action'],
            help='Action for overriding rules.',
            enum={
                'Block': 'Block',
                'Log': 'Log',
                'Redirect': 'Redirect'
            },
        )

        # Hide unrelated arguments
        args_schema.managed_rules._registered = False
        args_schema.custom_rules._registered = False
        args_schema.enabled_state._registered = False
        args_schema.mode._registered = False
        args_schema.redirect_url._registered = False
        args_schema.request_body_check._registered = False
        args_schema.custom_block_response_body._registered = False
        args_schema.custom_block_response_status_code._registered = False
        args_schema.log_scrubbing._registered = False
        args_schema.sku._registered = False
        args_schema.tags._registered = False
        args_schema.etag._registered = False
        args_schema.location._registered = False
        args_schema.captcha_expiration_in_minutes._registered = False
        args_schema.javascript_challenge_expiration_in_minutes._registered = False

        return args_schema

    def pre_instance_update(self, instance):
        args = self.ctx.args

        rule_set_type = args.rule_set_type.to_serialized_data()
        version = args.version.to_serialized_data()
        rule_set_action = (args.rule_set_action.to_serialized_data()
                           if hasattr(args, 'rule_set_action') and args.rule_set_action else None)

        new_rule_set = {
            'ruleSetType': rule_set_type,
            'ruleSetVersion': version,
        }
        if rule_set_action:
            new_rule_set['ruleSetAction'] = rule_set_action

        managed_rules = instance.properties.managed_rules
        if managed_rules is None:
            instance.properties.managed_rules = {'managedRuleSets': [new_rule_set]}
            return

        managed_rule_sets = managed_rules.managed_rule_sets
        if managed_rule_sets is None:
            managed_rules.managed_rule_sets = [new_rule_set]
            return

        # Check if rule set type already exists, if so replace it
        found = False
        for i, rule_set in enumerate(managed_rule_sets):
            if rule_set.rule_set_type.to_serialized_data().upper() == rule_set_type.upper():
                managed_rule_sets[i] = new_rule_set
                found = True
                break

        if not found:
            managed_rule_sets.append(new_rule_set)


class RemoveAzureManagedRuleSet(_WafPolicyUpdate):
    """Remove a managed rule set from a WAF policy."""

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)

        args_schema.rule_set_type = AAZStrArg(
            options=['--type'],
            help='The type of the managed rule set.',
            required=True,
        )

        # Hide unrelated arguments
        args_schema.managed_rules._registered = False
        args_schema.custom_rules._registered = False
        args_schema.enabled_state._registered = False
        args_schema.mode._registered = False
        args_schema.redirect_url._registered = False
        args_schema.request_body_check._registered = False
        args_schema.custom_block_response_body._registered = False
        args_schema.custom_block_response_status_code._registered = False
        args_schema.log_scrubbing._registered = False
        args_schema.sku._registered = False
        args_schema.tags._registered = False
        args_schema.etag._registered = False
        args_schema.location._registered = False
        args_schema.captcha_expiration_in_minutes._registered = False
        args_schema.javascript_challenge_expiration_in_minutes._registered = False

        return args_schema

    def pre_instance_update(self, instance):
        args = self.ctx.args
        rule_set_type = args.rule_set_type.to_serialized_data()

        managed_rules = instance.properties.managed_rules
        if managed_rules is None or managed_rules.managed_rule_sets is None:
            return

        # Filter out the rule set with matching type
        managed_rules.managed_rule_sets = [
            rs for rs in managed_rules.managed_rule_sets
            if rs.rule_set_type.to_serialized_data().upper() != rule_set_type.upper()
        ]


class ListAzureManagedRuleSet(_WafPolicyShow):
    """List managed rule sets in a WAF policy."""

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)

        # Disable --ids for list command
        args_schema.policy_name._id_part = None

        return args_schema

    def _output(self, *args, **kwargs):
        result = self.deserialize_output(self.ctx.vars.instance, client_flatten=True)
        return result.get('managedRules', {}).get('managedRuleSets', [])


class AddOverrideAzureManagedRuleSet(_WafPolicyUpdate):
    """Add a rule override to an Azure managed rule set."""

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)

        args_schema.rule_set_type = AAZStrArg(
            options=['--type'],
            help='The type of the managed rule set.',
            required=True,
        )
        args_schema.rule_group_id = AAZStrArg(
            options=['--rule-group-id'],
            help='The managed rule group ID.',
            required=True,
        )
        args_schema.rule_id = AAZStrArg(
            options=['--rule-id'],
            help='The managed rule ID.',
            required=True,
        )
        args_schema.action = AAZStrArg(
            options=['--action'],
            help='Action for overriding the rule.',
            enum={
                'Allow': 'Allow',
                'Block': 'Block',
                'Log': 'Log',
                'Redirect': 'Redirect',
                'AnomalyScoring': 'AnomalyScoring'
            },
        )
        args_schema.disabled = AAZBoolArg(
            options=['--disabled'],
            help='Whether to disable the rule.',
        )
        args_schema.sensitivity = AAZStrArg(
            options=['--sensitivity'],
            help='Describes the override sensitivity to be applied when rule matches.',
            enum={
                'High': 'High',
                'Medium': 'Medium',
                'Low': 'Low'
            },
        )

        # Hide unrelated arguments
        args_schema.managed_rules._registered = False
        args_schema.custom_rules._registered = False
        args_schema.enabled_state._registered = False
        args_schema.mode._registered = False
        args_schema.redirect_url._registered = False
        args_schema.request_body_check._registered = False
        args_schema.custom_block_response_body._registered = False
        args_schema.custom_block_response_status_code._registered = False
        args_schema.log_scrubbing._registered = False
        args_schema.sku._registered = False
        args_schema.tags._registered = False
        args_schema.etag._registered = False
        args_schema.location._registered = False
        args_schema.captcha_expiration_in_minutes._registered = False
        args_schema.javascript_challenge_expiration_in_minutes._registered = False

        return args_schema

    # pylint: disable=too-many-nested-blocks
    def pre_instance_update(self, instance):
        args = self.ctx.args

        rule_set_type = args.rule_set_type.to_serialized_data()
        rule_group_id = args.rule_group_id.to_serialized_data()
        rule_id = args.rule_id.to_serialized_data()
        action = (args.action.to_serialized_data()
                  if hasattr(args, 'action') and args.action else None)
        disabled = (args.disabled.to_serialized_data()
                    if hasattr(args, 'disabled') and args.disabled else None)
        sensitivity = (args.sensitivity.to_serialized_data()
                       if hasattr(args, 'sensitivity') and args.sensitivity else None)

        override = {
            'ruleId': rule_id,
            'enabledState': 'Disabled' if disabled else 'Enabled',
        }
        if action:
            override['action'] = action
        if sensitivity:
            override['sensitivity'] = sensitivity

        managed_rules = instance.properties.managed_rules
        if managed_rules is None or managed_rules.managed_rule_sets is None:
            raise ResourceNotFoundError(f"Rule set type '{rule_set_type}' not found")

        set_rule = False
        for rule_set in managed_rules.managed_rule_sets:
            if rule_set.rule_set_type.to_serialized_data().upper() == rule_set_type.upper():
                if rule_set.rule_group_overrides is None:
                    rule_set.rule_group_overrides = []

                for rg in rule_set.rule_group_overrides:
                    if rg.rule_group_name.to_serialized_data().upper() == rule_group_id.upper():
                        if rg.rules is None:
                            rg.rules = []

                        # Check if rule already exists
                        for j, rule in enumerate(rg.rules):
                            if rule.rule_id.to_serialized_data().upper() == rule_id.upper():
                                rg.rules[j] = override
                                set_rule = True
                                break

                        if not set_rule:
                            rg.rules.append(override)
                            set_rule = True
                        break

                if not set_rule:
                    # Create new rule group override
                    rule_set.rule_group_overrides.append({
                        'ruleGroupName': rule_group_id,
                        'rules': [override]
                    })
                    set_rule = True
                break

        if not set_rule:
            raise ResourceNotFoundError(f"Rule set type '{rule_set_type}' not found")


class RemoveOverrideAzureManagedRuleSet(_WafPolicyUpdate):
    """Remove a rule override from an Azure managed rule set."""

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)

        args_schema.rule_set_type = AAZStrArg(
            options=['--type'],
            help='The type of the managed rule set.',
            required=True,
        )
        args_schema.rule_group_id = AAZStrArg(
            options=['--rule-group-id'],
            help='The managed rule group ID.',
            required=True,
        )
        args_schema.rule_id = AAZStrArg(
            options=['--rule-id'],
            help='The managed rule ID.',
            required=True,
        )

        # Hide unrelated arguments
        args_schema.managed_rules._registered = False
        args_schema.custom_rules._registered = False
        args_schema.enabled_state._registered = False
        args_schema.mode._registered = False
        args_schema.redirect_url._registered = False
        args_schema.request_body_check._registered = False
        args_schema.custom_block_response_body._registered = False
        args_schema.custom_block_response_status_code._registered = False
        args_schema.log_scrubbing._registered = False
        args_schema.sku._registered = False
        args_schema.tags._registered = False
        args_schema.etag._registered = False
        args_schema.location._registered = False
        args_schema.captcha_expiration_in_minutes._registered = False
        args_schema.javascript_challenge_expiration_in_minutes._registered = False

        return args_schema

    # pylint: disable=too-many-nested-blocks
    def pre_instance_update(self, instance):
        args = self.ctx.args

        rule_set_type = args.rule_set_type.to_serialized_data()
        rule_group_id = args.rule_group_id.to_serialized_data()
        rule_id = args.rule_id.to_serialized_data()

        managed_rules = instance.properties.managed_rules
        if managed_rules is None or managed_rules.managed_rule_sets is None:
            raise ResourceNotFoundError(f"Rule '{rule_id}' not found")

        removed_rule = False
        for rule_set in managed_rules.managed_rule_sets:
            if rule_set.rule_set_type.to_serialized_data().upper() == rule_set_type.upper():
                if rule_set.rule_group_overrides is None:
                    continue

                for i, rg in enumerate(rule_set.rule_group_overrides):
                    if rg.rule_group_name.to_serialized_data().upper() == rule_group_id.upper():
                        if rg.rules is None:
                            continue

                        for j, rule in enumerate(rg.rules):
                            if rule.rule_id.to_serialized_data().upper() == rule_id.upper():
                                del rg.rules[j]
                                # Remove empty rule group override
                                if not rg.rules:
                                    del rule_set.rule_group_overrides[i]
                                removed_rule = True
                                break
                        break
                break

        if not removed_rule:
            raise ResourceNotFoundError(f"Rule '{rule_id}' not found")


class ListOverrideAzureManagedRuleSet(_WafPolicyShow):
    """List rule overrides for an Azure managed rule set."""

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)

        # Disable --ids for list command
        args_schema.policy_name._id_part = None

        args_schema.rule_set_type = AAZStrArg(
            options=['--type'],
            help='The type of the managed rule set.',
            required=True,
        )

        return args_schema

    def _output(self, *args, **kwargs):
        result = self.deserialize_output(self.ctx.vars.instance, client_flatten=True)
        ctx_args = self.ctx.args

        rule_set_type = ctx_args.rule_set_type.to_serialized_data()

        managed_rule_sets = result.get('managedRules', {}).get('managedRuleSets', [])
        for rule_set in managed_rule_sets:
            if rule_set.get('ruleSetType', '').upper() == rule_set_type.upper():
                return rule_set.get('ruleGroupOverrides', [])

        raise ResourceNotFoundError(f"Rule set '{rule_set_type}' not found")


# region Custom Rules

def _hide_update_args(args_schema):
    """Helper function to hide unrelated update arguments."""
    args_schema.managed_rules._registered = False
    args_schema.custom_rules._registered = False
    args_schema.enabled_state._registered = False
    args_schema.mode._registered = False
    args_schema.redirect_url._registered = False
    args_schema.request_body_check._registered = False
    args_schema.custom_block_response_body._registered = False
    args_schema.custom_block_response_status_code._registered = False
    args_schema.log_scrubbing._registered = False
    args_schema.sku._registered = False
    args_schema.tags._registered = False
    args_schema.etag._registered = False
    args_schema.location._registered = False
    args_schema.captcha_expiration_in_minutes._registered = False
    args_schema.javascript_challenge_expiration_in_minutes._registered = False


def _remove_policy_name_alias(args_schema):
    """Remove -n and --name aliases from policy_name so rule_name can use them.
    Must also remove from _fields_alias_map to avoid conflict."""
    # Remove aliases from the internal alias map
    if '-n' in args_schema._fields_alias_map:
        del args_schema._fields_alias_map['-n']
    if '--name' in args_schema._fields_alias_map:
        del args_schema._fields_alias_map['--name']
    # Update the options list
    args_schema.policy_name._options = ['--policy-name']


def _hide_update_args_for_custom_rules(args_schema):
    """Helper function to hide unrelated update arguments for custom rule commands.
    Also removes -n/--name aliases from policy_name to allow rule_name to use them."""
    _hide_update_args(args_schema)
    _remove_policy_name_alias(args_schema)


class CreateCustomRule(_WafPolicyUpdate):
    """Create a custom rule in a WAF policy."""

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZIntArg, AAZListArg

        args_schema = super()._build_arguments_schema(*args, **kwargs)

        # Remove -n and --name aliases from policy_name so rule_name can use them
        _remove_policy_name_alias(args_schema)

        args_schema.rule_name = AAZStrArg(
            options=['--name', '-n', '--rule-name'],
            help='Name of the custom rule.',
            required=True,
        )
        args_schema.priority = AAZIntArg(
            options=['--priority'],
            help='Priority of the rule. Rules with a lower value will be evaluated before rules with a higher value.',
            required=True,
        )
        args_schema.rule_type = AAZStrArg(
            options=['--rule-type'],
            help='Type of the rule.',
            required=True,
            enum={
                'MatchRule': 'MatchRule',
                'matchrule': 'MatchRule',
                'RateLimitRule': 'RateLimitRule',
                'ratelimitrule': 'RateLimitRule'
            },
        )
        args_schema.action = AAZStrArg(
            options=['--action'],
            help='Action to take when the rule matches.',
            required=True,
            enum={
                'Allow': 'Allow',
                'allow': 'Allow',
                'Block': 'Block',
                'block': 'Block',
                'Log': 'Log',
                'log': 'Log',
                'Redirect': 'Redirect',
                'redirect': 'Redirect'
            },
        )
        args_schema.rate_limit_duration = AAZIntArg(
            options=['--rate-limit-duration'],
            help='Rate limit duration in minutes. Required for RateLimitRule.',
        )
        args_schema.rate_limit_threshold = AAZIntArg(
            options=['--rate-limit-threshold'],
            help='Rate limit threshold. Required for RateLimitRule.',
        )
        args_schema.disabled = AAZBoolArg(
            options=['--disabled'],
            help='Whether to disable the rule.',
        )
        # Match condition parameters for creating rule with initial match condition
        args_schema.match_variable = AAZStrArg(
            options=['--match-variable'],
            help='Variable to match against. Use format "variable.selector" for selector-based variables.',
        )
        args_schema.operator = AAZStrArg(
            options=['--operator'],
            help='Comparison operator.',
            enum={
                'Any': 'Any',
                'BeginsWith': 'BeginsWith',
                'Contains': 'Contains',
                'EndsWith': 'EndsWith',
                'Equal': 'Equal',
                'GeoMatch': 'GeoMatch',
                'GreaterThan': 'GreaterThan',
                'GreaterThanOrEqual': 'GreaterThanOrEqual',
                'IPMatch': 'IPMatch',
                'LessThan': 'LessThan',
                'LessThanOrEqual': 'LessThanOrEqual',
                'RegEx': 'RegEx'
            },
        )
        args_schema.values = AAZListArg(
            options=['--values'],
            help='List of values to match against.',
        )
        args_schema.values.Element = AAZStrArg()
        args_schema.negate = AAZBoolArg(
            options=['--negate'],
            help='Whether to negate the condition.',
        )
        args_schema.transforms = AAZListArg(
            options=['--transforms'],
            help='List of transforms to apply.',
        )
        args_schema.transforms.Element = AAZStrArg(
            enum={
                'Lowercase': 'Lowercase',
                'RemoveNulls': 'RemoveNulls',
                'Trim': 'Trim',
                'Uppercase': 'Uppercase',
                'UrlDecode': 'UrlDecode',
                'UrlEncode': 'UrlEncode'
            },
        )

        _hide_update_args(args_schema)
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        rule_type = args.rule_type.to_serialized_data()
        rate_limit_duration = (args.rate_limit_duration.to_serialized_data()
                               if hasattr(args, 'rate_limit_duration') and args.rate_limit_duration
                               else None)
        rate_limit_threshold = (args.rate_limit_threshold.to_serialized_data()
                                if hasattr(args, 'rate_limit_threshold') and args.rate_limit_threshold
                                else None)

        is_rate_limit = rule_type.lower() == "ratelimitrule"
        if is_rate_limit and (rate_limit_duration is None or rate_limit_threshold is None):
            raise RequiredArgumentMissingError(
                "--rate-limit-duration and --rate-limit-threshold are required for a RateLimitRule")

    def pre_instance_update(self, instance):
        args = self.ctx.args

        rule_name = args.rule_name.to_serialized_data()
        priority = args.priority.to_serialized_data()
        rule_type = args.rule_type.to_serialized_data()
        action = args.action.to_serialized_data()
        rate_limit_duration = (args.rate_limit_duration.to_serialized_data()
                               if hasattr(args, 'rate_limit_duration') and args.rate_limit_duration
                               else None)
        rate_limit_threshold = (args.rate_limit_threshold.to_serialized_data()
                                if hasattr(args, 'rate_limit_threshold') and args.rate_limit_threshold
                                else None)
        disabled = (args.disabled.to_serialized_data()
                    if hasattr(args, 'disabled') and args.disabled else None)

        # Get optional match condition parameters
        match_variable = (args.match_variable.to_serialized_data()
                          if hasattr(args, 'match_variable') and args.match_variable else None)
        operator = (args.operator.to_serialized_data()
                    if hasattr(args, 'operator') and args.operator else None)
        values = (args.values.to_serialized_data()
                  if hasattr(args, 'values') and args.values else None)
        negate = (args.negate.to_serialized_data()
                  if hasattr(args, 'negate') and args.negate else None)
        transforms = (args.transforms.to_serialized_data()
                      if hasattr(args, 'transforms') and args.transforms else None)

        match_conditions = []
        if match_variable and operator and values:
            # Parse selector from match_variable (e.g., "RequestHeader.User-Agent")
            selector = None
            variable_parts = match_variable.split('.')
            if len(variable_parts) == 2:
                match_variable = variable_parts[0]
                selector = variable_parts[1]

            new_condition = {
                'matchVariable': match_variable,
                'operator': operator,
                'matchValue': values,
            }
            if selector:
                new_condition['selector'] = selector
            if negate is not None:
                new_condition['negateCondition'] = negate
            if transforms:
                new_condition['transforms'] = transforms
            match_conditions.append(new_condition)

        new_rule = {
            'name': rule_name,
            'priority': priority,
            'ruleType': rule_type,
            'action': action,
            'matchConditions': match_conditions,
            'enabledState': 'Disabled' if disabled else 'Enabled'
        }
        if rate_limit_duration is not None:
            new_rule['rateLimitDurationInMinutes'] = rate_limit_duration
        if rate_limit_threshold is not None:
            new_rule['rateLimitThreshold'] = rate_limit_threshold

        custom_rules = instance.properties.custom_rules
        if custom_rules is None:
            instance.properties.custom_rules = {'rules': [new_rule]}
        elif custom_rules.rules is None:
            custom_rules.rules = [new_rule]
        else:
            custom_rules.rules.append(new_rule)


class UpdateCustomRule(_WafPolicyUpdate):
    """Update a custom rule in a WAF policy."""

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZIntArg

        args_schema = super()._build_arguments_schema(*args, **kwargs)

        # Remove -n and --name aliases from policy_name so rule_name can use them
        _remove_policy_name_alias(args_schema)

        args_schema.rule_name = AAZStrArg(
            options=['--name', '-n', '--rule-name'],
            help='Name of the custom rule.',
            required=True,
        )
        args_schema.priority = AAZIntArg(
            options=['--priority'],
            help='Priority of the rule.',
        )
        args_schema.action = AAZStrArg(
            options=['--action'],
            help='Action to take when the rule matches.',
            enum={
                'Allow': 'Allow',
                'allow': 'Allow',
                'Block': 'Block',
                'block': 'Block',
                'Log': 'Log',
                'log': 'Log',
                'Redirect': 'Redirect',
                'redirect': 'Redirect'
            },
        )
        args_schema.rate_limit_duration = AAZIntArg(
            options=['--rate-limit-duration'],
            help='Rate limit duration in minutes.',
        )
        args_schema.rate_limit_threshold = AAZIntArg(
            options=['--rate-limit-threshold'],
            help='Rate limit threshold.',
        )
        args_schema.disabled = AAZBoolArg(
            options=['--disabled'],
            help='Whether to disable the rule.',
        )

        _hide_update_args(args_schema)
        return args_schema

    def pre_instance_update(self, instance):
        args = self.ctx.args

        rule_name = args.rule_name.to_serialized_data()
        priority = (args.priority.to_serialized_data()
                    if hasattr(args, 'priority') and args.priority else None)
        action = (args.action.to_serialized_data()
                  if hasattr(args, 'action') and args.action else None)
        rate_limit_duration = (args.rate_limit_duration.to_serialized_data()
                               if hasattr(args, 'rate_limit_duration') and args.rate_limit_duration
                               else None)
        rate_limit_threshold = (args.rate_limit_threshold.to_serialized_data()
                                if hasattr(args, 'rate_limit_threshold') and args.rate_limit_threshold
                                else None)
        disabled = (args.disabled.to_serialized_data()
                    if hasattr(args, 'disabled') and args.disabled else None)

        custom_rules = instance.properties.custom_rules
        if custom_rules is None or custom_rules.rules is None:
            raise ResourceNotFoundError(f"Rule '{rule_name}' not found")

        found_rule = False
        for rule in custom_rules.rules:
            if rule.name.to_serialized_data().lower() == rule_name.lower():
                found_rule = True
                if priority is not None:
                    rule.priority = priority
                if action is not None:
                    rule.action = action
                if rate_limit_duration is not None:
                    rule.rate_limit_duration_in_minutes = rate_limit_duration
                if rate_limit_threshold is not None:
                    rule.rate_limit_threshold = rate_limit_threshold
                if disabled is not None:
                    rule.enabled_state = 'Disabled' if disabled else 'Enabled'
                break

        if not found_rule:
            raise ResourceNotFoundError(f"Rule '{rule_name}' not found")


class DeleteCustomRule(_WafPolicyUpdate):
    """Delete a custom rule from a WAF policy."""

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)

        # Remove -n and --name aliases from policy_name so rule_name can use them
        _remove_policy_name_alias(args_schema)

        args_schema.rule_name = AAZStrArg(
            options=['--name', '-n', '--rule-name'],
            help='Name of the custom rule.',
            required=True,
        )

        _hide_update_args(args_schema)
        return args_schema

    def pre_instance_update(self, instance):
        args = self.ctx.args
        rule_name = args.rule_name.to_serialized_data()

        custom_rules = instance.properties.custom_rules
        if custom_rules is None or custom_rules.rules is None:
            return

        custom_rules.rules = [
            rule for rule in custom_rules.rules
            if rule.name.to_serialized_data().lower() != rule_name.lower()
        ]


class ListCustomRules(_WafPolicyShow):
    """List custom rules in a WAF policy."""

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)

        # Disable --ids for list command
        args_schema.policy_name._id_part = None

        return args_schema

    def _output(self, *args, **kwargs):
        result = self.deserialize_output(self.ctx.vars.instance, client_flatten=True)
        return result.get('customRules', {}).get('rules', [])


class ShowCustomRule(_WafPolicyShow):
    """Show a custom rule in a WAF policy."""

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)

        # Remove -n and --name aliases from policy_name so rule_name can use them
        _remove_policy_name_alias(args_schema)

        args_schema.rule_name = AAZStrArg(
            options=['--name', '-n', '--rule-name'],
            help='Name of the custom rule.',
            required=True,
        )

        return args_schema

    def _output(self, *args, **kwargs):
        result = self.deserialize_output(self.ctx.vars.instance, client_flatten=True)
        ctx_args = self.ctx.args
        rule_name = ctx_args.rule_name.to_serialized_data()

        rules = result.get('customRules', {}).get('rules', [])
        for rule in rules:
            if rule.get('name', '').lower() == rule_name.lower():
                return rule

        raise ResourceNotFoundError(f"Rule '{rule_name}' not found")


# endregion

# region Custom Rule Match Conditions


class AddCustomRuleMatchCondition(_WafPolicyUpdate):
    """Add a match condition to a custom rule."""

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZListArg

        args_schema = super()._build_arguments_schema(*args, **kwargs)

        # Remove -n and --name aliases from policy_name so rule_name can use them
        _remove_policy_name_alias(args_schema)

        args_schema.rule_name = AAZStrArg(
            options=['--name', '-n', '--rule-name'],
            help='Name of the custom rule.',
            required=True,
        )
        args_schema.match_variable = AAZStrArg(
            options=['--match-variable'],
            help='Variable to match against. Use format "variable.selector" for selector-based variables.',
            required=True,
        )
        args_schema.operator = AAZStrArg(
            options=['--operator'],
            help='Comparison operator.',
            required=True,
            enum={
                'Any': 'Any',
                'BeginsWith': 'BeginsWith',
                'Contains': 'Contains',
                'EndsWith': 'EndsWith',
                'Equal': 'Equal',
                'GeoMatch': 'GeoMatch',
                'GreaterThan': 'GreaterThan',
                'GreaterThanOrEqual': 'GreaterThanOrEqual',
                'IPMatch': 'IPMatch',
                'LessThan': 'LessThan',
                'LessThanOrEqual': 'LessThanOrEqual',
                'RegEx': 'RegEx'
            },
        )
        args_schema.values = AAZListArg(
            options=['--values'],
            help='List of values to match against.',
            required=True,
        )
        args_schema.values.Element = AAZStrArg()

        args_schema.negate = AAZBoolArg(
            options=['--negate'],
            help='Whether to negate the condition.',
        )
        args_schema.transforms = AAZListArg(
            options=['--transforms'],
            help='List of transforms to apply.',
        )
        args_schema.transforms.Element = AAZStrArg(
            enum={
                'Lowercase': 'Lowercase',
                'RemoveNulls': 'RemoveNulls',
                'Trim': 'Trim',
                'Uppercase': 'Uppercase',
                'UrlDecode': 'UrlDecode',
                'UrlEncode': 'UrlEncode'
            },
        )

        _hide_update_args(args_schema)
        return args_schema

    def pre_instance_update(self, instance):
        args = self.ctx.args

        rule_name = args.rule_name.to_serialized_data()
        match_variable = args.match_variable.to_serialized_data()
        operator = args.operator.to_serialized_data()
        values = args.values.to_serialized_data()
        negate = args.negate.to_serialized_data() if hasattr(args, 'negate') and args.negate else None
        transforms = args.transforms.to_serialized_data() if hasattr(args, 'transforms') and args.transforms else None

        # Parse selector from match_variable (e.g., "RequestHeader.User-Agent")
        selector = None
        variable_parts = match_variable.split('.')
        if len(variable_parts) == 2:
            match_variable = variable_parts[0]
            selector = variable_parts[1]

        new_condition = {
            'matchVariable': match_variable,
            'operator': operator,
            'matchValue': values,
        }
        if selector:
            new_condition['selector'] = selector
        if negate is not None:
            new_condition['negateCondition'] = negate
        if transforms:
            new_condition['transforms'] = transforms

        custom_rules = instance.properties.custom_rules
        if custom_rules is None or custom_rules.rules is None:
            raise ResourceNotFoundError(f"Rule '{rule_name}' not found")

        found_rule = False
        for rule in custom_rules.rules:
            if rule.name.to_serialized_data().upper() == rule_name.upper():
                found_rule = True
                if rule.match_conditions is None:
                    rule.match_conditions = []
                rule.match_conditions.append(new_condition)
                break

        if not found_rule:
            raise ResourceNotFoundError(f"Rule '{rule_name}' not found")


class RemoveCustomRuleMatchCondition(_WafPolicyUpdate):
    """Remove a match condition from a custom rule."""

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZIntArg

        args_schema = super()._build_arguments_schema(*args, **kwargs)

        # Remove -n and --name aliases from policy_name so rule_name can use them
        _remove_policy_name_alias(args_schema)

        args_schema.rule_name = AAZStrArg(
            options=['--name', '-n', '--rule-name'],
            help='Name of the custom rule.',
            required=True,
        )
        args_schema.index = AAZIntArg(
            options=['--index'],
            help='0-based index of the match condition to remove.',
            required=True,
        )

        _hide_update_args(args_schema)
        return args_schema

    def pre_instance_update(self, instance):
        from azure.cli.core.azclierror import InvalidArgumentValueError

        args = self.ctx.args

        rule_name = args.rule_name.to_serialized_data()
        index = args.index.to_serialized_data()

        custom_rules = instance.properties.custom_rules
        if custom_rules is None or custom_rules.rules is None:
            raise ResourceNotFoundError(f"Rule '{rule_name}' not found")

        found_rule = False
        for rule in custom_rules.rules:
            if rule.name.to_serialized_data().upper() == rule_name.upper():
                found_rule = True

                if rule.match_conditions is None or index >= len(rule.match_conditions):
                    raise InvalidArgumentValueError("Index out of bounds")

                rule.match_conditions = [
                    v for i, v in enumerate(rule.match_conditions) if i != index
                ]
                break

        if not found_rule:
            raise ResourceNotFoundError(f"Rule '{rule_name}' not found")


class ListCustomRuleMatchConditions(_WafPolicyShow):
    """List match conditions for a custom rule."""

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)

        # Disable --ids for list command
        args_schema.policy_name._id_part = None

        # Remove -n and --name aliases from policy_name so rule_name can use them
        _remove_policy_name_alias(args_schema)

        args_schema.rule_name = AAZStrArg(
            options=['--name', '-n', '--rule-name'],
            help='Name of the custom rule.',
            required=True,
        )

        return args_schema

    def _output(self, *args, **kwargs):
        result = self.deserialize_output(self.ctx.vars.instance, client_flatten=True)
        ctx_args = self.ctx.args
        rule_name = ctx_args.rule_name.to_serialized_data()

        rules = result.get('customRules', {}).get('rules', [])
        for rule in rules:
            if rule.get('name', '').upper() == rule_name.upper():
                return rule.get('matchConditions', [])

        raise ResourceNotFoundError(f"Rule '{rule_name}' not found")


# endregion
