from typing import Dict
from .tool_manager import ToolManager
from .data_broker import DataBroker
from ..knowledge_base.knowledge_base import KnowledgeBase
from ..common.types import Step, DebugStep

import asyncio


class Orchestrator():
    def __init__(self) -> None:
        self.executed_tasks = []
        self.running_tasks = []
        self.submitted_steps: Dict[str, Step] = {}
        self.pending_steps = []
        self.tool_manager = ToolManager()
        self.data_broker = DataBroker(self.tool_manager)
        self.knowledge_base = KnowledgeBase()

    async def run(self, scenario: str) -> None:
        self.pending_steps = self.knowledge_base.get_debug_steps_by_scenario(scenario)

        while self.pending_steps or self.running_tasks:
            print("poll")
            while self.pending_steps:
                step = self.pending_steps.pop(0)
                step_name = step.get_name()
                if isinstance(step, DebugStep):
                    step.attach_data_broker(self.data_broker)
                t = asyncio.create_task(step.run(), name=step_name)
                self.running_tasks.append(t)
                self.submitted_steps[step_name] = step
                print("task added")
                await asyncio.sleep(0.5)
            all_next_steps = []
            for t in self.running_tasks:
                if t.done():
                    print("task done")
                    self.executed_tasks.append(t)
                    self.running_tasks.remove(t)
                    next_steps = self.submitted_steps[t.get_name()].get_next_steps()
                    for ns in next_steps:
                        if isinstance(ns, Step):
                            all_next_steps.append(ns)
                        elif ns in all_next_steps:
                            print("step already in all_next_steps, skipping")
                        else:
                            all_next_steps.append(ns)
            for ns in all_next_steps:
                if not isinstance(ns, Step):
                    self.pending_steps.append(ns())
                else:
                    self.pending_steps.append(ns)
            await asyncio.sleep(1)
            await asyncio.gather(*self.running_tasks)
        print("executed_tasks", self.executed_tasks)
        print("running_tasks", self.running_tasks)
        print("submitted_steps", self.submitted_steps)
        print("pending_steps", self.pending_steps)
        return
