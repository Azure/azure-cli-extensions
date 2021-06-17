Initial conda installation:
- need to run `conda init` after installation to make the command prompt work
- needed to run `python .\pywin32_postinstall.py -install` in C:\Users\beheim\Anaconda3\Scripts

Local conda environment: azdevenv
Commands for new creation: 
- open Anaconda Powershell Prompt
- `conda create -n azdevenv python=3.8 pip`
- `conda activate azdevenv`
- `pip install azdev`
- `azdev setup --cli  C:\Users\beheim\Source\Repos\az-cli --repo C:\Users\beheim\Source\Repos\az-quantum`

IMPORTANT: 
To make sure the source code version of extensions is used, make sure to install them using 
    `azdev extension add <extension-name>`

Bug workaround that was needed for the last one (https://github.com/Azure/azure-cli-dev-tools/issues/307):
in C:\Users\beheim\Anaconda3\envs\azdevenv\Lib\site-packages\azdev\utilities\command.py
edited py_cmd to replace
    python_bin = sys.executable if not env_path else os.path.join(env_path, 'Scripts' if sys.platform == 'win32' else 'bin', 'python')
with
    python_bin = sys.executable if not env_path else os.path.join(env_path, 'python') if sys.platform == 'win32' else os.path.join(env_path, 'bin', 'python')

documentation for az cli development: https://github.com/Azure/azure-cli-dev-tools
Commands:
- open Anaconda Powershell Prompt
- `conda activate azdevenv`
