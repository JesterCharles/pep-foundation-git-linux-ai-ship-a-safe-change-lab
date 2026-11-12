# Ship a safe change

A teammate asked an AI coding assistant to change a tiny deployment-status helper.
The assistant's edit is waiting, uncommitted, in a real Git repository, next to a
`PROPOSAL.md` that says what the edit does.

You decide from the real diff whether the proposal's claims hold, then make the code
meet its acceptance criteria, commit only the files you mean to, merge a teammate's
branch that conflicts with yours, and prove the result with the tests.

- **Time:** about 18 minutes. If you pass 20, stop and use **Troubleshooting**.
- **You need:** Git 2.23 or newer and Python 3.11 or newer.
- **Offline:** no account, network, container or AI assistant.

## Your path

```text
Open project -> Set up -> Tests: 7 fail -> Steps 3-7 -> Tests: 7 ok -> Stop
```

In words: open the project, set it up and see all 7 checks fail, work through
steps 3 to 7 in order, then run the checks again and stop when all 7 pass.

## Quick start

1. **Open the project.** Open this lab's folder in VS Code. It is already on your
   machine, so you do not need to clone anything. Open a terminal with
   **Terminal > New Terminal**; it starts in the project folder, the one that holds
   this README. Check your tools with `git --version` and `python --version`.
2. **Set up, then run the starter tests:**

   ```text
   python tests/setup_lab.py
   python -m unittest discover -s tests -v
   ```

   **Expect:** `Lab ready in starter/ship-safe-change/ on branch main.`, then all 7
   checks `FAIL`. That is normal before you start: each failure message names what
   is missing. Now move into the lab repository, where steps 3 to 7 happen:
   `cd starter/ship-safe-change`
3. **Find out where you are and what changed** with `ls -a` and `git status`.
4. **Check each claim against the diff** in `PROPOSAL.md` and write down your review
   decision (outside the project folder).
5. **Make the change on a feature branch:** create `feature/safe-status`, ignore
   `.env` in `.gitignore`, and make `status_message()` in `status_message.py` meet
   the proposal's acceptance criteria. Check names: `reads_deploy`,
   `expected_feature_branch`.
6. **Run the checks and commit** exactly `.gitignore` and `status_message.py`.
   Check names: `env_file`, `focused`, `worktree`.
7. **Merge the teammate's branch and resolve the conflict** in `status_message.py`,
   keeping both sides' work. Check name: `merge`.
8. **Prove it:** go back to the project folder and run every check:

   ```text
   cd ../..
   python -m unittest discover -s tests -v
   ```

   **Expect:** all 7 checks report `ok`, then `OK`. You are done: stop here.

**Check one step at a time.** From `starter/ship-safe-change`, put the step's check
names after `-k`:

```text
python -m unittest discover -s ../../tests -v -k reads_deploy
```

**Expect:** those checks report `ok`. If one says `FAIL`, read the message under it.

## Step-by-step guide

Steps 3 to 7 run in the lab repository, `starter/ship-safe-change`.

### Step 3: Find out where you are and what changed

```text
pwd
ls -a
git status
```

**Expect:** the path ends in `ship-safe-change`; the list includes `.env`,
`.gitignore`, `PROPOSAL.md` and `status_message.py`; you are `On branch main`, with
`status_message.py` modified and `.env` untracked. An untracked `.env` is one
`git add .` away from being committed.

### Step 4: Check each claim against the diff

Open `PROPOSAL.md` and read its two claims and its acceptance criteria. Then show the
assistant's actual edit:

```text
git diff
```

For each claim, find the diff line that supports it, or note that none does.

<details>
<summary>Hint</summary>

- Claim 1 says the name comes from `DEPLOY_ENV`. In the `+` lines of
  `status_message.py`, where does the deployment name come from?
- Claim 2 says `.env` can no longer be committed. Does the diff touch `.gitignore`?
  Does `git status` still list `.env`?

</details>

Write your review decision, **request changes** or **approve**, with one line of
evidence per claim. Keep this note outside the project folder (on paper or in a
notes app) so it never becomes an untracked file. The rest of the lab is the
requested change.

### Step 5: Make the change on a feature branch

```text
git switch -c feature/safe-status
```

**Expect:** `Switched to a new branch 'feature/safe-status'`. The uncommitted edit
comes with you.

**Ignore `.env` first.** Open `.gitignore`, add a line that matches the `.env` file
below the comments, and save. Run `git status` again: `.env` is no longer listed and
`.gitignore` is modified.

**Then fix the code.** In `status_message.py`, replace the hard-coded deployment
name so that the function reads `DEPLOY_ENV` and falls back to `development` when it
is not set.

<details>
<summary>Hint</summary>

The Python you need:

- `import os` at the top of the file gives access to the process environment.
- `os.environ.get("NAME", "fallback")` returns the variable called `NAME`, or
  `"fallback"` when it is not set.

</details>

Do not read or parse `.env` in the code, and keep the return format
`<deployment>: ready`.

### Step 6: Run the checks and review your own diff

```text
python -m unittest discover -s ../../tests -v
```

**Expect:** `test_reads_deploy_env_and_has_default ... ok`, while
`test_env_file_is_ignored_and_untracked` still fails because the `.gitignore` change
is not committed yet. Other checks fail until later steps.

Confirm exactly what you will commit. Name the files; never use `git add .` or
`git add -A` here:

```text
git diff
git add .gitignore status_message.py
git status
git diff --staged
git commit -m "Read deployment name from DEPLOY_ENV and ignore .env"
```

**Expect:** before the commit, exactly two staged files, `.gitignore` and
`status_message.py`, and no `.env`. `git diff` shows unstaged changes;
`git diff --staged` shows what you staged.

### Step 7: Merge the teammate's branch and resolve the conflict

A teammate's branch, `integration/copy-update`, changed the same lines of
`status_message.py`:

```text
git merge integration/copy-update
```

**Expect:** `CONFLICT (content): Merge conflict in status_message.py` and
`Automatic merge failed`. `git status` lists `status_message.py` under
`Unmerged paths`.

Open `status_message.py`. Between `<<<<<<< HEAD` and `=======` is your version;
between `=======` and `>>>>>>> integration/copy-update` is the teammate's. Write the
final text so it keeps both sides' intent:

- your behavior: the name still comes from `DEPLOY_ENV`, with the `development`
  fallback;
- the teammate's work: their support-team comment and their `help_message()`
  function, word for word.

Delete all three marker lines, save, then finish the merge:

```text
git add status_message.py
git commit -m "Merge integration/copy-update into feature/safe-status"
git log --oneline --graph --decorate -5
```

**Expect:** a merge commit at the top of `feature/safe-status`, with your commit and
the teammate's commit as its two parents, and `git status` reports
`nothing to commit, working tree clean`. Now do step 8. Only when all checks pass
does your evidence support changing your review note from **request changes** to
**ready for review**.

## Reference

- **What the 7 checks look at:** that `status_message()` meets the acceptance
  criteria, that `.env` is ignored and in no commit, that you are on
  `feature/safe-status` with `main` unchanged, that your commits change only
  `.gitignore` and `status_message.py`, that the teammate's branch is merged with
  `help_message()` kept, that no conflict markers remain, and that nothing is left
  uncommitted except ignored files. Nothing uses the network.
- **Expected output:** when everything passes, the output matches
  `expected/on-completion.txt`; only the run time differs.
- **Lab settings:** setup gives the lab repository a training name and email for that
  repository only; your own Git settings are not read or changed.
- **Start again:** from the project folder, `python tests/setup_lab.py` deletes
  `starter/ship-safe-change/` (including any file you added there) and rebuilds it.
- **Clean up when finished:** from the project folder, `python tests/cleanup_lab.py`
  deletes the lab repository, your local `.env` and any added files, and restores the
  shipped starter files.
- **Leave these as they are:** `tests/`, `fixtures/` and `expected/`.

## Troubleshooting

| Problem | Fix |
|---|---|
| `python: command not found`, or a version older than 3.11 | Run `python3 --version` (Windows: `py -3 --version`). If it shows 3.11 or newer, type `alias python=python3` once in this terminal (PowerShell: `Set-Alias python py`; cmd: `doskey python=py -3 $*`). |
| `discover` says `Start directory is not importable`, `No such file or directory` or finds no tests | Use `-s tests` in the project folder and `-s ../../tests` in `starter/ship-safe-change`. |
| `The lab repository is missing` | From the project folder, run `python tests/setup_lab.py`. |
| Windows cmd or PowerShell | Use `cd starter\ship-safe-change` and `cd ..\..` in cmd. List all files with `Get-ChildItem -Force` (PowerShell) or `dir /a` (cmd); in cmd, `cd` alone shows where you are. |
| `main has new commits` | You committed before switching branches. Rerun setup and start again from step 3. |
| `.env was committed` or `.env is staged` | Rerun setup; add the `.env` line to `.gitignore` before any `git add`, and name files explicitly. |
| `changed [...]` lists extra files | A commit included more than `.gitignore` and `status_message.py`. Rerun setup and stage the two files by name. |
| An editor opens after a Git command | The command had no `-m "..."`. Save and close the editor to accept the message, or rerun with `-m`. |
| `Conflict marker left in status_message.py` | Remove every line starting `<<<<<<<`, `=======` or `>>>>>>>`, then `git add status_message.py` and `git commit -m "Remove conflict markers"`. |
| `help_message() wording was lost` | Your resolution dropped the teammate's side. Rerun setup if needed and keep their comment and function. |
| Your lab state is broken | From the project folder, run `python tests/setup_lab.py`, then repeat the steps in order. |

## Optional: work on your own computer

You only need this if you were not given the project. Clone
`https://github.com/JesterCharles/pep-foundation-git-linux-ai-ship-a-safe-change-lab`,
open the cloned folder in VS Code or another editor, and start at **Quick start**.
If you have no Python 3.11 or newer, install it from python.org/downloads, then open
a new terminal.
