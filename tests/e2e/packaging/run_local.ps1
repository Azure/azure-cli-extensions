# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
#
# Convenience runner for the e2e packaging tests. Resolves the Python
# interpreter portably in this order so it works the same way locally and in
# any contributor's checkout:
#
#   1. -Python <path> argument (explicit override)
#   2. $env:VIRTUAL_ENV  (the venv the developer has activated)
#   3. `python` on PATH  (anything else, including a system install)
#
# Anything else (e.g. a hard-coded path to a personal venv) is a portability
# bug -- this script must not require a particular folder name to exist.

[CmdletBinding()]
param(
    [switch]$SmokeOnly,
    [string]$Python
)

$ErrorActionPreference = "Stop"

if (-not $Python) {
    if ($env:VIRTUAL_ENV) {
        if ($IsWindows -or $env:OS -eq "Windows_NT") {
            $Python = Join-Path $env:VIRTUAL_ENV "Scripts\python.exe"
        } else {
            $Python = Join-Path $env:VIRTUAL_ENV "bin/python"
        }
    } else {
        $cmd = Get-Command python -ErrorAction SilentlyContinue
        if (-not $cmd) {
            throw "No Python interpreter found. Activate a venv or pass -Python <path>."
        }
        $Python = $cmd.Source
    }
}

if (-not (Test-Path $Python)) {
    throw "Python interpreter not found at: $Python"
}

$pytestArgs = @("-m", "pytest", "tests/e2e/packaging", "-q")
if ($SmokeOnly) {
    $pytestArgs += @("-m", "smoke")
}

& $Python @pytestArgs
