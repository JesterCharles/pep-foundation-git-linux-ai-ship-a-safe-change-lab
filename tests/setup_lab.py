"""Create (or reset) the lab repository in starter/ship-safe-change/.

Run from the lab folder:  python tests/setup_lab.py
Re-running it is the reset path: it replaces all work inside starter/ship-safe-change/.
"""

import os
import shutil
import sys

from lab_support import (
    EMPTY_EXCLUDES,
    FIXTURES,
    LOCAL_CONFIG,
    MAIN,
    REPO,
    TEAMMATE,
    git,
    reset_starter,
    restore_starter_files,
    write_fixture,
)

# Fixed identity and timestamps make every learner's starting history identical.
# GIT_CONFIG_GLOBAL points setup's own commits away from personal hooks or signing settings.
FIXED = {
    "GIT_AUTHOR_NAME": "PEP Lab",
    "GIT_AUTHOR_EMAIL": "lab@example.invalid",
    "GIT_COMMITTER_NAME": "PEP Lab",
    "GIT_COMMITTER_EMAIL": "lab@example.invalid",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
}


def commit(message, timestamp):
    stamp = f"{timestamp} +0000"
    env = dict(FIXED, GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
    git("add", "--all", env=FIXED)
    git("commit", "--quiet", "--no-verify", "-m", message, env=env)


def main():
    if shutil.which("git") is None:
        sys.exit("Git was not found. Install Git, check `git --version`, then run setup again.")
    if sys.version_info < (3, 11):
        sys.exit("Python 3.11 or newer is required. Check `python --version`.")

    if (REPO / ".git").exists():
        print("WARNING: resetting the lab. All work inside starter/ship-safe-change/ is replaced.")
    reset_starter()

    # Initial project on main.
    for source in sorted((FIXTURES / "initial").iterdir()):
        write_fixture(source, REPO / source.name)
    git("init", "--quiet", env=FIXED)
    git("symbolic-ref", "HEAD", f"refs/heads/{MAIN}", env=FIXED)
    (REPO / EMPTY_EXCLUDES).parent.mkdir(parents=True, exist_ok=True)
    (REPO / EMPTY_EXCLUDES).write_bytes(b"")
    for key, value in LOCAL_CONFIG:
        git("config", "--local", key, value, env=FIXED)
    commit("Add deployment status helper", 1767261600)

    # The teammate's prepared branch edits the same lines the proposal touches.
    git("switch", "--quiet", "-c", TEAMMATE, env=FIXED)
    write_fixture(FIXTURES / "copy-update" / "status_message.py", REPO / "status_message.py")
    commit("Add support copy and help message", 1767265200)
    git("switch", "--quiet", MAIN, env=FIXED)

    # The assistant's proposed edit waits, uncommitted, in the working tree.
    restore_starter_files()
    write_fixture(FIXTURES / "local-env.txt", REPO / ".env")

    print("Lab ready in starter/ship-safe-change/ on branch main.")
    print("Next: cd starter/ship-safe-change, then run git status.")


if __name__ == "__main__":
    main()
