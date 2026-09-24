::------------------------------------------------------------------------------
:: Copyright (c) Microsoft Corporation. All rights reserved.
::------------------------------------------------------------------------------

:: Description:
::
:: Instructions to be invoked under the build CI pipeline in AzureDevOps.
::
:: Kickoff wheel install tests against different python versions in `$TOX_ENV`.
::
:: Prerequisites:
::
::   ENV VARS:
::
::   - export TOX_ENV=py36|py37|py38
::
:: Usage:
::
:: $ pipeline-windows.cmd

@echo off
SetLocal EnableDelayedExpansion

set REPO_ROOT_DIR=%~dp0..\..\..\
set DIST_DIR=%~dp0..\..\..\output\unit-tests
set AZURE_EXTENSION_DIR=%REPO_ROOT_DIR%

if "%TOX_ENV%"=="" (
    echo TOX_ENV environment variable not set to (py311)
)

if "%PAT_TOKEN%"=="" (
    echo No PAT_TOKEN set
)

if exist %DIST_DIR% rmdir /s /q %DIST_DIR%
mkdir %DIST_DIR%

:: Install arcdata azure-cli extension to navigate the build/task processes
:: CALL python %REPO_ROOT_DIR%\scripts\dev_setup.py

set INDEX_URL=https://build:%PAT_TOKEN%@msdata.pkgs.visualstudio.com/Tina/_packaging/Tina_PublicPackages/pypi/simple

CALL pip install -r %REPO_ROOT_DIR%\dev-requirements.txt --index-url %INDEX_URL%
CALL pip install -e %REPO_ROOT_DIR%\arcdata --index-url %INDEX_URL%
CALL pip install -e %REPO_ROOT_DIR%\tools/pytest-az --index-url %INDEX_URL%

python --version
python3 --version
copy %REPO_ROOT_DIR%\scripts\ci\unit-tests\tox.ini %DIST_DIR%
CALL tox -e %TOX_ENV% -c %DIST_DIR%\tox.ini
if %ERRORLEVEL% NEQ 0 EXIT 1