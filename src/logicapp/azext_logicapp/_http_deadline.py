# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import io
import time
from http.client import HTTPConnection


def remaining_timeout(deadline, idle_timeout=None):
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError("HTTP observation deadline expired.")
    return min(remaining, idle_timeout) if idle_timeout is not None else remaining


class _DeadlineReader(io.RawIOBase):
    def __init__(self, source, sock, deadline):
        super().__init__()
        self.source = source
        self.sock = sock
        self.deadline = deadline
        self.idle_timeout = sock.gettimeout()

    def readable(self):
        return True

    def fileno(self):
        return self.source.fileno()

    def readinto(self, buffer):
        self.sock.settimeout(remaining_timeout(self.deadline, self.idle_timeout))
        received = self.source.readinto(buffer)
        remaining_timeout(self.deadline)
        return received

    def close(self):
        try:
            self.source.close()
        finally:
            super().close()


class DeadlineSocket:
    """Budget raw receives, before HTTP buffering can aggregate trickled bytes."""

    def __init__(self, sock, deadline):
        self.sock = sock
        self.deadline = deadline
        self.idle_timeout = sock.gettimeout()

    def __getattr__(self, name):
        return getattr(self.sock, name)

    def _set_timeout(self):
        self.sock.settimeout(remaining_timeout(self.deadline, self.idle_timeout))

    def recv(self, *args, **kwargs):
        self._set_timeout()
        data = self.sock.recv(*args, **kwargs)
        remaining_timeout(self.deadline)
        return data

    def recv_into(self, *args, **kwargs):
        self._set_timeout()
        received = self.sock.recv_into(*args, **kwargs)
        remaining_timeout(self.deadline)
        return received

    def send(self, *args, **kwargs):
        self._set_timeout()
        sent = self.sock.send(*args, **kwargs)
        remaining_timeout(self.deadline)
        return sent

    def sendall(self, *args, **kwargs):
        self._set_timeout()
        self.sock.sendall(*args, **kwargs)
        remaining_timeout(self.deadline)

    def makefile(self, mode="rb", buffering=None):
        if mode != "rb":
            raise ValueError("Deadline HTTP readers require binary input.")
        source = self.sock.makefile("rb", buffering=0)
        reader = _DeadlineReader(source, self.sock, self.deadline)
        return reader if buffering == 0 else io.BufferedReader(reader)


class DeadlineHTTPConnection(HTTPConnection):
    def __init__(self, *args, deadline, **kwargs):
        super().__init__(*args, **kwargs)
        self.deadline = deadline

    def connect(self):
        self.timeout = remaining_timeout(self.deadline, self.timeout)
        super().connect()
        self.sock = DeadlineSocket(self.sock, self.deadline)
        try:
            remaining_timeout(self.deadline)
        except TimeoutError:
            self.sock.close()
            raise
