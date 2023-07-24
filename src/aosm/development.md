### Prerequisites

1. `python 3.8+`


### Dev environment setup

Follow [https://github.com/Azure/azure-cli-dev-tools](https://github.com/Azure/azure-cli-dev-tools)

Clone both azure-cli and azure-cli-extensions

Note for azure-cli-extensions we are currently on a fork : https://github.com/jddarby/azure-cli-extensions
```bash
# Go into your git clone of az-cli-extensions
cd azure-cli-extensions

# Create a virtual environment to run in
python3.8 -m venv ~/.virtualenvs/az-cli-env
source ~/.virtualenvs/az-cli-env/bin/activate

# Ensure you have pip
python -m pip install -U pip

# Install azdev
pip install azdev

git checkout add-aosm-extension

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
azdev test aosm

cd src/aosm
mypy . --ignore-missing-imports --no-namespace-packages --exclude "azext_aosm/vendored_sdks/*"
```
The standard Python tool, `black`, is useful for automatically formatting your code.

You can use python-static-checks in your dev environment if you want, to help you:
```bash
pip3 install -U --index-url https://pkgs.dev.azure.com/msazuredev/AzureForOperators/_packaging/python/pypi/simple/ python-static-checks==4.0.0
python-static-checks fmt
```

### Unit tests
To run unit tests run `azdev test aosm`.

To get code coverage run:
```bash
pip install coverage 
cd src/aosm
coverage erase
coverage run -m pytest .
coverage report --include="*/src/aosm/*" --omit="*/src/aosm/azext_aosm/vendored_sdks/*","*/src/aosm/azext_aosm/tests/*" -m
```

### Pipelines
The pipelines for the Azure CLI run in ADO, not in github.
To trigger a pipeline you need to create a PR against main.
Until we do the initial merge to main we don't want to have a PR to main for every code review.
Instead we have a single PR for the `add-aosm-extension` branch: https://github.com/Azure/azure-cli-extensions/pull/6426
Once you have merged your changes to `add-aosm-extension` then look at the Azure Pipelines under https://github.com/Azure/azure-cli-extensions/pull/6426/checks, click on the link that says `<X> errors / <Y> warnings`.

