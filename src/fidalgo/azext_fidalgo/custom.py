# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError


#def create_fidalgo(cmd, resource_group_name, fidalgo_name, location=None, tags=None):
#    raise CLIError('TODO: Implement `fidalgo create`')

#def update_fidalgo(cmd, instance, tags=None):
#    with cmd.update_context(instance) as c:
#        c.set_param('tags', tags)
#    return instance


def list_project(client,
                dev_center,
                fidalgo_dns_suffix=None,
                top=None,
                filter_=None):
    return client.list_by_dev_center(dev_center=dev_center,
                                     fidalgo_dns_suffix=get_dns_suffix(fidalgo_dns_suffix),
                                     top=None,
                                     filter=None)

def fidalgo_pool_list(client,
                      project_name,
                      dev_center,
                      fidalgo_dns_suffix=None,
                      top=None,
                      filter_=None):
    return client.list(dev_center=dev_center,
                       fidalgo_dns_suffix=get_dns_suffix(fidalgo_dns_suffix),
                       top=top,
                       filter=filter_,
                       project_name=project_name)


def fidalgo_pool_show(client,
                      pool_name,
                      project_name,
                      dev_center,
                      fidalgo_dns_suffix=None):
    return client.get(pool_name=pool_name,
                      project_name=project_name,
                      dev_center=dev_center,
                      fidalgo_dns_suffix=get_dns_suffix(fidalgo_dns_suffix))


def fidalgo_virtual_machine_list(client,
                                 dev_center,
                                 fidalgo_dns_suffix=None,
                                 filter_=None,
                                 top=None,
                                 project_name=None,
                                 user_id=None):
    if project_name is not None:
        if user_id is None:
            user_id = 'me'
        return client.list_by_project(filter=filter_,
                                      top=top,
                                      project_name=project_name,
                                      user_id=user_id,
                                      dev_center=dev_center,
                                      fidalgo_dns_suffix=get_dns_suffix(fidalgo_dns_suffix))
    return client.list(filter=filter_,
                       top=top,
                       dev_center=dev_center,
                       fidalgo_dns_suffix=get_dns_suffix(fidalgo_dns_suffix))


def fidalgo_virtual_machine_show(client,
                                 project_name,
                                 virtual_machine_name,
                                 dev_center,
                                 user_id='me',
                                 fidalgo_dns_suffix=None):
    return client.get(project_name=project_name,
                      user_id=user_id,
                      virtual_machine_name=virtual_machine_name,
                      dev_center=dev_center,
                      fidalgo_dns_suffix=get_dns_suffix(fidalgo_dns_suffix))


def fidalgo_virtual_machine_create(client,
                                   project_name,
                                   virtual_machine_name,
                                   pool_name,
                                   dev_center,
                                   user_id='me',
                                   fidalgo_dns_suffix=None):
    body = {}
    body['pool_name'] = pool_name
    return client.create(project_name=project_name,
                         user_id=user_id,
                         virtual_machine_name=virtual_machine_name,
                         body=body,
                         dev_center=dev_center,
                         fidalgo_dns_suffix=get_dns_suffix(fidalgo_dns_suffix))


def fidalgo_virtual_machine_delete(client,
                                   project_name,
                                   virtual_machine_name,
                                   dev_center,
                                   user_id='me',
                                   fidalgo_dns_suffix=None):
    return client.delete(project_name=project_name,
                         user_id=user_id,
                         virtual_machine_name=virtual_machine_name,
                         dev_center=dev_center,
                         fidalgo_dns_suffix=get_dns_suffix(fidalgo_dns_suffix))


def fidalgo_virtual_machine_assign(client,
                                   project_name,
                                   virtual_machine_name,
                                   new_owner,
                                   dev_center,
                                   user_id='me',
                                   fidalgo_dns_suffix=None):
    body = {}
    body['new_owner'] = new_owner
    return client.assign(project_name=project_name,
                         user_id=user_id,
                         virtual_machine_name=virtual_machine_name,
                         body=body,
                         dev_center=dev_center,
                         fidalgo_dns_suffix=get_dns_suffix(fidalgo_dns_suffix))


def fidalgo_virtual_machine_get_rdp_file_content(client,
                                                 project_name,
                                                 virtual_machine_name,
                                                 dev_center,
                                                 user_id='me',
                                                 fidalgo_dns_suffix=None):
    return client.get_rdp_file_contents(project_name=project_name,
                                        user_id=user_id,
                                        virtual_machine_name=virtual_machine_name,
                                        dev_center=dev_center,
                                        fidalgo_dns_suffix=get_dns_suffix(fidalgo_dns_suffix))


def fidalgo_virtual_machine_start(client,
                                  project_name,
                                  virtual_machine_name,
                                  dev_center,
                                  user_id='me',
                                  fidalgo_dns_suffix=None):
    return client.start(project_name=project_name,
                        user_id=user_id,
                        virtual_machine_name=virtual_machine_name,
                        dev_center=dev_center,
                        fidalgo_dns_suffix=get_dns_suffix(fidalgo_dns_suffix))


def fidalgo_virtual_machine_stop(client,
                                 project_name,
                                 virtual_machine_name,
                                 dev_center,
                                 user_id='me',
                                 fidalgo_dns_suffix=None):
    return client.stop(project_name=project_name,
                       user_id=user_id,
                       virtual_machine_name=virtual_machine_name,
                       dev_center=dev_center,
                       fidalgo_dns_suffix=get_dns_suffix(fidalgo_dns_suffix))



# todo: how to pass optional arg so we don't have to redefine the dns suffix here?
def get_dns_suffix(user_provided_value):
    if user_provided_value == None:
        return 'devcenters.fidalgo.azure.com'
    else:
        return user_provided_value
