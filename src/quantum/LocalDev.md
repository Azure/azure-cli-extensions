Local conda environment: az-dev
Commands for new creation: 
- conda create -n az-dev python=3.8 pip
- pip install azdev
- azdev setup --cli  C:\Users\beheim\Source\Repos\az-cli --repo C:\Users\beheim\Source\Repos\az-quantum

Bug workaround that was needed for the last one (https://github.com/Azure/azure-cli-dev-tools/issues/307):
in C:\Users\beheim\AppData\Local\Continuum\anaconda3\envs\az-dev\lib\site-packages\azdev\command.py
edited py_cmd to replace
    python_bin = sys.executable if not env_path else os.path.join(env_path, 'Scripts' if sys.platform == 'win32' else 'bin', 'python')
with
    python_bin = sys.executable


documentation for az cli development: https://github.com/Azure/azure-cli-dev-tools
Commands:
- open Anaconda Powershell Prompt
- conda activate az-dev
