from typing import Callable, List
from msrest.polling import LROPoller
from knack.log import get_logger

logger = get_logger(__name__)

class DataStoreCreationStep():
    def __init__(self, name: str, delegate: Callable[[], LROPoller], params):
        self.delegate = delegate
        self.params = params
        self.name = name

class DataStoreCreator():
    def __init__(self, steps: List[DataStoreCreationStep]):
        if not steps:
            raise 'Steps cannot be empty'
        self.steps = steps
        self._current_poller = None
        self._is_active = True

    def create(self):
        self._run_step()
        return self
    def _run_step(self, *args):
        if self.steps:
            if args:
                print(args)
            step = self.steps.pop(0)
            logger.info('Configuring %s', step.name)
            self._current_poller = step.delegate(**step.params)
            self._current_poller.add_done_callback(self._run_step)
        else:
            self._is_active = False
    def result(self, timeout):
        if self._current_poller:
            self._current_poller.result(timeout)

    def done(self):
        if self._is_active:
            return False
        return True
