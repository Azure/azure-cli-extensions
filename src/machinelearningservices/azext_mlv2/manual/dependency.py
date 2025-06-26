# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import pkg_resources

REQUIREMENTS = []
with open("azext_mlv2/manual/requirements.txt", "rt") as fd:
    REQUIREMENTS = [str(requirement) for requirement in pkg_resources.parse_requirements(fd)]
DEPENDENCIES = REQUIREMENTS
