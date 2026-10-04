# ArcData Extension for Azure CLI

[![Build Status](https://msdata.visualstudio.com/Tina/_apis/build/status/azure-cli-extension/azure-cli-extension?branchName=master)](https://msdata.visualstudio.com/Tina/_build/latest?definitionId=20974&branchName=master)
[![Stage Status](https://msdata.vsrm.visualstudio.com/_apis/public/Release/badge/febab204-74cf-49d9-8bd9-65ce89e60d0b/140/578)](https://msdata.visualstudio.com/Tina/_release?_a=releases&view=all&definitionId=140)
[![Production Status](https://msdata.vsrm.visualstudio.com/_apis/public/Release/badge/febab204-74cf-49d9-8bd9-65ce89e60d0b/140/579)](https://msdata.visualstudio.com/Tina/_release?_a=releases&view=all&definitionId=140)



The ArcData Extension for Azure CLI adds the `sql mi-arc` command to the Azure CLI 2.0.

## Development setup

[Development setup](./doc/dev-setup)

##### LINUX and macOS
```bash
cd ./arcdata/projects/azure-cli-extension
export AZURE_EXTENSION_DIR=$(pwd)
python3 ./scripts/dev_setup.py
source ./env/bin/activate
az extension list
```

##### Windows
```bash
cd .\arcdata\projects\azure-cli-extension
set AZURE_EXTENSION_DIR=%cd%
python .\scripts\dev_setup.py
.\env\Scripts\activate.bat
az extension list
```

## Quick start usage

1. [Install the Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli). You must have at least `v2.0.69`, which you can verify with `az --version` command.

1. Add the ArcData Extension `az extension add --name arcdata`

## Usage

```bash
$az [group] [subgroup] [command] {parameters}
```

Adding the ArcData Extension adds the `sql mi-arc` group. For usage and help content for any command, 
pass in the `--help` parameter, for example:

```bash
$ az sql mi-arc --help
```

## Contribute

See our [contribution guidelines](CONTRIBUTING.md) to learn how you can contribute to this project.

## License

[MIT License](LICENSE)
