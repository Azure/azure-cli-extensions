from .types import Step, ActionStep


class ActionStepA(ActionStep):
    def __init__(self) -> None:
        super().__init__()

    def run(self) -> Step:
        print("ActionStepA")


class ActionStepB(ActionStep):
    def __init__(self) -> None:
        super().__init__()

    def run(self) -> Step:
        print("ActionStepB")


class ActionStepC(ActionStep):
    def __init__(self) -> None:
        super().__init__()

    def run(self) -> Step:
        print("ActionStepC")
