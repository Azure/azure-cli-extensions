from typing import Dict
from random import randint
from abc import ABC, abstractmethod


class DataCollector:
    def __init__(self) -> None:
        self.data = None

    def run(self) -> None:
        # some code to collect data
        pass

    def get_data(self, refresh_cached_data=False):
        if self.data is None or refresh_cached_data:
            self.run()
        return self.data

    def gc():
        # clean up the resources used by the data collector
        pass

    def export():
        # export the data to a file/remote storage
        pass


class DataCollectorCoreDNSConfigMap(DataCollector):
    def __init__(self) -> None:
        super().__init__()

    def run(self) -> None:
        # some code to collect data
        self.data = "a" if randint(0, 1) else "b"


class DataCollectorIGDNS(DataCollector):
    def __init__(self) -> None:
        super().__init__()

    def run(self) -> None:
        # some code to collect data
        self.data = "c" if randint(0, 1) else "d"


class SharedDataCollector():
    def __init__(self) -> None:
        self.data_collectors: Dict[str, DataCollector] = {
            "core_dns_config_map": DataCollectorCoreDNSConfigMap(),
            "ig_dns": DataCollectorIGDNS(),
        }

    def get_core_dns_config_map_data(self):
        return self.data_collectors["core_dns_config_map"].get_data()

    def get_ig_dns_data(self):
        return self.data_collectors["ig_dns"].get_data()
