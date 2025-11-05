**AZCLI Coding Handbook**

[[_TOC_]]

# Develop with Decorator Pattern

## Overview

The following is an overview flowchart showing the execution flow of the `aks create` cli command based on the decorator pattern.

![decorator_v2_workflow.png](/.attachments/decorator_v2_workflow-ffe484eb-af42-4838-ad1e-ec743a67f90b.png)

Currently, cli commands that use this paradigm are `aks create`, `aks update`, `aks nodepool add` and `aks nodepool update`. The controller of the `aks nodepool add/update` command also applies to the nodepool part of the cluster manipulated by command `aks create/update`.

Based on this architecture, aks-preview can easily reuse code in azure-cli/acs, and only need to write code for additional supported options.

## Design Pattern

In azure-cli, for operations such as create and update, we are essentially putting the parameters set by the user step by step into a structured object that is finally sent as the request body when calling the api. Based on the decorator pattern, the following classes are designed to handle each stage separately.

![decorator_v2_overview.png](/.attachments/decorator_v2_overview-45782857-3c65-4377-b9a2-78585be9a4ec.png)

### AKSModels

Responsible for loading the definition of structured objects (i.e. api models).

* This class stores the models used in `aks_create` and `aks_update` and can load models of different api versions for azure-cli and azure-cli-extensions by specifying the parameter `resource_type`.

![decorator_v2_model.png](/.attachments/decorator_v2_model-0cfd64c2-91e7-4b66-8e57-ab936ceefee4.png)

### AKSParamDict

Responsible for storing the original parameters passed in by the aks commands as an internal dictionary.

* Only expose the "get" method externally to obtain parameter values, while recording usage.

![decorator_v2_param.png](/.attachments/decorator_v2_param-df4e7ca9-d989-4553-a98a-c07d6c679e23.png)

### AKSContext

Responsible for obtaining parameter values. In addition, may normalize or complete parameter values or perform cross validation between multiple parameters (the verification of a single parameter is handled by the validator (defined in `_validators.py`) specified in the parameter declaration (defined in `_params.py`)).

- This class provides getter functions to obtain the value of each parameter in `aks_create` and `aks_update`. Each getter function is responsible for obtaining the corresponding one or more parameter values, and perform necessary parameter value completion or normalization and validation checks.

* This class also stores a copy of the original function parameters, some intermediate variables (such as the subscription ID), a reference of the ManagedCluster object and an indicator that specifies the current decorator mode (currently supports create and update).

* In the create mode, the most basic principles is that when parameters are put into a certain profile (and further decorated into the ManagedCluster object by AKSCreateDecorator), it shouldn't be modified any more, only read-only operations (e.g. validation) can be performed. In other words, when we try to get the value of a parameter, we should use its attribute value in the `mc` object as a preference. Only when the value has not been set in the `mc` object, we could return the user input value. 

* In the update mode, in contrast to the create mode, we should use the value provided by the user to update the corresponding attribute value in the `mc` object.

* When adding support for a new parameter, you need to provide a "getter" function named `get_xxx`, where `xxx` is the parameter name. In this function, the process of obtaining parameter values, dynamic completion (optional), and validation (optional) should be followed. The obtaining of parameter values should further follow the order of obtaining from the ManagedCluster object or from the original value.

* When checking the validity of parameter values, a pair of parameters checking each other will cause a loop call. To avoid this problem, you can implement an extra internal function with options to skip validation (`enable_validation`) or dynamic completion (`read_only`).

![decorator_v2_context.png](/.attachments/decorator_v2_context-aab69ce0-60c8-4488-8692-d881873741d7.png)

### AKSDecorator

Internal controller of `aks create/update`/`aks nodepool add/update`. Responsible for assembling structured objects (e.g. `ManagedCluster`) and sending api requests. 

* Break down the all-in-one `aks_create/aks_update` function into several relatively independent functions (some of them have a certain order dependency) that **only focus on** handling a specific profile (e.g. network profile) or processing a piece of external logic (e.g. attach acr).
* An overall control function is provided (e.g. `construct_default_mc_profile/update_default_mc_profile`). By calling the aforementioned independent functions one by one, a complete ManagedCluster object is gradually decorated and finally requests are sent to create a new cluster or update an existing cluster.

![decorator_v2_decorator_ap.png](/.attachments/decorator_v2_decorator_ap-5a0a55de-2de7-4c6e-8574-94564e07098b.png)
![decorator_v2_decorator_mc.png](/.attachments/decorator_v2_decorator_mc-a44f9dfc-814c-4ce2-bf72-ffb0bb1724be.png)

### Advanced Features
* Early Exit

  In some cases (such as illegal user input), we would like to exit gracefully (with exit code 0) rather than throw an exception and forcibly terminate the process (with exit code other than 0). Now, we have supported this feature by providing a custom exception type `DecoratorEarlyExitException`. You can exit gracefully by throwing this specific exception anywhere in the process of creating (or updating) the ManagedCluster profile.

* Static Type Checking

  We have added type hints for all functions in file `decoratory.py`. We are planning to perform static type checking with library like `mypy`.


## Implementation Details - Code

- For decorator implementation, please refer to
    - [acs/base_decorator.py](https://github.com/Azure/azure-cli/blob/dev/src/azure-cli/azure/cli/command_modules/acs/base_decorator.py)
    - [acs/managed_cluster_decorator.py](https://github.com/Azure/azure-cli/blob/dev/src/azure-cli/azure/cli/command_modules/acs/managed_cluster_decorator.py)
    - [acs/agentpool_decorator.py](https://github.com/Azure/azure-cli/blob/dev/src/azure-cli/azure/cli/command_modules/acs/agentpool_decorator.py)
    - [aks-preview/managed_cluster_decorator.py](https://github.com/Azure/azure-cli-extensions/blob/main/src/aks-preview/azext_aks_preview/managed_cluster_decorator.py)
    - [aks-preview/agentpool_decorator.py](https://github.com/Azure/azure-cli-extensions/blob/main/src/aks-preview/azext_aks_preview/agentpool_decorator.py)

- For unit test of the decorator, please refer to
    - [acs/test_managed_cluster_decorator.py](https://github.com/Azure/azure-cli/blob/dev/src/azure-cli/azure/cli/command_modules/acs/tests/latest/test_managed_cluster_decorator.py)
    - [acs/test_agentpool_decorator.py](https://github.com/Azure/azure-cli/blob/dev/src/azure-cli/azure/cli/command_modules/acs/tests/latest/test_agentpool_decorator.py)
    - [aks-preview/test_managed_cluster_decorator.py](https://github.com/Azure/azure-cli-extensions/blob/main/src/aks-preview/azext_aks_preview/tests/latest/test_managed_cluster_decorator.py)
    - [aks-preview/test_agentpool_decorator.py](https://github.com/Azure/azure-cli-extensions/blob/main/src/aks-preview/azext_aks_preview/tests/latest/test_agentpool_decorator.py)

## FAQ

**1. Why and when will we read the parameter value from the `ManagedCluster` object?**

- In the **update** mode, the parameter value is not obtained from `mc` because we just need to use the value provided by the user to overwrite the value in mc.

- But in the **create** mode, `mc` is completely blank in the initial state, and our duty is to assemble the user's input into a complete `mc`. For some parameters, if the user does not specify a value explicitly, cli will perform dynamic completion. However, if dynamic completion is performed multiple times, the result value may be different. To ensure the consistency of the state and avoid unnecessary trouble, **the following regulation must be followed**.

  _Once the attribute corresponding to the parameter is set in the `mc` object, when we read the parameter value again, the value from the `mc` object will prevail. In other words, we will not and not be able to "modify" the parameter value anymore, the value will be treated as read only._

- In practice, for those parameters that are available in both create and update modes, for the part that determine the value in the getter function, to additionally check that the current decorator mode is create before obtaining the value from the mc object would be enough.

**2. Why are there getter functions in the form of internal functions (i.e. function name starts with `_`)?** 

- For getter functions with complex logic, we have both "public" function and "internal" function (function name starts with `_`) for them.
  - The "public" function basically has no parameter and **should be used in the decorator class** (e.g. `AKSCreateDecorator/AKSPreviewCreateDecorator`), where users do not need to consider the details of getter implementation.
  - The "internal" function has many parameters, which are used to control whether to perform validation or dynamic completion, etc. It **should be used in the context class** (e.g. `AKSContext/AKSPreviewContext`). With proper parameter settings, we would avoid loop calls during cross-validation.

    Take the most common `enable_validation` parameter as an example, the default value is `False`, which means if you call the internal function without any parameter, it will skip the validation part and usually this would be enough to avoid loop calls.

    _The situations that require additional parameter settings are usually related to dynamic completion._ At present, all these cases are in azure-cli/acs. Some of the parameters involved are service principal and managed identity, fqdn subdomain and dns prefix.

- Take the getters for `enable_pod_identity` and `disable_pod_identity` as an example, when verifying whether `disable_pod_identity` is set at the same time in the getter of `enable_pod_identity`, we will call the getter of `disable_pod_identity` to obtain its value, and the verification part of `disable_pod_identity` will also obtain the value of `enable_pod_identity` by calling its getter to verify whether the two are assigned at the same time. If we do not use a "flag" to escape this verification, we will fall into a loop call.


**3. Why are some models stored in a nested way？(e.g. `lb_models` in `AKSModels`, `nat_gateway_models` and `pod_identity_models` in `AKSPreviewModels`)**

- First of all, we have separate files to handle the logic related to these models (e.g. create or update the corresponding sub-profile). But we don't want to hard-code the import statements with some specific api version in these separate files to load model definitions, so we pass these models through parameters.

- Take the `pod_identity_models` as an example, we store the two models of `ManagedClusterPodIdentityProfile` and `ManagedClusterPodIdentityException` in the `pod_identity_models` property of `AKSPreviewModels`. This attribute is a SimpleNamespace and will be set when needed (lazy initialization). In those functions that need to use model definitions, we will pass the SimpleNamespace as a parameter and models could be accessed with the dot operator like pod_identity_models.ManagedClusterPodIdentityProfile, which avoids the hard coded import statements (e.g. from xxxx_xx_xx import xxxx).


## Unit Test in Decorator Pattern

After refactoring with the decorator pattern, we can write unit test cases for the model class, context class and decorator class separately. **The purpose is to ensure that every code path is covered (i.e. 100% test coverage).**

### AKSModelsTestCase

In this class, we test whether the model definition loaded through cli-core is consistent with the model definition loaded by ourselves.

### AKSContextTestCase

In this class, we test each getter function, by giving different parameters or specially set `ManagedCluster` object as the context, check that the obtained value or thrown exception is the same as expected. 

### AKSDecoratorTestCase

In this class, we test the controller function of each sub-profile (which is equivalent to an integration test of multiple getter functions from the context class), checking that the created/updated profile is consistent with the expectation.

### Agentpool Test Cases

For agentpool-related tests, the implementation will be tested in two modes (standalone and managedcluster). Considering that most functions behave the same in these two modes, the test function is first written under class named `XXXCommonTestCase` with name similar to `common_xxx`, and under class named `XXXModeTestCase` previous test function is called (and tested) with function name similar to `test_xxx` (Python's test framework will take functions starting with `test_` as test cases).

### Sample Unit Test Cases
```python
def test_get_param_xyz(self):
    # default
    ctx_1 = AKSContext(
        self.cmd,
        AKSManagedClusterParamDict({"param_xyz": None}),  # default value
        self.models,
        DecoratorMode.CREATE,  # testing create mode
    )
    # check the obtained value is the same as the default value
    self.assertEqual(ctx_1.get_param_xyz(), None)

    mc_1 = self.models.ManagedCluster(xyz="test_xyz")
    ctx_1.attach_mc(mc_1)
    # check the obtained value is the same as the value set in the ManagedCluster object
    self.assertEqual(ctx_1.get_param_xyz(), "test_xyz")
```


## Development Guidance

### Add new option in `aks create/update`/`aks nodepool add/update` (in the scope of the decorator pattern)

* Add declarations (type, validation, help message, etc.) for new options.
  - Add parameter declarations to the entry function of the corresponding command in `custom.py`.
  - Add the type, optional option names, default value and other declarations in `_params.py`.
  - Add the validator correponding to the option in `_validators.py`.
  - Add help information in `_help.py`.
* Add a getter function for each parameter in the context class `AKSContext`.
* Update (or add) the control function corresponding to the sub-profile to which the parameter belongs in the decorator class `AKSCreateDecorator` or `AKSUpdateDecorator`.
* Add both unit and live test cases.
* Example PR: [{AKS} add `networkPluginMode` support](https://github.com/Azure/azure-cli-extensions/pull/4855)

### Add new command (out of the scope of the decorator pattern)

* Add declarations for new commands.
  - Add the definition of the client factory (find the operation group provided by the SDK) corresponding to the command in `_client_factory.py`.
  - Add the mapping between command name and entry function name in `commands.py`.
  - Add command implementation (entry function) in `custom.py`.
* Add declarations (type, validation, help message, etc.) for new options.
  - Add parameter declarations to the entry function of the corresponding command in `custom.py`.
  - Add the type, optional option names, default value and other declarations in `_params.py`.
  - Add the validator correponding to the option in `_validators.py`.
  - Add help information in `_help.py`.
* Add both unit and live test cases.
* Example PR: [[AKS] Trusted Access Role Binding CLI](https://github.com/Azure/azure-cli-extensions/pull/4955)


### More examples

#### [AKS-Preview] Add support for sub-profile gmsa profile of windows profile and `--enable-windows-gmsa`, `--gmsa-dns-server` and `--gmsa-root-domain-name` options.
PR: [#4024](https://github.com/Azure/azure-cli-extensions/pull/4024)

Key Points:
* Introduce newly added model `WindowsGmsaProfile` in `AKSPreviewModels`.
* Add getter function `get_enable_windows_gmsa` and `get_gmsa_dns_server_and_root_domain_name` in `AKSPreviewContext`.
  * Since mutual verification is involved, internal functions are created for these two getter functions.
  * As the logic of verification is the same, an independent helper function is created for parameter verification.
* Overwrite function `set_up_windows_profile` in `AKSPreviewCreateDecorator` to set up gmsa sub-profile.
  * Inherit function `set_up_windows_profile` from `AKSCreateDecorator` and call it to create the basic windows profile.
* Add test cases for the functions involved above.

#### [AKS-Preview] Enable dual-stack.
PR: [#4174](https://github.com/Azure/azure-cli-extensions/pull/4174), [#4219](https://github.com/Azure/azure-cli-extensions/pull/4219)

Key Points:
* Add getter function `get_pod_cidrs_and_service_cidrs_and_ip_families` and `get_load_balancer_managed_outbound_ipv6_count` in `AKSPreviewContext`.
* Overwrite function `set_up_network_profile` in `AKSPreviewCreateDecorator` to set up dual-stack related parameters.
  * Inherit function `set_up_windows_profile` from `AKSCreateDecorator` and call it to create the basic network profile.
* Overwrite function `update_load_balancer_profile` in `AKSPreviewUpdateDecorator` to set dual-stack related parameters.
  * Do not call the base function from `AKSUpdateDecorator`.
* Modify helper functions in `_loadbalancer.py` to add support for dual-stack related parameters.
* Add test cases for the functions involved above.

#### [Azure-cli] Add support for `azure-keyvault-secrets-provider` addon and `--enable-secret-rotation` and `--rotation-poll-interval` options.
PR: [#19986](https://github.com/Azure/azure-cli/pull/19986), [#20039](https://github.com/Azure/azure-cli/pull/20039)

Key Points:
* Modify function `get_addon_consts` in `AKSContext` to add newly supported addon constants.
* Add getter functions `get_enable_secret_rotation` and `get_rotation_poll_interval` in `AKSContext`.
* Add function `build_azure_keyvault_secrets_provider_addon_profile` in `AKSCreateDecorator` to handle the logic of creating the corresponding addon profile.
* Modify function `set_up_addon_profiles` in `AKSCreateDecorator` to add support for handling this addon.
* Add test cases for the functions involved above.


## Contribution
### PR Title

In azure-cli, there are strict requirements on the title of the PR. If the PR is a user-oriented modification, please start the title with `[AKS]` and such a title will be recorded in the [release note](https://github.com/MicrosoftDocs/azure-docs-cli/blob/master/docs-ref-conceptual/release-notes-azure-cli.md). If the PR is not a user-detectable modification, please start the title with `{AKS}` and such a title will not be recorded in the release note.

Quoted from [official documentation](https://github.com/Azure/azure-cli/tree/dev/doc/authoring_command_modules#format-pr-description)

> Please follow the instruction in the PR template to provide a description of the PR and the testing guide if possible.

> If you would like to write multiple history notes for one PR or overwrite the message in the PR title as a history note, please write the notes under `History Notes` section in the PR description, following the same format described above. The PR template already contains the history note template, just change it if needed. In this case, the PR title could be a summary of all the changes in this PR and will not be put into `HISTORY.rst` in our pipeline. The PR title still needs to start with `[Component Name]`. You can delete the `History Notes` section if not needed.

For azure-cli-extensions, there are no special restrictions, but please start your title with `[AKS]` or `{AKS}`, which will facilitate classification and review.

### Recommendation

* Add concise help information (description and example) for each command and option.
* Use 2 separate options to control the state of a _switch_ (usually named "enabled" in the swagger spec, accepting bool values), one for enable (e.g., `--enable-feature-x`) and the one for disable (e.g., `--disable-feature-x`). Do not use `three_state_flag`.
* Handle parameter values carefully.
  * Beware of nulls.
  * Set appropriate default value.
  * Verify parameter values (single parameter and multiple interacting parameters).
  * Determine parameter values according to the context (dynamic completion, acquisition from the model, etc.).
* Pay attention to the dependencies between multiple sub-profiles.
* Use precise error types and provide accurate error messages.
* Write sufficient live and unit test cases.
  * Please refer to section [Live Test](#Live-Test) and [Unit Test](#Unit-Test) for more details.


# Appendix
## Dependency between aks-preview and azure-cli/acs (azure-cli-core)
See [readme.rst](https://github.com/azure/azure-cli-extensions/tree/main/src/aks-preview#dependency-between-aks-preview-and-azure-cliacs-azure-cli-core).

If the version does not match, a prompt message similar to the following will be given by azure-cli

![147800134-3ab8b466-704d-40d7-86e7-e832de00fe31.png](/.attachments/147800134-3ab8b466-704d-40d7-86e7-e832de00fe31-c8d3a9ef-d1a3-44ec-8403-11103b4c6cdb.png)


## Comparisons between Azure-cli and Azure-cli-extensions

Broadly speaking, azure-cli includes command modules, core, test sdk and telemetry module. Specifically, the command modules provide specific command implementation by module (in our case, aks commands are implemented in acs module), core provides the basic framework, test sdk provides the test framework, and telemetry is used to monitor command usage.

In contrast, azure-cli-extensions only provides command modules and each command module is used to "expand" (if the command name is the same, it actually is a complete replacement) the implementation of the command module in azure-cli for previewing some commands and options (in our case, aks commands are extended by aks-preview).

| Official Repo | Master branch | module | module prefix | resource type | api version | release schedule |
|-|-|-|-|-|-|-|
| [Azure/azure-cli](https://github.com/Azure/azure-cli) | dev | acs | acs | MGMT_CONTAINERSERVICE | 2022-07-01 (`latest` profile, **default**) <br> 2020-11-01 (`2020-09-01-hybrid` profile) | once per month |
| [Azure/azure-cli-extensions](https://github.com/Azure/azure-cli-extensions) | main | aks-preview | azext_aks_preview | CUSTOM_MGMT_AKS_PREVIEW | 2022-07-02-preview | on demand |


## Overall Workflow in Azure-CLI

You might wonder how azure-cli works, briefly speaking, after cli accepts user input, it will perform the following steps:

1. Validate and convert user's input into structured object.
1. Package the object into the request body and send the request through API calls (supported by SDK).
1. Beautifully output request results.

Azure-cli is developed based on [knack](https://github.com/microsoft/knack), and its underlying implementation is event-driven. But for most developers, the implementation of new options or new commands is concentrated in a specific entry function, and there is no need to consider how to deal with events in the cli framework.

The following is a slightly detailed explanation of the events that will be triggered after cli accepts user's input.
1. Parse the main command (in our case, usually this should be `aks`), sub-command (like `create`) and options (like `-g myResourceGroup -n myResourceName`)

1. Query the corresponding command (like `aks create`) from the command table.

    The command table is automatically generated according to the content defined in file `commands.py` in each module (in our case, this should be `acs` in azure-cli and `aks-preview` in azure-cli-extensions).

    The command table has 3 levels, namely module, (command) group and command. The following table is a simplified example.

    | Module | Group | Command |
    |-|-|-|
    | acs | aks | browse <br> create <br> update <br> ... |
    | acs | aks nodepool | add <br> update <br> upgrade <br> ... |
    | acs | ... | ... |

    It should be noted that if the extension is installed and after the command table index is rebuilt, when using the commands supported by both azure-cli (core cli) and azure-cli-extensions (extended cli), only the implementation in the extended cli will be adopted. In other words, the implementation of the command will be completely replaced by the extended cli. For those commands that do not have a corresponding implementation in the extended cli, the implementation in the core cli would be called when the command is executed.

    If only the extension is installed, but the command index is not reconstructed, the implementation in the extension cannot be invoked. Taking the `aks` command group as an example, calling the commands implemented on both sides (e.g. `aks create`) will not rebuild the index. The index will only be rebuilt when the additional supported commands in aks-preview (e.g. `aks maintenanceconfiguration`) or any non-existent command (e.g. `aks fake-command`) is called.


1. Parse the parameters entered by the user. The parameters supported by the command are defined in file `_params.py`. Here you can also define a list of option names corresponding to the parameter, specify the type of parameter value, and provide custom validators and completers. Since the order of parameter parsing is not fixed, the official document does not recommend adding dependency on other parameters in the validator. The implementation of validators and completers are defined in file `_completers.py` and `_validators.py`, respectively.

1. Pass the parsed parameters to the entry function and call the entry function.

    The mapping relationship between entry functions and commands is defined in file `commands.py` and the entry functions are usually defined in file `custom.py`. For example, the entry function of command `aks create` is `aks_create`.

    The formal parameters of the entry function are composed of `cmd`, `client` and the parameter form variables of all the options supported by the corresponding command.

    Variable `cmd` is an instance of class `azure.cli.core.commands.AzCliCommand`, which stores the context of the command and can be used to dynamically obtain the model provided in the SDK (however, this is extremely **not recommended**).

    Variable `client` is an instance of the SDK client (in our case, this should be `ContainerServiceClient` provided by the azure-mgmt-containerservice SDK). A client is loaded according to the definition in file `_client_facotry.py`.  The client provides models and operations, but in the entry function, we usually only use the operations it provides (for sending requests), and the loading of the models is taken care of by some other part. In the past, we used global import or dynamic loading through `cmd` in the entry function to load the models, but this also brings us great trouble when updating the api version or reusing the code in aks-preview. So now we provide class `AKSModels` in file `decorator.py` to obtain the models uniformly, and using parameter `resource_type`, we can load models of different api versions for core cli (acs) and extended cli (aks-preview).

    Under normal circumstances, the main logic of the command implementation is located here, which is also the place we need to pay most attention to. The return value of the entry function is usually a call to an operation of the SDK client.

1. Process the return value of the entry function.

    If the entry function returns a call to an operation in the SDK, then poll and wait for the operation result. If the operation succeeds, parse the result and print it to the console beautifully; otherwise output error message.


## Option Form vs. Parameter Form

* option
  * parameter form used in the command line
  * examples: `--resource-group`, `-g`(short form)
* parameter
  * formal parameters in function definitions
  * examples: `resource_group_name` in function `aks_create`
* argument
  * parameters actually passed to the function
  * examples: `{resource_group}` (the form written in test case, actually something like `clitestabcde`) for `resource_group_name`


## Setup

### Pre-Steps - Install Python and Set up a Virtual Environment

#### Install Python

Find the version that suits you from the [official release page](https://www.python.org/downloads/). 
> For compatibility with azure-cli, please use version >= 3.7

  - For ubuntu, the official apt source contains a specific version of python. If you choose to use the default version,
    > The default `python` command usually uses python 2.7, python 2 and python 3 are not compatible and python 2 is not supported by azure-cli, please use the `python3` command to explicitly call python 3.
    - for `ubuntu:18.04 (bionic)`, default python3 is python 3.6, not supported by azure-cli anymore! Upgrade the system version or refer to the follow-up instructions.
    - for `ubuntu:20.04 (focal)`, default python3 is python 3.8, install via `apt update && apt install -y python3 python3.8-venv`
      - If you want to write code with python, please also execute `apt install python3.8-pip python3.8-dev`.
    - for `ubuntu:22.04 (jammy)`, default python3 is python 3.10, install via `apt update && apt install -y python3 python3.10-venv`
      - If you want to write code with python, please also execute `apt install python3.10-pip python3.10-dev`.

    If the default version doesn't meet your needs, you can install a specific version of python from the apt source maintained by the deadsnakes team. For more details, please refer to this [page](https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa).
    > Note: Please don't change the default version of python3. Otherwise, you will most likely break your system.
  - For windows, it is recommended to download the file `Windows installer (xx-bit)` and follow the instructions of the GUI program to install it step by step.

#### Set up a Virtual Environment

> It is recommended to set up a separate (python) virtual environment for azure-cli related development and testing, as the python-related changes made in this virtual environment will not affect the python in your system environment, that is to say, it will not break any other system tools that depend on python.

- Create a virtual environment via `python -m venv azenv` (use `python3 -m venv azenv` instead if you have both python2 and python3 installed).
  > This will create a new folder `azenv` (could be replaced with other names you like) under the current working directory.

  > In case you want to remove this virtual environment, just remove this folder directly, and all python-related changes made in the virtual environment will be completely deleted.

  If you see any error message like `TypeError: expected str, bytes or os.PathLike object, not NoneType` when setting up azure-cli and azure-cli-extensions with `azdev` later (seems to happen commonly on mac), please remove the `azenv` folder you just created and try the following commands instead. Notes from fangluguo: on Dev Box, **you should use `python -m venv azenv` or `python3 -m venv azenv`**. The following command through virtualenv doesn't work in that the local repo cannot be used through `azdev setup -c {local-path-to-azure-cli-repo} -r {local-path-to-azure-cli-extensions-repo}`.
  ```
  python3 -m pip install virtualenv
  virtualenv -p python3 azenv
  ```

- Activate the virtual environment via `source azenv/bin/activate` (from ubuntu bash) or `.\azenv\Scripts\activate` (from windows cmd).
  > Every time you use a python-based tool installed in this virtual environment, need to make sure the virtual environment is activated in the current shell session.
- Exit the virtual environment via `deactivate`.

### [Recommended] Install azure-cli in a Python Virtual Environment (for use only, not for development)

> In case you just want to use azure-cli in a worry-free way, any system package update should **NOT** break your usage.

Follow the guidance in section [Pre-Steps - Install Python and Set up a Virtual Environment](#pre-steps---install-python-and-set-up-a-virtual-environment).
> The `[venv]` tag means you should run the command with virtual environment activated.
1. [venv] Upgrade pip (python package manager) via `pip install --upgrade pip`
1. [venv] Install azure-cli via `pip install azure-cli`
1. [venv] Check the installed azure-cli via `az version`

**Optional steps**
- [Optional][venv] Upgrade azure-cli via `az upgrade -y`
- [Optional][venv] Install aks-preview via `az extension add -n aks-preview`
- [Optional][venv] Remove aks-preview via `az extension remove -n aks-preview`

### Setup from Source Code (aka Developer Mode)

> In case you want to add new functionality or debug.

Follow the guidance in section [Pre-Steps - Install Python and Set up a Virtual Environment](#pre-steps---install-python-and-set-up-a-virtual-environment).
> The `[venv]` tag means you should run the command with virtual environment activated.

1. Clone the official or your forked repo from GitHub.
1. [venv] upgrade pip (python package manager) via `pip install --upgrade pip`
1. [venv] Install `azdev` via `pip install -U azdev`, which will be used to setup azure-cli and perform tests later.
1. [venv] Setup azure-cli and azure-cli-extensions in development mode.

    `azdev setup -c {local-path-to-azure-cli-repo} -r {local-path-to-azure-cli-extensions-repo}`

    > Replace `{local-path-to-azure-cli-repo}` and `{local-path-to-azure-cli-extensions-repo}` properly.

    > If you see any error message like `TypeError: expected str, bytes or os.PathLike object, not NoneType`, please remove the `azenv` folder and go back to "Set up a Virtual Environment" and try the other option.

Congratulations! You have completed the installation of **azure-cli** (**but not aks-preview yet**). If you want to install aks-preview, please continue with the additional step 5.
Note: When using `az aks` or other commands, the corresponding implementation in azure-cli will be used, and any changes to the local code will be promptly fed back into use.

5. **[additonal step for aks-preview]**[venv]  If you want to install/uninstall aks-preview from azure-cli-extensions, please follow the steps below.
    - Install `aks-preview`.
      `azdev extension add aks-preview`
    - Uninstall `aks-preview`.
      `azdev extension remove aks-preview`

### Preview SDK Changes
To preview, test, or do implementation work for a new feature ahead of time in

#### azure-cli/acs

1. Follow [Setup from Source Code (aka Developer Mode)](#Setup-from-Source-Code-(aka-Developer-Mode)) to configure the development environment.

1. The preview SDK could be found from a pipeline named `SDK azure-sdk-for-python-track2` in the PR to rest-api-specs repo. Please choose the **`.whl`** file. The following is a sample screenshot.
![image.png](/.attachments/image-1bdc238c-6e13-4cdb-a2f8-5f17811ea78f.png)

1. Please do the following 3 steps，
    1. Follow the instructions under section `Code Changes` in this [doc](https://dev.azure.com/msazure/CloudNativeCompute/_wiki/wikis/CloudNativeCompute.wiki/358325/Upgrade-SDK-and-API-Version-for-acs-and-aks-preview-in-Azure-CLI?anchor=code-changes) to vendor the above-mentioned SDK to azure-cli.
    2. [venv] Install the previously downloaded SDK.
      `pip install azure_mgmt_containerservice-x.x.x-py3-none-any.whl`
        > Replace `x.x.x` properly.

    3. [venv] Follow step `4. [venv] Setup azure-cli and azure-cli-extensions in development mode.` in section [Setup from Source Code (aka Developer Mode)](#Setup-from-Source-Code-(aka-Developer-Mode)) to setup azure-cli again.

    Note: DRI will be responsible for vendor the officially released SDK (see api plan doc in the folder of [Monthly-API-Review](https://dev.azure.com/msazure/CloudNativeCompute/_wiki/wikis/CloudNativeCompute.wiki/40767/Monthly-API-Review)), so you could skip the step of regenerating the recording files (section `Recording Files`).

1. [Optional] May follow section [Update cloud config](#Update-cloud-config) if the manifest has not been deployed to all (global prod) regions. You'll need to change the global ARM endpoint (`https://management.azure.com/`) to the regional endpoint (e.g. `https://eastus2euap.management.azure.com/`) where the new manifest has been deployed.

#### azure-cli-extensions/aks-preview

1. Follow [Setup from Source Code (aka Developer Mode)](#Setup-from-Source-Code-(aka-Developer-Mode)) to configure the development environment.

1. The preview SDK could be found from a pipeline named `SDK azure-sdk-for-python-track2` in the PR to rest-api-specs repo. Please choose the **`.zip`** file. The following is a sample screenshot.
![image.png](/.attachments/image-a6c7a012-6ba7-4f80-ba64-2daba4fad5f5.png)

1. Follow the instructions under section `Code Changes - aks-preview` in this [doc](https://msazure.visualstudio.com/CloudNativeCompute/_wiki/wikis/CloudNativeCompute.wiki/358325/Upgrade-SDK-and-API-Version-for-acs-and-aks-preview-in-Azure-CLI?anchor=code-changes---aks-preview) to vendor the above-mentioned SDK to aks-preview.
Note: DRI will be responsible for vendor the officially released SDK (see api plan doc in the folder of [Monthly-API-Review](https://dev.azure.com/msazure/CloudNativeCompute/_wiki/wikis/CloudNativeCompute.wiki/40767/Monthly-API-Review)), so you could skip the step of regenerating the recording files (section `Recording Files`).

1. [Optional] May follow section [Update cloud config](#Update-cloud-config) if the manifest has not been deployed to all (global prod) regions. You'll need to change the global ARM endpoint (`https://management.azure.com/`) to the regional endpoint (e.g. `https://eastus2euap.management.azure.com/`) where the new manifest has been deployed.

### Update cloud config

#### Update arm endpoint

Note: This is usually used for testing a preview API/SDK in some specific regions that ARM manifest has been partially released (but not fully released yet) in aks-preview.

Update the default arm endpoint to the endpoint in an euap region.
```
az cloud update --endpoint-resource-manager https://eastus2euap.management.azure.com/
```

Reset to the default arm endpoint.
```
az cloud update --endpoint-resource-manager https://management.azure.com/
```

#### Update profile

Note: This is typically used for backward compatibility testing in azure-cli/acs.

Update (api) profile to `2020-09-01-hybrid`.
```
az cloud update --profile 2020-09-01-hybrid
```

Reset to the default (api) profile.
```
az cloud update --profile latest
```

#### Check cloud config

Check current cloud config.
```
az cloud show
```

### Install from Wheel Files (Private Preview)

> To use azure-cli, you must at least have azure-cli-core and azure-cli installed. The corresponding wheel file names are
> - [CI build](https://dev.azure.com/azclitools/public/_build?definitionId=32&_a=summary)
>    - From the `Checks` panel find the link to open the pipeline summary page.
    ![image.png](/.attachments/image-b6e0a9ce-5d66-4252-a838-88dc26a98435.png)
>    - Click on the `x published` link to view the details of the pipeline artifacts.
    ![image.png](/.attachments/image-d0e79a53-2ed1-4b95-833a-befd18adb72f.png)
>    - `pypi` corresponds to a zip file, which contains the installation packages in whl format.
    ![image.png](/.attachments/image-0c19e98f-df34-4543-99e0-924dfe818b91.png)
    - `azure_cli_core-{version}.{build}-py3-none-any.whl`
    - `azure_cli-{version}.{build}-py3-none-any.whl`
> - [Local build](#local-build)
    - `azure_cli_core-{version}-py3-none-any.whl`
    - `azure_cli-{version}-py3-none-any.whl`

Follow the guidance in section [Pre-Steps - Install Python and Set up a Virtual Environment](#pre-steps---install-python-and-set-up-a-virtual-environment).
> The `[venv]` tag means you should run the command with virtual environment activated.
- [venv] Install them **in order** by executing the following commands.

  `pip install azure_cli_core-{xxx}.whl`
  `pip install azure_cli-{xxx}.whl`

  > Replace {xxx} properly.

- [venv] To use aks-preview from azure-cli-extensions, you **must have azure-cli installed first**. Then additionally install the wheel file named `aks_preview-{version}-py2.py3-none-any.whl` with the following command.

  `az extension add --source aks_preview-{version}-py2.py3-none-any.whl`

  > Replace {version} properly.

### BugBash Environment Preparation

It is highly recommended to prepare a container image with the preview version of azure-cli (and aks-preview if necessary) pre-installed for users to test. The overall process is as follows
1. Choose a base image (e.g. Ubuntu 20.04 (with Python 3.8 as default) or Ubuntu 22.04 (with Python 3.10 as default), test only) and start a new container. 
1. Follow [Setup from Source Code (aka Developer Mode)](#Setup-from-Source-Code-(aka-Developer-Mode)) or [Install from Wheel Files (Private Preview)](#Install-from-Wheel-Files-(Private-Preview)) to setup azure-cli (and aks-preview if necessary) in the container.
1. Commit the container into a new image for BugBash.
1. Push the image to an acr that users can download anonymously (test only).

## Tests

### Live Test

The main purpose of the live test is to test the **data model** (bound to a certain version of the api). The main test method is to check that the corresponding fields in the returned data model are as expected.

More specifically, we use live test to ensure that the options entered by the user are correctly converted into the data model. After sending to ARM/RP for processing, the data model in the returned response is still in line with expectations in the production environment. Normally, the live test is **not responsible** for confirming that the specified options take effect.

Live test cases can be executed in live mode and replay mode. In live mode, real requests will be sent to create resources during the test and recording files will be generated automatically (under `test/latest/recordings`). In replay mode, no real request will be sent. The request will be intercepted and the framework will look for a matching request from the recording file, and return the previously recorded response as the return result of the request.

Therefore, only when test cases are executed in live mode will they interact with ARM/RP to ensure that the data model meets the expectations. The replay mode can only ensure that the way of processing parameters on the cli side has not changed, which is more like an integrated unit test.

For a live test case, usually it should be written in file `test_aks_commands.py` with the help of azure-cli-testsdk (supported by vcr and pytest). If you need to use other azure resources, you can use cli to create them directly in the test case.

If you are adding new test cases, it is highly **recommended** to use the method described in section [Create Cassette File(s) for Newly Added Test Case(s)](https://dev.azure.com/msazure/CloudNativeCompute/_wiki/wikis/CloudNativeCompute.wiki/358312/AZCLI-AKS-Live-Unit-Test-Pipeline?anchor=create-cassette-file(s)-for-newly-added-test-case(s)) to generate the recording file through the pipeline.

The default subscription used by our pipelines and runner does not register any features other than `AKSHTTPCustomFeatures`, so test cases involving features that do not support feature validation by custom header cannot be executed in live mode. Please refer to section [Bypass Test Case](https://dev.azure.com/msazure/CloudNativeCompute/_wiki/wikis/CloudNativeCompute.wiki/358312/AZCLI-AKS-Live-Unit-Test-Pipeline?anchor=bypass-test-case) to bypass the test case.

### Unit Test

Unit testing acts like a fixture in cli and is used to ensure that new changes do not break the original implementation and provide more comprehensive test coverage.

Unit test cases are written based on the python standard library `unittest`. For reference, you can read the existing unit test cases in file `test_decorator.py`.


### Local Test
#### Prerequisites

> Make sure you have gone through the [Setup from Source Code (aka Developer Mode)](#Setup-from-Source-Code-(aka-Developer-Mode)) section.

The tool azdev can help us perform tests and format checks, but **the implementation to be tested depends on what is installed**. Take the aks commands as an example, if you **do not have `aks-preview` installed**, you are testing the implementation in folder `azure-cli/src/azure-cli/azure/cli/command_modules/acs`; if you **have `aks-preview` installed and loaded**, you are testing the implementation in folder `azure-cli-extensions/src/aks-preview/azext_aks_preview`.

#### Execute Live Tests

`azdev test {module-or-test-case}`

> Replace {module-or-test-case} with the module or the test case(s) you would like to test.

Test Command Options:

- `--discover`: Build test index. If the test is executed for the first time, the test case name is changed, or a new test case is added, **must** add this option in your command. Otherwise, this option will waste some time for indexing.

- `--live`: Perform tests in live mode. Real requests will be sent to create resources during the test and recording files will be generated automatically (under `test/latest/recordings`). If this option is not specified, the test will be executed in replay mode, which means the requests will be mocked by existing recording files, however if no such recording file exists, it will fall back to execution in live mode.
  - To run tests in live mode, you need to log in and specify a subscription with sufficient resources and permissions.
  `az login`
  `az subscription account set -s {subsription-id}`

- `--series`: Perform tests serially. If this option is not specified, the test will be executed in parallel. **For OSX users, it's highly recommended to run tests with this option.** 

  > Parallel execution of tests based on pytest has some issues on OSX.

- `--no-exitfirst`: Continue to execute other test cases when a test case fails.

Examples:

- `azdev test acs --discover`
  Build test index and test all the cases under the `acs` module in replay mode (also in parallel). If any test case fails, it will immediately exit the test process.

- `azdev test acs.test_aks_create_default_service --series`
  Test the single case `test_aks_create_default_service` in azure-cli serially.

- `azdev test acs.test_aks_commands --live --no-exitfirst`
  Test all the cases defined in file `azure-cli/src/azure-cli/azure/cli/command_modules/acs/tests/latest/test_aks_commands.py` in live mode (also in parallel). The test process will not terminate prematurely even if a test case fails.

- `azdev test azext_aks_preview.{new_test_case_name} --discover --series --live`
  > Replace {new_test_case_name} with the test case (i.e. function) name you would like to test.

  Build test index and test specified single case (function) defined in file `src/aks-preview/azext_aks_preview/tests/latest/test_aks_commands.py` in live mode (also in serial).

#### Execute Unit Tests

- Test a whole file
Execute the following command under the test file directory (usually `test/latest`).
`python -m unittest {test_file_name}` or `pytest {test_file_name}` (pytest is installed along with [azdev](#setup-from-source-code-(aka-developer-mode)))
  > Replace {test_file_name} with the file you would like to test.

- Test those test cases whose name matches the keyword
Execute the following command under the test file directory (usually `test/latest`).
`pytest -k {test_keyword}` (pytest is installed along with [azdev](#setup-from-source-code-(aka-developer-mode)))
  > Replace {test_keyword} with the what you would like to test. Do remember to include the {test_keyword} when you name your test cases.

#### Execute Format Check

`azdev style {module-or-test-case}` or `azdev linter {module-or-test-case}`

> Replace {module-or-test-case} with the module or the test case(s) you would like to test.


### Check-in Pipelines

There are two types of tests, live test and unit test. Please refer to section [Live Test](#Live-Test) and [Unit Test](#Unit-Test) for more details.

For more details about the PR check-in pipeline, please refer the wiki page [AZCLI AKS Live & Unit Test Pipeline](https://dev.azure.com/msazure/CloudNativeCompute/_wiki/wikis/CloudNativeCompute.wiki/358312/AZCLI-AKS-Live-Unit-Test-Pipeline).


### Runner and Monitor

For more details about the cli runner, please refer the wiki page [AZCLI AKS Runner (azcli-aks-metrics)](https://dev.azure.com/msazure/CloudNativeCompute/_wiki/wikis/CloudNativeCompute.wiki/358314/AZCLI-AKS-Runner-(azcli-aks-metrics)).


## Build & Release
### Local Build
#### Prerequisites

> Make sure you have python 3 and the following python libraries installed (check with `pip list`).
  - pip
  - setuptools
  - wheel

For changes to the azure-cli command modules (e.g. you changed the implementation of the aks command in the acs module), go to path `azure-cli/src/azure-cli`, and run command `python setup.py bdist_wheel`. You'll find the wheel file named `azure_cli-{version}-py3-none-any.whl` under `azure-cli/src/azure-cli/dist`.

For changes to azure-cli-core, go to path `azure-cli/src/azure-cli-core`, and run command `python setup.py bdist_wheel`. You'll find the wheel file named `azure_cli_core-{version}-py3-none-any.whl` under `azure-cli/src/azure-cli-core/dist`.

For changes to aks-preview in azure-cli-extensions, go to path `azure-cli-extensions/src/aks-preview`, and run `python setup.py bdist_wheel`. You'll find the wheel file named `aks_preview-{version}-py2.py3-none-any.whl` under `azure-cli-extensions/src/aks-preview/dist`.


### Official Release and Hotfix

For azure-cli, the release schedule is once per month and the specific plan is announced [here](https://github.com/Azure/azure-cli/milestones). Just make sure that your code is fully tested, the title of the PR complies with the aforementioned [specifications](#PR-Title) and merged into the `dev` branch before the code complete date. The cli team will handle the details of the release.

~~As for hotfix ([sample PR](https://github.com/Azure/azure-cli/pull/18795)), please adjust the target branch of your PR to the `release` branch, and include the word "Hotfix:" in the title of the PR. There is no fixed plan for the release of the hotfix, and you need to communicate with the members of the cli team separately.~~ Unless there is no workaround, now the cli team tends not to release hotfix versions.

For azure-cli-extensions, release is more flexible. You only need to update the version information in file [setup.py](https://github.com/Azure/azure-cli-extensions/blob/main/src/aks-preview/setup.py) and historical information in file [HISTORY.rst](https://github.com/Azure/azure-cli-extensions/blob/main/src/aks-preview/HISTORY.rst) in your PR. After the PR is merged into the `main` branch, a release PR ([sample](https://github.com/Azure/azure-cli-extensions/pull/4019)) will be automatically generated. When the release PR is merged, the release is completed.

As for hotfix, since the released version cannot be changed, the hotfix method is to create a new release.

### SDK, Resource Type, Profile and API Version

The SDK provides models and operations of all api versions supported by RP, but the actual api version used by a command in cli is uniquely determined by a specific resource type in an api profile. In azure-cli, it supports multiple sets of api profiles and the definition of api profiles is written in [file](https://github.com/Azure/azure-cli/blob/dev/src/azure-cli-core/azure/cli/core/profiles/_shared.py). Each set of api profile is a dictionary, which records the SDKProfile (i.e. value) corresponding to each resource type (i.e. key). In a SDKProfile, different api versions can be specified for different operation types.
 
In our case, the name of our SDK is `azure-mgmt-containerservice` and we support the default `latest` profile and `2020-09-01-hybrid` profile. In these two sets of api profiles, our resource type name is `MGMT_CONTAINERSERVICE`. In the default `latest` profile, the default api version we use (for managed cluster operations, i.e. aks commands) is `2021-07-01`, the api version used for container service related operations (i.e. acs commands) is `2017-07-01 `, and the api version used for open shift related operations (i.e. osa commands) is `2019-09-30-preview`. While in the `2020-09-01-hybrid` profile, we take `2020-11-01` as the default api version for aks commands.

In aks-preview, we always use the latest api version we support (currently `2021-09-01`) and the corresponding resource type name is `CUSTOM_MGMT_AKS_PREVIEW`.

For more details about upgrading SDK and api version, please refer the wiki page [Upgrade SDK and API Version for acs and aks-preview in Azure-CLI](https://dev.azure.com/msazure/CloudNativeCompute/_wiki/wikis/CloudNativeCompute.wiki/358325/Upgrade-SDK-and-API-Version-for-acs-and-aks-preview).

### Swagger and SDK

As far as I know, swagger is our (public) api definition and recorded in [Azure/azure-rest-api-specs](https://github.com/Azure/azure-rest-api-specs/tree/main/specification/containerservice/resource-manager/Microsoft.ContainerService/stable) repo on GitHub. SDKs in multiple languages including python will be automatically released within a few days after the branch of the new api version is merged.

Our python SDK named `azure-mgmt-containerservice` is published on [pypi](https://pypi.org/project/azure-mgmt-containerservice/). SDKs with version numbers lower than `14.0.0` are based on track 1 architecture, and those with a version greater than or equal to `14.0.0` are track 2 based.

For more details about track 1/2 SDK, please refer this [doc](https://github.com/Azure/azure-cli/blob/dev/doc/track_2_migration_guidance.md). For track 2 migration, please refer [cli migration](https://dev.azure.com/msazure/CloudNativeCompute/_wiki/wikis/CloudNativeCompute.wiki/161177/Track-2-SDK-Migration-CLI) and [extensions migration](https://dev.azure.com/msazure/CloudNativeCompute/_wiki/wikis/CloudNativeCompute.wiki/165132/Track-2-SDK-Migration-Extensions).

For more details about publishing api and SDK, please refer the wiki page [Update API, Manifest, Swagger and SDK](https://dev.azure.com/msazure/CloudNativeCompute/_wiki/wikis/CloudNativeCompute.wiki/358321/Update-API-Manifest-Swagger-and-SDK).

### Telemetry Data

For client side telemetry data, follow [wiki](https://devdiv.visualstudio.com/DevDiv/_wiki/wikis/DevDiv.wiki/9768/Accessing-DevDiv-Data) to request access, more details about CLI temetry in [doc](https://microsoft.sharepoint.com/teams/IoTToolingTeam/_layouts/15/Doc.aspx?sourcedoc=%7B8a3ef76b-61e5-4d4c-9ee5-69ab3a65816d%7D&action=edit&wd=target(AZ%20CLI%2FKnowledge%20base.one%7C18bc64ee-9328-497d-804e-6436006ca9a5%2Fc.%20CLI%20Telemetry%7Cd11629f0-3003-40b2-9eb6-08d16fd2b105%2F)&share=IgFr9z6K5WFMTZ7laas6ZYFtAbJ4YW_ffaxfECO4xmvM7UY).

For server side telemetry data, check kusto log from ARM.HttpIncomingRequests
[sample query](https://armprodgbl.eastus.kusto.windows.net/ARMProd?query=H4sIAAAAAAAEAG2R0UvDMBDG3wf7H44x2AZzovhaoZSqBbuNtMrwZcT01sXZJl4uOsU%2f3sw5YWJeQj6%2b%2b913l0YqMie4tbKtQLuV%2f%2fh4j5g8QizyOZkqvQbpYNHtDLsdCGcxqSTLR%2blwOBD44tGxG4wmN8w2a5VpdFsf5H3BJ%2bCWMdD76tk7RoIoQPrKE2HLyx9xGRzW6JYPRW9rJIQyy9OijPM5XEYgazO8WI%2bOHSypRhbojCeFIfGrrnY9IujlWSJmxeyqnCSzaRln01QUqbjPkrR3zPAOKa5DGlhLZwlXegu9%2bOFOpMltdnr%2bx11Kt5nKBr97%2fDN3ESLxb40l84SKYU6otMNSNxgMjR2DsUiStWl3sDEERhM%2bYf%2bwksId9lIg75QDjeUG4azbCUv4Ar0%2bCt26AQAA&web=0)
```
macro-expand isfuzzy=true ARMProdEG as X
(
    X.database('Requests').HttpIncomingRequests
    | extend $cluster = X.$current_cluster_endpoint
    | where TIMESTAMP >= ago(4h)
    | where targetResourceProvider == "MICROSOFT.CONTAINERSERVICE"
    | where userAgent hasprefix "AZURECLI/2"
    | where TaskName == "HttpIncomingRequestStart"
    | project PreciseTimeStamp, operationName, commandName, parameterSetName
    | take 1
)
```

|PreciseTimeStamp|operationName|commandName|parameterSetName|
|-|-|-|-|
|2024-04-25 01:54:48.7952769|GET/SUBSCRIPTIONS/RESOURCEGROUPS/PROVIDERS/MICROSOFT.CONTAINERSERVICE/MANAGEDCLUSTERS/|aks show|--subscription --name --resource-group --output|
|2024-04-25 02:01:08.2033833|POST/SUBSCRIPTIONS/RESOURCEGROUPS/PROVIDERS/MICROSOFT.CONTAINERSERVICE/MANAGEDCLUSTERS/LISTCLUSTERUSERCREDENTIAL|aks get-credentials|--resource-group --name|
|2024-04-25 02:01:38.6980023|GET/SUBSCRIPTIONS/RESOURCEGROUPS/PROVIDERS/MICROSOFT.CONTAINERSERVICE/MANAGEDCLUSTERS/|aks show|--name --resource-group --query -o|


## Request for Help

For aks related issues, feel free to ping @<Fuming Zhang>.

For other general azure-cli related issues, please email azclidev@microsfot.com or join teams [Azure CLIs partners](https://teams.microsoft.com/l/team/19%3aDNHD30SQx04UX9PnCIQ5d4fum1t28Mvjx5RJkrSBNBU1%40thread.tacv2/conversations?groupId=9a661795-1b01-4a5b-9dd5-be571422334c&tenantId=72f988bf-86f1-41af-91ab-2d7cd011db47) for help.

## Reference
- [Managed Identity Command Guideline](https://github.com/Azure/azure-cli/blob/dev/doc/managed_identity_command_guideline.md).
