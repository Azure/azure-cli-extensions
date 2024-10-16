from .knowledge_base_action import *
from .knowledge_base_debug import *
from .data_collector import SharedDataCollector


class Orchestrator():
    def __init__(self) -> None:
        self.steps = []
        self.shared_data_collector = SharedDataCollector()

    def run(self):
        pass
