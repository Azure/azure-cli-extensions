# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument


def create_internet_analyzer_profile(cmd, client,
                                     resource_group,
                                     name,
                                     location=None,
                                     tags=None,
                                     enabled_state=None,
                                     etag=None):
    body = {}
    body['location'] = location  # str
    body['tags'] = tags  # dictionary
    body['enabled_state'] = enabled_state  # str
    body['etag'] = etag  # str
    return client.create_or_update(resource_group_name=resource_group, profile_name=name, parameters=body)


def delete_internet_analyzer_profile(cmd, client,
                                     resource_group,
                                     name):
    return client.delete(resource_group_name=resource_group, profile_name=name)


def update_internet_analyzer_profile(cmd, client,
                                     resource_group,
                                     name,
                                     location=None,
                                     tags=None,
                                     enabled_state=None,
                                     etag=None):
    body = client.get(resource_group_name=resource_group, profile_name=name).as_dict()
    body.location = location  # str
    body.tags = tags  # dictionary
    body.enabled_state = enabled_state  # str
    body.etag = etag  # str
    return client.create_or_update(resource_group_name=resource_group, profile_name=name, parameters=body)


def list_internet_analyzer_profile(cmd, client,
                                   resource_group):
    if resource_group is not None:
        return client.list_by_resource_group(resource_group_name=resource_group)
    return client.list()


def get_internet_analyzer_profile(cmd, client,
                                  resource_group,
                                  name):
    return client.get(resource_group, name)


def list_internet_analyzer_preconfigured_endpoint(cmd, client,
                                                  resource_group,
                                                  profile_name):
    return client.list(resource_group_name=resource_group, profile_name=profile_name)


def create_internet_analyzer_test(cmd, client,
                                  resource_group,
                                  profile_name,
                                  name,
                                  location=None,
                                  tags=None,
                                  description=None,
                                  endpoint_a_name=None,
                                  endpoint_a_endpoint=None,
                                  endpoint_b_name=None,
                                  endpoint_b_endpoint=None,
                                  enabled_state=None):
    body = {}
    body['location'] = location  # str
    body['tags'] = tags  # dictionary
    body['description'] = description  # str
    body.setdefault('endpoint_a', {})['name'] = endpoint_a_name  # str
    body.setdefault('endpoint_a', {})['endpoint'] = endpoint_a_endpoint  # str
    body.setdefault('endpoint_b', {})['name'] = endpoint_b_name  # str
    body.setdefault('endpoint_b', {})['endpoint'] = endpoint_b_endpoint  # str
    body['enabled_state'] = enabled_state  # str
    return client.create_or_update(resource_group_name=resource_group, profile_name=profile_name, experiment_name=name, parameters=body)


def delete_internet_analyzer_test(cmd, client,
                                  resource_group,
                                  profile_name,
                                  name):
    return client.delete(resource_group_name=resource_group, profile_name=profile_name, experiment_name=name)


def update_internet_analyzer_test(cmd, client,
                                  resource_group,
                                  profile_name,
                                  name,
                                  location=None,
                                  tags=None,
                                  description=None,
                                  endpoint_a_name=None,
                                  endpoint_a_endpoint=None,
                                  endpoint_b_name=None,
                                  endpoint_b_endpoint=None,
                                  enabled_state=None):
    body = client.get(resource_group_name=resource_group, profile_name=profile_name, experiment_name=name).as_dict()
    body.location = location  # str
    body.tags = tags  # dictionary
    body.description = description  # str
    body.endpoint_a.name = endpoint_a_name  # str
    body.endpoint_a.endpoint = endpoint_a_endpoint  # str
    body.endpoint_b.name = endpoint_b_name  # str
    body.endpoint_b.endpoint = endpoint_b_endpoint  # str
    body.enabled_state = enabled_state  # str
    return client.create_or_update(resource_group_name=resource_group, profile_name=profile_name, experiment_name=name, parameters=body)


def list_internet_analyzer_test(cmd, client,
                                resource_group,
                                profile_name):
    return client.list_by_profile(resource_group_name=resource_group, profile_name=profile_name)


def get_internet_analyzer_test(cmd, client,
                               resource_group,
                               profile_name,
                               name):
    return client.get(resource_group_name=resource_group, profile_name=profile_name, experiment_name=name)


def get_timeseries(cmd, client,
                   resource_group,
                   profile_name,
                   test_name,
                   aggregation_interval,
                   start_date_time_utc,
                   end_date_time_utc,
                   timeseries_type,
                   endpoint,
                   country=None):
    return client.get_timeseries(resource_group_name=resource_group, profile_name=profile_name, experiment_name=test_name, aggregation_interval=aggregation_interval, start_date_time_utc=start_date_time_utc, end_date_time_utc=end_date_time_utc, timeseries_type=timeseries_type, country=country, endpoint=endpoint)


def get_latency_scorecards(cmd, client,
                           resource_group,
                           profile_name,
                           test_name,
                           aggregation_interval,
                           country=None,
                           end_date_time_utc=None):
    return client.get_latency_scorecards(resource_group_name=resource_group, profile_name=profile_name, experiment_name=test_name, aggregation_interval=aggregation_interval, country=country, end_date_time_utc=end_date_time_utc)
