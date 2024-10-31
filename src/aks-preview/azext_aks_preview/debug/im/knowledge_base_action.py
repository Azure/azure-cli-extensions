from .types import Step, ActionStep


class ActionStepA(ActionStep):
    def __init__(self) -> None:
        super().__init__()

    def run(self) -> Step:
        print(self)


class ActionStepB(ActionStep):
    def __init__(self) -> None:
        super().__init__()

    def run(self) -> Step:
        print(self)


class ActionStepC(ActionStep):
    def __init__(self) -> None:
        super().__init__()

    def run(self) -> Step:
        print(self)
