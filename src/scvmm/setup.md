### Prerequisites

1. `python 3.8+`
2. `nodejs lts`

### Dev environment setup

```bash
# Set up azcli extension environent.
azext_name="scvmm" # Folder name of the extension.
export azcli="$HOME/Code/azure/cli" # Path to the base folder for azcli development.
export vmwop="$HOME/Code/AzureArc-VMwareOperator" # path to Operator code.
autorest_version="latest" # Version of autorest. You can use "latest", but make sure it works.

mkdir -p $azcli/sdks # This folder will contain sdks generated using autorest,
cd $azcli
export AZCLI_SRC_PATH="$azcli/azure-cli" # Include this in the shell source like ~/.bashrc or ~/.zshrc

git clone https://github.com/Azure/azure-cli.git
git clone https://github.com/Azure/azure-cli-extensions.git
git clone git@github.com:Azure/azure-rest-api-specs.git swagger-prod # Contains the swagger

# Set up python environment.
python -m venv .venv
source .venv/bin/activate # azcli extension development should be done under some virtual environment.
pip install --upgrade pip
pip install azdev
azdev setup -c $azcli/azure-cli
azdev extension repo add $azcli/azure-cli-extensions # azdev will now know that this folder contains source code for extensions under development.

export azext="$azcli/azure-cli-extensions/src/$azext_name"

# Copy the azcli code to `azure-cli-extensions/src`, as this is the registered path for all azcli extensions.
# You cannot add extensions from any other path.
cp -r $vmwop/src/AzCli/scvmm $azext
cd $azext/..
azdev extension add $azext_name

# sdk generation using autorest.
npm i -g autorest

versions_flags=(--version=3.7.4 --use=@autorest/python@~5.12.0 --use=@autorest/modelerfour@~4.19.3)

# Path to the readme.md may vary. The following is the path for scvmm.
autorest $azcli/swagger-prod/specification/scvmm/resource-manager/readme.md --track2 --python --python-sdks-folder=$azcli/sdks --python-mode=update "${versions_flags[@]}"
# Remove the existing sdk.
rm -rf $azext/azext_scvmm/vendored_sdks
# Replace the old sdk by the newly generated sdk. The patch may vary for other extensions.
mv $azcli/sdks/azure-mgmt/scvmm $azext/azext_scvmm/vendored_sdks
```

### VSCode environment setup.

The .vscode.example folder contains sample vscode workspace configuration.

```bash
# Please ensure python environment is activated.
# black is used for formatting python files, flake8 is for linting them.
pip install black flake8
cd $azext
cp -r .vscode.example .vscode
sed -i "s~\$azcli~$azcli~g" .vscode/settings.json
code .
```

### Linting and Tests

azdev style scvmm
azdev linter --include-whl-extensions scvmm
azdev test scvmm

### Useful resources

1. [Python version and environment manager](https://github.com/pyenv/pyenv-installer).

```bash
# Install prerequisites for ubuntu.
sudo apt install -y build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
xz-utils tk-dev libffi-dev liblzma-dev python-openssl git
curl https://pyenv.run | bash
exec $SHELL
pyenv install 3.8.10
```

2. [Lightweight nodejs version manager](https://github.com/mklement0/n-install)

```
curl -L https://bit.ly/n-install | bash -s -- -y lts
exec $SHELL
```

3. Python formatter : https://github.com/psf/black
