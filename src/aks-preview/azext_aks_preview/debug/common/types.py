from __future__ import annotations
from typing import List
from ..controller.data_broker import DataBroker
from datetime import datetime


class Step:
    def __init__(self) -> None:
        self.applicable_scenarios: List[str] = []
        self.summary: str = ""
        self.next_steps: List[Step] = []

    async def run(self) -> None:
        pass

    def get_name(self) -> str:
        return self.__class__.__name__ + datetime.now().strftime("%H%M%S")

    def get_summary(self) -> str:
        return self.summary

    def get_next_steps(self) -> List[Step]:
        return self.next_steps


class DebugStep(Step):
    def __init__(self) -> None:
        super().__init__()
        self.data_broker = None

    def attach_data_broker(self, data_broker: DataBroker) -> None:
        self.data_broker = data_broker


class ActionStep(Step):
    def __init__(self) -> None:
        super().__init__()
