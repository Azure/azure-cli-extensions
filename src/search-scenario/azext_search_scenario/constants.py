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
        if name == "scenario":
            search_type = SearchType.Scenario
        elif name == "command":
            search_type = SearchType.Command
        return search_type


SEARCH_SERVICE_URL = "https://cli-recommendation.azurewebsites.net/api/SearchService"
