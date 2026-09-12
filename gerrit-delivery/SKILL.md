---
name: gerrit-delivery
description: Prepare and upload narrowly scoped changes from a multi-repository checkout to Gerrit, including repository discovery, commit-message policy, review refs, and CI status interpretation. Use only when the user asks to commit, upload, or manage a Gerrit review.
---

# Gerrit Delivery

Gerrit upload changes external state. Inspect and stage freely when authorized to prepare a submission, but push only when the user explicitly asks to upload/submit.

## Repository routing

Many firmware SDKs use repo-style multi-repository checkouts. Locate the repository that actually tracks the target path with `git -C <candidate> status` or the nearest `.git` link.

- Confirm the live remote, project, and target branch; never copy another project's host or branch assumptions blindly.
- Do not force-add a path from an outer repository merely because an inner repository or ignore rule hides it.

## Delivery workflow

1. Show branch, upstream, remote, status, and recent commits in the correct nested repository.
2. Identify unrelated tracked modifications and untracked backups. Stage exact paths only.
3. Review the cached diff/stat and run `git diff --cached --check`.
4. Use the local Gerrit `commit-msg` hook so the commit receives a `Change-Id`.
5. Follow the commit template in [references/commit-template.md](references/commit-template.md).
6. Push to `refs/for/<branch>`, capture the Gerrit change URL, and report exactly which files were included.
7. If rejected, fix only the stated policy issue, preserve the Change-Id when updating an existing review, amend, and retry once the commit is valid.

Do not claim server compilation succeeded from an upload alone. `Build-Verify: No votes` means no successful verification result is present. Trigger mechanisms are installation-specific; inspect available UI actions or team CI documentation instead of guessing a comment command.
