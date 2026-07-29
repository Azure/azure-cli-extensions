# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Sequence


@dataclass(frozen=True)
class CommandResult:
    command: Sequence[str]
    returncode: int
    stdout: str
    stderr: str


class CommandError(RuntimeError):
    def __init__(self, result: CommandResult):
        formatted = (
            "Command failed with exit code {code}\n"
            "command: {cmd}\n"
            "stdout:\n{out}\n"
            "stderr:\n{err}\n"
        ).format(
            code=result.returncode,
            cmd=" ".join(result.command),
            out=result.stdout,
            err=result.stderr,
        )
        super().__init__(formatted)
        self.result = result


def _resolve_executable(name: str) -> str:
    """Resolve `name` via PATH/PATHEXT.

    On Windows, tools like `az` are shipped as `az.cmd`; `subprocess.run` with a
    list argv and no `shell=True` does not perform PATHEXT lookup, so a bare
    `az` fails with FileNotFoundError. `shutil.which` honours PATHEXT and
    returns the resolved path (e.g. `C:\\...\\az.cmd`) which subprocess can
    launch directly.
    """
    if os.path.sep in name or (sys.platform == "win32" and "/" in name):
        return name
    resolved = shutil.which(name)
    return resolved or name


def run_command(
    command: Sequence[str],
    cwd: Optional[Path] = None,
    env: Optional[Dict[str, str]] = None,
    check: bool = True,
) -> CommandResult:
    merged_env = dict(os.environ)
    if env:
        merged_env.update(env)

    resolved_command = [_resolve_executable(command[0]), *command[1:]] if command else []

    completed = subprocess.run(
        resolved_command,
        cwd=str(cwd) if cwd else None,
        env=merged_env,
        text=True,
        capture_output=True,
        check=False,
    )

    result = CommandResult(
        command=command,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )

    if check and result.returncode != 0:
        raise CommandError(result)

    return result
