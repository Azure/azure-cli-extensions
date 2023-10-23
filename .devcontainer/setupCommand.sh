#!/bin/bash
. /home/vscode/env/bin/activate

cd /workspaces
git clone https://github.com/Azure/azure-cli.git azure-cli
azdev setup --cli ./azure-cli --repo ./azure-cli-extensions
az --version