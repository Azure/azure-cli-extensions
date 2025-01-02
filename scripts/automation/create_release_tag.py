import os
import re
import requests
import subprocess
from typing import List, Dict, Tuple, Optional
import sys

TARGET_FILE = "src/index.json"

def get_api_urls() -> Tuple[str, str]:
    """Generate GitHub API URLs based on GITHUB_REPOSITORY environment variable."""
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not repo:
        print("Error: GITHUB_REPOSITORY environment variable is not set")
        print("This script is designed to run in GitHub Actions environment")
        sys.exit(1)

    base_url = f"https://api.github.com/repos/{repo}"
    return f"{base_url}/releases", f"{base_url}/git/tags"

def get_file_changes() -> List[str]:
    diff_output = subprocess.check_output(
        ["git", "diff", "HEAD^", "HEAD", "--", TARGET_FILE],
        text=True
    )

    added_lines = [
        line[1:].strip()
        for line in diff_output.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]

    return added_lines

def parse_filename(added_lines: List[str]) -> Optional[str]:
    for line in added_lines:
        if '"filename":' in line:
            try:
                filename = line.split(":")[1].strip().strip('",')
                return filename
            except IndexError:
                print(f"Error parsing line: {line}")
    return None

def generate_tag_and_title(filename: str) -> Tuple[str, str]:
    match = re.match(r"^(.*?)[-_](\d+\.\d+\.\d+[a-z0-9]*)", filename)
    if not match:
        raise ValueError(f"Invalid filename format: {filename}")

    name = match.group(1).replace("_", "-")
    version = match.group(2)

    tag_name = f"{name}-{version}"
    release_title = f"Release {tag_name}"
    return tag_name, release_title

def check_tag_exists(url: str, tag_name: str, headers: Dict[str, str]) -> bool:
    response = requests.get(
        f"{url}/{tag_name}",
        headers=headers
    )
    return response.status_code == 200

def create_release(url: str, release_data: Dict[str, str], headers: Dict[str, str]) -> None:
    try:
        response = requests.post(
            url,
            json=release_data,
            headers=headers
        )
        response.raise_for_status()
        print(f"Successfully created release for {release_data['tag_name']}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to create release for {release_data['tag_name']}: {e}")

def main():
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        print("Error: GITHUB_TOKEN environment variable is required")
        sys.exit(1)

    # Get API URLs from environment
    release_url, tag_url = get_api_urls()
    
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        added_lines = get_file_changes()
        if not added_lines:
            print("No changes found in index.json")
            return

        filename = parse_filename(added_lines)
        if not filename:
            print("No filename found in changes")
            return

        try:
            tag_name, release_title = generate_tag_and_title(filename)
            
            commit_sha = subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                text=True
            ).strip()

            if check_tag_exists(tag_url, commit_sha, headers):
                print(f"Commit {commit_sha} already has a tag, skipping...")
                return

            release_data = {
                "tag_name": tag_name,
                "target_commitish": commit_sha,
                "name": release_title,
                "body": release_title
            }

            create_release(release_url, release_data, headers)

        except ValueError as e:
            print(f"Error generating tag for filename {filename}: {e}")
            return

    except Exception as e:
        print(f"Unexpected error: {e}")
        raise

if __name__ == "__main__":
    main()
