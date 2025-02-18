import struct
import requests
from .target_handler import AUTHTYPES, run_cli_cmd
from .sql_handler import ResourceNotFoundError, SqlHandler
from azure.cli.core import telemetry
from knack.log import get_logger
from azure.cli.core.azclierror import CLIInternalError
from azure.cli.command_modules.serviceconnector._resource_config import AUTH_TYPE

logger = get_logger(__name__)


