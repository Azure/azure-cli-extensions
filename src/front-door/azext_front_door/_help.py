# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

from azext_front_door.vendored_sdks.models import MatchCondition, Operator

# region FrontDoor
helps['network front-door'] = """
    type: group
    short-summary: Manage Front Doors.
"""

helps['network front-door create'] = """
    type: command
    short-summary: Create a Front Door.
"""

helps['network front-door list'] = """
    type: command
    short-summary: List Front Doors.
"""

helps['network front-door show'] = """
    type: command
    short-summary: Get the details of a Front Door.
"""

helps['network front-door update'] = """
    type: command
    short-summary: Update settings of a Front Door.
"""

helps['network front-door delete'] = """
    type: command
    short-summary: Delete a Front Door.
"""
# endregion

# region FrontDoor BackendPool
helps['network front-door backend-pool'] = """
    type: group
    short-summary: Manage Front Door backend pools.
"""

helps['network front-door backend-pool create'] = """
    type: command
    short-summary: Create a Front Door backend pool.
    long-summary: >
        Since a backend pool must contain a backend, this command
        also creates the first backend. To add additional backends,
        use the `az network front-door backend-pool backend add` command.
"""

helps['network front-door backend-pool list'] = """
    type: command
    short-summary: List Front Door backend pools.
"""

helps['network front-door backend-pool show'] = """
    type: command
    short-summary: Get the details of a Front Door backend pool.
"""

helps['network front-door backend-pool delete'] = """
    type: command
    short-summary: Delete a Front Door backend pool.
"""
# endregion

# region FrontDoor BackendPool Backend
helps['network front-door backend-pool backend'] = """
    type: group
    short-summary: Manage backends of Front Door backend pools.
"""

helps['network front-door backend-pool backend add'] = """
    type: command
    short-summary: Add a backend to a Front Door backend pool.
"""

helps['network front-door backend-pool backend list'] = """
    type: command
    short-summary: List backends of a Front Door backend pool.
"""

helps['network front-door backend-pool backend remove'] = """
    type: command
    short-summary: Remove a backend from a Front Door backend pool.
"""
# endregion

# region FrontDoor FrontendEndpoint
helps['network front-door frontend-endpoint'] = """
    type: group
    short-summary: Manage Front Door frontend endpoints.
"""

helps['network front-door frontend-endpoint create'] = """
    type: command
    short-summary: Create a Front Door frontend endpoint.
"""

helps['network front-door frontend-endpoint list'] = """
    type: command
    short-summary: List Front Door frontend endpoints.
"""

helps['network front-door frontend-endpoint show'] = """
    type: command
    short-summary: Get the details of a Front Door frontend endpoint.
"""

helps['network front-door frontend-endpoint delete'] = """
    type: command
    short-summary: Delete a Front Door frontend endpoint.
"""

# endregion

# region FrontDoor LoadBalancingSettings
helps['network front-door load-balancing'] = """
    type: group
    short-summary: Manage Front Door load-balancing settings.
"""
helps['network front-door load-balancing create'] = """
    type: command
    short-summary: Create Front Door load-balancing settings.
"""

helps['network front-door load-balancing list'] = """
    type: command
    short-summary: List Front Door load-balancing settingss.
"""

helps['network front-door load-balancing show'] = """
    type: command
    short-summary: Get the details of a Front Door load-balancing settings bundle.
"""

helps['network front-door load-balancing delete'] = """
    type: command
    short-summary: Delete Front Door load-balancing settings.
"""

# endregion

# region FrontDoor HealthProbeSettings
helps['network front-door probe'] = """
    type: group
    short-summary: Manage Front Door health probe settings.
"""
helps['network front-door probe create'] = """
    type: command
    short-summary: Create Front Door health probe settings.
"""

helps['network front-door probe list'] = """
    type: command
    short-summary: List Front Door health probe settings.
"""

helps['network front-door probe show'] = """
    type: command
    short-summary: Get the details of a Front Door health probe settings bundle.
"""

helps['network front-door probe delete'] = """
    type: command
    short-summary: Delete Front Door health probe settings.
"""

# endregion

# region FrontDoor RoutingRule
helps['network front-door routing-rule'] = """
    type: group
    short-summary: Manage Front Door routing rules.
"""
helps['network front-door routing-rule create'] = """
    type: command
    short-summary: Create a Front Door routing rule.
"""

helps['network front-door routing-rule list'] = """
    type: command
    short-summary: List Front Door routing rules.
"""

helps['network front-door routing-rule show'] = """
    type: command
    short-summary: Get the details of a Front Door routing rule.
"""

helps['network front-door routing-rule delete'] = """
    type: command
    short-summary: Delete a Front Door routing rule.
"""
# endregion

# region WAFPolicy
helps['network waf-policy'] = """
    type: group
    short-summary: Manage WebApplication Firewall (WAF) policies.
"""

helps['network waf-policy create'] = """
    type: command
    short-summary: Create a WAF policy.
"""

helps['network waf-policy list'] = """
    type: command
    short-summary: List WAF policies.
"""

helps['network waf-policy show'] = """
    type: command
    short-summary: Get the details of a WAF policy.
"""

helps['network waf-policy update'] = """
    type: command
    short-summary: Update settings of a WAF policy.
"""

helps['network waf-policy delete'] = """
    type: command
    short-summary: Delete a WAF policy.
"""

helps['network waf-policy set-managed-ruleset'] = """
    type: command
    short-summary: Configure Azure-managed ruleset.
"""

helps['network waf-policy custom-rule'] = """
    type: group
    short-summary: Manage WAF policy custom rules.
"""

helps['network waf-policy custom-rule create'] = """
    type: command
    short-summary: Create a WAF policy custom rule.
    parameters:
        - name: --match-condition
          short-summary: Match condition for the rule.
          long-summary: |

            Usage:   --match-condition VARIABLE OPERATOR [VALUE [VALUE ...]]

              Variable allowed values: {variables}

              Operator allowed values: {operators}

            Multiple match conditions can be specified by using more than one `--match-condition` argument.
""".format(
    variables=', '.join([x.value for x in MatchCondition]),
    operators=', '.join([x.value for x in Operator])
)

helps['network waf-policy custom-rule list'] = """
    type: command
    short-summary: List WAF policy custom rules.
"""

helps['network waf-policy custom-rule show'] = """
    type: command
    short-summary: Get the details of a WAF policy custom rule.
"""

helps['network waf-policy custom-rule delete'] = """
    type: command
    short-summary: Delete a WAF policy custom rule.
"""
# endregion
