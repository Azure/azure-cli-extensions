#!e:\projects\azurecli\azure-cli-extensions\e-env\scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'tabulate==0.8.6','console_scripts','tabulate'
__requires__ = 'tabulate==0.8.6'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('tabulate==0.8.6', 'console_scripts', 'tabulate')()
    )
