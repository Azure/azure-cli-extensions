# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from enum import Enum


class SearchType(int, Enum):
    All = 1
    Scenario = 2
    Command = 3

    @staticmethod
    def get_search_type_by_name(name):
        search_type = SearchType.All
        if name and name.lower() == "scenario":
            search_type = SearchType.Scenario
        elif name and name.lower() == "command":
            search_type = SearchType.Command
        return search_type


class MatchType(int, Enum):
    All = 1
    And = 2
    Or = 3
    
    @staticmethod
    def get_match_type_by_name(name):
        match_type = MatchType.All
        if name and name.lower() == "and":
            match_type = MatchType.And
        elif name and name.lower() == "or":
            match_type = MatchType.Or
        return match_type


SEARCH_SERVICE_URL = "https://cli-recommendation.azurewebsites.net/api/SearchService"
