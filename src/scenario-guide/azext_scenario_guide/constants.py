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
    def get(scope):
        if not scope:
            return SearchScope.All

        if scope.lower() == "scenario":
            return SearchScope.Scenario

        if scope.lower() == "command":
            return SearchScope.Command

        return SearchScope.All


class MatchRule(int, Enum):
    All = 1
    And = 2
    Or = 3

    @staticmethod
    def get(rule):
        if not rule:
            return MatchRule.All

        if rule.lower() == "and":
            return MatchRule.And

        if rule.lower() == "or":
            return MatchRule.Or

        return MatchRule.All


SEARCH_SERVICE_URL = "https://cli-recommendation.azurewebsites.net/api/SearchService"


HIGHLIGHT_MARKER = ("<em>", "</em>")


class FeedbackOption(int, Enum):
    NO_RESULT = -1
    """`az scenario guide` get no result from search service"""
    NO_SELECT = 0
    """User selects none of the results and exits immediately after searching"""

    @staticmethod
    def SELECT(option):
        """User selects the option-th scenario in results"""
        return option
