"""Rewrite the upstream pull-request table between the PRS markers in README.md."""

import json
import os
import re
import urllib.request

USER = "MrlixiangWE"
README = "README.md"
START, END = "<!-- PRS:START -->", "<!-- PRS:END -->"
# Repositories we contribute to upstream; the user's own repos and forks are skipped.
SKIP_OWNERS = {USER}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER, "Accept": "application/vnd.github+json"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


def main():
    items = fetch(f"https://api.github.com/search/issues?q=is:pr+author:{USER}&sort=created&order=desc&per_page=100")["items"]
    rows = []
    for it in items:
        repo = it["repository_url"].split("/repos/")[1]
        if repo.split("/")[0] in SKIP_OWNERS:
            continue
        pr = it["pull_request"]
        if pr.get("merged_at"):
            state = "merged"
        elif it["state"] == "open":
            state = "open"
        else:
            continue
        rows.append((repo, it["number"], it["title"], it["html_url"], state))

    merged = sum(1 for r in rows if r[4] == "merged")
    repos = sorted({r[0] for r in rows})
    lines = [f"{merged} merged, {len(rows) - merged} open, across " + ", ".join(f"`{r}`" for r in repos), ""]
    lines += ["| Repository | Pull request | Status |", "|---|---|---|"]
    for repo, num, title, url, state in rows[:15]:
        lines.append(f"| {repo} | [#{num}]({url}) {title} | {state} |")

    text = open(README, encoding="utf-8").read()
    new = f"{START}\n" + "\n".join(lines) + f"\n{END}"
    text = re.sub(re.escape(START) + r".*?" + re.escape(END), new, text, flags=re.S)
    open(README, "w", encoding="utf-8").write(text)


if __name__ == "__main__":
    main()
