# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError


def create_importpipeline(cmd, client, resource_group_name, registry_name, location=None, tags=None):
    
    raise CLIError('TODO: Implement `importpipeline create`')

def list_importpipeline(cmd, client, resource_group_name=None):
    print("doggo")
    raise CLIError('TODO: Implement `importpipeline list`')

def delete_importpipeline(cmd, client, resource_group_name=None):
    raise CLIError('TODO: Implement `importpipeline list`')

def get_importpipeline(cmd, client, resource_group_name=None):
    raise CLIError('TODO: Implement `importpipeline list`')

def update_importpipeline(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance

def create_exportpipeline(cmd, client, resource_group_name, registry_name, location=None, tags=None):
    raise CLIError('TODO: Implement `exportpipeline create`')

def list_exportpipeline(cmd, client, resource_group_name=None):
    raise CLIError('TODO: Implement `exportpipeline list`')

def delete_exportpipeline(cmd, client, resource_group_name=None):
    raise CLIError('TODO: Implement `exportpipeline list`')

def get_exportpipeline(cmd, client, resource_group_name=None):
    raise CLIError('TODO: Implement `exportpipeline list`')

def update_exportpipeline(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance

def create_pipelinerun(cmd, client, resource_group_name, registry_name, location=None, tags=None):
    raise CLIError('TODO: Implement `pipelinerun create`')

def list_pipelinerun(cmd, client, resource_group_name=None):
    raise CLIError('TODO: Implement `pipelinerun list`')

def delete_pipelinerun(cmd, client, resource_group_name=None):
    raise CLIError('TODO: Implement `pipelinerun list`')

def get_pipelinerun(cmd, client, resource_group_name=None):
    raise CLIError('TODO: Implement `pipelinerun list`')
