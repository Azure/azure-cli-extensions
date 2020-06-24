# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

LINUX_GITHUB_ACTIONS_SUPPORTED_STACKS = [
  'NODE|12-lts',
  'NODE|10-lts',
  'NODE|10.14',
  'NODE|10.6',
  'NODE|10.1',
  'PYTHON|3.8',
  'PYTHON|3.7',
  'PYTHON|3.6',
  'DOTNETCORE|2.1',
  'DOTNETCORE|3.1',
  'JAVA|8-jre8',
  'TOMCAT|8.5-jre8',
  'TOMCAT|9.0-jre8',
  'JAVA|11-java11',
  'TOMCAT|8.5-java11',
  'TOMCAT|9.0-java11'
]

WINDOWS_GITHUB_ACTIONS_SUPPORTED_STACKS = [
  'node|12-lts',
  'node|10.6',
  'node|10.14',
  'python|3.6',
  'DOTNETCORE|2.1',
  'DOTNETCORE|3.1',
  'java|1.8|Tomcat|8.5',
  'java|1.8|Tomcat|9.0',
  'java|1.8|Java SE|8',
  'java|11|Tomcat|8.5',
  'java|11|Tomcat|9.0',
  'java|11|Java SE|8'
]

LINUX_RUNTIME_STACK_INFO = {
  'node|12-lts': {
    'display_name': 'NODE|12-lts',
    'github_actions_version': '12.x'
  },
  'node|10-lts': {
    'display_name': 'NODE|10-lts',
    'github_actions_version': '10.x'
  },
  'node|10.14': {
    'display_name': 'NODE|10.14',
    'github_actions_version': '10.14'
  },
  'node|10.10': {
    'display_name': 'NODE|10.10',
    'github_actions_version': '10.10'
  },
  'node|10.6': {
    'display_name': 'NODE|10.6',
    'github_actions_version': '10.6'
  },
  'node|10.1': {
    'display_name': 'NODE|10.1',
    'github_actions_version': '10.1'
  },
  'python|3.8': {
    'display_name': 'PYTHON|3.8',
    'github_actions_version': '3.8'
  },
  'python|3.7': {
    'display_name': 'PYTHON|3.7',
    'github_actions_version': '3.7'
  },
  'python|3.6': {
    'display_name': 'PYTHON|3.6',
    'github_actions_version': '3.6'
  },
  'dotnetcore|2.1': {
    'display_name': 'DOTNETCORE|2.1',
    'github_actions_version': '2.1.804'
  },
  'dotnetcore|3.1': {
    'display_name': 'DOTNETCORE|3.1',
    'github_actions_version': '3.1.102'
  },
  'java|8-jre8': {
    'display_name': 'JAVA|8-jre8',
    'github_actions_version': '8'
  },
  'tomcat|8.5-jre8': {
    'display_name': 'TOMCAT|8.5-jre8',
    'github_actions_version': '8'
  },
  'tomcat|9.0-jre8': {
    'display_name': 'TOMCAT|9.0-jre8',
    'github_actions_version': '8'
  },
  'java|11-java11': {
    'display_name': 'JAVA|11-java11',
    'github_actions_version': '11'
  },
  'tomcat|8.5-java11': {
    'display_name': 'TOMCAT|8.5-java11',
    'github_actions_version': '11'
  },
  'tomcat|9.0-java11': {
    'display_name': 'TOMCAT|9.0-java11',
    'github_actions_version': '11'
  }
}

WINDOWS_RUNTIME_STACK_INFO = {
  'node': {
    '12.13.0': { # WEBSITE_NODE_DEFAULT_VERSION
      'display_name': 'node|12-lts',
      'github_actions_version': '12.13.0'
    },
    '10.0.0': {
      'display_name': 'node|10.0',
      'github_actions_version': '10.0.0'
    },
    '10.6.0': {
      'display_name': 'node|10.6',
      'github_actions_version': '10.6.0'
    },
    '10.14.1': {
      'display_name': 'node|10.14',
      'github_actions_version': '10.14.1'
    }
  },
  'python': {
    '3.4': { # python_version
      'display_name': 'python|3.6',
      'github_actions_version': '3.6'
    }
  },
  'dotnetcore': {
    '2.1': { # dotnetcore_version
      'display_name': 'DOTNETCORE|2.1',
      'github_actions_version': '3.1.102'
    },
    '3.1': {
      'display_name': 'DOTNETCORE|3.1',
      'github_actions_version': '2.1.804'
    }
  },
  'java': {
    ('1.8', 'tomcat', '8.5'): { # (java_version, java_container, java_container_version)
      'display_name': 'java|1.8|Tomcat|8.5',
      'github_actions_version': '8'
    },
    ('1.8', 'tomcat', '9.0'): {
      'display_name': 'java|1.8|Tomcat|9.0',
      'github_actions_version': '8'
    },
    ('1.8', 'java', 'se'): {
      'display_name': 'java|1.8|Java SE|8',
      'github_actions_version': '8'
    },
    ('11', 'tomcat', '8.5'): {
      'display_name': 'java|11|Tomcat|8.5',
      'github_actions_version': '11'
    },
    ('11', 'tomcat', '9.0'): {
      'display_name': 'java|11|Tomcat|9.0',
      'github_actions_version': '11'
    },
    ('11', 'java', 'se'): {
      'display_name': 'java|11|Java SE|8',
      'github_actions_version': '11'
    }
  }
}

LINUX_GITHUB_ACTIONS_WORKFLOW_TEMPLATE_PATH = {
  'node': 'AppService/linux/nodejs-webapp-on-azure.yml',
  'python': 'AppService/linux/python-webapp-on-azure.yml',
  'dotnetcore': 'AppService/linux/aspnet-core-webapp-on-azure.yml',
  'java': 'AppService/linux/java-jar-webapp-on-azure.yml',
  'tomcat': 'AppService/linux/java-war-webapp-on-azure.yml'
}

WINDOWS_GITHUB_ACTIONS_WORKFLOW_TEMPLATE_PATH = {
  'node': 'AppService/windows/nodejs-webapp-on-azure.yml',
  'python': 'AppService/windows/python-webapp-on-azure.yml',
  'dotnetcore': 'AppService/windows/aspnet-core-webapp-on-azure.yml',
  'java': 'AppService/windows/java-jar-webapp-on-azure.yml',
  'tomcat': 'AppService/windows/java-war-webapp-on-azure.yml'
}