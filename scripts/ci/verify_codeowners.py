# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import print_function

import os
import sys

from util import get_repo_root

REPO_ROOT = get_repo_root()
CODEOWNERS = os.path.join(REPO_ROOT, '.github', 'CODEOWNERS')
SRC_DIR = os.path.join(REPO_ROOT, 'src')


def get_src_dir_codeowners():
    contents = []
    with open(CODEOWNERS) as f:
        contents = [x.strip() for x in f.readlines()]
    return dict([x.split(' ', 1) for x in contents if x.startswith('/src/') and x.split(' ')[0].endswith('/')])


def main():
    owners = get_src_dir_codeowners()
    dangling_entries = [e for e in owners if not os.path.isdir(os.path.join(REPO_ROOT, e[1:]))]
    missing_entries = ['/src/{}/'.format(p) for p in os.listdir(SRC_DIR)
                       if os.path.isdir(os.path.join(SRC_DIR, p)) and '/src/{}/'.format(p) not in owners]
    if dangling_entries or missing_entries:
        print('Errors whilst verifying {}!'.format(CODEOWNERS))
        if dangling_entries:
            print("Remove the following {} as these directories don't exist.".format(dangling_entries),
                  file=sys.stderr)
        if missing_entries:
            print("The following directories are missing codeowners {}.".format(missing_entries),
                  file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
