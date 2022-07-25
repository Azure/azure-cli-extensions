# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from enum import Enum


class SearchScope(int, Enum):
    All = 1
    Scenario = 2
    Command = 3

    @staticmethod
    def get_search_scope_by_name(name):
        if not name:
            return SearchScope.All

        if name.lower() == "scenario":
            return SearchScope.Scenario

        if name.lower() == "command":
            return SearchScope.Command

        return SearchScope.All


class MatchRule(int, Enum):
    All = 1
    And = 2
    Or = 3

    @staticmethod
    def get_match_rule_by_name(name):
        if not name:
            return MatchRule.All

        if name.lower() == "and":
            return MatchRule.And

        if name.lower() == "or":
            return MatchRule.Or

        return MatchRule.All


SEARCH_SERVICE_URL = "https://cli-recommendation.azurewebsites.net/api/SearchService"
