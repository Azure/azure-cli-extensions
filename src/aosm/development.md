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
-  FAIL - HIGH severity: unrecognized_help_entry_rule
    Help-Entry: `aosm definition build` - Not a recognized command or command-group
    Help-Entry: `aosm definition delete` - Not a recognized command or command-group
    Help-Entry: `aosm definition generate-config` - Not a recognized command or command-group
    Help-Entry: `aosm definition publish` - Not a recognized command or command-group
    Help-Entry: `aosm definition` - Not a recognized command or command-group

-  pass: unrecognized_help_parameter_rule 
-  pass: expired_command_group 
-  FAIL - HIGH severity: missing_group_help
    Command-Group: `aosm nfd` - Missing help
    Command-Group: `aosm nsd` - Missing help

-  pass: expired_command 
-  pass: missing_command_help 
-  pass: no_ids_for_list_commands 
-  FAIL - HIGH severity: bad_short_option
    Parameter: aosm nfd publish, `manifest_parameters_json_file` - Found multi-character short options: -mp. Use a single character or convert to a long-option.

-  pass: expired_option 
-  pass: expired_parameter 
-  pass: missing_parameter_help 
-  pass: no_parameter_defaults_for_update_commands 
-  pass: no_positional_parameters 
-  FAIL - HIGH severity: option_length_too_long
    Parameter: aosm nsd publish, `manifest_parameters_json_file` - The lengths of all options ['--manifest-parameters-json-file'] are longer than threshold 22. Argument manifest_parameters_json_file must have a short abbreviation.

-  pass: option_should_not_contain_under_score 

Run custom pylint rules.
Running pylint on extensions...

No violations found for custom pylint rules.
Linter: PASSED
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

### Unit tests
To run unit tests run `azdev test aosm`.  All tests are expected to pass.

If one of the publish tests fails, then it might be because you have made small tweaks and the recording is now out of date.
Delete the relevant file under tests/latest/recordings (the file names match the name of the tests), and re-run the test.
If that passes it will create a new recording for you.

*DO NOT CHECK the recording in.*

There is an issue at the moment where it doesn't redact credentials and that will mean you get pinged by S360.


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
