# Microsoft Azure CLI 'AI Examples' Extension

Improve user experience by adding AI powered examples to command help content.

This extension changes the default examples provided when calling `-h` or `--help` on a command, such as `az vm create -h`, with ones selected by an AI powered service. The service provides examples based on Azure usage, internet sources, and other factors.
 
Install it via: 
`az extension add --name ai-examples`
 
## Background
 
The az find module provides examples to the users when they search for a specific command or do natural language queries. Unfortunately, it requires the users to know about and use the command, which is not part of the normal flow of a CLI user. So instead this extension meets the user and replaces the normal examples from the `-h` or `--help` with AI enhanced ones.
 
In addition to providing examples based on user telemetry, it also adds examples to groups and commands that do not have any baked into the CLI.
 
## Examples
 
**Command example**

```bash
> az storage blob list -h
 
Command
    az storage blob list : List blobs in a given container.
 
Arguments
    --container-name -c [Required] : The container name.
    --auth-mode                    : The mode in which to run the command. "login" mode will
                                     directly use your login credentials for the authentication. The
                                     legacy "key" mode will attempt to query for an account key if
                                     no authentication parameters for the account are provided.
                                     Environment variable: AZURE_STORAGE_AUTH_MODE.  Allowed values:
                                     key, login.
    --delimiter                    : When the request includes this parameter, the operation returns
                                     a :class:`~azure.storage.blob.models.BlobPrefix` element in the
                                     result list that acts as a placeholder for all blobs whose
                                     names begin with the same substring up to the appearance of the
                                     delimiter character. The delimiter may be a single character or
                                     a string.
    --include                      : Specifies additional datasets to include: (c)opy-info,
                                     (m)etadata, (s)napshots, (d)eleted-soft. Can be combined.
    --marker                       : An opaque continuation token. This value can be retrieved from
                                     the next_marker field of a previous generator object if
                                     num_results was specified and that generator has finished
                                     enumerating results. If specified, this generator will begin
                                     returning results from the point where the previous generator
                                     stopped.
    --num-results                  : Specifies the maximum number of results to return. Provide "*"
                                     to return all.  Default: 5000.
    --prefix                       : Filters the results to return only blobs whose names begin with
                                     the specified prefix.
    --timeout                      : Request timeout in seconds. Applies to each call to the
                                     service.
 
Storage Account Arguments
    --account-key                  : Storage account key. Must be used in conjunction with storage
                                     account name. Environment variable: AZURE_STORAGE_KEY.
    --account-name                 : Storage account name. Related environment variable:
                                     AZURE_STORAGE_ACCOUNT. Must be used in conjunction with either
                                     storage account key or a SAS token. If neither are present, the
                                     command will try to query the storage account key using the
                                     authenticated Azure account. If a large number of storage
                                     commands are executed the API quota may be hit.
    --connection-string            : Storage account connection string. Environment variable:
                                     AZURE_STORAGE_CONNECTION_STRING.
    --sas-token                    : A Shared Access Signature (SAS). Must be used in conjunction
                                     with storage account name. Environment variable:
                                     AZURE_STORAGE_SAS_TOKEN.
 
Global Arguments
    --debug                        : Increase logging verbosity to show all debug logs.
    --help -h                      : Show this help message and exit.
    --output -o                    : Output format.  Allowed values: json, jsonc, none, table, tsv,
                                     yaml, yamlc.  Default: json.
    --query                        : JMESPath query string. See http://jmespath.org/ for more
                                     information and examples.
    --subscription                 : Name or ID of subscription. You can configure the default
                                     subscription using `az account set -s NAME_OR_ID`.
    --verbose                      : Increase logging verbosity. Use --debug for full debug logs.
 
Examples
    List blobs in a given container. (autogenerated)
        az storage blob list --container-name MyContainer
 
 
    List all storage blobs in a container whose names start with 'foo'; will match names such as
    'foo', 'foobar', and 'foo/bar'
        az storage blob list --container-name MyContainer --prefix foo
```

**Group example**

```bash
> az eventgrid -h
 
Group
    az eventgrid : Manage Azure Event Grid topics, event subscriptions, domains and domain topics.
 
Subgroups:
    domain             : Manage event domains.
    event-subscription : Manage event subscriptions.
    topic              : Manage Azure Event Grid topics.
    topic-type         : Get details for topic types.
 
Examples
    Create a new event subscription. (autogenerated)
        az eventgrid event-subscription create --endpoint /subscriptions/{SubID}/resourceGroups/Test
        RG/providers/Microsoft.EventHub/namespaces/n1/eventhubs/EH1 --name es1 --source-resource-id
        "/subscriptions/{SubID}/resourceGroups/{RG}/providers/Microsoft.EventGrid/domains/domain1/to
        pics/t1"
 
 
    List event subscriptions. (autogenerated)
        az eventgrid event-subscription list
 
 
    List shared access keys of a domain. (autogenerated)
        az eventgrid domain key list --name MyDomain --resource-group MyResourceGroup
 
 
    Get the details of a topic (autogenerated)
        az eventgrid topic show --name topic1 --resource-group rg1
 

For more specific examples, use: az find "az eventgrid"
 
Please let us know how we are doing: https://aka.ms/clihats
```