import os

DEBUG_ROOT_DIR = os.path.join(os.path.expanduser('~'), ".azaksdebug")
DEBUG_TOOL_DIR = os.path.join(DEBUG_ROOT_DIR, "tool")
DEBUG_DATA_DIR = os.path.join(DEBUG_ROOT_DIR, "data")
DEBUG_KUBECONFIG_PATH = os.path.join(DEBUG_ROOT_DIR, "kubeconfig")
