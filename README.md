# Ship a safe change

A teammate asked an AI coding assistant to change a tiny deployment-status helper.
The assistant's edit is waiting, uncommitted, in a real Git repository, next to a `PROPOSAL.md` that says what the edit does.
Your job is to decide, from the real diff, whether those claims are supported and record your review decision.
Then you make the code meet the proposal's acceptance criteria, commit only the files you mean to, merge a teammate's branch that conflicts with yours, and prove the result with a test run.

About 18 minutes (an estimate, not yet measured with learners); stop at 20 and use **Troubleshooting** if you are stuck.
Everything runs on your own computer, offline: no account, no network, no container engine.
You will not need an AI assistant.

## Open the project

This repository is the whole lab. Clone it, then open the cloned folder in VS Code or any
other editor or IDE (in VS Code: **File > Open Folder**). Nothing in this lab runs in a browser.

Run every command below in a terminal at the repository root, the folder that holds this
README: in VS Code use **Terminal > New Terminal**, which opens there; with any other editor,
open a terminal and `cd` into the clone. The steps call this folder the lab folder.

## 1. Check your tools

Open a terminal at the repository root (the folder that holds this README).
Type each command and press Enter:

```text
git --version
python --version
```

**Expect:** `git version 2.23` or newer, and `Python 3.11` or newer.

Every lab command starts with `python`.
If `python --version` fails, or prints a version older than 3.11, find the launcher that works in your terminal and make `python` mean it for this terminal window:

| Your terminal | Check this works and shows 3.11 or newer | Then type this once |
|---|---|---|
| macOS or Linux (zsh or bash) | `python3 --version` | `alias python=python3` |
| Windows PowerShell | `py -3 --version` | `Set-Alias python py` |
| Windows cmd | `py -3 --version` | `doskey python=py -3 $*` |
| Git Bash on Windows | `py -3 --version` | `alias python='py -3'` |

Run `python --version` again; **expect** `Python 3.11` or newer.
The alias lasts only for this terminal window: type it again if you open a new one.
If no launcher works, install Python 3.11 or newer from python.org/downloads (on Windows, the Python install manager gives every terminal a `python` command), open a new terminal and start this step again.
On Windows, if `python` opens the Microsoft Store or says it is not found, open Start, search for **Manage app execution aliases**, turn on the **Python (default)** aliases and open a new terminal.

## 2. Create the lab repository

From this lab folder, run:

```text
python tests/setup_lab.py
```

**Expect:** `Lab ready in starter/ship-safe-change/ on branch main.`

Setup builds a small Git repository inside `starter/ship-safe-change/`.
It sets a training name and email for that repository only; your own Git settings are not read or changed.
Running setup again resets the lab: it deletes the whole `starter/ship-safe-change/` folder, including any file you added there, and rebuilds it.

## 3. Find out where you are and what changed

Move into the repository:

```text
cd starter/ship-safe-change
```

(In Windows cmd, type `cd starter\ship-safe-change`.)

Check your location and list every file, including hidden ones:

| Shell | Location | List all files |
|---|---|---|
| macOS, Linux, Git Bash | `pwd` | `ls -a` |
| PowerShell | `pwd` | `Get-ChildItem -Force` |
| cmd | `cd` | `dir /a` |

**Expect:** the path ends in `ship-safe-change`, and the list includes `.env`, `.gitignore`, `PROPOSAL.md` and `status_message.py`.

Now run:

```text
git status
```

**Expect:** you are `On branch main`; `status_message.py` is modified but not staged; `.env` is listed as untracked.
An untracked `.env` is one `git add .` away from being committed.

## 4. Check each claim against the diff

Open `PROPOSAL.md` in any text editor and read its two claims and its acceptance criteria.
Then show the assistant's actual edit:

```text
git diff
```

For each claim, find the diff line that supports it, or note that none does:

- Claim 1 says the name comes from `DEPLOY_ENV`. Look at the `+` lines in `status_message.py`: where does the deployment name come from?
- Claim 2 says `.env` can no longer be committed. Does the diff touch `.gitignore` at all? Does `git status` still list `.env`?

Write your review decision, **request changes** or **approve**, with one line of evidence per claim.
Keep this note outside the lab folder (paper or a notes app), so it never becomes an untracked file.
The rest of the lab is the requested change.

## 5. Make the change on a feature branch

Create and switch to a branch for the fix:

```text
git switch -c feature/safe-status
```

**Expect:** `Switched to a new branch 'feature/safe-status'`.
The uncommitted edit comes with you; `git status` still shows it.

**Ignore `.env` first.**
Open `.gitignore`, add a line that matches the `.env` file below the comments, and save.
Run `git status` again.
**Expect:** `.env` is no longer listed; `.gitignore` is now modified.

**Then fix the code.**
Open `status_message.py`.
Replace the hard-coded deployment name so that the function reads `DEPLOY_ENV` and falls back to `development` when it is not set.
The Python you need:

- `import os` at the top of the file gives access to the process environment.
- `os.environ.get("NAME", "fallback")` returns the variable called `NAME`, or `"fallback"` when it is not set.

Do not read or parse `.env` in the code, and keep the return format `<deployment>: ready`.

## 6. Run the checks and review your own diff

Go back to the lab folder and run the test command:

```text
cd ../..
python -m unittest discover -s tests -v
```

(In Windows cmd, type `cd ..\..`.)

**Expect:** `test_reads_deploy_env_and_has_default ... ok` and `test_env_file_is_ignored_and_untracked ... FAIL`, plus other failures for steps you have not done yet.
`test_env_file_is_ignored_and_untracked` still fails because the `.gitignore` change is not committed yet.
Read the message under each `FAIL`: it names the next action.

Return to the repository with `cd starter/ship-safe-change` and confirm exactly what you will commit:

```text
git diff
git add .gitignore status_message.py
git status
git diff --staged
```

**Expect:** `git status` shows exactly two staged files, `.gitignore` and `status_message.py`, and no `.env`.
`git diff` printed your unstaged changes; after `git add`, `git diff` would print nothing and `git diff --staged` shows the same two changes.
Name files explicitly: never `git add .` or `git add -A` here.

Commit:

```text
git commit -m "Read deployment name from DEPLOY_ENV and ignore .env"
```

## 7. Merge the teammate's branch and resolve the conflict

A teammate's branch, `integration/copy-update`, changed the same lines of `status_message.py`.
Merge it into your branch:

```text
git merge integration/copy-update
```

**Expect:** `CONFLICT (content): Merge conflict in status_message.py` and `Automatic merge failed`.
`git status` now lists `status_message.py` under `Unmerged paths`.

Open `status_message.py`.
Between `<<<<<<< HEAD` and `=======` is your version; between `=======` and `>>>>>>> integration/copy-update` is the teammate's.
Write the final text so that it keeps both sides' intent:

- your behavior: the name still comes from `DEPLOY_ENV`, with the `development` fallback;
- the teammate's work: their support-team comment and their `help_message()` function, word for word.

Delete all three marker lines, save, then finish the merge:

```text
git add status_message.py
git commit -m "Merge integration/copy-update into feature/safe-status"
```

**Expect:** `git status` reports `nothing to commit, working tree clean`.

## 8. Prove it before you call it ready

Look at the history you built:

```text
git log --oneline --graph --decorate -5
```

**Expect:** a merge commit at the top on `feature/safe-status`, with your commit and the teammate's commit as its two parents.

Return to the lab folder and run the same test command as before:

```text
cd ../..
python -m unittest discover -s tests -v
```

**Expect:** all seven checks report `ok`, then `OK` (see **Expected output** below).
Only now does your evidence support updating your review note from **request changes** to **ready for review**.

## How the checks work

The test command is `python -m unittest discover -s tests -v`, run from this lab folder.
It reads the real state of the repository with Git and imports your `status_message.py`; it never needs the network.

| Check | What it confirms |
|---|---|
| `test_reads_deploy_env_and_has_default` | `status_message()` uses `DEPLOY_ENV` and returns `development: ready` when it is unset |
| `test_env_file_is_ignored_and_untracked` | `.env` is ignored by a committed `.gitignore` rule and is in no commit |
| `test_expected_feature_branch_is_checked_out` | you are on `feature/safe-status`, and `main` has no new commits |
| `test_feature_commit_is_focused` | your own commits change only `.gitignore` and `status_message.py` |
| `test_prepared_branch_is_merged` | your branch has a merge commit that brings in `integration/copy-update`, and `help_message()` survived |
| `test_merge_is_resolved_without_markers` | no unmerged files, no merge in progress, no conflict markers in files or in the commit |
| `test_worktree_is_clean_except_ignored_files` | nothing is left uncommitted apart from ignored files such as `.env` |

## Expected output

Right after setup, all seven checks fail, each with a message naming the next action.
On completion the output matches `expected/on-completion.txt`; only the run time differs:

```text
test_env_file_is_ignored_and_untracked (...) ... ok
test_expected_feature_branch_is_checked_out (...) ... ok
test_feature_commit_is_focused (...) ... ok
test_merge_is_resolved_without_markers (...) ... ok
test_prepared_branch_is_merged (...) ... ok
test_reads_deploy_env_and_has_default (...) ... ok
test_worktree_is_clean_except_ignored_files (...) ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.2s

OK
```

## Offline note

Setup and checks use only Git and the Python standard library.
There is no remote, no download and no network call; the repository and the teammate's branch are created locally by setup.

## Cleanup

When you are finished, run this from the lab folder:

```text
python tests/cleanup_lab.py
```

It deletes the whole `starter/ship-safe-change/` folder (the lab repository's `.git` folder, your local `.env` and any file you added there) and the Python cache in `tests/`, then rewrites the starter files exactly as they were shipped.
It touches nothing outside this lab folder.

## Troubleshooting

| Symptom | What to do |
|---|---|
| `python: command not found`, or `python` opens the Microsoft Store | Go back to step 1: make `python` mean your Python 3 launcher for this terminal, or on Windows turn on the **Python (default)** app execution aliases. |
| `The lab repository is missing` | Run `python tests/setup_lab.py` from the lab folder. |
| `discover` says `Start directory is not importable` or finds no tests | You ran the test command inside `starter/ship-safe-change`. Go back to the lab folder first. |
| `main has new commits` | You committed before switching branches. Rerun setup and start from step 3. |
| `.env was committed` or `.env is staged` | Rerun setup; this time add the `.env` line to `.gitignore` before any `git add`, and name files explicitly. |
| `changed [...]` lists extra files | A commit included more than `.gitignore` and `status_message.py`. Rerun setup and stage the two files by name. |
| An editor opens after a Git command | You ran a commit or merge without `-m "..."`. Save and close the editor to accept the message, or rerun with `-m`. |
| `Conflict marker left in status_message.py` | Remove every line starting `<<<<<<<`, `=======` or `>>>>>>>`, then `git add status_message.py` and `git commit -m "Remove conflict markers"`. |
| `help_message() wording was lost` | Your resolution dropped the teammate's side. Rerun setup if needed and keep their comment and function. |
| You are lost or past 20 minutes | Rerun `python tests/setup_lab.py` (it resets everything), then repeat the steps in order. |
