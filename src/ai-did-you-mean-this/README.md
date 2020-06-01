# Microsoft Azure CLI 'AI Did You Mean This' Extension #

### Installation ###
To install the extension, use the below CLI command
```
az extension add --name ai-did-you-mean-this
```

### Background ###
The purpose of this extension is help users recover from failure. Once installed, failure recovery recommendations will automatically be provided for supported command failures. In cases where no recommendations are available, a prompt to use `az find` will be shown provided that the command can be matched to a valid CLI command.
### Limitations ###
For now, recommendations are limited to parser failures (i.e. not in a command group, argument required, unrecognized parameter, expected one argument, etc). Support for more core failures is planned for a future release. 
### Try it out! ###
The following examples demonstrate how to trigger the extension. For a more complete list of supported CLI failure types, see this [CLI PR](https://github.com/Azure/azure-cli/pull/12889). Keep in mind that the recommendations shown here may be different from the ones that you receive.

#### az account ####
```
> az account
az account: error: the following arguments are required: _subcommand
usage: az account [-h]
                  {list,set,show,clear,list-locations,get-access-token,lock,management-group}
                  ...

Here are the most common ways users succeeded after [account] failed:
        az account list
        az account show
```

#### az account set ####
```
> az account set
az account set: error: the following arguments are required: --subscription/-s
usage: az account set [-h] [--verbose] [--debug] [--only-show-errors]
                      [--output {json,jsonc,yaml,yamlc,table,tsv,none}]
                      [--query JMESPATH] --subscription SUBSCRIPTION

Here are the most common ways users succeeded after [account set] failed:
        az account set --subscription Subscription
```

#### az group create ####
```
>az group create
az group create: error: the following arguments are required: --name/--resource-group/-n/-g, --location/-l
usage: az group create [-h] [--verbose] [--debug] [--only-show-errors]
                       [--output {json,jsonc,yaml,yamlc,table,tsv,none}]
                       [--query JMESPATH] [--subscription _SUBSCRIPTION]
                       --name RG_NAME --location LOCATION
                       [--tags [TAGS [TAGS ...]]] [--managed-by MANAGED_BY]

Here are the most common ways users succeeded after [group create] failed:
        az group create --location westeurope --resource-group MyResourceGroup
```
#### az vm list ###
```
> az vm list --query ".id"
az vm list: error: argument --query: invalid jmespath_type value: '.id'
usage: az vm list [-h] [--verbose] [--debug] [--only-show-errors]
                  [--output {json,jsonc,yaml,yamlc,table,tsv,none}]
                  [--query JMESPATH] [--subscription _SUBSCRIPTION]
                  [--resource-group RESOURCE_GROUP_NAME] [--show-details]

Sorry I am not able to help with [vm list]
Try running [az find "az vm list"] to see examples of [vm list] from other users.
```
### Developer Build ###
If you want to try an experimental release of the extension, it is recommended you do so in a [Docker container](https://www.docker.com/resources/what-container). Keep in mind that you'll need to install Docker and pull the desired [Azure CLI image](https://hub.docker.com/_/microsoft-azure-cli) from the Microsoft Container Registry before proceeding.

#### Setting up your Docker Image ####
To run the Azure CLI Docker image as an interactive shell, run the below command by replacing `<version>` with your desired CLI version
```bash
docker run -it mcr.microsoft.com/azure-cli:<version>
export EXT="ai-did-you-mean-this"
pip install --upgrade --target ~/.azure/cliextensions/$EXT "git+https://github.com/christopher-o-toole/azure-cli-extensions.git@thoth-extension#subdirectory=src/$EXT&egg=$EXT"
```
Each time you start a new shell, you'll need to login before you can start using the extension. To do so, run
```bash
az login
```
and follow the instructions given in the prompt.  Once you're logged in, try out the extension by issuing a faulty command 
```
> az account
az account: error: the following arguments are required: _subcommand
usage: az account [-h]
                  {list,set,show,clear,list-locations,get-access-token,lock,management-group}
                  ...

Here are the most common ways users succeeded after [account] failed:
        az account list
        az account show
```