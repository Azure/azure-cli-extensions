# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from timeit import default_timer as timer


class Timer():
    def __init__(self):
        super().__init__()
        self._start = 0
        self._elapsed = 0

    def start(self):
        self._start = timer()

    def stop(self):
        self._elapsed = timer() - self._start

    def __enter__(self):
        self.start()

    def __exit__(self, *_):
        self.stop()

    @property
    def elapsed(self) -> float:
        return self._elapsed

    @property
    def elapsed_ms(self) -> float:
        return self.elapsed * 1000
