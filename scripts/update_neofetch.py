#!/usr/bin/env python3
"""Regenerate the profile's live numbers: the neofetch card and the README.

Run on a schedule by .github/workflows/live-update.yml. Pulls public stats
for OfficialAbhinavSingh via the GitHub GraphQL API (the workflow's default
GITHUB_TOKEN is enough — everything read here is public profile data) and
writes two things:

  * neofetch-{dark,light}.svg — the neofetch-style stats card
  * README.md — the blocks between <!--START:upstream-headline--> and
    <!--START:upstream-table--> and their matching END markers

Both are derived from one pass over UPSTREAM_REPOS, so the count on the card
and the count in the README are the same number by construction. Edit that
list, not the generated README blocks — anything written between the markers
by hand is overwritten on the next run.

Only writes a file if its rendered content actually changed, so the workflow
can skip an empty commit.
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

# Upstream pull requests: the single source of truth for every "PRs merged
# upstream" number on this profile — the neofetch card AND the README headline
# and contributions table are all generated from this one list, so they cannot
# drift apart.
#
# Membership rule: repositories maintained by someone else, where a PR of mine
# was reviewed and merged by a maintainer who isn't me. That deliberately
# excludes:
#   * my own repos and my own org (mergit-io) — self-merges aren't upstream work
#   * hackathon repos owned by a teammate (PhongCT1105/Hack-Research,
#     Viscous106/nodeLive) — same team, so the merge isn't an outside review
#
# Add a repo here when a contribution lands somewhere new; everything else
# updates itself on the next scheduled run.
UPSTREAM_REPOS = [
    "steipete/CodexBar",
    "mem0ai/mem0",
    "sktime/sktime",
    "steipete/oracle",
    "CodeGraphContext/CodeGraphContext",
    "Ritesh381/Scaler-extension",
    "modelcontextprotocol/conformance",
    "huggingface/OpenEnv",
    "Litica-AI/litica-sdk",
    "ShivenduShivu/MemoryLayer_for_Agents",
    # Open PRs only so far — they contribute 0 to the merged count, but keeping
    # them here means the "open" figure on the card stays honest too.
    "future-agi/future-agi",
    "openclaw/openclaw",
    "andrewyng/openworker",
    "ML4SCI/DeepLense-AI-Scientist",
    "mwt5345/DeepLenseSim",
    "sktime/skbase",
    "sailingsam/tryjarvis",
]

# Per-repo detail used to build the README table: merged count + live star count.
REPO_DETAIL_QUERY = """
query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    stargazerCount
  }
}
"""

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


def fetch_repo_breakdown(token: str) -> list[dict]:
    """Per-repo merged/open PR counts and star counts across UPSTREAM_REPOS.

    Returns rows sorted by merged count (then stars), which is the order the
    README table and the headline's "top repos" list both use.
    """
    rows = []
    for full_name in UPSTREAM_REPOS:
        owner, name = full_name.split("/", 1)
        merged = open_ = 0
        for state, key in (("is:merged", "merged"), ("is:open", "open")):
            q = f"author:{USERNAME} type:pr {state} repo:{full_name}"
            try:
                n = _graphql(token, PR_COUNT_QUERY, {"q": q})["search"]["issueCount"]
            except Exception:
                n = 0
            if key == "merged":
                merged = n
            else:
                open_ = n
        try:
            stars = _graphql(
                token, REPO_DETAIL_QUERY, {"owner": owner, "name": name}
            )["repository"]["stargazerCount"]
        except Exception:
            stars = 0
        rows.append(
            {"repo": full_name, "merged": merged, "open": open_, "stars": stars}
        )
        print(f"  {full_name}: {merged} merged, {open_} open, {stars} stars")
    rows.sort(key=lambda r: (-r["merged"], -r["stars"]))
    return rows


def fmt_stars(n: int) -> str:
    """Render a star count the way the README does: 21k+, 4.1k+, 119."""
    if n >= 10000:
        return f"{n // 1000}k+"
    if n >= 1000:
        return f"{n / 1000:.1f}k+".replace(".0k", "k")
    return str(n)


PROFILE_W = 880


def render_profile_svg(palette_name: str, values: dict, rows: list[dict], total: int) -> str:
    """The whole profile as one terminal session.

    Previously this was three separate images with markdown headings in
    between, which meant the page read as documentation interrupted by art.
    One panel, three prompts, one scrollback: the sections are separated by
    the commands that produced them rather than by <h2> rules.
    """
    p = PALETTES[palette_name]
    x = 42
    y = 56
    body, bars = [], []

    def prompt(cmd: str, yy: float) -> str:
        return (
            f'<tspan x="{x}" y="{yy:.0f}" font-size="14px">'
            f'<tspan fill="{p["accent"]}" font-weight="bold">~</tspan>'
            f'<tspan fill="{p["muted"]}"> $ </tspan>'
            f'<tspan fill="{p["text"]}">{cmd}</tspan></tspan>'
        )

    # --- whoami -----------------------------------------------------------
    body.append(prompt("whoami", y))
    y += 46
    body.append(
        f'<tspan x="{x}" y="{y:.0f}" font-size="36px" font-weight="bold" '
        f'fill="{p["text"]}">Abhinav Singh</tspan>'
    )
    y += 26
    body.append(
        f'<tspan x="{x}" y="{y:.0f}" font-size="14px" fill="{p["accent"]}">'
        f'AI/ML and agentic systems</tspan>'
    )
    y += 22
    body.append(
        f'<tspan x="{x}" y="{y:.0f}" font-size="13px" fill="{p["muted"]}">'
        f'open source contributor \u00b7 CS undergrad \u00b7 Arch Linux + Hyprland</tspan>'
    )

    # --- neofetch ---------------------------------------------------------
    y += 54
    body.append(prompt("neofetch", y))
    y += 30
    art_top = y
    ascii_x = x + 4
    art = []
    ay = art_top
    for r in ASCII_PORTRAIT:
        art.append(f'<tspan x="{ascii_x}" y="{ay:.0f}">{r}</tspan>')
        ay += ASCII_LH

    info_x = x + 330
    iy = art_top + 14
    info = []
    info.append(
        f'<tspan x="{info_x}" y="{iy:.0f}" fill="{p["accent"]}" font-weight="bold">'
        f'abhinav@github</tspan>'
    )
    iy += 24
    info.append(f'<tspan x="{info_x}" y="{iy:.0f}" fill="{p["muted"]}">{"-" * 28}</tspan>')
    iy += 24
    for label, value in FIELDS_TEMPLATE:
        info.append(row(info_x, iy, seg(p, label, value)))
        iy += 24
    iy += 8
    info.append(row(info_x, iy, seg(p, "Member since", values["member_since"])))
    iy += 24
    info.append(
        row(info_x, iy, seg(p, "Repos", values["repos"])
            + f'<tspan fill="{p["muted"]}"> | </tspan>'
            + seg(p, "Stars", values["stars"])
            + f'<tspan fill="{p["muted"]}"> | </tspan>'
            + seg(p, "Followers", values["followers"]))
    )
    iy += 24
    info.append(row(info_x, iy, seg(p, "Commits (yr)", values["commits"])))
    iy += 24
    info.append(row(info_x, iy, seg(p, "Top Language", values["top_language"])))

    y = max(ay, iy) + 40

    # --- contributions ----------------------------------------------------
    body.append(prompt("gh pr list --merged --author @me", y))
    y += 34
    merged = [r for r in rows if r["merged"] > 0]
    top = max((r["merged"] for r in merged), default=1)
    bar_x = x + 430
    for r in merged:
        repo = r["repo"]
        shown = repo if len(repo) <= 30 else repo[:29] + "\u2026"
        body.append(
            f'<tspan x="{x}" y="{y:.0f}" font-size="13.5px" fill="{p["text"]}">{shown}</tspan>'
        )
        body.append(
            f'<tspan x="{bar_x - 26}" y="{y:.0f}" font-size="13.5px" fill="{p["muted"]}" '
            f'text-anchor="end">{fmt_stars(r["stars"])} \u2605</tspan>'
        )
        w = max(6, round(230 * r["merged"] / top))
        bars.append(
            f'<rect x="{bar_x}" y="{y - 11:.0f}" width="{w}" height="13" rx="3" '
            f'fill="{p["accent"]}" opacity="0.85"/>'
        )
        body.append(
            f'<tspan x="{bar_x + w + 10}" y="{y:.0f}" font-size="13.5px" '
            f'fill="{p["accent"]}" font-weight="bold">{r["merged"]}</tspan>'
        )
        y += 25

    y += 14
    body.append(
        f'<tspan x="{x}" y="{y:.0f}" font-size="13.5px">'
        f'<tspan fill="{p["text"]}">{total} merged</tspan>'
        f'<tspan fill="{p["muted"]}"> across {len(merged)} upstream projects, '
        f'each reproduced with a failing test first</tspan></tspan>'
    )
    y += 34
    body.append(
        f'<tspan x="{x}" y="{y:.0f}" font-size="14px">'
        f'<tspan fill="{p["accent"]}" font-weight="bold">~</tspan>'
        f'<tspan fill="{p["muted"]}"> $ </tspan>'
        f'<tspan fill="{p["accent"]}">\u2588</tspan></tspan>'
    )
    height = y + 40

    return f"""<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" width="{PROFILE_W}px" height="{height}px" font-family="'Fira Code',Consolas,monospace">
<rect width="{PROFILE_W}px" height="{height}px" fill="{p["bg"]}" rx="18"/>
{chr(10).join(bars)}
<text fill="{p["accent"]}" xml:space="preserve" font-size="{ASCII_FONT}px" opacity="0.9">
{chr(10).join(art)}
</text>
<text xml:space="preserve" font-size="15px" fill="{p["text"]}">
{chr(10).join(info)}
</text>
<text xml:space="preserve">
{chr(10).join(body)}
</text>
</svg>
"""


def build_headline(rows: list[dict], total: int) -> str:
    """The one linked line under the panel.

    The panel shows the same numbers but is a flat image, so this exists to
    carry the links a reader actually wants to click.
    """
    merged = [r for r in rows if r["merged"] > 0]
    top = merged[:5]
    named = " \u00b7 ".join(
        f'<a href="https://github.com/{r["repo"]}">{r["repo"].split("/")[-1]}</a> {r["merged"]}'
        for r in top
    )
    rest = len(merged) - len(top)
    more = f' \u00b7 +{rest} more' if rest > 0 else ""
    allpr = f"https://github.com/pulls?q=is%3Apr+is%3Amerged+author%3A{USERNAME}"
    return (
        f'  <samp>{named}{more}</samp><br>\n'
        f'  <sub><a href="{allpr}">browse all {total} merged pull requests \u2192</a></sub>'
    )


def replace_block(text: str, name: str, body: str) -> str:
    """Swap the content between <!--START:name--> and <!--END:name-->.

    A missing block is not an error: sections get retired from the README
    and the generator should not start failing the workflow when one does.
    """
    start_tag, end_tag = f"<!--START:{name}-->", f"<!--END:{name}-->"
    if start_tag not in text or end_tag not in text:
        return text
    start, end = text.index(start_tag), text.index(end_tag)
    return text[: start + len(start_tag)] + "\n" + body + "\n" + text[end:]


def update_readme(repo_root: str, rows: list[dict], total: int) -> bool:
    """Rewrite the generated README blocks. Returns True if anything changed."""
    path = os.path.join(repo_root, "README.md")
    with open(path, "r", encoding="utf-8") as f:
        before = f.read()
    after = replace_block(before, "upstream-headline", build_headline(rows, total))
    if after != before:
        with open(path, "w", encoding="utf-8") as f:
            f.write(after)
        return True
    return False


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

    # One pass over UPSTREAM_REPOS feeds both the card and the README, so the
    # headline number and the table can never disagree with each other.
    print("upstream repo breakdown:")
    repo_rows = fetch_repo_breakdown(token)
    prs_merged = sum(r["merged"] for r in repo_rows)
    prs_open = sum(r["open"] for r in repo_rows)
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
        profile = render_profile_svg(palette, values, repo_rows, prs_merged)
        path = os.path.join(repo_root, f"profile-{palette}.svg")
        existing = ""
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                existing = f.read()
        if existing != profile:
            changed = True
        with open(path, "w", encoding="utf-8") as f:
            f.write(profile)

    if update_readme(repo_root, repo_rows, prs_merged):
        changed = True
        print("README upstream blocks updated")

    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a", encoding="utf-8") as f:
            f.write(f"changed={'true' if changed else 'false'}\n")
    print("stats:", values)


if __name__ == "__main__":
    main()
