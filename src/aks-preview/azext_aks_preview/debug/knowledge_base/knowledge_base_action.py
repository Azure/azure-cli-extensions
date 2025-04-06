from knack.log import get_logger

from ..common.types import ActionStep

logger = get_logger(__name__)


class ActionStepPrompt(ActionStep):
    def __init__(self, data=None) -> None:
        super().__init__(data=data)
        self.summary = f"Prompt: {data}"

    async def run(self) -> None:
        logger.info("[action step] Prompt: %s", self.data)


class NoActionStep(ActionStep):
    def __init__(self, data=None) -> None:
        super().__init__(data=data)
        self.summary = "No action required"

    async def run(self) -> None:
        logger.debug("[action step] No action required")
        return
