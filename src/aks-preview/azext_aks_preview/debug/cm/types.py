from __future__ import annotations
from typing import List

from .data_collector import SharedDataCollector


class Step:
    def __init__(self) -> None:
        self.tags: List[str] = []
        self.next_steps: List[Step] = []

    def run(self) -> Step:
        pass

    def get_next_steps(self) -> List[Step]:
        return self.next_steps


class DebugStep(Step):
    def __init__(self) -> None:
        super().__init__()

    def attch_shared_data_collector(self, shared_data_collector: SharedDataCollector) -> None:
        self.shared_data_collector = shared_data_collector


class ActionStep(Step):
    def __init__(self) -> None:
        super().__init__()


class NoActionStep(Step):
    def __init__(self) -> None:
        super().__init__()

    def run(self) -> Step:
        print("NoActionStep")

    def get_next_steps(self) -> List[Step]:
        return []
