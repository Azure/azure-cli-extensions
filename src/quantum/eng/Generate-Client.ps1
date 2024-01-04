# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

<#
.SYNOPSIS
(Re)Generate the underlying Azure Quantum Python data-plane or control-plane client for the CLI based on the latest published Swagger.
.DESCRIPTION
(Re)Generate the underlying Azure Quantum Python data-plane or control-plane client for the CLI based on the latest published Swagger.
.PARAMETER SwaggerRepoUrl
The URL of the git repo that contains the Swagger and AutoRest ReadMe.md configurations (defaults to "https://github.com/Azure/azure-rest-api-specs")
.PARAMETER SwaggerRepoBranch
The name of the swagger repo branch (defaults to "main")
.PARAMETER SwaggerTagVersion
The Swagger version to be used (defaults to "", which will use the default tag from the main ReadMe.md)
.PARAMETER ClientToGenerate
Select which client to generate: data-plane or control-plane (defaults to "data-plane")

.EXAMPLE
./eng/Generate-Client.ps1

# Regenerate the data-plane client using the latest published Swagger from the official repo

.EXAMPLE
./eng/Generate-Client.ps1 -SwaggerRepoBranch "feature/quantum/update-clients"

# Regenerate the data-plane client using the Swagger from the official repo, but from a feature branch

.EXAMPLE
./eng/Generate-Client.ps1 -SwaggerTagVersion "package-2019-11-04-preview"

# Regenerate the data-plane client using the an older version of the Swagger

.EXAMPLE
./eng/Generate-Client.ps1 -ClientToGenerate "control-plane"

# Regenerate the control-plane client using the latest published Swagger from the official repo

#>

[CmdletBinding()]
Param (
    [string] $SwaggerRepoUrl = "https://github.com/Azure/azure-rest-api-specs",
    [string] $SwaggerRepoBranch = "main",
    [string] $SwaggerTagVersion,
    [string] $ClientToGenerate = "data-plane"
)

# Select which client to generate
if ([string]::IsNullOrEmpty($ClientToGenerate) -or ($ClientToGenerate -eq "data-plane"))
{
    $AutoRestConfig = "$SwaggerRepoUrl/blob/$SwaggerRepoBranch/specification/quantum/data-plane/readme.md"
    $OutputFolder = "./azext_quantum/vendored_sdks/azure_quantum/"
}
else
{
    if ($ClientToGenerate -eq "control-plane")
    {
        $AutoRestConfig = "$SwaggerRepoUrl/blob/$SwaggerRepoBranch/specification/quantum/resource-manager/readme.md"
        $OutputFolder = "./azext_quantum/vendored_sdks/azure_mgmt_quantum/"
    }
    else
    {
        Write-Error "ERROR: ClientToGenerate parameter not recognized."
        return -1
    }
}

Write-Verbose "Output folder: $OutputFolder"
Write-Verbose "Deleting previous output folder contents"
if (Test-Path $OutputFolder)
{
    Remove-Item $OutputFolder -Recurse | Write-Verbose
}

Write-Verbose "Installing latest AutoRest client"
npm install -g autorest@latest | Write-Verbose

if ([string]::IsNullOrEmpty($SwaggerTagVersion))
{
    Write-Verbose "Generating the client based on:`nConfig: $AutoRestConfig"
    autorest $AutoRestConfig `
        --verbose `
        --python `
        --python-mode=cli `
        --output-folder=$OutputFolder `
        | Write-Verbose
}
else
{
    Write-Verbose "Generating the client based on:`nConfig: $AutoRestConfig`nTag: $SwaggerTagVersion"
    autorest $AutoRestConfig `
        --verbose `
        --python `
        --python-mode=cli `
        --tag=$SwaggerTagVersion `
        --output-folder=$OutputFolder `
        | Write-Verbose
}
