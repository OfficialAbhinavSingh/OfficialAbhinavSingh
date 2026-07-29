#!/usr/bin/env python3
"""Regenerate neofetch-{dark,light}.svg with real, live GitHub data.

Run on a schedule by .github/workflows/live-update.yml. Pulls public stats
for OfficialAbhinavSingh via the GitHub GraphQL API (the workflow's default
GITHUB_TOKEN is enough — everything read here is public profile data) and
renders them into a neofetch-style card. Only writes the files if the
rendered content actually changed, so the workflow can skip an empty commit.
"""

import datetime
import os
import sys
import urllib.request
import json

USERNAME = "OfficialAbhinavSingh"
GRAPHQL_URL = "https://api.github.com/graphql"

# Main query — fetches personal stats plus a list of orgs the user belongs to.
# We get org-scoped commit counts in a second query (see ORG_COMMIT_QUERY).
QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    repositoriesContributedTo(includeUserRepositories: false, contributionTypes: [COMMIT, ISSUE, PULL_REQUEST, REPOSITORY]) {
      totalCount
    }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 1, orderBy: {field: SIZE, direction: DESC}) {
          nodes { name }
        }
      }
    }
    contributionsCollection {
      totalCommitContributions
    }
    organizations(first: 20) {
      nodes {
        login
      }
    }
  }
}
"""

# Per-org commit count query — called once per organisation.
# GitHub only counts commits in org repos toward your profile graph when
# your membership is public; this query uses the same scoping.
ORG_COMMIT_QUERY = """
query($login: String!, $org: ID!) {
  user(login: $login) {
    contributionsCollection(organizationID: $org) {
      totalCommitContributions
    }
  }
}
"""

# Separate query to resolve an org login → GraphQL node ID
ORG_ID_QUERY = """
query($org: String!) {
  organization(login: $org) {
    id
  }
}
"""

# Upstream pull requests: counted only over projects owned by someone else, so
# the number means "PRs other maintainers merged", not "PRs I merged into my own
# repos". Add a repo here when a contribution lands somewhere new.
UPSTREAM_REPOS = [
    "steipete/CodexBar",
    "mem0ai/mem0",
    "huggingface/OpenEnv",
    "sktime/sktime",
    "future-agi/future-agi",
    "openclaw/openclaw",
    "andrewyng/openworker",
    "Ritesh381/Scaler-extension",
    "ShivenduShivu/MemoryLayer_for_Agents",
    "ML4SCI/DeepLense-AI-Scientist",
    "mwt5345/DeepLenseSim",
    "CodeGraphContext/CodeGraphContext",
]

PR_COUNT_QUERY = """
query($q: String!) {
  search(query: $q, type: ISSUE) {
    issueCount
  }
}
"""


def _graphql(token: str, query: str, variables: dict) -> dict:
    """Execute a GraphQL query and return the parsed 'data' field."""
    body = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(
        GRAPHQL_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": USERNAME,
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        payload = json.load(resp)
    if "errors" in payload:
        raise RuntimeError(payload["errors"])
    return payload["data"]


def fetch_stats(token: str) -> dict:
    return _graphql(token, QUERY, {"login": USERNAME})["user"]


def fetch_org_id(token: str, org_login: str) -> str | None:
    """Resolve an organisation login to its GraphQL node ID."""
    try:
        data = _graphql(token, ORG_ID_QUERY, {"org": org_login})
        return data["organization"]["id"]
    except Exception:
        return None


def fetch_org_commits(token: str, org_id: str) -> int:
    """Return the user's commit count inside a specific organisation."""
    try:
        data = _graphql(token, ORG_COMMIT_QUERY, {"login": USERNAME, "org": org_id})
        return data["user"]["contributionsCollection"]["totalCommitContributions"]
    except Exception:
        return 0


def fetch_upstream_prs(token: str) -> tuple[int, int]:
    """Return (merged, open) PR counts across UPSTREAM_REPOS."""
    scope = " ".join(f"repo:{r}" for r in UPSTREAM_REPOS)
    counts = []
    for state in ("is:merged", "is:open"):
        q = f"author:{USERNAME} type:pr {state} {scope}"
        try:
            counts.append(_graphql(token, PR_COUNT_QUERY, {"q": q})["search"]["issueCount"])
        except Exception:
            counts.append(0)
    return counts[0], counts[1]


def member_since(created_at: str) -> str:
    created = datetime.datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    now = datetime.datetime.now(datetime.timezone.utc)
    months = (now.year - created.year) * 12 + (now.month - created.month)
    if now.day < created.day:
        months -= 1
    years, rem_months = divmod(max(months, 0), 12)
    parts = []
    if years:
        parts.append(f"{years} year{'s' if years != 1 else ''}")
    parts.append(f"{rem_months} month{'s' if rem_months != 1 else ''}")
    return ", ".join(parts)


# ASCII rendering of Abhinav's own GitHub avatar (avatars.githubusercontent.com/u/221158347),
# generated once via a luminance->charset density map (see scripts/photo_to_ascii.py) and
# baked in here — the photo doesn't change on a schedule, so there's no need to re-fetch and
# re-process an image on every CI run just to reproduce the same art.
ASCII_PORTRAIT = [
    r"  .*#####-.....:*###%%######%%#=.........:+####%*:..",
    r".::=@@@@@@*-----%@@@%*=-:--==+*=:-------+@@@@@@@+-::",
    r"::::-#@@@@@%=-----:.             .:---=#@@@@@@*-::::",
    r"=:::::+@@@@@@*-.           .        .+@@@@@@#=--=*%#",
    r"@%+-:::-#@@@@@.         ....         -@@@@@+-=+%@@@@",
    r"@@@@*=-:-+@@@-       :-=+****+++=-:. .#@@+-=%@@@@@@@",
    r"@@@@@@%+-:-#%:   .-+#%@@@@@@@@@@%#+=. =*-..#@@@@@%+-",
    r"*%@@@@@@@#*+#:..:=#%%@@@@@@@@@@%%##+-:-+-..-#@@#=---",
    r"%#%@@@@@@@##@=.-+*#%%@@@@@@@@@@@%%##*-#@#=-+*##**%@%",
    r"#%%%%%@@%*+#@#-+#*==++++*%%%#+++=--=#*@@%#*#%@%#@@@@",
    r"+%@@%#%%#==%@@+****+=---=**++=--=+==+*%%#**%@@@%#%@@",
    r"*@@@@@@@@%*@@%#*+#%**+**#+#*++**+#++*****++%@@@%+=+=",
    r"@@@@@@@@@@*@@%####@%%%%#*#@@*+####%%##**+==*%@%#=-=-",
    r"@@@@@%@@@#*@@%%%%%##%##*#%@@%**###%%%#**+--*#%#*----",
    r"%@@%***##*+%@@%#%%@@@@@%##%%*##%@@@%%#**=--*%%%*===-",
    r"=+++==+**+=*@@@%####****=-=-:=*###%%%%#+=:-#@@@%*+++",
    r"--====++==-+%@@@####=-=+*****++-:*##@@@#=-=%@@@%#***",
    r"-===--=====+%@@@%*###%%%%%##%#***##%@@@@#=+@@@@%****",
    r"-=++==+*##*%@@@*=++*#%%%@%%%%%###*+@@@@@@##@@@@%++==",
    r":+*#**#%%@@@@@= .*=-=+##%@@%%%#*+= -@@@@@@@@@@@%---:",
    r"=#%@@@@@@@@@@+  =**+=::.::-======:  =@@@@@@@@@@@=--:",
    r"#@@@@@@@@@@@%.  -*****+=------==-    +@@@@@@@@@@##*+",
    r"@@@@@@@@@@@@+    =###****+=====-     *%%@@@@@@@@@@%#",
    r"@@@@@@@@@@@@*     -*######**+=:.    .*%%%@@@@@@@@@@#",
    r"@@@@@@@@@@@@%:     .-*%@%##*+=-.    :#%@%%@@@%%%@@@@",
    r"@@@%%@@@@@@@@+       .-*%%%#*=.     :#@@%%#*+#%%%%%%",
    r"@@@%##%@@@@@@#.      ...:===-.      -%@@%%*+#%%%%%%%",
]

FIELDS_TEMPLATE = [
    ("OS", "Arch Linux"),
    ("Kernel", "Linux (Zen)"),
    ("WM", "Hyprland"),
    ("Shell", "zsh"),
    ("Languages", "Python · TS · Rust · JS"),
]

PALETTES = {
    "dark": {
        "bg": "#14100e",
        "text": "#f5efea",
        "muted": "#f5efea99",
        "accent": "#f0732d",
    },
    "light": {
        "bg": "#fff8f4",
        "text": "#111111",
        "muted": "#11111199",
        "accent": "#f0732d",
    },
}

TEXT_FONT = 15
TEXT_LH = 25
ASCII_FONT = 9
ASCII_LH = 10
TOP_PAD = 30
LEFT_ASCII_X = 18
LEFT_TEXT_X = 330
CARD_WIDTH = 780
DIVIDER = "-" * 30


def seg(p: dict, label: str, value) -> str:
    return (
        f'<tspan fill="{p["accent"]}">{label}</tspan>'
        f'<tspan fill="{p["muted"]}">: </tspan>'
        f'<tspan fill="{p["text"]}">{value}</tspan>'
    )


def row(x: int, y: float, inner: str) -> str:
    return f'<tspan x="{x}" y="{y:.0f}">{inner}</tspan>'


def render_svg(palette_name: str, values: dict) -> str:
    p = PALETTES[palette_name]
    lines = []
    y = TOP_PAD
    lines.append(f'<tspan x="{LEFT_TEXT_X}" y="{y:.0f}" fill="{p["accent"]}" font-weight="bold">abhinav@github</tspan>')
    y += TEXT_LH
    lines.append(f'<tspan x="{LEFT_TEXT_X}" y="{y:.0f}" fill="{p["muted"]}">{DIVIDER}</tspan>')
    y += TEXT_LH

    for label, value in FIELDS_TEMPLATE:
        lines.append(row(LEFT_TEXT_X, y, seg(p, label, value)))
        y += TEXT_LH

    y += TEXT_LH * 0.3
    lines.append(f'<tspan x="{LEFT_TEXT_X}" y="{y:.0f}" fill="{p["muted"]}">{DIVIDER}</tspan>')
    y += TEXT_LH
    lines.append(row(LEFT_TEXT_X, y, seg(p, "Member since", values["member_since"])))
    y += TEXT_LH

    y += TEXT_LH * 0.3
    lines.append(f'<tspan x="{LEFT_TEXT_X}" y="{y:.0f}" fill="{p["muted"]}">{DIVIDER}</tspan>')
    y += TEXT_LH
    repos_line = (
        seg(p, "Repos", values["repos"])
        + f'<tspan fill="{p["muted"]}"> {{</tspan>'
        + seg(p, "Contributed", values["contributed"])
        + f'<tspan fill="{p["muted"]}">}} | </tspan>'
        + seg(p, "Stars", values["stars"])
    )
    lines.append(row(LEFT_TEXT_X, y, repos_line))
    y += TEXT_LH
    commits_line = (
        seg(p, "Commits (past yr)", values["commits"])
        + f'<tspan fill="{p["muted"]}"> | </tspan>'
        + seg(p, "Followers", values["followers"])
    )
    lines.append(row(LEFT_TEXT_X, y, commits_line))
    y += TEXT_LH
    lines.append(row(LEFT_TEXT_X, y, seg(p, "Top Language", values["top_language"])))
    y += TEXT_LH
    upstream_line = (
        seg(p, "Upstream PRs", f'{values["prs_merged"]} merged')
        + f'<tspan fill="{p["muted"]}"> | </tspan>'
        + seg(p, "In review", values["prs_open"])
    )
    lines.append(row(LEFT_TEXT_X, y, upstream_line))
    y += TEXT_LH

    text_height = y + TOP_PAD * 0.6
    ascii_height = TOP_PAD + len(ASCII_PORTRAIT) * ASCII_LH + TOP_PAD * 0.6
    height = int(max(text_height, ascii_height))

    ascii_lines = []
    ay = TOP_PAD
    for r in ASCII_PORTRAIT:
        ascii_lines.append(f'<tspan x="{LEFT_ASCII_X}" y="{ay}">{r}</tspan>')
        ay += ASCII_LH

    return f'''<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" width="{CARD_WIDTH}px" height="{height}px" font-family="'Fira Code',Consolas,monospace">
<rect width="{CARD_WIDTH}px" height="{height}px" fill="{p["bg"]}" rx="16"/>
<text fill="{p["accent"]}" xml:space="preserve" font-size="{ASCII_FONT}px">
{chr(10).join(ascii_lines)}
</text>
<text fill="{p["text"]}" xml:space="preserve" font-size="{TEXT_FONT}px">
{chr(10).join(lines)}
</text>
</svg>
'''


def main() -> None:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN not set", file=sys.stderr)
        sys.exit(1)

    user = fetch_stats(token)
    repo_nodes = user["repositories"]["nodes"]
    stars = sum(n["stargazerCount"] for n in repo_nodes)
    lang_counts: dict = {}
    for n in repo_nodes:
        langs = n["languages"]["nodes"]
        if langs:
            name = langs[0]["name"]
            lang_counts[name] = lang_counts.get(name, 0) + 1
    top_language = max(lang_counts, key=lang_counts.get) if lang_counts else "n/a"

    # --- Organisation commit contributions -----------------------------------
    # GitHub only shows org commits on your profile when membership is public.
    # We mirror that behaviour: iterate every org the token can see, resolve its
    # node ID, then fetch the org-scoped contribution count and add it to the
    # personal total so the neofetch card matches the profile graph.
    personal_commits = user["contributionsCollection"]["totalCommitContributions"]
    org_nodes = user.get("organizations", {}).get("nodes", [])
    org_commit_total = 0
    org_names: list[str] = []
    for org in org_nodes:
        org_login = org["login"]
        org_id = fetch_org_id(token, org_login)
        if org_id:
            count = fetch_org_commits(token, org_id)
            if count > 0:
                org_commit_total += count
                org_names.append(f"@{org_login}")
                print(f"  org {org_login}: {count} commits")

    total_commits = personal_commits + org_commit_total
    orgs_label = ", ".join(org_names) if org_names else "(none visible)"
    print(f"personal commits: {personal_commits}  |  org commits: {org_commit_total}  |  orgs: {orgs_label}")

    prs_merged, prs_open = fetch_upstream_prs(token)
    print(f"upstream PRs: {prs_merged} merged, {prs_open} open")

    values = {
        "member_since": member_since(user["createdAt"]),
        "repos": user["repositories"]["totalCount"],
        "contributed": user["repositoriesContributedTo"]["totalCount"],
        "stars": stars,
        "followers": user["followers"]["totalCount"],
        "commits": total_commits,          # now includes org contributions
        "top_language": top_language,
        "prs_merged": prs_merged,
        "prs_open": prs_open,
    }

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    changed = False
    for palette in ("dark", "light"):
        svg = render_svg(palette, values)
        path = os.path.join(repo_root, f"neofetch-{palette}.svg")
        existing = ""
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                existing = f.read()
        if existing != svg:
            changed = True
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)

    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a", encoding="utf-8") as f:
            f.write(f"changed={'true' if changed else 'false'}\n")
    print("stats:", values)


if __name__ == "__main__":
    main()
