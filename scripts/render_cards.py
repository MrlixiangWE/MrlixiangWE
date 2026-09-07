"""Render the language and activity cards as self-contained SVGs.

Reads public data from the GitHub API and writes cards/languages.svg and
cards/activity.svg, so the profile does not depend on a third-party image
service. Requires GITHUB_TOKEN for the GraphQL contribution calendar.
"""

import json
import os
import urllib.request
from collections import Counter
from datetime import date

USER = "MrlixiangWE"
TOKEN = os.environ.get("GITHUB_TOKEN")
API = "https://api.github.com"

LANG_COLORS = {
    "Python": "#3572A5", "C++": "#f34b7d", "C": "#555555", "CUDA": "#3A4E3A", "Shell": "#89e051",
    "Java": "#b07219", "Jupyter Notebook": "#DA5B0B", "Go": "#00ADD8", "Rust": "#dea584",
    "TypeScript": "#3178c6", "JavaScript": "#f1e05a", "HTML": "#e34c26", "Dockerfile": "#384d54",
    "Makefile": "#427819", "Triton": "#6f42c1",
}

# GitHub reports private work only as restrictedContributionsCount: an aggregate
# with no repository and no language attached, and it will not disclose more.
# This is therefore a declared split, not a measured one - state how private
# commits divide by language and they are apportioned accordingly.
PRIVATE_LANGUAGES = {"Python": 1.0}


def fetch(url, data=None):
    headers = {"User-Agent": USER, "Accept": "application/vnd.github+json"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


def commits_by_language():
    """Commits in the last 12 months, grouped by the primary language of the repository they went to.

    commitContributionsByRepository covers public repositories only. Dropping
    the private remainder left this card summing to 59 beside an activity card
    reading 808, so it is folded in via PRIVATE_LANGUAGES above.
    """
    query = """query($login:String!){ user(login:$login){ contributionsCollection{
        restrictedContributionsCount
        commitContributionsByRepository(maxRepositories:100){
          repository{ nameWithOwner primaryLanguage{ name } } contributions{ totalCount } } } } }"""
    c = fetch(f"{API}/graphql", {"query": query, "variables": {"login": USER}}
              )["data"]["user"]["contributionsCollection"]
    total = Counter()
    for entry in c["commitContributionsByRepository"]:
        lang = (entry["repository"]["primaryLanguage"] or {}).get("name") or "Other"
        total[lang] += entry["contributions"]["totalCount"]
    restricted = c["restrictedContributionsCount"]
    if restricted:
        share = sum(PRIVATE_LANGUAGES.values()) or 1
        for lang, weight in PRIVATE_LANGUAGES.items():
            total[lang] += round(restricted * weight / share)
    return total


def upstream_prs():
    items = fetch(f"{API}/search/issues?q=is:pr+author:{USER}&per_page=100")["items"]
    merged = open_ = 0
    repos = set()
    for it in items:
        repo = it["repository_url"].split("/repos/")[1]
        if repo.startswith(USER + "/"):
            continue
        if it["pull_request"].get("merged_at"):
            merged += 1
            repos.add(repo)
        elif it["state"] == "open":
            open_ += 1
            repos.add(repo)
    return merged, open_, len(repos)


def contributions():
    if not TOKEN:
        return None
    query = """query($login:String!){ user(login:$login){
        contributionsCollection{ contributionCalendar{ totalContributions }
          totalCommitContributions totalPullRequestReviewContributions
          restrictedContributionsCount }
        followers{ totalCount } } }"""
    d = fetch(f"{API}/graphql", {"query": query, "variables": {"login": USER}})["data"]["user"]
    c = d["contributionsCollection"]
    # totalCommitContributions counts public repositories only; work in private
    # repositories is reported separately as restrictedContributionsCount and is
    # already part of contributionCalendar.totalContributions. Adding it back is
    # what makes the two rows of the activity card agree with each other.
    return {
        "year": c["contributionCalendar"]["totalContributions"],
        "commits": c["totalCommitContributions"],
        "private": c["restrictedContributionsCount"],
        "reviews": c["totalPullRequestReviewContributions"],
        "followers": d["followers"]["totalCount"],
    }


def streaks():
    """Current and longest run of consecutive active days in the last 12 months.

    Computed from our own calendar rather than a third-party streak service:
    those query the API with a token of their own, which cannot see private
    contributions, so they report a fraction of the real figure.
    """
    if not TOKEN:
        return None
    query = """query($login:String!){ user(login:$login){ contributionsCollection{
        contributionCalendar{ totalContributions weeks{ contributionDays{ date contributionCount } } } } } }"""
    cal = fetch(f"{API}/graphql", {"query": query, "variables": {"login": USER}}
                )["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]

    longest = run = 0
    best_end = end = None
    for d in days:
        if d["contributionCount"] > 0:
            run += 1
            end = d["date"]
            if run > longest:
                longest, best_end = run, end
        else:
            run = 0

    # A quiet day that is still in progress should not break the current streak.
    tail = days[:-1] if days and days[-1]["contributionCount"] == 0 else days
    current = 0
    for d in reversed(tail):
        if d["contributionCount"] == 0:
            break
        current += 1

    return {
        "total": cal["totalContributions"],
        "current": current,
        "current_from": tail[-current]["date"] if current else None,
        "current_to": tail[-1]["date"] if current else None,
        "longest": longest,
        "longest_from": days[[d["date"] for d in days].index(best_end) - longest + 1]["date"] if longest else None,
        "longest_to": best_end,
        "since": days[0]["date"] if days else None,
    }


def streak_card(s, path):
    if not s:
        return
    def span(a, b):
        return f"{a} – {b}" if a and b else "—"
    cols = [("Total contributions", s["total"], span(s["since"], s["current_to"] or s["longest_to"])),
            ("Current streak", s["current"], span(s["current_from"], s["current_to"])),
            ("Longest streak", s["longest"], span(s["longest_from"], s["longest_to"]))]
    w, h = 420, 130
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="Segoe UI,Helvetica,Arial,sans-serif">',
           '<style>text{fill:#8b949e} .t{fill:#c9d1d9;font-weight:600;font-size:16px} .l{font-size:11px}'
           ' .n{fill:#58a6ff;font-weight:700;font-size:26px} .d{font-size:10px;fill:#6e7681}'
           '@media (prefers-color-scheme: light){text{fill:#57606a} .t{fill:#24292f} .n{fill:#0969da} .d{fill:#8b949e}}</style>',
           f'<text x="20" y="30" class="t">Streak</text>',
           f'<text x="{w - 20}" y="30" class="l" text-anchor="end">last 12 months</text>']
    for i, (label, value, sub) in enumerate(cols):
        cx = 70 + i * 140
        if i:
            out.append(f'<line x1="{cx - 70}" y1="46" x2="{cx - 70}" y2="118" stroke="#30363d" stroke-width="1"/>')
        out += [f'<text x="{cx}" y="80" class="n" text-anchor="middle">{value}</text>',
                f'<text x="{cx}" y="98" class="l" text-anchor="middle">{esc(label)}</text>',
                f'<text x="{cx}" y="113" class="d" text-anchor="middle">{esc(sub)}</text>']
    out.append("</svg>")
    open(path, "w", encoding="utf-8").write("\n".join(out))


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")


def languages_card(counts, path):
    top = counts.most_common(8)
    total = sum(counts.values()) or 1
    w, h, pad = 420, 60 + 26 * len(top), 20
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="Segoe UI,Helvetica,Arial,sans-serif">',
           '<style>text{fill:#8b949e} .t{fill:#c9d1d9;font-weight:600;font-size:16px} .l{font-size:12px}'
           '@media (prefers-color-scheme: light){text{fill:#57606a} .t{fill:#24292f}}</style>',
           f'<text x="{pad}" y="30" class="t">Commits by language, last 12 months</text>']
    x = pad
    bar_w = w - 2 * pad
    for lang, n in top:
        seg = max(2, round(bar_w * n / total))
        out.append(f'<rect x="{x}" y="42" width="{seg}" height="8" rx="2" fill="{LANG_COLORS.get(lang, "#8b949e")}"/>')
        x += seg
    for i, (lang, n) in enumerate(top):
        y = 74 + 26 * i
        out.append(f'<circle cx="{pad + 6}" cy="{y - 4}" r="5" fill="{LANG_COLORS.get(lang, "#8b949e")}"/>')
        out.append(f'<text x="{pad + 18}" y="{y}" class="l">{esc(lang)}</text>')
        unit = "commit" if n == 1 else "commits"
        out.append(f'<text x="{w - pad}" y="{y}" class="l" text-anchor="end">{n} {unit}, {100 * n / total:.1f}%</text>')
    out.append("</svg>")
    open(path, "w", encoding="utf-8").write("\n".join(out))


def activity_card(merged, open_, nrepos, contrib, path):
    rows = [("Upstream pull requests merged", merged), ("Upstream pull requests open", open_),
            ("Upstream projects contributed to", nrepos)]
    if contrib:
        rows += [("Contributions, last 12 months", contrib["year"]),
                 ("Commits, last 12 months", contrib["commits"] + contrib["private"])]
    w, h, pad = 420, 60 + 26 * len(rows), 20
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="Segoe UI,Helvetica,Arial,sans-serif">',
           '<style>text{fill:#8b949e} .t{fill:#c9d1d9;font-weight:600;font-size:16px} .l{font-size:12px} .v{fill:#58a6ff;font-weight:700;font-size:13px}'
           '@media (prefers-color-scheme: light){text{fill:#57606a} .t{fill:#24292f} .v{fill:#0969da}}</style>',
           f'<text x="{pad}" y="30" class="t">Activity</text>',
           f'<text x="{w - pad}" y="30" class="l" text-anchor="end">updated {date.today().isoformat()}</text>']
    for i, (label, value) in enumerate(rows):
        y = 64 + 26 * i
        out.append(f'<text x="{pad}" y="{y}" class="l">{esc(label)}</text>')
        out.append(f'<text x="{w - pad}" y="{y}" class="v" text-anchor="end">{value}</text>')
    out.append("</svg>")
    open(path, "w", encoding="utf-8").write("\n".join(out))


def main():
    os.makedirs("cards", exist_ok=True)
    languages_card(commits_by_language(), "cards/languages.svg")
    merged, open_, nrepos = upstream_prs()
    activity_card(merged, open_, nrepos, contributions(), "cards/activity.svg")
    streak_card(streaks(), "cards/streak.svg")


if __name__ == "__main__":
    main()
