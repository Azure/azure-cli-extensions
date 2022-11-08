# Azure QBS Extension for Azure CLI

The Azure QBS Extension for Azure CLI adds commands to interact with your existing Quorum Blockchain Service installation.
It simplifies the interaction with the management API as defined by [OpenAPI definition](https://management.onquorum.net/swagger/index.html).

## Quick start

1. [Install the Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli).

2. Add the Azure QBS Extension `az extension add --name qbs`

3. Run the `az login` command.

   If the CLI can open your default browser, it will do so and load a sign-in page. Otherwise, you need to open a
   browser page and follow the instructions on the command line to enter an authorization code after navigating to
   [https://aka.ms/devicelogin](https://aka.ms/devicelogin) in your browser. For more information, see the
   [Azure CLI login page](https://docs.microsoft.com/cli/azure/authenticate-azure-cli).

See the [Get started guide](https://docs.microsoft.com/azure/devops/cli/get-started?view=azure-devops) for detailed setup instructions.

## Usage

```bash
$ az qbs [subgroup] [command] {parameters}
```

Adding the Azure QBS Extension adds `qbs` group.
For usage and help content for any command, pass in the `--help` parameter, for example:

```
$ az qbs --help

Group
    az qbs : Commands to interact with "Quorum Blockchain Service" Azure Managed Applications.

Subgroups:
    consortium        : Manage consortium (private blockchain network), where the blockchain network
                        is limited to specific network participants.
    firewall          : Configure firewall rules to limit which IP addresses, or IP address ranges,
                        are allowed to attempt to connect to your nodes.
    invite            : Invite a member to join a consortium. More information available at
                        https://consensys.net/docs/qbs/en/latest/concepts/consortiums/.
    location          : List blockchain members by location.
    member            : Manage individual blockchain members.
    scheduled-restart : Schedule planned restarts for the VMs in your blockchain member.
    transaction-node  : Add or remove additional transaction nodes to your blockchain member.
```

- Checkout the CLI docs at [docs.microsoft.com - Azure DevOps CLI](https://docs.microsoft.com/azure/devops/cli/).
- Check out other examples in the [How-to guides](https://docs.microsoft.com/azure/devops/cli/?view=azure-devops#how-to-guides) section.
- You can view the various commands and its usage here - [docs.microsoft.com - Azure DevOps Extension Reference](https://docs.microsoft.com/en-us/cli/azure/devops?view=azure-cli-latest)

## Development

Environmental variables `AZ_CLI_QBS_MANAGEMENT_URL` and `AZ_CLI_QBS_RESOURCE_ID` can be used to change the request target.

## License

MIT License