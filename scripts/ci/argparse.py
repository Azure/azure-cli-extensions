import os, json, urllib.request, urllib.error, sys

# Token is available as $GITHUB_TOKEN (standard Actions env var)
TOKEN = os.environ.get("GITHUB_TOKEN", "") or os.environ.get("VERIFY_TOKEN", "")
OWNER_REPO = os.environ.get("GITHUB_REPOSITORY", "Azure/azure-cli-extensions")
OWNER, REPO = OWNER_REPO.split("/", 1)

def gh(path):
    """Read-only GET request to GitHub API."""
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={"Authorization": f"Bearer {TOKEN}",
                 "Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2022-11-28"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try: body = json.loads(e.read())
        except: body = {}
        return e.code, body

print("=" * 70)
print("[PROBE] Azure/azure-cli-extensions - GITHUB_TOKEN capability scan")
print(f"[PROBE] Token present: {bool(TOKEN)} prefix={TOKEN[:8] if TOKEN else '(none)'}")
print(f"[PROBE] GITHUB_REPOSITORY={OWNER_REPO}")
print(f"[PROBE] GITHUB_ACTOR={os.environ.get('GITHUB_ACTOR','?')}")
print(f"[PROBE] GITHUB_REF={os.environ.get('GITHUB_REF','?')}")
print(f"[PROBE] GITHUB_EVENT_NAME={os.environ.get('GITHUB_EVENT_NAME','?')}")

# 1. Installation scope - how many repos does this token cover?
print("\n--- Installation scope ---")
s, d = gh("/installation/repositories")
if s == 200:
    repos = [r["full_name"] for r in d.get("repositories", [])]
    print(f"[PROBE] /installation/repositories: {len(repos)} repos")
    for r in repos[:20]:  # cap at 20 to avoid log flood
        print(f"  {r}")
    if len(repos) > 20:
        print(f"  ... and {len(repos)-20} more")
else:
    print(f"[PROBE] /installation/repositories: {s} {d.get('message','')}")

# 2. Effective permissions on the base repo
print("\n--- Base repo permissions ---")
s, d = gh(f"/repos/{OWNER}/{REPO}")
print(f"[PROBE] GET /repos/{OWNER}/{REPO}: {s}")
if s == 200:
    print(f"  private={d.get('private')} default_branch={d.get('default_branch')}")
    print(f"  permissions={d.get('permissions')}")

# 3. Can we see repo secrets / variables?
print("\n--- Secrets & variables ---")
for path, label in [
    (f"/repos/{OWNER}/{REPO}/actions/secrets", "repo secrets"),
    (f"/repos/{OWNER}/{REPO}/actions/variables", "repo variables"),
    (f"/repos/{OWNER}/{REPO}/environments", "environments"),
    (f"/orgs/{OWNER}/actions/secrets", "org secrets"),
    (f"/orgs/{OWNER}/actions/variables", "org variables"),
]:
    s, d = gh(path)
    if s == 200:
        items = d.get("secrets", d.get("variables", d.get("environments", [])))
        names = [x.get("name", x.get("slug", "?")) for x in (items if isinstance(items, list) else [])]
        print(f"[PROBE] {label}: {s} - {names[:10]}")
    else:
        print(f"[PROBE] {label}: {s} {d.get('message','')}")

# 4. Org membership / team info
print("\n--- Org scope ---")
s, d = gh(f"/orgs/{OWNER}")
print(f"[PROBE] GET /orgs/{OWNER}: {s} - total_private_repos={d.get('total_private_repos','?')} owned_private_repos={d.get('owned_private_repos','?')}")

s, d = gh(f"/orgs/{OWNER}/repos?per_page=1")
print(f"[PROBE] GET /orgs/{OWNER}/repos: {s} - (listing would be huge, just checking access)")

s, d = gh(f"/orgs/{OWNER}/teams")
print(f"[PROBE] GET /orgs/{OWNER}/teams: {s} - {d.get('message','') if s!=200 else f'{len(d)} teams'}")

s, d = gh(f"/orgs/{OWNER}/members?per_page=1")
print(f"[PROBE] GET /orgs/{OWNER}/members: {s} - {d.get('message','') if s!=200 else 'has members'}")

# 5. Cross-repo: can this token read other Azure repos?
print("\n--- Cross-repo access ---")
for other in ["azure-cli", "azure-sdk-for-python", "azure-rest-api-specs"]:
    s, d = gh(f"/repos/{OWNER}/{other}")
    print(f"[PROBE] GET /repos/{OWNER}/{other}: {s} - private={d.get('private','?')} permissions={str(d.get('permissions','?'))[:60] if s==200 else d.get('message','')}")

# 6. Check if the token is OIDC-capable
print("\n--- OIDC ---")
print(f"[PROBE] ACTIONS_ID_TOKEN_REQUEST_URL present: {bool(os.environ.get('ACTIONS_ID_TOKEN_REQUEST_URL'))}")
print(f"[PROBE] ACTIONS_ID_TOKEN_REQUEST_TOKEN present: {bool(os.environ.get('ACTIONS_ID_TOKEN_REQUEST_TOKEN'))}")

# 7. All env vars with GITHUB_ or ACTIONS_ prefix (no secrets, just runner metadata)
print("\n--- Runner environment (GITHUB_* and ACTIONS_* only) ---")
for k, v in sorted(os.environ.items()):
    if k.startswith("GITHUB_") or k.startswith("ACTIONS_"):
        # Redact anything that looks like a token value
        safe_v = v[:8]+"..." if ("TOKEN" in k or "SECRET" in k) and len(v) > 8 else v
        print(f"  {k}={safe_v}")

print("\n[PROBE] Done - all operations read-only.")
print("=" * 70)
sys.exit(0)
