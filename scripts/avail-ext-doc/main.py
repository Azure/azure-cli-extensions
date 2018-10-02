
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import sys
import subprocess
import logging

import collections
import datetime
from pkg_resources import parse_version

from jinja2 import Template  # pylint: disable=import-error

from git import Repo
from github import Github

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

GH_TOKEN = os.environ.get('GH_TOKEN')
TRAVIS_BUILD_ID = os.environ.get('TRAVIS_BUILD_ID')
TRAVIS_REPO_SLUG = os.environ.get('TRAVIS_REPO_SLUG')
TRAVIS_COMMIT = os.environ.get('TRAVIS_COMMIT')
DOC_REPO_SLUG = os.environ.get('DOC_REPO_SLUG')
REPO_LOCATION = os.environ.get('REPO_LOCATION') 
SCRIPTS_LOCATION = os.path.join(REPO_LOCATION, 'scripts')

REPO_CLI_DOCS = 'https://{}@github.com/{}'.format(GH_TOKEN, DOC_REPO_SLUG)
CLONED_CLI_DOCS = os.path.join(os.path.sep, 'doc-repo')
AVAILABLE_EXTENSIONS_DOC = os.path.join(CLONED_CLI_DOCS, 'docs-ref-conceptual', 'azure-cli-extensions-list.md')
TEMPLATE_FILE = "list-template.md"

sys.path.insert(0, SCRIPTS_LOCATION)
from ci.util import get_index_data

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

def update_extensions_list(template_file, output_file):
    template = None
    with open(template_file, 'r') as doc_template:
        template = Template(doc_template.read())
    if template is None:
        raise RuntimeError("Failed to read template file {}".format(template_file))
    with open(output_file, 'w') as output:
        output.write(template.render(extensions=get_extensions(), date=datetime.date.today().strftime("%m/%d/%Y")))

def date_only_diff(diff):
    if not diff:
        return True
    stats = diff.split('\t')
    return stats[0] == 1 and stats[1] == 1

def commit_update(doc_repo):
    doc_repo.git.add(doc_repo.working_tree_dir)
    if date_only_diff(doc_repo.git.diff(staged=True, numstat=True)):
        logger.warning('No changes. Exiting')
        return
    github_con = Github(GH_TOKEN)
    user = github_con.get_user()
    doc_repo.git.config('user.email', user.email or 'azpycli@microsoft.com')
    doc_repo.git.config('user.name', user.name)
    logger.info('Cloned %s', CLONED_CLI_DOCS)
    branch_name = 'az-ext-list-ci-{}'.format(TRAVIS_BUILD_ID)
    local_branch = doc_repo.create_head(branch_name)
    local_branch.checkout()
    commit_url = 'https://github.com/{}/commit/{}'.format(TRAVIS_REPO_SLUG, TRAVIS_COMMIT)
    commit_msg = 'Update CLI extensions available doc.\n Triggered by {} - ' \
                 'TRAVIS_BUILD_ID={}\n{}'.format(TRAVIS_REPO_SLUG, TRAVIS_BUILD_ID, commit_url)
    doc_repo.index.commit(commit_msg)
    doc_repo.git.push('origin', local_branch.name, set_upstream=True)
    gh_repo = github_con.get_repo(DOC_REPO_SLUG)
    gh_repo.create_pull(
        title='Update CLI extensions available doc',
        body=commit_msg,
        head=local_branch.name,
        base='master')

def main():
    doc_repo = Repo.clone_from(REPO_CLI_DOCS, CLONED_CLI_DOCS)
    update_extensions_list(TEMPLATE_FILE, AVAILABLE_EXTENSIONS_DOC)
    commit_update(doc_repo)

if __name__ == '__main__':
    main()