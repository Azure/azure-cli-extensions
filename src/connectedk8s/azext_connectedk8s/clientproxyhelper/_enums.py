# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import annotations

from enum import Enum


class ProxyStatus(Enum):
    FirstRun = 0
    HCTokenRefresh = 1
    AccessTokenRefresh = 2
    AllRefresh = 3

    @classmethod
    def should_hc_token_refresh(cls, status: ProxyStatus) -> bool:
        return status in {cls.FirstRun, cls.HCTokenRefresh, cls.AllRefresh}

    @classmethod
    def should_access_token_refresh(cls, status: ProxyStatus) -> bool:
        return status in {cls.FirstRun, cls.AccessTokenRefresh, cls.AllRefresh}
