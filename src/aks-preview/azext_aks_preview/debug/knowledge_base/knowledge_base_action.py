from ..common.types import ActionStep


class ActionStepPrompt(ActionStep):
    def __init__(self, msg) -> None:
        super().__init__()
        self.summary = "[Action]: Prompt"
        self.msg = msg

    async def run(self) -> None:
        print(self.msg)


class NoActionStep(ActionStep):
    def __init__(self) -> None:
        super().__init__()
        self.summary = "[Action]: No action required"

    async def run(self) -> None:
        return
