# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from enum import Enum


class SearchType(int, Enum):
    All = 1,
    Scenario = 2,
    Command = 3,


SEARCH_SERVICE_URL = "https://cli-recommendation.azurewebsites.net/api/SearchService"
