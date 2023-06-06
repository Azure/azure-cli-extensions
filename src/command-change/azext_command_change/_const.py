# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
BLOB_SETTING_CONFIG_FILE = "blob_config.ini"
script_directory = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE_PATH = f"{script_directory}/{BLOB_SETTING_CONFIG_FILE}"

DOWNLOAD_THREADS = 10


CMD_PROPERTY_REMOVE_BREAK_LIST = []
CMD_PROPERTY_ADD_BREAK_LIST = ["confirmation"]
CMD_PROPERTY_UPDATE_BREAK_LIST = []

PARA_PROPERTY_REMOVE_BREAK_LIST = ["options", "id_part", "nargs"]
PARA_PROPERTY_ADD_BREAK_LIST = ["required", "choices", "nargs"]
PARA_PROPERTY_UPDATE_BREAK_LIST = ["default", "aaz_default"]

EXPORTED_CSV_META_HEADER = ["module", "cmd_name", "rule_id", "rule_name", "is_break",
                            "rule_message", "suggest_message"]

CHANGE_RULE_MESSAGE_MAPPING = {
    "1000": "default Message",
    "1001": "cmd `{0}` added",
    "1002": "cmd `{0}` removed",
    "1003": "cmd `{0}` added property `{1}`",
    "1004": "cmd `{0}` removed property `{1}`",
    "1005": "cmd `{0}` updated property `{1}` from `{2}` to `{3}`",
    "1006": "cmd `{0}` added parameter `{1}`",
    "1007": "cmd `{0}` removed parameter `{1}`",
    "1008": "cmd `{0}` update parameter `{1}`: added property `{2}`",
    "1009": "cmd `{0}` update parameter `{1}`: removed property `{2}`",
    "1010": "cmd `{0}` update parameter `{1}`: updated property `{2}` from `{3}` to `{4}`",
    "1011": "sub group `{0}` added",
    "1012": "sub group `{0}` removed",
}

CHANGE_SUGGEST_MESSAGE_MAPPING = {
    "1000": "default Message",
    "1001": "please confirm cmd `{0}` added",
    "1002": "please confirm cmd `{0}` removed",
    "1003": "please remove property `{0}` for cmd `{1}`",
    "1004": "please add back property `{0}` for cmd `{1}`",
    "1005": "please change property `{0}` from `{1}` to `{2}` for cmd `{3}`",
    "1006": "please remove parameter `{0}` for cmd `{1}`",
    "1007": "please add back parameter `{0}` for cmd `{1}`",
    "1008": "please remove property `{0}` for parameter `{1}` for cmd `{2}`",
    "1009": "please add back property `{0}` for parameter {1}` for cmd `{2}`",
    "1010": "please change property `{0}` from `{1}` to `{2}` for parameter `{3}` of cmd `{4}`",
    "1011": "please confirm sub group `{0}` added",
    "1012": "please confirm sub group `{0}` removed",
}

