# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging
import sys


def parse_module_name(levels=1):
    module_name = None
    module_levels = __name__.split(".")
    if len(module_levels) < levels:
        print("Failed to parse {}-level module name from '{}'".format(levels, __name__))
    else:
        module_name = ".".join(module_levels[:levels])
    return module_name


def setup_logging(root_logger_name=None, log_path="az_aks_tool.log"):
    if root_logger_name == "" or root_logger_name.isspace():
        root_logger_name = parse_module_name()
    logger = logging.getLogger(root_logger_name)
    logger.setLevel(level=logging.DEBUG)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # FileHandler
    file_handler = logging.FileHandler(filename=log_path, mode="w")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level=logging.DEBUG)
    logger.addHandler(file_handler)

    # StreamHandler
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(level=logging.INFO)
    logger.addHandler(stream_handler)
