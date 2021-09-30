
def cosmosdb_data_transfer_job_create2(client,
                                      resource_group_name,
                                      account_name,
                                      job_name,
                                      source,
                                      destination):
    job_create_properties = {}
    job_create_properties['source'] = source
    job_create_properties['destination'] = destination
    job_create_parameters = {}
    job_create_parameters['properties'] = job_create_properties
    return client.create(resource_group_name=resource_group_name,
                         account_name=account_name,
                         job_name=job_name,
                         job_create_parameters=job_create_parameters)