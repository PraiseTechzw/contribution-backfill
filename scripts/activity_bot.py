#!/usr/bin/env python3
"""Activity generator: commits, pushes, PRs, issues, and reviews on a repo you control.

Requires: git, gh (GitHub CLI) authenticated with `gh auth login`.
"""

from __future__ import annotations

import argparse
import random
import subprocess
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

MESSAGES = (
    "docs: add example",
    "feat: add snippet",
    "fix: correct typo",
    "refactor: tidy snippets",
    "test: extend coverage",
)


def run(cmd: list[str], retries: int = 3, **kw) -> str:
    """Run a command, retrying transient failures (network/DNS), raising with stderr context."""
    last_err = ""
    for attempt in range(retries):
        result = subprocess.run(cmd, capture_output=True, text=True, **kw)
        if result.returncode == 0:
            return result.stdout.strip()
        last_err = result.stderr
        # only retry network-ish failures; fail fast on everything else
        transient = any(
            s in last_err
            for s in ("Could not resolve host", "Connection", "timeout", "Temporary failure")
        )
        if not transient or attempt == retries - 1:
            break
        time.sleep(2**attempt)
    raise RuntimeError(f"{' '.join(cmd)} failed:\n{last_err}")


class ActivityBot:
    def __init__(self, repo_dir: Path, seed: int | None = None, dry_run: bool = False):
        self.repo_dir = repo_dir
        self.rng = random.Random(seed)
        self.dry_run = dry_run
        self.commit_count = 0

    # ---------- commits ----------

    def commit(self, when: datetime, message: str, file_path: Path) -> None:
        """Create a commit dated at `when` (env dates avoid rewriting history)."""
        if self.dry_run:
            print(f"[dry-run] commit on {when:%Y-%m-%d}: {message}")
            self.commit_count += 1
            return
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(
            f"Test entry {self.commit_count} at {when.isoformat()}\n{message}\n",
            encoding="utf-8",
        )
        env_date = when.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        run(["git", "-C", str(self.repo_dir), "add", str(file_path.relative_to(self.repo_dir))])
        run(["git", "-C", str(self.repo_dir), "-c", "commit.gpgsign=false", "commit",
             "--date", env_date, "-m", message],
            env={"GIT_AUTHOR_DATE": env_date,
                 "GIT_COMMITTER_DATE": env_date,
                 "PATH": "/usr/local/bin:/usr/bin:/bin",
                 "HOME": str(Path.home())})
        self.commit_count += 1

    def generate_commits(self, count: int, start: date, weekdays_only: bool) -> list[datetime]:
        stamps: list[datetime] = []
        d = start
        while len(stamps) < count:
            if weekdays_only and d.weekday() >= 5:
                d += timedelta(days=1)
                continue
            # 1-3 commits per day, varied hours (9:00–18:00)
            for _ in range(self.rng.randint(1, 3)):
                if len(stamps) >= count:
                    break
                hour = self.rng.randint(9, 18)
                stamps.append(datetime(d.year, d.month, d.day, hour, self.rng.randint(0, 59),
                                       tzinfo=timezone.utc))
            d += timedelta(days=1)
        return stamps

    # ---------- push / branch ----------

    def push(self, branch: str, remote: str = "origin") -> None:
        if self.dry_run:
            print(f"[dry-run] git push -u {remote} {branch}")
            return
        run(["git", "-C", str(self.repo_dir), "push", "-u", remote, branch])

    def create_branch(self, branch: str) -> None:
        if self.dry_run:
            print(f"[dry-run] git checkout -B {branch}")
            return
        run(["git", "-C", str(self.repo_dir), "checkout", "-B", branch])

    # ---------- GitHub via gh CLI ----------

    def gh(self, *args: str, input_json: str | None = None) -> str:
        cmd = ["gh", *args]
        if self.dry_run:
            print(f"[dry-run] gh {' '.join(args)}")
            if args[:3] == ("pr", "create", "--base"):
                return "https://github.com/example/example/pull/1"
            if args[:2] == ("issue", "create"):
                return "https://github.com/example/example/issues/1"
            if args[:2] == ("repo", "view"):
                return "main"
            return ""
        return run(cmd + (["--input", "-"] if input_json else []), input=input_json or None)

    def default_branch(self, remote: str = "origin") -> str:
        """Ask GitHub for the repo's default branch (handles master vs main)."""
        try:
            return self.gh("repo", "view", "--json", "defaultBranchRef",
                           "--jq", ".defaultBranchRef.name") or "main"
        except RuntimeError:
            return "main"

    def create_pull_request(self, branch: str, base: str, title: str, body: str) -> str:
        out = self.gh("pr", "create", "--base", base, "--head", branch,
                      "--title", title, "--body", body)
        return out  # gh prints the PR URL

    def create_issue(self, title: str, body: str) -> str:
        return self.gh("issue", "create", "--title", title, "--body", body)

    def add_review(self, pr_number: str, body: str, event: str = "COMMENT") -> str:
        # event: APPROVE | REQUEST_CHANGES | COMMENT
        return self.gh("pr", "review", pr_number, "--body", body, "--" + event.lower())

    def add_pr_comment(self, pr_number: str, body: str) -> str:
        return self.gh("pr", "comment", pr_number, "--body", body)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate commits, PRs, issues, reviews.")
    parser.add_argument("--repo", type=Path, required=True, help="path to local git repo")
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--start", type=date.fromisoformat, default=date.today() - timedelta(days=60))
    parser.add_argument("--weekdays-only", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--branch", default="activity/fixture")
    parser.add_argument("--base", default="",
                        help="base branch (default: auto-detect remote default, e.g. master/main)")
    parser.add_argument("--issues", type=int, default=0, help="number of issues to open")
    parser.add_argument("--reviews", type=int, default=0, help="review comments on the PR")
    parser.add_argument("--no-pr", action="store_true", help="skip PR creation")
    parser.add_argument("--push", action="store_true", help="push branch (implied by PR)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    bot = ActivityBot(args.repo, seed=args.seed, dry_run=args.dry_run)

    base = args.base or bot.default_branch()
    print(f"Using base branch: {base}")

    stamps = bot.generate_commits(args.count, args.start, args.weekdays_only)
    fixture = args.repo / "activity-log.md"
    bot.create_branch(args.branch)
    for when in stamps:
        bot.commit(when, MESSAGES[bot.commit_count % len(MESSAGES)], fixture)

    if not bot.dry_run:
        # Preflight: fail fast if the branch has no commits ahead of base
        ahead = run(["git", "-C", str(args.repo), "rev-list", "--count", f"{base}..{args.branch}"])
        if ahead == "0":
            raise RuntimeError(
                f"No commits between {base} and {args.branch}; refusing to push/open PR. "
                f"Delete the branch and re-run: git branch -D {args.branch} "
                f"&& git push origin --delete {args.branch}"
            )

    if args.push or not args.no_pr:
        bot.push(args.branch)

    pr_url = None
    if not args.no_pr:
        pr_url = bot.create_pull_request(
            args.branch, base,
            "Fixture: activity test data",
            "Automated test data. Do not merge — fixture branch.",
        )
        print(f"PR: {pr_url}")
        pr_number = pr_url.rstrip("/").split("/")[-1]
        for i in range(args.reviews):
            bot.add_review(pr_number, f"Automated review note #{i + 1} (test fixture).")

    for i in range(args.issues):
        issue_url = bot.create_issue(f"Fixture issue #{i + 1}",
                                     "Automated test issue — safe to close.")
        print(f"Issue: {issue_url}")

    print(f"Done: {bot.commit_count} commits on {args.branch}")


if __name__ == "__main__":
    main()