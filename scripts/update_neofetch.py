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


CALENDAR_QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount weekday } }
      }
    }
  }
}
"""

# Card chrome, shared by every panel. Dark in both themes on purpose: a
# terminal window that turns white in light mode stops reading as a terminal.
CARD_BG = "#0d1117"
CARD_PANEL = "#161b22"
CARD_LINE = "#30363d"
CARD_TEXT = "#e6edf3"
CARD_MUTED = "#8b949e"
ACCENT = "#f0732d"
TITLEBAR = 34


def chrome(w: int, h: int, title: str) -> str:
    """Traffic lights and a title bar, so each panel reads as a window."""
    return f"""<rect width="{w}" height="{h}" rx="10" fill="{CARD_BG}" stroke="{CARD_LINE}"/>
<path d="M0 10 a10 10 0 0 1 10 -10 h{w - 20} a10 10 0 0 1 10 10 v{TITLEBAR - 10} h-{w} z" fill="{CARD_PANEL}"/>
<line x1="0" y1="{TITLEBAR}" x2="{w}" y2="{TITLEBAR}" stroke="{CARD_LINE}"/>
<circle cx="18" cy="17" r="5" fill="#ff5f57"/>
<circle cx="36" cy="17" r="5" fill="#febc2e"/>
<circle cx="54" cy="17" r="5" fill="#28c840"/>
<text x="{w // 2}" y="22" text-anchor="middle" font-size="11.5px" fill="{CARD_MUTED}">{title}</text>"""


def calendar_stats(days: list[dict]) -> dict:
    """Streaks and totals from the raw calendar.

    Streaks ignore today when it is still empty: a day that has not happened
    yet should not break a run that is otherwise alive.
    """
    counts = [d["contributionCount"] for d in days]
    active = [c for c in counts if c > 0]
    total = sum(counts)

    longest = run = 0
    for c in counts:
        run = run + 1 if c > 0 else 0
        longest = max(longest, run)

    tail = counts[:-1] if counts and counts[-1] == 0 else counts
    current = 0
    for c in reversed(tail):
        if c == 0:
            break
        current += 1

    best = max(days, key=lambda d: d["contributionCount"]) if days else {"date": "", "contributionCount": 0}

    months: dict[str, int] = {}
    for d in days:
        months.setdefault(d["date"][:7], 0)
        months[d["date"][:7]] += d["contributionCount"]

    return {
        "total": total,
        "current": current,
        "longest": longest,
        "active": len(active),
        "days": len(counts),
        "best": best["contributionCount"],
        "best_date": best["date"],
        "avg": round(total / len(active), 1) if active else 0.0,
        "months": sorted(months.items())[-12:],
    }


def render_heatmap_svg(weeks: list[list[dict]], total: int) -> str:
    """The contribution graph.

    Two things make this read cleanly rather than as a smear. Levels are
    discrete, the way GitHub's own graph is, so a busy day is obviously
    busier than a quiet one instead of a slightly different alpha. And the
    cells animate in on a stagger, which only works because the animation is
    declarative CSS: GitHub proxies this through camo as a flat <img>, so
    anything driven by JavaScript would never run.
    """
    cell, step = 13, 16
    left, top = 36, 54
    w = left + len(weeks) * step + 22
    h = top + 7 * step + 50

    peak = max((d["contributionCount"] for wk in weeks for d in wk), default=1) or 1
    # Five steps, empty plus four intensities, thresholds on the quartiles.
    levels = [CARD_PANEL, "#5b2d14", "#8f4419", "#c25c22", ACCENT]

    def level(n: int) -> int:
        if n <= 0:
            return 0
        return min(4, 1 + int(3 * (n - 1) / max(peak - 1, 1)))

    cells, labels = [], []
    seen: set[str] = set()
    i = 0
    for wi, wk in enumerate(weeks):
        for d in wk:
            x = left + wi * step
            y = top + d["weekday"] * step
            lv = level(d["contributionCount"])
            cls = "c g" if lv else "c"
            cells.append(
                f'<rect class="{cls}" x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2.5" '
                f'fill="{levels[lv]}" style="animation-delay:{i * 0.004:.3f}s"/>'
            )
            i += 1
        month = wk[0]["date"][:7]
        if month not in seen and wk[0]["date"][8:10] <= "07":
            seen.add(month)
            labels.append(
                f'<text class="lbl" x="{left + wi * step}" y="{top - 10}">'
                f'{MONTHS[int(month[5:7]) - 1]}</text>'
            )

    for wd, lbl in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        labels.append(
            f'<text class="lbl" x="2" y="{top + wd * step + 10}">{lbl}</text>'
        )

    legend_x = w - 150
    legend = [f'<text class="lbl" x="{legend_x - 34}" y="{h - 16}">Less</text>']
    for n, col in enumerate(levels):
        legend.append(
            f'<rect x="{legend_x + n * 16}" y="{h - 27}" width="{cell}" height="{cell}" '
            f'rx="2.5" fill="{col}"/>'
        )
    legend.append(f'<text class="lbl" x="{legend_x + 5 * 16 + 4}" y="{h - 16}">More</text>')

    return f"""<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" width="{w}px" height="{h}px" font-family="'Fira Code',ui-monospace,Consolas,monospace">
<style>
  text.lbl {{ fill:{CARD_MUTED}; font-size:11px; }}
  .c {{ transform-box:fill-box; transform-origin:center; opacity:0;
       animation:pop 0.5s ease-out both; }}
  .g {{ animation:pop 0.5s ease-out both, flash 0.7s ease-out both; }}
  @keyframes pop {{ 0%{{opacity:0;transform:scale(.2)}} 60%{{opacity:1;transform:scale(1.12)}} 100%{{opacity:1;transform:scale(1)}} }}
  @keyframes flash {{ 0%{{filter:brightness(2.3)}} 45%{{filter:brightness(2.3)}} 100%{{filter:brightness(1)}} }}
  @media (prefers-reduced-motion: reduce) {{ .c {{ opacity:1 !important; animation:none !important; }} }}
</style>
{chrome(w, h, "abhinav@github: ~/contributions")}
{chr(10).join(labels)}
{chr(10).join(cells)}
{chr(10).join(legend)}
<text x="{left}" y="{h - 16}" font-size="12px" fill="{CARD_MUTED}">
<tspan fill="{ACCENT}" font-weight="bold">{total:,}</tspan> contributions in the last year</text>
</svg>
"""


MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def tile(x: int, y: int, w: int, h: int, label: str, value: str, sub: str, unit: str = "") -> str:
    # A space inside the tspan renders at the small font size, so it is
    # nearly invisible beside a 26px number. Offset explicitly instead.
    unit_tspan = (
        f'<tspan dx="7" font-size="13px" fill="{CARD_MUTED}">{unit}</tspan>' if unit else ""
    )
    return f"""<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{CARD_PANEL}" stroke="{CARD_LINE}"/>
<text x="{x + 14}" y="{y + 22}" font-size="11px" fill="{CARD_MUTED}"><tspan fill="{ACCENT}">$</tspan> {label}</text>
<text x="{x + 14}" y="{y + 52}" font-size="26px" font-weight="bold" fill="{CARD_TEXT}">{value}{unit_tspan}</text>
<text x="{x + 14}" y="{y + 72}" font-size="10.5px" fill="{CARD_MUTED}">{sub}</text>"""


def render_stats_svg(s: dict, values: dict) -> str:
    """The numbers card: six tiles over a per-month bar chart."""
    w = 420
    pad, gap = 14, 10
    tw = (w - pad * 2 - gap) // 2
    th = 86
    y = TITLEBAR + 14

    pct = round(100 * s["active"] / s["days"]) if s["days"] else 0
    cells = [
        ("current streak", f'{s["current"]}', "days", "unbroken"),
        ("longest streak", f'{s["longest"]}', "days", "best run"),
        ("contributions", f'{s["total"]:,}', "", "in the last year"),
        ("active days", f'{s["active"]}', f'/ {s["days"]}', f"{pct}% of the year"),
        ("best day", f'{s["best"]}', "", s["best_date"]),
        ("upstream PRs", f'{values["prs_merged"]}', "", f'merged · {values["prs_open"]} in review'),
    ]
    out = []
    for i, (label, val, unit, sub) in enumerate(cells):
        cx = pad + (i % 2) * (tw + gap)
        cy = y + (i // 2) * (th + gap)
        out.append(tile(cx, cy, tw, th, label, val, sub, unit))

    chart_y = y + 3 * (th + gap)
    ch = 150
    out.append(
        f'<rect x="{pad}" y="{chart_y}" width="{w - pad * 2}" height="{ch}" rx="8" '
        f'fill="{CARD_PANEL}" stroke="{CARD_LINE}"/>'
    )
    out.append(
        f'<text x="{pad + 14}" y="{chart_y + 22}" font-size="11px" fill="{CARD_MUTED}">'
        f'<tspan fill="{ACCENT}">$</tspan> contributions / month</text>'
    )
    months = s["months"]
    peak = max((n for _, n in months), default=1) or 1
    bw = (w - pad * 2 - 36) // max(len(months), 1)
    base = chart_y + ch - 26
    for i, (m, n) in enumerate(months):
        bh = max(3, round((base - chart_y - 36) * n / peak))
        bx = pad + 18 + i * bw
        out.append(
            f'<rect x="{bx}" y="{base - bh}" width="{bw - 6}" height="{bh}" rx="2" fill="{ACCENT}" opacity="0.85"/>'
        )
        out.append(
            f'<text x="{bx + (bw - 6) / 2:.0f}" y="{base + 14}" font-size="9px" fill="{CARD_MUTED}" '
            f'text-anchor="middle">{MONTHS[int(m[5:7]) - 1][0]}</text>'
        )
    h = chart_y + ch + pad

    return f"""<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" width="{w}px" height="{h}px" font-family="'Fira Code',ui-monospace,Consolas,monospace">
{chrome(w, h, "abhinav@github: ~/stats")}
{chr(10).join(out)}
</svg>
"""


def render_portrait_svg() -> str:
    """The ASCII portrait, sized to sit level with the stats card."""
    w = 420
    art, y = [], TITLEBAR + 26
    for r in ASCII_PORTRAIT:
        art.append(f'<tspan x="30" y="{y:.0f}">{r}</tspan>')
        y += 11.6
    h = y + 44
    return f"""<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" width="{w}px" height="{h}px" font-family="'Fira Code',ui-monospace,Consolas,monospace">
{chrome(w, h, "abhinav@github: ~/portrait")}
<text fill="{ACCENT}" xml:space="preserve" font-size="10px" opacity="0.92">
{chr(10).join(art)}
</text>
<text x="30" y="{h - 18}" font-size="11px" fill="{CARD_MUTED}">
<tspan fill="{ACCENT}">$</tspan> whoami <tspan fill="{CARD_TEXT}">Abhinav Singh</tspan></text>
</svg>
"""


def render_upstream_svg(rows: list[dict], total: int) -> str:
    """Merged pull requests per upstream project, as bars."""
    w = 860
    merged = [r for r in rows if r["merged"] > 0]
    peak = max((r["merged"] for r in merged), default=1)
    x = 30
    y = TITLEBAR + 34
    bar_x = 430
    out = []
    out.append(
        f'<text x="{x}" y="{y}" font-size="12.5px" fill="{CARD_MUTED}">'
        f'<tspan fill="{ACCENT}">$</tspan> gh pr list --merged --author @me</text>'
    )
    y += 30
    bars = []
    for r in merged:
        name = r["repo"] if len(r["repo"]) <= 34 else r["repo"][:33] + "\u2026"
        out.append(f'<text x="{x}" y="{y}" font-size="12.5px" fill="{CARD_TEXT}">{name}</text>')
        out.append(
            f'<text x="{bar_x - 24}" y="{y}" font-size="12.5px" fill="{CARD_MUTED}" '
            f'text-anchor="end">{fmt_stars(r["stars"])} \u2605</text>'
        )
        bw = max(6, round(300 * r["merged"] / peak))
        bars.append(
            f'<rect x="{bar_x}" y="{y - 11}" width="{bw}" height="13" rx="3" fill="{ACCENT}" opacity="0.85"/>'
        )
        out.append(
            f'<text x="{bar_x + bw + 10}" y="{y}" font-size="12.5px" fill="{ACCENT}" '
            f'font-weight="bold">{r["merged"]}</text>'
        )
        y += 24
    y += 10
    out.append(
        f'<text x="{x}" y="{y}" font-size="12px" fill="{CARD_MUTED}">'
        f'<tspan fill="{CARD_TEXT}" font-weight="bold">{total} merged</tspan> across '
        f'{len(merged)} upstream projects, each reproduced with a failing test first</text>'
    )
    h = y + 24
    return f"""<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" width="{w}px" height="{h}px" font-family="'Fira Code',ui-monospace,Consolas,monospace">
{chrome(w, h, "abhinav@github: ~/upstream")}
{chr(10).join(bars)}
{chr(10).join(out)}
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
    cal = _graphql(token, CALENDAR_QUERY, {"login": USERNAME})["user"][
        "contributionsCollection"
    ]["contributionCalendar"]
    weeks = [w["contributionDays"] for w in cal["weeks"]]
    days = [d for w in weeks for d in w]
    stats = calendar_stats(days)
    print(f"calendar: {stats['total']} contributions, streak {stats['current']}, best {stats['best']}")

    artifacts = {
        "contrib-heatmap.svg": render_heatmap_svg(weeks, cal["totalContributions"]),
        "portrait.svg": render_portrait_svg(),
        "stats.svg": render_stats_svg(stats, values),
        "upstream.svg": render_upstream_svg(repo_rows, prs_merged),
    }
    for name, svg in artifacts.items():
        path = os.path.join(repo_root, name)
        existing = ""
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                existing = f.read()
        if existing != svg:
            changed = True
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)

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
