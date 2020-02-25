
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
This script must be run at the root of repo folder, which is azure-cli-extensions/
It's used to update a file "azure-cli-extensions-list.md" of MicrosoftDocs/azure-cli-docs.
The file content is list of all available latest extensions.
"""

import os
import sys

import collections
import datetime
from pkg_resources import parse_version

from jinja2 import Template  # pylint: disable=import-error


SCRIPTS_LOCATION = os.path.abspath(os.path.join('.', 'scripts'))

AZURE_DOCS_CLI_REPO_PATH = os.path.join('.', 'azure-docs-cli')
AVAILABLE_EXTENSIONS_DOC = os.path.join(AZURE_DOCS_CLI_REPO_PATH, 'docs-ref-conceptual', 'azure-cli-extensions-list.md')
TEMPLATE_FILE = os.path.join(SCRIPTS_LOCATION, "ci", "avail-ext-doc", "list-template.md")

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
