# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, too-many-statements
def load_arguments(self, _):

    
    with self.argument_context("approle list") as c:
        c.argument(
            "app", options_list=["--app", "-a"], help="Application id or display name"
        )

    with self.argument_context("approle assignment add") as c:
        c.argument(
            "service_principal",
            options_list=["--service-principal", "-s"],
            help="Service principal object id, display name or principalName",
        )
        c.argument(
            "app",
            options_list=["--app", "-a"],
            help="Application id or app display name",
        )
        c.argument(
            "role", options_list=["--role", "-r"], help="Role value ie. User.Read"
        )

    with self.argument_context("approle assignment list") as c:
        c.argument(
            "service_principal",
            options_list=["--service-principal", "-s"],
            help="Service principal object id, display name or principalName",
        )

    with self.argument_context("approle assignment remove") as c:
        c.argument(
            "service_principal",
            options_list=["--service-principal", "-s"],
            help="Service principal object id, display name or principalName",
        )
        c.argument(
            "role_assignment_id",
            options_list=["--role-assignment-id", "-r"],
            help="Id of the role assignment ie. QcQ9bB5nuEe6eVGtCAjasjA53tcG25VJjEnObuEi75E",
        )
