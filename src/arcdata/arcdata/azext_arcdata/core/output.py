# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from azext_arcdata.core.util import singleton
from knack.util import CommandResultItem
from io import TextIOWrapper
from collections import OrderedDict

import sys

__all__ = ["OutputStream", "IOBuffer"]

# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #


@singleton
class OutputStream(object):
    __ORIGINAL_STDOUT__ = sys.stdout
    """
    Placeholder for the original system stdout.
    """

    __ORIGINAL_STDERR__ = sys.stderr
    """
    Placeholder for the original system stderr.
    """

    terminator = "\n"

    def __init__(self):
        self.repurpose()

    @property
    def stdout(self):
        return self._stdout

    @property
    def stderr(self):
        return self._stderr

    def repurpose(self):
        # if OutputProducer.structured_output:
        #    sys.stdout = stdout = IOBuffer(BytesIO(), sys.stdout.encoding)
        #    sys.stderr = stderr = IOBuffer(BytesIO(), sys.stderr.encoding)
        # else:
        stdout = Stdout()
        stderr = Stderr()

        self._stdout = stdout
        self._stderr = stderr

    def flush(self):
        # -- capture any buffered stdout --
        sys.stdout.seek(0)
        stdout = sys.stdout.read().rstrip().split(self.terminator)
        sys.stdout = self.__ORIGINAL_STDOUT__
        sys.stdout.flush()
        self._stdout = [] if len(stdout) == 1 and stdout[0] == "" else stdout

        # -- capture any buffered stderr --
        sys.stderr.seek(0)
        stderr = sys.stderr.read().rstrip().split(self.terminator)
        sys.stderr = self.__ORIGINAL_STDERR__
        sys.stderr.flush()
        self._stderr = [] if len(stderr) == 1 and stderr[0] == "" else stderr

        return self._stdout, self._stderr


# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #


class IOBuffer(TextIOWrapper):
    terminator = "\n"

    def write(self, obj):
        """
        Write string to stream.
        :param obj: The item written to the stream as a string.
        :return: Returns the number of characters written (which is always
                 equal to the length of the string).
        """
        from knack.output import format_table, format_json

        try:
            if isinstance(obj, list):
                obj = format_table(CommandResultItem(obj, is_query_active=True))
            elif isinstance(obj, dict) or isinstance(obj, OrderedDict):
                obj = format_json(CommandResultItem(obj, is_query_active=True))
            else:  # primitives
                obj = str(obj).rstrip()

            if obj:
                return super(IOBuffer, self).write(obj + self.terminator)
        except TypeError:
            # redirect encoded byte strings directly to buffer
            return super(IOBuffer, self).buffer.write(obj)


# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #


class StdIO(str):
    """
    StdIO represents the base IOSink for `stdout` and `stderr`. It provides a
    blocking IOSink so using this to write will block until the output is
    written.
    """

    terminator = "\n"

    def __new__(cls, io=sys.stdout, color=None):
        obj = super(StdIO, cls).__new__(cls)
        obj.io = io
        obj.color = color
        return obj

    @property
    def lines(self):
        return self.split(self.terminator)

    @property
    def qlines(self):
        return [line.split() for line in self.split(self.terminator)]

    def write(self, obj, color=None, end="\n"):
        """
        A display stdout or stderro print hook equipped with a unicode
        fallback hook.

        Pseudo code originating from:
        https://docs.python.org/3/library/sys.html#sys.displayhook

        :param obj: The text string to write to stdout or stderr.
        :param color: Optional text color.
        :param end: Include an ending newline to stdout or stderr.
        """
        import colorama
        from knack.output import format_json, format_table

        def color_output(msg, c):
            enable_color = False
            try:
                # Color if tty stream available
                enable_color = (self.color or c) and sys.stdin.isatty()
            except AttributeError:
                pass

            if enable_color:
                try:
                    c = c or self.color
                    msg = "{}{}{}".format(c, obj, colorama.Style.RESET_ALL)
                except KeyError:
                    pass

            return msg

        try:
            if isinstance(obj, list):
                obj = format_table(CommandResultItem(obj, is_query_active=True))
            elif isinstance(obj, dict) or isinstance(obj, OrderedDict):
                obj = format_json(CommandResultItem(obj, is_query_active=True))
            else:  # primitives
                obj = str(obj)

            self.io.write(color_output(obj, color))
        except ValueError:
            # -- pytest --
            sys.stdout.write(obj)
            if end:
                sys.stdout.write(end)
            return
        except UnicodeEncodeError:
            # Fallback shim to ascii with replace with backslashed escape
            # sequences
            bytes_string = obj.encode(self.io.encoding, "backslashreplace")
            if hasattr(self.io, "buffer"):
                self.io.buffer.write(bytes_string)
            else:
                self.io.write(bytes_string.decode(self.io.encoding, "strict"))
        if end:
            self.io.write(end)

        self.io.flush()


class Stdout(StdIO):
    def __new__(cls):
        return super(Stdout, cls).__new__(cls, io=sys.stdout)


class Stderr(StdIO):
    def __new__(cls):
        from colorama import Fore

        return super(Stderr, cls).__new__(cls, io=sys.stderr, color=Fore.RED)
