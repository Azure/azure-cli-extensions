# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['migrate location'] = """
    type: group
    short-summary: migrate location
"""

helps['migrate location check-name-availability'] = """
    type: command
    short-summary: Checks whether the project name is available in the specified region.
"""

helps['migrate assessment-options'] = """
    type: group
    short-summary: migrate assessment-options
"""

helps['migrate assessment-options show'] = """
    type: command
    short-summary: Get the available options for the properties of an assessment.
"""

helps['migrate projects'] = """
    type: group
    short-summary: migrate projects
"""

helps['migrate projects list'] = """
    type: command
    short-summary: Get all the projects in the subscription.
"""

helps['migrate projects show'] = """
    type: command
    short-summary: Get the project with the specified name.
"""

helps['migrate projects create'] = """
    type: command
    short-summary: Create a project with specified name. If a project already exists, update it.
"""

helps['migrate projects update'] = """
    type: command
    short-summary: Update a project with specified name. Supports partial updates, for example only tags can be provided.
"""

helps['migrate projects delete'] = """
    type: command
    short-summary: Delete the project. Deleting non-existent project is a no-operation.
"""

helps['migrate projects get-keys'] = """
    type: command
    short-summary: Gets the Log Analytics Workspace ID and Primary Key for the specified project.
"""

helps['migrate machines'] = """
    type: group
    short-summary: migrate machines
"""

helps['migrate machines list'] = """
    type: command
    short-summary: Get data of all the machines available in the project. Returns a json array of objects of type 'machine' defined in Models section.
"""

helps['migrate machines show'] = """
    type: command
    short-summary: Get the machine with the specified name. Returns a json object of type 'machine' defined in Models section.
"""

helps['migrate groups'] = """
    type: group
    short-summary: migrate groups
"""

helps['migrate groups list'] = """
    type: command
    short-summary: Get all groups created in the project. Returns a json array of objects of type 'group' as specified in the Models section.
"""

helps['migrate groups show'] = """
    type: command
    short-summary: Get information related to a specific group in the project. Returns a json object of type 'group' as specified in the models section.
"""

helps['migrate groups create'] = """
    type: command
    short-summary: Create a new group by sending a json object of type 'group' as given in Models section as part of the Request Body. The group name in a project is unique. Labels can be applied on a group as part of creation.

If a group with the groupName specified in the URL already exists, then this call acts as an update.

This operation is Idempotent.
"""

helps['migrate groups delete'] = """
    type: command
    short-summary: Delete the group from the project. The machines remain in the project. Deleting a non-existent group results in a no-operation.

A group is an aggregation mechanism for machines in a project. Therefore, deleting group does not delete machines in it.
"""

helps['migrate assessments'] = """
    type: group
    short-summary: migrate assessments
"""

helps['migrate assessments list'] = """
    type: command
    short-summary: Get all assessments created in the project.

Returns a json array of objects of type 'assessment' as specified in Models section.
"""

helps['migrate assessments show'] = """
    type: command
    short-summary: Get an existing assessment with the specified name. Returns a json object of type 'assessment' as specified in Models section.
"""

helps['migrate assessments create'] = """
    type: command
    short-summary: Create a new assessment with the given name and the specified settings. Since name of an assessment in a project is a unique identifier, if an assessment with the name provided already exists, then the existing assessment is updated.

Any PUT operation, resulting in either create or update on an assessment, will cause the assessment to go in a "InProgress" state. This will be indicated by the field 'computationState' on the Assessment object. During this time no other PUT operation will be allowed on that assessment object, nor will a Delete operation. Once the computation for the assessment is complete, the field 'computationState' will be updated to 'Ready', and then other PUT or DELETE operations can happen on the assessment.

When assessment is under computation, any PUT will lead to a 400 - Bad Request error.
"""

helps['migrate assessments delete'] = """
    type: command
    short-summary: Delete an assessment from the project. The machines remain in the assessment. Deleting a non-existent assessment results in a no-operation.

When an assessment is under computation, as indicated by the 'computationState' field, it cannot be deleted. Any such attempt will return a 400 - Bad Request.
"""

helps['migrate assessments get-report-download-url'] = """
    type: command
    short-summary: Get the URL for downloading the assessment in a report format.
"""

helps['migrate assessed-machines'] = """
    type: group
    short-summary: migrate assessed-machines
"""

helps['migrate assessed-machines list'] = """
    type: command
    short-summary: Get list of machines that assessed as part of the specified assessment. Returns a json array of objects of type 'assessedMachine' as specified in the Models section.

Whenever an assessment is created or updated, it goes under computation. During this phase, the 'status' field of Assessment object reports 'Computing'.
During the period when the assessment is under computation, the list of assessed machines is empty and no assessed machines are returned by this call.
"""

helps['migrate assessed-machines show'] = """
    type: command
    short-summary: Get an assessed machine with its size & cost estimate that was evaluated in the specified assessment.
"""

helps['migrate operations'] = """
    type: group
    short-summary: migrate operations
"""

helps['migrate operations list'] = """
    type: command
    short-summary: Get a list of REST API supported by Microsoft.Migrate provider.
"""
