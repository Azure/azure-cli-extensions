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

# Install pyYAML types
python3 -m pip install types-PyYAML

# Add the extension to your local CLI
azdev extension add aosm
```
### Generating the AOSM Python SDK
TODO

### VSCode environment setup.

Make sure your VSCode is running in the same python virtual environment

### Linting and Tests

#### Style
```bash
azdev style aosm
```

Expected output:
```
===============
| Style Check |
===============

Extensions: aosm

Running pylint on extensions...
Pylint: PASSED

Running flake8 on extensions...
Flake8: PASSED
```

#### Linter
```bash
azdev linter --include-whl-extensions aosm
```

Current expected output:
```

==============
| CLI Linter |
==============

Modules: aosm

Initializing linter with command table and help files...

 Results
=========

-  pass: faulty_help_example_parameters_rule
-  pass: faulty_help_example_rule
-  pass: faulty_help_type_rule
-  pass: unrecognized_help_entry_rule
-  pass: unrecognized_help_parameter_rule
-  pass: expired_command_group
-  pass: missing_group_help
-  pass: expired_command
-  pass: missing_command_help
-  pass: no_ids_for_list_commands
-  pass: bad_short_option
-  pass: expired_option
-  pass: expired_parameter
-  pass: missing_parameter_help
-  pass: no_parameter_defaults_for_update_commands
-  pass: no_positional_parameters
-  pass: option_length_too_long
-  pass: option_should_not_contain_under_score
```

#### Typing
```bash
cd src/aosm
mypy . --ignore-missing-imports --no-namespace-packages --exclude "azext_aosm/vendored_sdks/*"
```

Expected output:
```
Success: no issues found in 33 source files
```

#### Auto-formatting
The standard Python tool, `black`, is useful for automatically formatting your code.

You can use python-static-checks in your dev environment if you want, to help you:
```bash
pip3 install -U --index-url https://pkgs.dev.azure.com/msazuredev/AzureForOperators/_packaging/python/pypi/simple/ python-static-checks==4.0.0
python-static-checks fmt
```

### Tests
The tests in this repository are split into unit tests and integration tests. Both tests live in the `tests/latest` folder and can be run using the `azdev test aosm` command. All tests are expected to pass. All unit tests and Integration tests are run as part of the pipeline. 
### Unit tests
To get code coverage run:
```bash
pip install coverage 
cd src/aosm
coverage erase
coverage run -m pytest .
coverage report --include="*/src/aosm/*" --omit="*/src/aosm/azext_aosm/vendored_sdks/*","*/src/aosm/azext_aosm/tests/*" -m
```

#### Integration tests
The integration tests are tests which run real azure CLI commands such as `az aosm nsd publish`. When running for the first time in a repository these tests will create a real resource group (with a randomly generated name starting with "cli_test_") in the subscription that is active on your account and deploy real AOSM resources. These resources will be cleaned up after the tests have run. After the first "live" run these tests will be automatically recorded in the `tests/latest/recordings` folder. These recordings record all communication between the CLI and Azure which mean that the next time the test is run it will no longer be run live but instead will be will be run against the recorded responses. This means that the tests will run much faster and will not create any real resources. The recording also does not rely on the knowledge of a subscription and the credentials will be removed from the recordings.

If one of the publish tests fails, then it might be because you have made small tweaks and the recording is now out of date.
Delete the relevant file under tests/latest/recordings (the file names match the name of the tests), and re-run the test.
If that passes it will create a new recording for you.

To find out more about integration tests see [here](https://github.com/Azure/azure-cli/blob/dev/doc/authoring_tests.md).

### Pipelines
The pipelines for the Azure CLI run in ADO, not in github.
To trigger a pipeline you need to create a PR against main.
Until we do the initial merge to main we don't want to have a PR to main for every code review.
Instead we have a single PR for the `add-aosm-extension` branch: https://github.com/Azure/azure-cli-extensions/pull/6426
Once you have merged your changes to `add-aosm-extension` then look at the Azure Pipelines under https://github.com/Azure/azure-cli-extensions/pull/6426/checks, click on the link that says `<X> errors / <Y> warnings`.
