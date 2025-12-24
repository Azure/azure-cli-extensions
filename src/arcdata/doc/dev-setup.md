# Development setup

>**Note:** It is highly recommended to install the `azure-cli-extension` into a virtual environment as to not pollute the global python 
packages or conflict with system packages.

### Quickstart

Install Python 3.6 or later from python.org, apt-get, or some other installer.

##### LINUX and macOS
```bash
export AZURE_EXTENSION_DIR=path/to/azure-cli-extension
python3 ./scripts/dev_setup.py
source ./env/bin/activate
az arcdata --help
az extension list
```

##### Windows
```cmd
set AZURE_EXTENSION_DIR=path\to\azure-cli-extension
python .\scripts\dev_setup.py
.\env\Scripts\activate.bat
az arcdata --help
az extension list
```

## Get the source

1. Clone the Azure Devops CLI extension repository.

   ```bash
   $ git clone https://msdata.visualstudio.com/DefaultCollection/Tina/_git/arcdata
   $ cd ./arcdata/projects/azure-cli-extension
   ```

## Create a virtual environment

1. From the `azure-cli-extension` directory, create and activate a new virtual environment:

   ```bash
   virtualenv env
   ```

1. Install and activate the new virtual environment:

   On Linux macOS:

   ```bash
   $ python -m venv ./env
   $ source ./env/bin/activate


   On Windows:

   ```bash
   $ python -m venv .\env
   $ .\env\Scripts\activate.bat
   ```

1. Run the `dev_setup.py` script to install the Azure ArcData CLI packages and other dependencies into your virtual environment:

   ```bash
   python scripts/dev_setup.py
   ```

## Developing

Run `az extension list` and `az arc -h` to verify your environment is setup properly.

1. `dev_setup.py` script has already set your `AZURE_EXTENSION_DIR` environment variable to `.azure\devcliextensions` directory that will hold the extensions being developed

    On Windows

    Run below command any time you make changes to your extension and want to see them reflected in the CLI.

    ```bash
    pip install --upgrade --target %AZURE_EXTENSION_DIR%\arcdata Dev\arcdata-cli-extension\arcdata
    ```

    * `%AZURE_EXTENSION_DIR%\arcdata` is the directory `pip` will install the extension to.

    * `Dev\arcdata-cli-extension\arcdata` is the directory with the source code of your extension.

    On Linux

    ```bash
    pip install --upgrade --target $AZURE_EXTENSION_DIR/arcdata Dev\arcdata-cli-extension\arcdata/
    ```

1. Run `az arc -h` again to verify if extension is installed properly.
