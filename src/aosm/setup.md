### Prerequisites

1. `python 3.8+`


### Dev environment setup

Follow [https://github.com/Azure/azure-cli-dev-tools](https://github.com/Azure/azure-cli-dev-tools)

Clone both azure-cli and azure-cli-extensions

Note for azure-cli-extensions we are currently on a fork : https://github.com/jddarby/azure-cli-extensions
```bash
# Go into your git clone of az-cli-extensions
cd az-cli-extensions

# Create a virtual environment to run in
python3.8 -m venv ~/.virtualenvs/az-cli-env
source ~/.virtualenvs/az-cli-env/bin/activate

# Ensure you have pip
python -m pip install -U pip

# Install azdev
pip install azdev

# Install all the python dependencies you need
azdev setup --cli /home/developer/code/azure-cli --repo .

# Add the extension to your local CLI
azdev extension add aosm
```
### Generating the AOSM Python SDK
TODO

### VSCode environment setup.

Make sure your VSCode is running in the same python virtual environment

### Linting and Tests
```bash
azdev style aosm
azdev linter --include-whl-extensions aosm
(Not written any tests yet)
azdev test aosm
```
You can use python-static-checks in your dev environment if you want, to help you:
```bash
pip3 install -U --index-url https://pkgs.dev.azure.com/msazuredev/AzureForOperators/_packaging/python/pypi/simple/ python-static-checks==4.0.0
python-static-checks fmt
```
