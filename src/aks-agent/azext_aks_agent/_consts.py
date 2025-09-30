# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# aks agent constants
CONST_AGENT_CONFIG_PATH_DIR_ENV_KEY = "HOLMES_CONFIGPATH_DIR"
CONST_AGENT_NAME = "AKS AGENT"
CONST_AGENT_NAME_ENV_KEY = "AGENT_NAME"
CONST_AGENT_CONFIG_FILE_NAME = "aksAgent.yaml"
CONST_PRIVACY_NOTICE_BANNER_ENV_KEY = "PRIVACY_NOTICE_BANNER"
# Privacy Notice Banner displayed in the format of rich.Console
CONST_PRIVACY_NOTICE_BANNER = (
    "When you send us this feedback, you agree we may combine this information, which might include other diagnostic data, to help improve Microsoft products and services.\n"
    "Processing of feedback data is governed by the Microsoft Products and Services Data Protection Addendum between your organization and Microsoft, and the feedback you submit is considered Personal Data under that addendum. [link=https://go.microsoft.com/fwlink/?LinkId=521839]Privacy Statement[/link]"
)

# MCP Integration Constants (ported from previous change)
CONST_MCP_BINARY_NAME = "aks-mcp"
CONST_MCP_DEFAULT_PORT = 8003
CONST_MCP_DEFAULT_URL = "http://localhost:8003/sse"
CONST_MCP_MIN_VERSION = "0.0.9"
CONST_MCP_GITHUB_REPO = "Azure/aks-mcp"
CONST_MCP_BINARY_DIR = "bin"
