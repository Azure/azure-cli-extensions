# Microsoft Azure CLI 'AI Did You Mean This' Extension #

### Installation ###
To install the extension, use the below CLI command
```
az extension add --name ai-did-you-mean-this
```

### Try it out! ###

### Developer Build ###
If you want to try an experimental release of the extension, it is recommended you do so in a [Docker Container](https://www.docker.com/resources/what-container). Keep in mind that you'll need to install Docker and pull the desired [Azure CLI image](https://hub.docker.com/_/microsoft-azure-cli) from the Microsoft Container Registry before preceding.

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
# az account
az account: error: the following arguments are required: _subcommand
usage: az account [-h]
                  {list,set,show,clear,list-locations,get-access-token,lock,management-group}
                  ...

Here are the most common ways users succeeded after [account] failed:
        az account list
        az account show
```