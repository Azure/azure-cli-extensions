# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# flake8: noqa

import logging

from azure.cli.core.extension import ExtensionNotInstalledException
from azure.cli.core.extension.operations import add_extension_to_path

try:
    add_extension_to_path("ml")
except ExtensionNotInstalledException:
    logging.warning("Either ml extension is not installed or you are running ml extension in dev mode")

from azext_mlv2.manual.custom import utils

# set caller info to current telemetry session
from azure.cli.core import telemetry

telemetry.set_debug_info("SystemInvoker", utils.get_cli_system_executed())

from ._telemetry import *
from .azure_openai_deployment import *
from .batch_deployment import *
from .batch_endpoint import *
from .component import *
from .compute import *
from .connection import *
from .data import *
from .datastore import *
from .environment import *
from .feature_set import *
from .feature_store import *
from .feature_store_entity import *
from .index import *
from .job import *
from .marketplace_subscription import *
from .model import *
from .online_deployment import *
from .online_endpoint import *
from .registry import *
from .schedule import *
from .serverless_endpoint import *
from .virtual_cluster import *
from .workspace import *
from .workspace_outbound_rule import *
from .capability_host import *

# nopycln: file
