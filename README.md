
# Project Setup

## Prerequisites

- **Python 3.12**

## Setup Instructions

### 1. Create a Virtual Environment

1. Open your terminal.
2. Navigate to your project directory.
3. Run the following command to create a new virtual environment:
    ```bash
    python3.12 -m venv myenv
    ```
4. Activate the virtual environment:
    - On Windows:
        ```bash
        myenv\Scripts\activate
        ```
    - On macOS/Linux:
        ```bash
        source myenv/bin/activate
        ```

### 2. Install Tools for Azure CLI Development

Follow the instructions *An external link was removed to protect your privacy.*.

1. Install `aaz-dev-tools`:
    ```bash
    pip install aaz-dev
    ```

### 3. Clone Repositories

Create a new folder named `CLI` and clone the following repositories into it:

1. *An external link was removed to protect your privacy.*
    ```bash
    git clone https://github.com/atharvau/azure-cli-extensions
    ```
2. *An external link was removed to protect your privacy.*
    ```bash
    git clone https://github.com/atharvau/azure-rest-api-specs-pr
    ```
3. *An external link was removed to protect your privacy.*
    ```bash
    git clone https://github.com/atharvau/azure-rest-api-specs
    ```
4. *An external link was removed to protect your privacy.*
    ```bash
    git clone https://github.com/atharvau/azure-cli
    ```
5. *An external link was removed to protect your privacy.*
    ```bash
    git clone https://github.com/atharvau/aaz
    ```

### 4. Pull Latest Builds

Ensure you checkout the correct branch for `azure-rest-api-specs-pr`:
```bash
cd azure-rest-api-specs-pr
git checkout <branch-name>
```

### 5. Setup Azure CLI Development Environment

Run the following command to download all dependencies:
```bash
azdev setup --cli {path to azure-cli} --repo {path to azure-cli-extensions}
```

## Azure CLI Extension

This repository contains workload operations. The main-workload-orchestration branch is the primary branch. 

### Source Code

The source code is located in `src/workload-orchestration`.

### Switcher Script

We have a switcher script that changes the source code between `Microsoft.edge` and `Private.edge`.

- To switch to `Microsoft.edge`:
    ```powershell
    .\switcher.ps1 -switch 'microsoft.edge'
    ```
- To switch to `Private.edge`:
    ```powershell
    .\switcher.ps1 -switch 'private.edge'
    ```

## Making Changes as per Swagger Change

1. Navigate to the required folder `src/workload-orchestration/<module>`.
2. Make the necessary changes in the respective files.
3. Raise a new PR to the main branch.

### Testing

1. Create a wheel file:
    ```bash
    cd src/workload-orchestration
    python setup.py bdist_wheel
    ```
2. In the `dist` folder, you will find the `.whl` file. Remove any unnecessary spaces and filenames.
3. Install the wheel file using:
    ```bash
    az extension add --source <File Path>
    ```
4. Test your changes.

---

Feel free to let me know if you need any further assistance!