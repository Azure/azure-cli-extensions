
# Extensions for Azure CLI 2.0

This repository serves two purposes and they are independent:

1. An index.json where you can add your extension and make it available through Azure CLI.
2. A source code directory, `src`, to host your extension source code.

For documentation on authoring an extension, see [Extension Documentation](https://github.com/Azure/azure-cli/tree/master/doc/extensions)

## About index.json

- The index is at `src/index.json`.
- Modify the index by creating a PR.
- All extensions added to the index *are public* and will be available to *all* CLI users.
- The index is synced to `https://aka.ms/azure-cli-extension-index-v1` every few minutes.
- Your extension source code does not have to be in this repository to be available in the index.
- If you don't want your extension to be part of the index, you can still host it externally and request users to install with `az extension add --source https://contoso.com/mywheel.whl`.
  * Users will not be able to add your extension by name, it will not be listed in the `az extension list-available` command and to update to a new version of your extension, the user has to first remove the currently installed extension and then add the new version.

Add your extension to the index to make it available in these CLI commands:
- `az extension add --name NAME` - Allows users to add an extension by name
- `az extension list-available` - Allows users to list the available extensions in the index
- `az extension update --name NAME` - Allows users to update an extension

## About source code in this repository

- Extension source code goes into the `src` directory.
- You can place your source code in this repository by creating a PR.
- Once CI is green and it has been approved, the PR can be merged.
- Ensure that you include an appropriate owner for your extension in `.github/CODEOWNERS`.
- Your extension artifact (i.e. `.whl`) will not live in this repository. You can publish your extension to PyPI or somewhere else such as Azure Storage.
- If you want your extension to appear in the index.json, modify the index.

# Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
