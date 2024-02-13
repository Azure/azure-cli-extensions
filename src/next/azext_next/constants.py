# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from enum import Enum


class RecommendType(int, Enum):
    All = 1
    Solution = 2
    Command = 3
    Scenario = 4

    @staticmethod
    def get(name):
        if name.lower() == "solution":
            return RecommendType.Solution
        if name.lower() == "command":
            return RecommendType.Command
        if name.lower() == "scenario":
            return RecommendType.Scenario
        return RecommendType.All
