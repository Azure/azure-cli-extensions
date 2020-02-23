
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
This script must be run at the root of repo folder, which is azure-cli-extensions/
"""

import os
import sys
import logging

import collections
import datetime
from pkg_resources import parse_version

from jinja2 import Template  # pylint: disable=import-error

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

AZURE_CLI_DOCS_REPO_PATH = './azure-cli-docs'

SCRIPTS_LOCATION = os.path.abspath(os.path.join('.', 'scripts'))

CLONED_CLI_DOCS = os.path.join('..', 'azure-docs-cli')
print('CLONED_CLI_DOCS =', CLONED_CLI_DOCS)
AVAILABLE_EXTENSIONS_DOC = os.path.join(CLONED_CLI_DOCS, 'docs-ref-conceptual', 'azure-cli-extensions-list.md')
print('AVAILABLE_EXTENSIONS_DOC =', AVAILABLE_EXTENSIONS_DOC)
TEMPLATE_FILE = os.path.join(SCRIPTS_LOCATION, "ci", "docs", "list-template.md")

sys.path.insert(0, SCRIPTS_LOCATION)
from ci.util import get_index_data, INDEX_PATH


def get_extensions():
    extensions = []
    index_extensions = collections.OrderedDict(sorted(get_index_data()['extensions'].items()))
    for _, exts in index_extensions.items():
        # Get latest version
        exts = sorted(exts, key=lambda c: parse_version(c['metadata']['version']), reverse=True)
        extensions.append({
            'name': exts[0]['metadata']['name'],
            'desc': exts[0]['metadata']['summary'],
            'version': exts[0]['metadata']['version'],
            'project_url': exts[0]['metadata']['extensions']['python.details']['project_urls']['Home'],
            'preview': 'Yes' if exts[0]['metadata'].get('azext.isPreview') else ''
        })
    return extensions


def update_extensions_list(output_file):
    with open(TEMPLATE_FILE, 'r') as doc_template:
        template = Template(doc_template.read())
    if template is None:
        raise RuntimeError("Failed to read template file {}".format(TEMPLATE_FILE))
    with open(output_file, 'w') as output:
        output.write(template.render(extensions=get_extensions(), date=datetime.date.today().strftime("%m/%d/%Y")))


def main():
    update_extensions_list(AVAILABLE_EXTENSIONS_DOC)


if __name__ == '__main__':
    main()
