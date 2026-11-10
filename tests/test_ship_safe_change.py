"""Public checks for "Ship a safe change".

Run from the lab folder:  python -m unittest discover -s tests -v
Each check reads repository state with machine-oriented Git commands, never decorative output.
"""

import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from lab_support import FEATURE, FOCUSED_PATHS, MAIN, REPO, TEAMMATE, git, git_env

# Keep the learner's project folder free of bytecode caches.
sys.dont_write_bytecode = True

SETUP_HINT = "Run `python tests/setup_lab.py` from the lab folder first."
MARKERS = ("<<<<<<<", "=======", ">>>>>>>", "|||||||")


def load_status_module():
    """Import starter/ship-safe-change/status_message.py fresh for each check."""
    path = REPO / "status_message.py"
    spec = importlib.util.spec_from_file_location("learner_status_message", path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except SyntaxError as problem:
        raise AssertionError(
            f"status_message.py is not valid Python (line {problem.lineno}). "
            "Look for leftover conflict markers or a typo."
        ) from None
    return module


def rev(name):
    result = git("rev-parse", "--verify", "--quiet", f"{name}^{{commit}}", check=False)
    return result.stdout.strip() if result.returncode == 0 else None


def is_ancestor(older, newer):
    return git("merge-base", "--is-ancestor", older, newer, check=False).returncode == 0


def committed_rules_ignore(path):
    """True when the .gitignore committed at HEAD, matched by Git itself, ignores path.

    The rules are checked in a throwaway repository, so the result does not depend on
    whether path exists on disk or on any personal ignore settings.
    """
    committed_rules = git("show", "HEAD:.gitignore", check=False).stdout
    with tempfile.TemporaryDirectory() as folder:
        scratch = Path(folder)
        (scratch / ".gitignore").write_text(committed_rules, encoding="utf-8")
        (scratch / "no-excludes").write_text("", encoding="utf-8")
        env = git_env({"GIT_CEILING_DIRECTORIES": str(scratch.parent)})
        subprocess.run(["git", "init", "--quiet", str(scratch)], env=env, check=True)
        result = subprocess.run(
            [
                "git",
                "-C",
                str(scratch),
                "-c",
                f"core.excludesFile={scratch / 'no-excludes'}",
                "check-ignore",
                "--quiet",
                "--no-index",
                "--",
                path,
            ],
            env=env,
        )
    return result.returncode == 0


class ShipSafeChange(unittest.TestCase):
    def setUp(self):
        if not (REPO / ".git").is_dir() or rev(MAIN) is None:
            self.fail(f"The lab repository is missing. {SETUP_HINT}")

    def latest_merge(self):
        merges = git("rev-list", "--merges", "-n", "1", "HEAD").stdout.split()
        return merges[0] if merges else None

    def test_reads_deploy_env_and_has_default(self):
        with mock.patch.dict(os.environ, {"DEPLOY_ENV": "staging"}):
            self.assertEqual(
                load_status_module().status_message(),
                "staging: ready",
                "With DEPLOY_ENV=staging, status_message() did not return 'staging: ready'. "
                "It must read DEPLOY_ENV instead of a hard-coded name.",
            )
        with mock.patch.dict(os.environ, {"DEPLOY_ENV": "qa-7"}):
            self.assertEqual(
                load_status_module().status_message(),
                "qa-7: ready",
                "status_message() did not use the value of DEPLOY_ENV.",
            )
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("DEPLOY_ENV", None)
            self.assertEqual(
                load_status_module().status_message(),
                "development: ready",
                "With DEPLOY_ENV unset, status_message() must return 'development: ready'.",
            )

    def test_env_file_is_ignored_and_untracked(self):
        ignored = git("check-ignore", "--quiet", "--no-index", ".env", check=False)
        self.assertEqual(
            ignored.returncode,
            0,
            ".env is not ignored. Add a pattern for .env to .gitignore.",
        )
        ever_tracked = git("log", "--all", "--format=%H", "--", ".env").stdout.strip()
        self.assertEqual(
            ever_tracked,
            "",
            ".env was committed on some branch. Rerun setup and keep .env out of every commit.",
        )
        self.assertEqual(
            git("ls-files", "--", ".env").stdout.strip(),
            "",
            ".env is staged. Unstage it with `git restore --staged .env`.",
        )
        self.assertTrue(
            committed_rules_ignore(".env"),
            "The .gitignore at HEAD does not ignore .env. Commit your .gitignore change.",
        )

    def test_expected_feature_branch_is_checked_out(self):
        branch = git("symbolic-ref", "--quiet", "--short", "HEAD", check=False).stdout.strip()
        self.assertEqual(
            branch,
            FEATURE,
            f"HEAD is on '{branch or 'a detached commit'}'. "
            f"Create and switch to {FEATURE} with git switch -c.",
        )
        self.assertEqual(
            git("rev-list", "--count", MAIN).stdout.strip(),
            "1",
            f"{MAIN} has new commits. Commit your work on {FEATURE}, not {MAIN}; "
            "rerun setup to start again.",
        )

    def test_feature_commit_is_focused(self):
        own = git("rev-list", "--no-merges", "HEAD", f"^{MAIN}", f"^{TEAMMATE}").stdout.split()
        self.assertTrue(own, f"There is no commit of your own on {FEATURE} yet.")
        touched = set()
        for commit in own:
            files = git("diff-tree", "--no-commit-id", "--name-only", "-r", commit).stdout.split()
            extra = sorted(set(files) - set(FOCUSED_PATHS))
            self.assertEqual(
                extra,
                [],
                f"Commit {commit[:7]} also changed {extra}. Your commits may change only "
                ".gitignore and status_message.py; check `git diff --staged` before committing.",
            )
            touched.update(files)
        self.assertEqual(
            sorted(touched),
            FOCUSED_PATHS,
            "Your commits must change both .gitignore and status_message.py; "
            f"they changed {sorted(touched) or 'nothing'}.",
        )

    def test_prepared_branch_is_merged(self):
        teammate = rev(TEAMMATE)
        self.assertIsNotNone(teammate, f"Branch {TEAMMATE} is missing. Rerun setup.")
        self.assertTrue(
            is_ancestor(teammate, "HEAD"),
            f"{TEAMMATE} is not merged. Run git merge {TEAMMATE} on {FEATURE}.",
        )
        merge = self.latest_merge()
        self.assertIsNotNone(merge, "There is no merge commit. Finish the merge with git commit.")
        parents = git("rev-list", "--parents", "-n", "1", merge).stdout.split()[1:]
        self.assertNotEqual(
            parents[0],
            teammate,
            f"The merge was made from {TEAMMATE}. Merge into {FEATURE} instead.",
        )
        module = load_status_module()
        self.assertTrue(
            hasattr(module, "help_message")
            and module.help_message()
            == "Status looks wrong? Ask in #deployments before you redeploy.",
            "The teammate's help_message() wording was lost in the merge. Keep both sides' changes.",
        )

    def test_merge_is_resolved_without_markers(self):
        teammate = rev(TEAMMATE)
        self.assertTrue(
            teammate and is_ancestor(teammate, "HEAD"),
            f"Nothing to resolve yet: merge {TEAMMATE} into {FEATURE} first.",
        )
        unmerged = git("ls-files", "--unmerged").stdout.strip()
        self.assertEqual(unmerged, "", "Git still lists unmerged files. Resolve, then git add them.")
        self.assertFalse(
            (REPO / ".git" / "MERGE_HEAD").exists(),
            "A merge is still in progress. Resolve it, git add the file, then git commit.",
        )
        for path in git("ls-files").stdout.splitlines():
            text = (REPO / path).read_text(encoding="utf-8", errors="replace")
            for line in text.splitlines():
                self.assertFalse(
                    line.startswith(MARKERS),
                    f"Conflict marker left in {path}: {line.strip()}",
                )
            committed = git("show", f"HEAD:{path}").stdout
            self.assertFalse(
                any(line.startswith(MARKERS) for line in committed.splitlines()),
                f"The commit at HEAD contains conflict markers in {path}. "
                "Remove them, git add the file and commit again.",
            )

    def test_worktree_is_clean_except_ignored_files(self):
        status = git("status", "--porcelain", "--untracked-files=all").stdout.splitlines()
        self.assertEqual(
            status,
            [],
            "The working tree has uncommitted changes:\n" + "\n".join(status),
        )


if __name__ == "__main__":
    unittest.main()
