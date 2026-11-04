#
# Run this script after re-emitting the code: 
#   powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\PostEmitter.ps1
#

# Change 1:
# I did manual edits to README.md and setup.py files. Make sure you restore 
# this version after you re-emit

& git -C $PSScriptRoot restore -- README.md
if ($LASTEXITCODE -ne 0) {
    throw "Failed to restore README.md after CLI emission."
}

& git -C $PSScriptRoot restore -- setup.py
if ($LASTEXITCODE -ne 0) {
    throw "Failed to restore setup.py after CLI emission."
}

# Change 2:
# Use CoPilot to fix an emitter bug (?). Use this prompt: 
#  Run "cls & azdev test foundry-cost-control --live --debug" and fix the resulting error. A similar fix was made in the past, so you can look at this commit for reference: https://github.com/Azure/azure-cli-extensions/pull/10298/changes/d981f14597cdcd118c3ab7b17264057944496a97
#
