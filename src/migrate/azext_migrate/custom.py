# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument


def migrate_location_check_name_availability(cmd, client,
                                             location_name,
                                             name):
    return client.check_name_availability(location_name=location_name, name=name)


def migrate_assessment_options_show(cmd, client,
                                    location_name):
    return client.get(location_name=location_name)


def migrate_projects_list(cmd, client,
                          resource_group_name=None):
    if resource_group_name is not None:
        return client.list_by_resource_group(resource_group_name=resource_group_name)
    return client.list_by_subscription()


def migrate_projects_show(cmd, client,
                          resource_group_name,
                          project_name):
    return client.get(resource_group_name=resource_group_name, project_name=project_name)


def migrate_projects_create(cmd, client,
                            resource_group_name,
                            project_name,
                            e_tag=None,
                            location=None,
                            tags=None,
                            customer_workspace_id=None,
                            customer_workspace_location=None,
                            provisioning_state=None):
    return client.create(resource_group_name=resource_group_name, project_name=project_name, e_tag=e_tag, location=location, tags=tags, customer_workspace_id=customer_workspace_id, customer_workspace_location=customer_workspace_location, provisioning_state=provisioning_state)


def migrate_projects_update(cmd, client,
                            resource_group_name,
                            project_name,
                            e_tag=None,
                            location=None,
                            tags=None,
                            customer_workspace_id=None,
                            customer_workspace_location=None,
                            provisioning_state=None):
    return client.update(resource_group_name=resource_group_name, project_name=project_name, e_tag=e_tag, location=location, tags=tags, customer_workspace_id=customer_workspace_id, customer_workspace_location=customer_workspace_location, provisioning_state=provisioning_state)


def migrate_projects_delete(cmd, client,
                            resource_group_name,
                            project_name):
    return client.delete(resource_group_name=resource_group_name, project_name=project_name)


def migrate_projects_get_keys(cmd, client,
                              resource_group_name,
                              project_name):
    return client.get_keys(resource_group_name=resource_group_name, project_name=project_name)


def migrate_machines_list(cmd, client,
                          resource_group_name,
                          project_name):
    return client.list_by_project(resource_group_name=resource_group_name, project_name=project_name)


def migrate_machines_show(cmd, client,
                          resource_group_name,
                          project_name,
                          machine_name):
    return client.get(resource_group_name=resource_group_name, project_name=project_name, machine_name=machine_name)


def migrate_groups_list(cmd, client,
                        resource_group_name,
                        project_name):
    return client.list_by_project(resource_group_name=resource_group_name, project_name=project_name)


def migrate_groups_show(cmd, client,
                        resource_group_name,
                        project_name,
                        group_name):
    return client.get(resource_group_name=resource_group_name, project_name=project_name, group_name=group_name)


def migrate_groups_create(cmd, client,
                          resource_group_name,
                          project_name,
                          group_name,
                          machines,
                          e_tag=None):
    return client.create(resource_group_name=resource_group_name, project_name=project_name, group_name=group_name, e_tag=e_tag, machines=machines)


def migrate_groups_delete(cmd, client,
                          resource_group_name,
                          project_name,
                          group_name):
    return client.delete(resource_group_name=resource_group_name, project_name=project_name, group_name=group_name)


def migrate_assessments_list(cmd, client,
                             resource_group_name,
                             project_name,
                             group_name=None):
    if resource_group_name is not None and project_name is not None and group_name is not None:
        return client.list_by_group(resource_group_name=resource_group_name, project_name=project_name, group_name=group_name)
    return client.list_by_project(resource_group_name=resource_group_name, project_name=project_name)


def migrate_assessments_show(cmd, client,
                             resource_group_name,
                             project_name,
                             group_name,
                             assessment_name):
    return client.get(resource_group_name=resource_group_name, project_name=project_name, group_name=group_name, assessment_name=assessment_name)


def migrate_assessments_create(cmd, client,
                               resource_group_name,
                               project_name,
                               group_name,
                               assessment_name,
                               azure_location,
                               azure_offer_code,
                               azure_pricing_tier,
                               azure_storage_redundancy,
                               scaling_factor,
                               percentile,
                               time_range,
                               stage,
                               currency,
                               azure_hybrid_use_benefit,
                               discount_percentage,
                               sizing_criterion,
                               e_tag=None):
    return client.create(resource_group_name=resource_group_name, project_name=project_name, group_name=group_name, assessment_name=assessment_name, e_tag=e_tag, azure_location=azure_location, azure_offer_code=azure_offer_code, azure_pricing_tier=azure_pricing_tier, azure_storage_redundancy=azure_storage_redundancy, scaling_factor=scaling_factor, percentile=percentile, time_range=time_range, stage=stage, currency=currency, azure_hybrid_use_benefit=azure_hybrid_use_benefit, discount_percentage=discount_percentage, sizing_criterion=sizing_criterion)


def migrate_assessments_delete(cmd, client,
                               resource_group_name,
                               project_name,
                               group_name,
                               assessment_name):
    return client.delete(resource_group_name=resource_group_name, project_name=project_name, group_name=group_name, assessment_name=assessment_name)


def migrate_assessments_get_report_download_url(cmd, client,
                                                resource_group_name,
                                                project_name,
                                                group_name,
                                                assessment_name):
    return client.get_report_download_url(resource_group_name=resource_group_name, project_name=project_name, group_name=group_name, assessment_name=assessment_name)


def migrate_assessed_machines_list(cmd, client,
                                   resource_group_name,
                                   project_name,
                                   group_name,
                                   assessment_name):
    return client.list_by_assessment(resource_group_name=resource_group_name, project_name=project_name, group_name=group_name, assessment_name=assessment_name)


def migrate_assessed_machines_show(cmd, client,
                                   resource_group_name,
                                   project_name,
                                   group_name,
                                   assessment_name,
                                   assessed_machine_name):
    return client.get(resource_group_name=resource_group_name, project_name=project_name, group_name=group_name, assessment_name=assessment_name, assessed_machine_name=assessed_machine_name)


def migrate_operations_list(cmd, client):
    return client.list()
