from ..common.types import ActionStep


class ActionStepPrompt(ActionStep):
    def __init__(self, data=None) -> None:
        super().__init__(data=data)
        self.summary = "[Action]: Prompt"

    async def run(self) -> None:
        print(self.data)


class NoActionStep(ActionStep):
    def __init__(self, data=None) -> None:
        super().__init__(data=data)
        self.summary = "[Action]: No action required"

    async def run(self) -> None:
        return
