
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import print_function

import os
import sys
import subprocess
import logging

from git import Repo
from github import Github

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

GH_TOKEN = os.environ.get('GH_TOKEN')
TRAVIS_BUILD_ID = os.environ.get('TRAVIS_BUILD_ID')
TRAVIS_REPO_SLUG = os.environ.get('TRAVIS_REPO_SLUG')
TRAVIS_COMMIT = os.environ.get('TRAVIS_COMMIT')
DOC_REPO_SLUG = os.environ.get('DOC_REPO_SLUG')

DOC_GEN_SCRIPT = os.path.join('repo', 'scripts', 'ci', 'available_extensions_doc.py')

REPO_CLI_DOCS = 'https://{}@github.com/{}'.format(GH_TOKEN, DOC_REPO_SLUG)
CLONED_CLI_DOCS = os.path.join(os.sep, 'doc-repo')
AVAILABLE_EXTENSIONS_DOC = os.path.join(CLONED_CLI_DOCS, 'docs-ref-conceptual', 'azure-cli-extensions-list.md')

def main():
    doc_repo = Repo.clone_from(REPO_CLI_DOCS, CLONED_CLI_DOCS)
    with open(AVAILABLE_EXTENSIONS_DOC, 'w') as f:
        subprocess.call([sys.executable, DOC_GEN_SCRIPT], stdout=f)
    doc_repo.git.add(doc_repo.working_tree_dir)
    if not doc_repo.git.diff(staged=True):
        logger.warning('No changes. Exiting')
        return
    github_con = Github(GH_TOKEN)
    user = github_con.get_user()
    doc_repo.git.config('user.email', user.email or 'azpycli@microsoft.com')
    doc_repo.git.config('user.name', user.name)
    logger.info('Cloned %s', CLONED_CLI_DOCS)
    local_branch = doc_repo.create_head('az-auto-ext-doc-{}'.format(TRAVIS_BUILD_ID))
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
        head='{}:{}'.format(user.login, local_branch.name),
        base='master')

if __name__ == '__main__':
    main()

