from typing import Dict, List
from .tool_manager import ToolManager
from .data_broker import DataBroker
from ..knowledge_base.knowledge_base import KnowledgeBase
from ..common.types import DebugStep, StepBuilder, StepBundle

import asyncio


async def handle_step(awaitable) -> None:
    try:
        await awaitable
    except Exception as e:
        print("caught exception", e)


class Orchestrator():
    def __init__(self) -> None:
        self.executed_tasks = []
        self.running_tasks = []
        self.submitted_steps: Dict[str, StepBundle] = {}
        self.pending_steps: List[StepBuilder] = []
        self.tool_manager = ToolManager()
        self.data_broker = DataBroker(self.tool_manager)
        self.knowledge_base = KnowledgeBase()

    async def run(self, scenario: str) -> None:
        self.pending_steps = self.knowledge_base.get_debug_steps_by_scenario(scenario)

        while self.pending_steps or self.running_tasks:
            print("reconciling")
            while self.pending_steps:
                step_builder = self.pending_steps.pop(0)
                step = step_builder.cls(step_builder.data)
                step_name = step_builder.get_identifier()
                if isinstance(step, DebugStep):
                    step.attach_data_broker(self.data_broker)
                t = asyncio.create_task(handle_step(step.run()), name=step_name)
                self.running_tasks.append(t)
                self.submitted_steps[step_name] = StepBundle(step, step_builder)
                print("task added:", step_name)
                await asyncio.sleep(0.5)
            all_next_steps: List[StepBuilder] = []
            left_running_tasks = []
            for t in self.running_tasks:
                if t.done():
                    print("task done:", t.get_name())
                    self.executed_tasks.append(t)
                    step_bundle = self.submitted_steps[t.get_name()]
                    next_steps = step_bundle.step.get_next_steps()
                    for ns in next_steps:
                        if ns in all_next_steps:
                            print("step already in all_next_steps, skipping")
                            continue
                        if ns in map(lambda x: x.builder, self.submitted_steps.values()):
                            print("step already submitted, skipping")
                            continue
                        all_next_steps.append(ns)
                else:
                    left_running_tasks.append(t)
            self.running_tasks = left_running_tasks
            self.pending_steps.extend(all_next_steps)
            await asyncio.sleep(1)
            # await asyncio.gather(*self.running_tasks)
        print("executed_tasks", self.executed_tasks)
        print("running_tasks", self.running_tasks)
        print("submitted_steps", self.submitted_steps)
        print("pending_steps", self.pending_steps)
        return
