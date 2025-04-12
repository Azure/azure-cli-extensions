import asyncio
from typing import Dict, List

from azure.cli.core.commands import progress
from knack.log import get_logger

from ..common.types import DebugStep, StepBuilder, StepBundle
from ..knowledge_base.knowledge_base import KnowledgeBase
from .data_broker import DataBroker
from .tool_manager import ToolManager

logger = get_logger(__name__)


async def handle_exception(awaitable) -> None:
    try:
        await awaitable
    except Exception as e:
        logger.warning("[orchestrator] caught exception: %s", e)


class Orchestrator():
    def __init__(self) -> None:
        self.executed_tasks = []
        self.running_tasks = []
        self.submitted_steps: Dict[str, StepBundle] = {}
        self.pending_steps: List[StepBuilder] = []
        self.tool_manager = ToolManager()
        self.data_broker = DataBroker(self.tool_manager)
        self.knowledge_base = KnowledgeBase()

    def close(self):
        for b in self.submitted_steps.values():
            b.progress_hook.end()
        self.data_broker.close()

    async def run(self, scenario: str) -> None:
        self.pending_steps = self.knowledge_base.get_debug_steps_by_scenario(scenario)

        while self.pending_steps or self.running_tasks:
            logger.debug("[orchestrator] reconciling")

            while self.pending_steps:
                step_builder = self.pending_steps.pop(0)
                step = step_builder.cls(step_builder.data)
                step_name = step_builder.get_identifier()
                step_progress = progress.ProgressHook()
                step_progress.init_progress(progress.get_progress_view(False))
                step_progress.add(message="Running step: {}".format(step_name))
                if isinstance(step, DebugStep):
                    step.attach_data_broker(self.data_broker)
                t = asyncio.create_task(handle_exception(step.run()), name=step_name)
                self.running_tasks.append(t)
                self.submitted_steps[step_name] = StepBundle(step, step_builder, step_progress)
                logger.debug("[orchestrator] submitted task: %s", step_name)
                await asyncio.sleep(0.5)

            all_next_steps: List[StepBuilder] = []
            left_running_tasks = []
            for t in self.running_tasks:
                step_name = t.get_name()
                step_bundle = self.submitted_steps[step_name]
                if t.done():
                    logger.debug("[orchestrator] task done: %s", step_name)
                    self.executed_tasks.append(t)
                    next_steps = step_bundle.step.get_next_steps()
                    for ns in next_steps:
                        if ns in all_next_steps:
                            logger.debug("[orchestrator] found duplicate next step, skipping")
                            continue
                        if ns in map(lambda x: x.builder, self.submitted_steps.values()):
                            logger.debug("[orchestrator] next step already submitted, skipping")
                            continue
                        all_next_steps.append(ns)
                else:
                    step_bundle.progress_hook.update()
                    left_running_tasks.append(t)
            self.running_tasks = left_running_tasks
            self.pending_steps.extend(all_next_steps)
            await asyncio.sleep(1)
            # await asyncio.gather(*self.running_tasks)
        logger.debug("[orchestrator] executed tasks: %s", self.executed_tasks)
        logger.debug("[orchestrator] running tasks: %s", self.running_tasks)
        logger.debug("[orchestrator] submitted steps: %s", self.submitted_steps)
        logger.debug("[orchestrator] pending steps: %s", self.pending_steps)
        self.close()
        return

    def get_summary(self) -> str:
        summary = []
        for step_name, step_bundle in self.submitted_steps.items():
            summary.append("[{}] {}".format(step_name, step_bundle.step.get_summary()))
        return "\n".join(summary)
