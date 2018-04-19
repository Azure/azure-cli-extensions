import os, sys, argparse, shutil
from subprocess import Popen, PIPE
from distutils.dir_util import copy_tree, remove_tree

_source_md = '### Source Origin:'
_exclude_dirs = ['__pycache__', '.idea', 'dist']
_exclude_exts = ['.pyc']
_replacements = {
    'azure.keyvault': 'azext_keyvault.keyvault',
    'azure.mgmt.keyvault': 'azext_keyvault.mgmt.keyvault',
    'azure.cli.command_modules.keyvault': 'azext_keyvault'
}
_code_file_header="""# pylint: skip-file
# ---------------------------------------------------------------------------
# The code for this extension file is pulled from the {} repo. Changes may 
# cause incorrect behavior and will be lost if the code is regenerated.
# Please see the readme.md at the base of the keyvault extension for details.
# ---------------------------------------------------------------------------
"""

def file_in_repo(path, file):
    p = Popen('git ls-files --error-unmatch %s' % file,stdout=PIPE, stderr=PIPE, cwd=path)
    return p.wait() == 0


def run_process(cmd, cwd):
    p = Popen(cmd, stdout=PIPE, stderr=PIPE, cwd=cwd)
    stdout, stderr = p.communicate()
    p.wait()
    if stderr:
        print('ERROR: %s' % stderr)
    return stdout.decode('utf-8').strip() if not stderr else None


def copy_file(src, dst, repo_name, replacements=None):
    _, extension = os.path.splitext(src)
    if extension.lower() == '.py':
        with open(src, mode='r') as s:
            with open(dst, mode='w') as d:
                d.write(_code_file_header.format(repo_name))
                if replacements:
                    old = s.readline()
                    while(old):
                        new = old
                        for orig, repl in replacements.items():
                            new = new.replace(orig, repl)

                        if len(old) != len(new):
                            print('\n\t-%s\t+%s' % (old, new))

                        d.write(new)
                        old = s.readline()
                else:
                    d.write(s.read())
    else:
        shutil.copyfile(src, dst)


def copy_files(src, dst, repo_name, replacements=None):
    # copy cli command module files
    for path, dirs, files in os.walk(src):
        for file in files:
            if file_in_repo(path, file):
                src_file = os.path.join(path, file)
                dst_file = src_file.replace(src, dst)
                print(dst_file)
                if not os.path.exists(os.path.dirname(dst_file)):
                    os.makedirs(os.path.dirname(dst_file))
                copy_file(src_file, dst_file, repo_nameg, replacements)


def copy_repo_files(src, dst, repo_name, replacements=None):

    branch = run_process('git rev-parse --abbrev-ref HEAD', cwd=src)
    head = run_process('git rev-parse HEAD', cwd=src)

    if not (branch and head):
        print('unable to obtain branch info from "%s"' % src)
        exit(1)

    tag = '%s/%s %s' % (repo_name, branch, head)

    print('copying %s:\n\t %s' % (src, tag))

    copy_files(src, dst, repo_name, replacements)

    return tag


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--sdk', help='the root directory of the local azure-sdk-for-python clone', required=True)
    parser.add_argument('--cli', help='the root directory of the local azure-cli clone', required=True)
    args = parser.parse_args()

    sdk_root = args.sdk
    cli_root = args.cli
    ext_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'azext_keyvault')

    data_sdk_src = os.path.join(sdk_root, 'azure-keyvault/azure/keyvault')
    mgmt_sdk_src = os.path.join(sdk_root, 'azure-mgmt-keyvault/azure/mgmt')

    data_sdk_dst = os.path.join(ext_root, 'keyvault')
    mgmt_sdk_dst = os.path.join(ext_root, 'mgmt')

    cli_src = os.path.join(cli_root, 'src/command_modules/azure-cli-keyvault/azure/cli/command_modules/keyvault')

    # delete exiting extension files
    if os.path.exists(ext_root):
        remove_tree(ext_root)

    # copy sdk files
    sdk_tag = copy_repo_files(data_sdk_src, data_sdk_dst, 'azure-sdk-for-python')
    sdk_tag = copy_repo_files(mgmt_sdk_src, mgmt_sdk_dst, 'azure-sdk-for-python')

    # copy cli files
    cli_tag = copy_repo_files(cli_src, ext_root, 'azure-cli', _replacements)

    # write the sources.md file
    with open(os.path.join(ext_root, 'source.md'), 'w') as f:
        f.write('\n\t'.join([_source_md, sdk_tag, cli_tag]) + '\n')
