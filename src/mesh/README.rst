Microsoft Azure CLI 'mesh' Command Module
==============================================================

Commands to manage Azure Service Fabric Mesh resources
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
::

    Group
        az mesh: Manage Azure Service Fabric Mesh resources.

    Commands:
        app create: Create an application.
        app delete: Delete an application.
        app list  : List applications.
        app show  : Show the details of an application.
        codepackage logs  : Tail the log of a container.

Commands to create an application
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
::

	Command
		az mesh app create: Create an Service Fabric Mesh application.

	Arguments
		--resource-group -g [Required]: Name of resource group. You can configure the default group
										using `az configure --defaults group=<name>`.
		--mode
		--no-wait                     : Do not wait for the long-running operation to finish.
		--parameters
		--template-file               : The full file path of creation template.
		--template-uri                : The full file path of creation template on a http or https link.

	Global Arguments
		--debug                       : Increase logging verbosity to show all debug logs.
		--help -h                     : Show this help message and exit.
		--output -o                   : Output format.  Allowed values: json, jsonc, table, tsv.
										Default: json.
		--query                       : JMESPath query string. See http://jmespath.org/ for more
										information and examples.
		--verbose                     : Increase logging verbosity. Use --debug for full debug logs.

	Examples
		Create an application with a template file on the remote.
			az mesh app create --resource-group mygroup --template-uri
			https://seabreezequickstart.blob.core.windows.net/quickstart/application-quickstart.json

		Create an application with a template file on local disk.
			az mesh app create --resource-group mygroup --template-file ./appTemplate.json
