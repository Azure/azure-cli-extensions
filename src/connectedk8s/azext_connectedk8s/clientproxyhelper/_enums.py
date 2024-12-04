from enum import Enum


class ProxyStatus(Enum):
    FirstRun = 0
    HCTokenRefresh = 1
    AccessTokenRefresh = 2
    AllRefresh = 3

    @classmethod
    def should_hc_token_refresh(cls, status):
        return status in {cls.FirstRun, cls.HCTokenRefresh, cls.AllRefresh}

    @classmethod
    def should_access_token_refresh(cls, status):
        return status in {cls.FirstRun, cls.AccessTokenRefresh, cls.AllRefresh}
