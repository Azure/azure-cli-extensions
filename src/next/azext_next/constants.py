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
