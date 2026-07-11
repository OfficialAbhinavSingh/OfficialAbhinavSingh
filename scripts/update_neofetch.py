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

QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
      totalCount
      nodes { stargazerCount }
    }
    contributionsCollection {
      totalCommitContributions
    }
  }
}
"""


def fetch_stats(token: str) -> dict:
    body = json.dumps({"query": QUERY, "variables": {"login": USERNAME}}).encode()
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
    return payload["data"]["user"]


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


ASCII_ARCH = [
    r"       /\ ",
    r"      /  \ ",
    r"     /\   \ ",
    r"    /      \ ",
    r"   /   ,,   \ ",
    r"  /   |  |   \ ",
    r" /_-''    ''-_\ ",
]

FIELDS_TEMPLATE = [
    ("OS", "Arch Linux"),
    ("Kernel", "Linux (Zen)"),
    ("WM", "Hyprland"),
    ("Shell", "zsh"),
    ("Languages", "Python · TS · Rust · JS"),
]

STATS_TEMPLATE = [
    ("Repos", "repos"),
    ("Stars", "stars"),
    ("Followers", "followers"),
    ("Commits (past year)", "commits"),
]

PALETTES = {
    "dark": {
        "bg": "#14100e",
        "text": "#f5efea",
        "muted": "#f5efea99",
        "accent": "#f0732d",
        "border": "#ffffff1f",
    },
    "light": {
        "bg": "#fff8f4",
        "text": "#111111",
        "muted": "#11111199",
        "accent": "#f0732d",
        "border": "#0000001a",
    },
}

LINE_HEIGHT = 24
TOP_PAD = 34
LEFT_ASCII_X = 24
LEFT_TEXT_X = 260


def render_svg(palette_name: str, values: dict) -> str:
    p = PALETTES[palette_name]
    lines = []
    lines.append(f'<tspan x="{LEFT_TEXT_X}" y="{TOP_PAD}" fill="{p["accent"]}" font-weight="bold">abhinav@github</tspan>')
    lines.append(
        f'<tspan x="{LEFT_TEXT_X}" y="{TOP_PAD + LINE_HEIGHT}" fill="{p["muted"]}">'
        + "-" * 28
        + "</tspan>"
    )
    y = TOP_PAD + LINE_HEIGHT * 2
    for label, value in FIELDS_TEMPLATE:
        lines.append(
            f'<tspan x="{LEFT_TEXT_X}" y="{y}">'
            f'<tspan fill="{p["accent"]}">{label}</tspan>'
            f'<tspan fill="{p["muted"]}">: </tspan>'
            f'<tspan fill="{p["text"]}">{value}</tspan>'
            "</tspan>"
        )
        y += LINE_HEIGHT
    y += LINE_HEIGHT * 0.4
    lines.append(
        f'<tspan x="{LEFT_TEXT_X}" y="{y:.0f}" fill="{p["muted"]}">' + "-" * 28 + "</tspan>"
    )
    y += LINE_HEIGHT
    lines.append(
        f'<tspan x="{LEFT_TEXT_X}" y="{y:.0f}">'
        f'<tspan fill="{p["accent"]}">Member since</tspan>'
        f'<tspan fill="{p["muted"]}">: </tspan>'
        f'<tspan fill="{p["text"]}">{values["member_since"]}</tspan>'
        "</tspan>"
    )
    y += LINE_HEIGHT
    for label, key in STATS_TEMPLATE:
        lines.append(
            f'<tspan x="{LEFT_TEXT_X}" y="{y:.0f}">'
            f'<tspan fill="{p["accent"]}">{label}</tspan>'
            f'<tspan fill="{p["muted"]}">: </tspan>'
            f'<tspan fill="{p["text"]}">{values[key]}</tspan>'
            "</tspan>"
        )
        y += LINE_HEIGHT

    height = int(y + TOP_PAD * 0.6)

    ascii_lines = []
    ay = TOP_PAD
    for row in ASCII_ARCH:
        ascii_lines.append(f'<tspan x="{LEFT_ASCII_X}" y="{ay}">{row}</tspan>')
        ay += LINE_HEIGHT

    return f'''<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" width="600px" height="{height}px" font-family="'Fira Code',Consolas,monospace" font-size="14px">
<rect width="600px" height="{height}px" fill="{p["bg"]}" rx="14"/>
<text fill="{p["accent"]}" xml:space="preserve">
{chr(10).join(ascii_lines)}
</text>
<text fill="{p["text"]}" xml:space="preserve">
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
    stars = sum(n["stargazerCount"] for n in user["repositories"]["nodes"])
    values = {
        "member_since": member_since(user["createdAt"]),
        "repos": user["repositories"]["totalCount"],
        "stars": stars,
        "followers": user["followers"]["totalCount"],
        "commits": user["contributionsCollection"]["totalCommitContributions"],
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
