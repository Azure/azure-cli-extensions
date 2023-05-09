# Microsoft Azure CLI 'confcom' Extension

- [Microsoft Azure CLI 'confcom' Extension](#microsoft-azure-cli-confcom-extension)
  - [Repository](#repository)
  - [Prerequisites](#prerequisites)
  - [Installation Instructions (End User)](#installation-instructions-end-user)
  - [Current Limitations](#current-limitations)
  - [Trademarks](#trademarks)

## Repository

- <https://github.com/Azure/azure-cli-extensions/tree/main/src/confcom>

## Prerequisites

**MacOS** is **NOT** supported yet

- **64-bit** `Python 3.6+` and `pip`
  - **64-bit** **Windows 10** or later
    - Install python3 version 3.6+ through [official download](https://www.python.org/downloads/)
    - or chocolatey: `choco install python`
  - Or **64-bit** Linux Distribution System, **Ubuntu 18.04** or later is recommended
    - Ubuntu 18.04 or later comes with python 3.6+ by default
- Docker Daemon
  - Linux(Ubuntu):

    ```bash
    sudo apt install docker.io
    ```

  - Windows: [Docker Desktop](https://www.docker.com/products/docker-desktop) and [WSL2](https://docs.microsoft.com/en-us/windows/wsl/install)

## Installation Instructions (End User)

1. Install Azure CLI through following ways:
   1. Option 1: (Windows and Linux) use `PyPI/pip(comes with 64-bit python)` to install `azure-cli`

      ```bash
      python3 -m pip install azure-cli
      ```

      - **Notes for Windows user ONLY**:  even you have 64-bit python3 installed already, windows version **Azure CLI** installation package comes with a 32-bit python, which is not supported for now. So please use the `PyPI/pip` solution to install `azure-cli`.

   2. Option 2:(Linux Only) [Install through Linux Package Tools](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-linux?pivots=apt).

2. Install the `confcom` extension:

   ```bash
   az extension add -n confcom
   ```

## Current Limitations

The `confcom` extension does not currently support:

- [ARM Template functions](https://learn.microsoft.com/en-us/azure/azure-resource-manager/templates/template-functions) other than `variables` and `parameters`.
- Variables and Parameters with non-primitive data types e.g. objects and arrays
- Nested and Linked ARM Templates

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft
trademarks or logos is subject to and must follow
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
