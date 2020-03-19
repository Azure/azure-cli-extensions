# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines

import json


def migrateprojects_database_instance_show(cmd, client,
                                           resource_group_name,
                                           migrate_project_name,
                                           database_instance_name):
    return client.get_database_instance(resource_group_name=resource_group_name, migrate_project_name=migrate_project_name, database_instance_name=database_instance_name)


def migrateprojects_database_instance_enumerate_database_instance(cmd, client,
                                                                  resource_group_name,
                                                                  migrate_project_name,
                                                                  continuation_token=None,
                                                                  page_size=None):
    return client.enumerate_database_instance(resource_group_name=resource_group_name, migrate_project_name=migrate_project_name, continuation_token=continuation_token, page_size=page_size)


def migrateprojects_database_show(cmd, client,
                                  resource_group_name,
                                  migrate_project_name,
                                  database_name):
    return client.get_database(resource_group_name=resource_group_name, migrate_project_name=migrate_project_name, database_name=database_name)


def migrateprojects_database_enumerate_database(cmd, client,
                                                resource_group_name,
                                                migrate_project_name,
                                                continuation_token=None,
                                                page_size=None):
    return client.enumerate_database(resource_group_name=resource_group_name, migrate_project_name=migrate_project_name, continuation_token=continuation_token, page_size=page_size)


def migrateprojects_event_show(cmd, client,
                               resource_group_name,
                               migrate_project_name,
                               event_name):
    return client.get_event(resource_group_name=resource_group_name, migrate_project_name=migrate_project_name, event_name=event_name)


def migrateprojects_event_delete(cmd, client,
                                 resource_group_name,
                                 migrate_project_name,
                                 event_name):
    return client.delete_event(resource_group_name=resource_group_name, migrate_project_name=migrate_project_name, event_name=event_name)


def migrateprojects_event_enumerate_event(cmd, client,
                                          resource_group_name,
                                          migrate_project_name,
                                          continuation_token=None,
                                          page_size=None):
    return client.enumerate_event(resource_group_name=resource_group_name, migrate_project_name=migrate_project_name, continuation_token=continuation_token, page_size=page_size)


def migrateprojects_machine_show(cmd, client,
                                 resource_group_name,
                                 migrate_project_name,
                                 machine_name):
    return client.get_machine(resource_group_name=resource_group_name, migrate_project_name=migrate_project_name, machine_name=machine_name)


def migrateprojects_machine_enumerate_machine(cmd, client,
                                              resource_group_name,
                                              migrate_project_name,
                                              continuation_token=None,
                                              page_size=None):
    return client.enumerate_machine(resource_group_name=resource_group_name, migrate_project_name=migrate_project_name, continuation_token=continuation_token, page_size=page_size)


def migrateprojects_migrate_project_show(cmd, client,
                                         resource_group_name,
                                         migrate_project_name):
    return client.get_migrate_project(resource_group_name=resource_group_name, migrate_project_name=migrate_project_name)


def migrateprojects_migrate_project_delete(cmd, client,
                                           resource_group_name,
                                           migrate_project_name):
    return client.delete_migrate_project(resource_group_name=resource_group_name, migrate_project_name=migrate_project_name)


def migrateprojects_migrate_project_put_migrate_project(cmd, client,
                                                        resource_group_name,
                                                        migrate_project_name,
                                                        e_tag=None,
                                                        location=None,
                                                        properties=None,
                                                        tags=None):
    properties = json.loads(properties) if isinstance(properties, str) else properties
    return client.put_migrate_project(resource_group_name=resource_group_name, migrate_project_name=migrate_project_name, e_tag=e_tag, location=location, properties=properties, tags=tags)


def migrateprojects_migrate_project_patch_migrate_project(cmd, client,
                                                          resource_group_name,
                                                          migrate_project_name,
                                                          e_tag=None,
                                                          location=None,
                                                          properties=None,
                                                          tags=None):
    properties = json.loads(properties) if isinstance(properties, str) else properties
    return client.patch_migrate_project(resource_group_name=resource_group_name, migrate_project_name=migrate_project_name, e_tag=e_tag, location=location, properties=properties, tags=tags)


def migrateprojects_migrate_project_register_tool(cmd, client,
                                                  resource_group_name,
                                                  migrate_project_name,
                                                  tool=None):
    return client.register_tool(resource_group_name=resource_group_name, migrate_project_name=migrate_project_name, tool=tool)


def migrateprojects_migrate_project_refresh_migrate_project_summary(cmd, client,
                                                                    resource_group_name,
                                                                    migrate_project_name,
                                                                    goal=None):
    return client.refresh_migrate_project_summary(resource_group_name=resource_group_name, migrate_project_name=migrate_project_name, goal=goal)


def migrateprojects_solution_show(cmd, client,
                                  resource_group_name,
                                  migrate_project_name,
                                  solution_name):
    return client.get_solution(resource_group_name=resource_group_name, migrate_project_name=migrate_project_name, solution_name=solution_name)


def migrateprojects_solution_delete(cmd, client,
                                    resource_group_name,
                                    migrate_project_name,
                                    solution_name):
    return client.delete_solution(resource_group_name=resource_group_name, migrate_project_name=migrate_project_name, solution_name=solution_name)


def migrateprojects_solution_put_solution(cmd, client,
                                          resource_group_name,
                                          migrate_project_name,
                                          solution_name,
                                          etag=None,
                                          properties=None):
    properties = json.loads(properties) if isinstance(properties, str) else properties
    return client.put_solution(resource_group_name=resource_group_name, migrate_project_name=migrate_project_name, solution_name=solution_name, etag=etag, properties=properties)


def migrateprojects_solution_patch_solution(cmd, client,
                                            resource_group_name,
                                            migrate_project_name,
                                            solution_name,
                                            etag=None,
                                            properties=None):
    properties = json.loads(properties) if isinstance(properties, str) else properties
    return client.patch_solution(resource_group_name=resource_group_name, migrate_project_name=migrate_project_name, solution_name=solution_name, etag=etag, properties=properties)


def migrateprojects_solution_get_config(cmd, client,
                                        resource_group_name,
                                        migrate_project_name,
                                        solution_name):
    return client.get_config(resource_group_name=resource_group_name, migrate_project_name=migrate_project_name, solution_name=solution_name)


def migrateprojects_solution_cleanup_solution_data(cmd, client,
                                                   resource_group_name,
                                                   migrate_project_name,
                                                   solution_name):
    return client.cleanup_solution_data(resource_group_name=resource_group_name, migrate_project_name=migrate_project_name, solution_name=solution_name)


def migrateprojects_solution_enumerate_solution(cmd, client,
                                                resource_group_name,
                                                migrate_project_name):
    return client.enumerate_solution(resource_group_name=resource_group_name, migrate_project_name=migrate_project_name)
