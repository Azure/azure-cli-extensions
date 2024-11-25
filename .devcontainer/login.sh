
. /workspaces/venv/bin/activate

export GITHUB_TOKEN=  # logout default account

if gh auth status -a 2>/dev/null | grep "Token scopes: " | grep -q "repo"; then  # check `repo` scope exists or not
    echo "You were already logged into GitHub."
else
    gh auth login -p https -w
fi
