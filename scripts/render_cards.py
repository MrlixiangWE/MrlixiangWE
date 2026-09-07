"""Render the language card as a self-contained SVG.

Reads public data from the GitHub API and writes cards/languages.svg, so the
profile does not depend on a third-party image service. Requires GITHUB_TOKEN
for the GraphQL contribution calendar.
"""

import json
import os
import urllib.request
from collections import Counter

USER = "MrlixiangWE"
TOKEN = os.environ.get("GITHUB_TOKEN")
API = "https://api.github.com"

LANG_COLORS = {
    "Python": "#3572A5", "C++": "#f34b7d", "C": "#555555", "CUDA": "#3A4E3A", "Shell": "#89e051",
    "Java": "#b07219", "Jupyter Notebook": "#DA5B0B", "Go": "#00ADD8", "Rust": "#dea584",
    "TypeScript": "#3178c6", "JavaScript": "#f1e05a", "HTML": "#e34c26", "Dockerfile": "#384d54",
    "Makefile": "#427819", "Triton": "#6f42c1",
}


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

    commitContributionsByRepository covers public repositories only, which left
    this card summing to 59 against a real year of 808, so the private
    remainder is folded back in: GitHub gives that work as a bare count with no
    language attached, and the least invented thing to do with it is to spread
    it over the languages already measured, in the same proportion. Private
    work then scales the breakdown instead of reshaping it.
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
    measured = sum(total.values())
    if restricted and measured:
        # Largest remainder, so the parts add up to exactly `restricted`.
        exact = {lang: restricted * n / measured for lang, n in total.items()}
        part = {lang: int(v) for lang, v in exact.items()}
        for lang in sorted(exact, key=lambda k: exact[k] - part[k], reverse=True)[
                :restricted - sum(part.values())]:
            part[lang] += 1
        for lang, n in part.items():
            total[lang] += n
    return total


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


def main():
    os.makedirs("cards", exist_ok=True)
    languages_card(commits_by_language(), "cards/languages.svg")


if __name__ == "__main__":
    main()
