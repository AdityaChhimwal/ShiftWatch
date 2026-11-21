# Lesson 5A: giving our project a memory

We now have a small service, a label validator, tests, and examples. As we change them, we need to answer a practical question: which version contained which behavior? A folder full of names such as `final`, `final2`, and `really-final` would make that difficult. Git records selected versions of the project and lets us inspect the changes between them.

Git runs on your computer. GitHub hosts a copy of a Git repository online. Saving a version with Git and sending that version to GitHub are two separate actions.

## Follow one real change

Suppose we improve the explanation in this lesson. Editing and saving this file changes the working folder. That alone creates no Git commit and changes nothing on GitHub.

Next, `git add docs/lessons/05-version-history.md` selects this file's current contents for the next commit. Git calls this selected snapshot the staging area. If we edit the file again afterward, that new edit needs another `git add` to enter the staged snapshot.

Then `git commit -m "docs: teach Git history and record the first publication"` records the staged snapshot in the local repository. A commit contains a message and a reference to the project version. Git assigns it an identifier; the short identifier for our first commit is `b801aa1`. The message helps a reader understand the purpose of the change, while the identifier distinguishes the exact commit.

Finally, `git push origin main` sends the local branch's commits to the configured remote repository. `origin` is our local nickname for `https://github.com/AdityaChhimwal/ShiftWatch.git`. `main` is our current branch: a named line of project history. A successful push updates that branch on GitHub.

```text
Working folder --git add--> Staging area --git commit--> Local history
                                                              |
                                                           git push
                                                              |
                                                              v
                                                       GitHub history
```

For example, if our local history contains commits A and B, but GitHub contains only A, then B has been committed but has not yet been pushed there. Editing, staging, committing, and pushing solve different parts of the journey.

## What we actually published

The existing GitHub repository was empty. We reviewed the current foundation, checked the existing four passing schema tests and dependency consistency, and published one baseline commit:

```text
b801aa1 feat: add health service, label validation, and guided project baseline
```

This snapshot includes the health endpoint, strict label-shape validation, assistant-authored tests, synthetic teaching examples, lessons, and historical evidence. We did not reconstruct imaginary earlier commits. Current implementation and teaching contributions are recorded as assistant-led; your demonstrated understanding is recorded separately in `PROJECT_STATE.md`.

The first push used `git push -u origin main`. The `-u` option saved the tracking relationship between local `main` and `origin/main`. Later we can use `git push` with that relationship, or explicitly name `origin main` as above.

## Read the history before changing it

These Git commands were exercised using the installed Windows Git. Their syntax is also suitable for your Git Bash terminal, opened in this project folder:

```bash
git status --short --branch
git log --oneline -3
git show --stat b801aa1
```

`status` describes the working/staged changes and branch relationship. `log` lists commits. `show --stat` summarizes the files changed by a commit. Before committing a future lesson, use `git diff` to inspect unstaged edits and `git diff --cached` to inspect what is staged. A successful commit does not run our Python tests automatically; relevant checks remain a separate step.

We will commit a coherent working change with a message describing its purpose, then push after the lesson. A meaningful message such as `feat: validate nonnegative label counts` tells a reader more than `update`. The purpose is a reviewable record of real work; some lessons may chiefly change an explanation or test rather than application behavior.

## What belongs in this history

Source code, tests, teaching examples, dependency requirements, and documentation belong in the repository. Our `.gitignore` excludes the installed `.venv`, temporary files, local databases, and `.env` configuration files. An ignore rule helps keep untracked files out of routine staging; it does not remove an already tracked file or replace reviewing the actual diff.

Keeping source history is one part of reproduction. Another computer also needs a compatible Python runtime and the required libraries. `requirements.txt` records exact library versions from this environment, but a clean installation and a running Docker container have not yet been verified. Lesson 5B will teach that separate problem through the small service we already have.

## One check

You edit a file, run `git add`, and successfully run `git commit`. You have not pushed. Does GitHub already contain that new commit? Which command sends it there?

Learner answer on 21 November: "It stays in the staging area and only visible in github when we use git push".

Assessment: the push-to-GitHub part is correct. The staging/local-history distinction needs correction and a retest; this does not yet pass the whole check.

### Follow the same change through three moments

Think of staging as preparing a photograph, committing as saving that photograph in your computer's album, and pushing as copying the saved photograph to the online album.

| Last successful command | What happened to our selected change? | Does GitHub have the new commit yet? |
|---|---|---|
| `git add` | Its contents are selected for the next commit; that new commit does not exist yet. | No |
| `git commit` | A new commit now records those contents in local Git history. | No |
| `git push` | The local commit has also been sent to GitHub. | Yes |

This traces one change with no additional edits. Committing does not remove the working files. Once committed, there is no outstanding staged difference for that change; a later edit can be staged for another commit.

We checked the actual repository before this correction was added. `git diff --cached --name-only` printed no filenames, while `git log -1 --oneline` printed:

```text
cb0c5bc docs: teach Git history and record the first publication
```

So that commit was already in local history even though no uncommitted staged changes were waiting. It had also been pushed in the previous lesson; this observation is not a new demonstration of an unpushed commit.

Retest: after successfully running `git add` and `git commit`, where is the new saved version recorded: the staging area or local Git history?

The retest has not yet been answered. Lesson 5 as a whole remains partial while this distinction, runtime reproduction, and container verification are pending.

The official [Git commit documentation](https://git-scm.com/docs/git-commit) and [Git push documentation](https://git-scm.com/docs/git-push) provide the full command behavior. This lesson uses their basic workflow on our actual project.
