
# Change 1:
# I did manual edits to README.md and setup.py files. Make sure you restore 
# this version after you re-emit

& git -C $PSScriptRoot restore -- README.md
if ($LASTEXITCODE -ne 0) {
    throw "Failed to restore README.md after CLI emission."
}

& git -C $PSScriptRoot restore -- setup.py
if ($LASTEXITCODE -ne 0) {
    throw "Failed to restore README.md after CLI emission."
}

# Change 2:
# Replaces 2026-09-15-preview with 2026-07-15-preview in azext_foundry_cost_control
# and its subfolders, excluding azext_foundry_cost_control\tests.
# Run from Windows Command Prompt:
# powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\PostEmitter.ps1

$ErrorActionPreference = 'Stop'

$oldValue = [System.Text.Encoding]::ASCII.GetBytes('2026-09-15-preview')
$newValue = [System.Text.Encoding]::ASCII.GetBytes('2026-07-15-preview')
$targetDirectory = Join-Path $PSScriptRoot 'azext_foundry_cost_control'
$excludedDirectory = [System.IO.Path]::GetFullPath(
    (Join-Path $targetDirectory 'tests')
).TrimEnd('\') + '\'
$updatedFileCount = 0
$replacementCount = 0

Get-ChildItem -LiteralPath $targetDirectory -File -Recurse | ForEach-Object {
    $filePath = [System.IO.Path]::GetFullPath($_.FullName)
    if ($filePath.StartsWith($excludedDirectory, [System.StringComparison]::OrdinalIgnoreCase)) {
        return
    }

    $content = [System.IO.File]::ReadAllBytes($filePath)
    $fileReplacementCount = 0

    for ($index = 0; $index -le $content.Length - $oldValue.Length; $index++) {
        $matches = $true
        for ($offset = 0; $offset -lt $oldValue.Length; $offset++) {
            if ($content[$index + $offset] -ne $oldValue[$offset]) {
                $matches = $false
                break
            }
        }

        if ($matches) {
            [System.Array]::Copy($newValue, 0, $content, $index, $newValue.Length)
            $fileReplacementCount++
            $index += $oldValue.Length - 1
        }
    }

    if ($fileReplacementCount -gt 0) {
        [System.IO.File]::WriteAllBytes($filePath, $content)
        $updatedFileCount++
        $replacementCount += $fileReplacementCount
        Write-Host "Updated: $filePath ($fileReplacementCount replacement(s))"
    }
}

Write-Host "Complete: $replacementCount replacement(s) in $updatedFileCount file(s)."

# Change 3:
# Use CoPilot to fix an emitter bug (?). Use this prompt: 
#  Run "cls & azdev test foundry-cost-control --live --debug" and fix the resulting error. A similar fix was made in the past, so you can look at this commit for reference: https://github.com/Azure/azure-cli-extensions/pull/10298/changes/d981f14597cdcd118c3ab7b17264057944496a97
#
