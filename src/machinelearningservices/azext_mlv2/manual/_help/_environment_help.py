# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from knack.help_files import helps


def get_environment_help():
    helps[
        "ml environment"
    ] = """
        type: group
        short-summary: Manage Azure ML environments.
        long-summary: >
            Azure ML environments define the execution environment for jobs and endpoint deployments,
            encapsulating the dependencies for training and inference. These environment definitions
            are built into Docker images.
    """
    helps[
        "ml environment list"
    ] = """
        type: command
        short-summary: List environments in a workspace.
        examples:
        - name: List all the environments in a workspace
          text: az ml environment list --resource-group my-resource-group --workspace-name my-workspace
        - name: List all the environment versions for the specified name in a workspace
          text: az ml environment list --name my-env --resource-group my-resource-group --workspace-name my-workspace
        - name: List all the environments in a workspace using --query argument to execute a JMESPath query on the results of commands.
          text: az ml environment list --query \"[].{Name:name}\"  --output table --resource-group my-resource-group --workspace-name my-workspace
        - name: List all the environments in a registry
          text: az ml environment list --registry-name my-registry-name --resource-group my-resource-group
        - name: List all the environment versions for the specified name in a registry
          text: az ml environment list --name my-env --registry-name my-registry-name --resource-group my-resource-group
    """
    helps[
        "ml environment show"
    ] = """
        type: command
        short-summary: Show details for an environment.
        examples:
        - name: Show details for an environment with the specified name and version
          text: az ml environment show --name my-env --version 1 --resource-group my-resource-group --workspace-name my-workspace
        - name: Show details for an environment in registry with the specified name and version
          text: az ml environment show --name my-env --version 1 --registry-name my-registry-name --resource-group my-resource-group
    """
    helps[
        "ml environment create"
    ] = """
        type: command
        short-summary: Create an environment.
        long-summary: >
            Environments can be defined from a Docker image, Dockerfile, or Conda file.
            Azure ML maintains a set of CPU and GPU Docker images that you can use as base images.
            For information on these images, see https://github.com/Azure/AzureML-Containers.


            The created environment will be tracked in the workspace under the specified name
            and version.
        examples:
        - name: Create an environment from a YAML specification file
          text: az ml environment create --file my_env.yml --resource-group my-resource-group --workspace-name my-workspace
        - name: Create an environment from a docker image
          text: az ml environment create --name my-env --version 1 --file my_env.yml  --image pytorch/pytorch --resource-group my-resource-group --workspace-name my-workspace
        - name: Create an environment from a build context
          text: az ml environment create --name my-env --version 1 --file my_env.yml  --build-context envs/context/ --dockerfile-path Dockerfile --resource-group my-resource-group --workspace-name my-workspace
        - name: Create an environment from a conda specification
          text: az ml environment create --name my-env --version 1 --file my_env.yml  --conda-file conda_dep.yml --image mcr.microsoft.com/azureml/openmpi3.1.2-ubuntu18.04 --resource-group my-resource-group --workspace-name my-workspace
        - name: Create an environment in registry from a YAML specification file
          text: az ml environment create --file my_env.yml --registry-name my-registry-name --resource-group my-resource-group
    """
    helps[
        "ml environment update"
    ] = """
        type: command
        short-summary: Update an environment.
        long-summary: >
            Only the 'description' and 'tags' properties can be updated.
    """
    helps[
        "ml environment archive"
    ] = """
        type: command
        short-summary: Archive an environment.
        long-summary: >
            Archiving an environment will hide it by default from list queries (`az ml environment list`). You
            can still continue to reference and use an archived environment in your workflows.
            You can archive either an environment container or a specific environment version. Archiving an
            environment container will archive all versions of the environment under that given name.
            You can restore an archived environment using `az ml environment restore`. If the entire
            environment container is archived, you cannot restore individual versions of the environment -
            you will need to restore the environment container.
        examples:
        - name: Archive an environment container (archives all versions of that environment)
          text: az ml environment archive --name my-env --resource-group my-resource-group --workspace-name my-workspace
        - name: Archive a specific environment version
          text: az ml environment archive --name my-env --version 1 --resource-group my-resource-group --workspace-name my-workspace
    """
    helps[
        "ml environment restore"
    ] = """
        type: command
        short-summary: Restore an archived environment.
        long-summary: >
            When an archived environment is restored, it will no longer be hidden from list queries (`az ml
            environment list`).
            If an entire environment container is archived, you can restore that archived container. This
            will restore all versions of the environment under that given name. You cannot restore only a
            specific environment version if the entire environment container is archived - you will need to
            restore the entire container. If only an individual environment version was archived, you can
            restore that specific version.
        examples:
        - name: Restore an archived environment container (restores all versions of that environment)
          text: az ml environment restore --name my-env --resource-group my-resource-group --workspace-name my-workspace
        - name: Restore a specific archived environment version
          text: az ml environment restore --name my-env --version 1 --resource-group my-resource-group --workspace-name my-workspace
    """
    helps[
        "ml environment share"
    ] = """
        type: command
        short-summary: Share a specific environment from workspace to registry.
        long-summary: >
            Copy an existing environment from a workspace to a registry for cross-workspace reuse.
        examples:
        - name: Share an existing environment from workspace to registry
          text: az ml environment share --name my-environment --version my-version --resource-group my-resource-group --workspace-name my-workspace --share-with-name new-name-in-registry --share-with-version new-version-in-registry --registry-name my-registry
    """
