
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
import string
import sys

import collections
import datetime
from packaging.version import Version

from jinja2 import Template  # pylint: disable=import-error
import requests

# After migration to OneBranch, clone azure-cli-extensions repo and azure-docs-cli repo are required.
# Also standardizes the directory structure:
# - $(System.DefaultWorkingDirectory)
#   - azure-cli-extensions
#   - azure-docs-cli
AZURE_CLI_EXTENSIONS_REPO_PATH = os.path.abspath(os.path.join('.', 'azure-cli-extensions'))
AZURE_DOCS_CLI_REPO_PATH = os.path.abspath(os.path.join('.', 'azure-docs-cli'))
AVAILABLE_EXTENSIONS_DOC = os.path.join(AZURE_DOCS_CLI_REPO_PATH, 'docs-ref-conceptual', 'Latest-version', 'azure-cli-extensions-list.md')
TEMPLATE_FILE = os.path.join(AZURE_CLI_EXTENSIONS_REPO_PATH, 'scripts', 'ci', 'avail-ext-doc', 'list-template.md')

sys.path.insert(0, os.path.join(AZURE_CLI_EXTENSIONS_REPO_PATH, 'scripts'))
from ci.util import get_index_data, INDEX_PATH

# azdev writes 'Home' for setup.py builds, derived from the deprecated Home-page field. It predates
# PEP 753 and does not normalize to 'homepage', so it has to be matched separately. Ordered, because
# the first match wins.
LEGACY_HOME_LABELS = ('home',)


def normalize_label(label):
    removal_map = str.maketrans('', '', string.punctuation + string.whitespace)
    return label.translate(removal_map).lower()


def get_project_url(metadata):
    """Return the extension's home page URL, or '' when it declares none.

    Labels reach index.json in two shapes. Newer entries carry a project_urls mapping under
    python.details; older ones carry the raw 'label, url' Project-URL line in project_url. Both
    are normalized the same way so the lookup does not depend on which shape an extension used.
    """
    details = metadata.get('extensions', {}).get('python.details', {})
    labelled = {}

    raw = metadata.get('project_url') or []
    for entry in [raw] if isinstance(raw, str) else raw:
        label, _, url = entry.partition(',')
        if url:
            labelled[normalize_label(label)] = url.strip()

    for label, url in (details.get('project_urls') or {}).items():
        labelled[normalize_label(label)] = url

    # Deliberately not falling back to 'source', 'repository' and friends. They carry different
    # semantics, and rendering an issue tracker as the project URL is worse than rendering nothing.
    for label in ('homepage', *LEGACY_HOME_LABELS):
        if labelled.get(label):
            return labelled[label]
    return ''


def get_extensions():
    extensions = []
    index_extensions = collections.OrderedDict(sorted(get_index_data()['extensions'].items()))
    for _, exts in index_extensions.items():
        # Get latest version
        exts = sorted(exts, key=lambda c: Version(c['metadata']['version']), reverse=True)

        # some extension modules may not include 'HISTORY.rst'
        project_url = get_project_url(exts[0]['metadata'])
        if not project_url:
            print(f"Warning: No project_url found for extension {exts[0]['metadata']['name']}")

        # requests.get('/HISTORY.rst') raises MissingSchema, so only probe when there is a URL.
        if project_url:
            history_tmp = project_url + '/HISTORY.rst'
            history = project_url if str(requests.get(history_tmp).status_code) == '404' else history_tmp
        else:
            history = ''
        if exts[0]['metadata'].get('azext.isPreview'):
            status = 'Preview'
        elif exts[0]['metadata'].get('azext.isExperimental'):
            status = 'Experimental'
        else:
            status = 'GA'

        extensions.append({
            'name': exts[0]['metadata']['name'],
            'desc': exts[0]['metadata']['summary'],
            'min_cli_core_version': exts[0]['metadata']['azext.minCliCoreVersion'],
            'version': exts[0]['metadata']['version'],
            'project_url': project_url,
            'history': history,
            'status': status
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
