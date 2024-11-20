#!/bin/bash

# define color codes
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m"  # no color

setup_repo() {
    local DIR_NAME="$1"
    local DIR_PATH="/workspaces/$DIR_NAME"
    local REPO="Azure/$DIR_NAME"

    if [ -d "$DIR_PATH" ]; then
        echo -e "\n${YELLOW}($DIR_NAME) Pulling the latest changes from upstream...${NC}"
        cd "$DIR_PATH"
        gh repo sync --source "$REPO"
        cd /workspaces
    else
        echo -e "\n${GREEN}($DIR_NAME) Forking and cloning the repository...${NC}"
        cd /workspaces
        gh repo fork "$REPO" --clone=true
    fi
}

SECONDS=0

pip install aaz-dev

# azdev repositories
setup_repo "azure-cli"
setup_repo "azure-cli-extensions"

azdev setup -c -r ./azure-cli-extensions

# aaz-dev repositories
setup_repo "aaz"
setup_repo "azure-rest-api-specs"
setup_repo "azure-rest-api-specs-pr"

ELAPSED_TIME=$SECONDS
echo -e "\n${YELLOW}Elapsed time: $((ELAPSED_TIME / 60)) min $((ELAPSED_TIME % 60)) sec.${NC}"
echo -e "${GREEN}Finished setup! Please launch the codegen tool via \`aaz-dev run -c azure-cli -e azure-cli-extensions -s azure-rest-api-specs -a aaz\`.${NC}\n"
