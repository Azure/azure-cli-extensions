from _constants import CREATE_APP_TEMPLATE

# def get_resource_group_list():
#     resource_group_list = [{'name': 'testrg123', 'location': 'East US'}, {'name': 'testrg456', 'location': 'West US'}]
#     return '\n'.join([f"name: {rg['name']}, location: {rg['location']}" for rg in resource_group_list])

def get_server_farm_id_list():
    pass

def create_app_template():
    template = CREATE_APP_TEMPLATE.format(resource_group_list='',
                                          app_service_plan_id_list='',
                                        )
    # assert len(template) <= 1024
    return template

def create_storage_template():
    pass

def create_connection_template(source_type, target_type):
    pass

get_template = {
    'create resource': {
        'web app': create_app_template,
        'storage': create_storage_template,
    },
    'connect resources': {
        
    }
}
