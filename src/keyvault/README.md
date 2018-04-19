
#  Key Vault Azure CLI Extension

The Azure CLI extension for Key Vault is an extension which previews unreleased functionality in the keyvault command module.  

__NOTE__: The code for this extension is automatedly pulled from the [azure-sdk-for-python](https://github.com/azure/azure-sdk-for-python) and the [azure-cli](https://github.com/azure/azure-cli) repos using update_extension.py, and updated to run as an Azure CLI extension.  Changes may cause incorrect behavior and will be lost if the code is regenerated.

## Manually updating the Extension

Clone the [azure-sdk-for-python](https://github.com/azure/azure-sdk-for-python) and the [azure-cli](https://github.com/azure/azure-cli) repos:

    $ git clone https://github.com/azure/azure-sdk-for-python.git
    $ git clone https://github.com/azure/azure-cli

Using python 3.* run update_extension.py:
     
    $ python update_extension.py --sdk <azure-sdk-for-python clone root> --cli <azure-cli clone root>