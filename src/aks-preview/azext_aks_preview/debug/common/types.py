from __future__ import annotations

import json
from typing import Any, List, NamedTuple, Type

from azure.cli.core.commands import progress

from ..controller.data_broker import DataBroker


class Step:
    def __init__(self) -> None:
        self.summary: str = ""
        self.next_steps: List[StepBuilder] = []

    async def run(self) -> None:
        pass

    def get_summary(self) -> str:
        return self.summary

    def get_next_steps(self) -> List[StepBuilder]:
        return self.next_steps


class DebugStep(Step):
    entry_step_for_scenarios = []

    def __init__(self, data=None) -> None:
        super().__init__()
        self.data = data
        self.data_broker = None

    def attach_data_broker(self, data_broker: DataBroker) -> None:
        self.data_broker = data_broker


class ActionStep(Step):
    def __init__(self, data=None) -> None:
        super().__init__()
        self.data = data


class StepBuilder(NamedTuple):
    cls: Type[Step]
    data: Any

    def get_identifier(self) -> str:
        return self.cls.__name__ + json.dumps(self.data)


class StepBundle(NamedTuple):
    step: Step
    builder: StepBuilder
    progress_hook: progress.ProgressHook
