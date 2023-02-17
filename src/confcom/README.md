# Microsoft Azure CLI 'confcom' Extension

- [Microsoft Azure CLI 'confcom' Extension](#microsoft-azure-cli-confcom-extension)
  - [Repository](#repository)
  - [Prerequisites](#prerequisites)
  - [Installation Instructions (End User)](#installation-instructions-end-user)
  - [Generating a confidential execution enforcement (cce) policy](#generating-a-confidential-execution-enforcement-cce-policy)
  - [Setup and Instructions for Developers](#setup-and-instructions-for-developers)
    - [Setup Development Environment](#setup-development-environment)
    - [Build Extension Binary(Wheel) and Run Extension Tests](#build-extension-binarywheel-and-run-extension-tests)
    - [Miscellaneous](#miscellaneous)
  - [Azure Container Registration authentication](#azure-container-registration-authentication)
    - [Authentication with service principals](#authentication-with-service-principals)
    - [Authenticate with Azure managed identity](#authenticate-with-azure-managed-identity)
  - [Trademarks](#trademarks)

## Repository

- <https://github.com/Azure/ACC-CLI/tree/main/az_extensions/confcom>

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

## Docker Standalone Instructions (End User)

### TODO: change this image when it goes to a public registry

1. Download the docker container: `fishersnpregistry.azurecr.io/confcom-cli:clean-room`
2. Run:

  ```bash
    docker run -v "$(pwd):/temp" -v /var/run/docker.sock:/var/run/docker.sock fishersnpregistry.azurecr.io/confcom-cli:clean-room az confcom acipolicygen -a temp/template.json
  ```

Notes:

- The first `-v` flag can be changed to go wherever in the local machine that has the input files for generating policies. For example, the ARM Template that is going to be used.
- The second `-v` is for mounting the Docker socket into the container, so Docker must be running on the host machine in order to generate policies from images that are contained within the Docker daemon. This includes images that need to be pulled from a remote registry.
- The path to the input file in the `az confcom acipolicygen` snippet must line up with where the local folder is getting mounted in the first `-v` flag. For example, above we are mounting to `/temp` in the container so the CLI command will be `az confcom acipolicygen -a /temp/template.json` because `template.json` is in the current local directory.

## Installation Instructions (End User)

1. Install Azure CLI through following ways:
   1. Option 1: (Windows and Linux) use `PyPI/pip(comes with 64-bit python)` to install `azure-cli`

      ```bash
      python3 -m pip install azure-cli
      ```

      - **Notes for Windows user ONLY**:  even you have 64-bit python3 installed already, windows version **Azure CLI** installation package comes with a 32-bit python, which is not supported for now. So please use the `PyPI/pip` solution to install `azure-cli`.

   2. Option 2:(Linux Only) [Install through Linux Package Tools](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-linux?pivots=apt).

## Generating a confidential execution enforcement (cce) policy

Please see [ACIConfidentialSecurityPolicySpec](https://microsoft-my.sharepoint.com/:w:/p/sewong/EV7PkPR5kWJMnmqm9TtWt0QBhmpYg1HqKwknw07DleugKQ?e=zLQZOl)

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft
trademarks or logos is subject to and must follow
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
