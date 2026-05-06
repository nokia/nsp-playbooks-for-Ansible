# Repository Git workflow

This project uses the default branch (`main`) as the integration target. Follow these rules so history stays clear and attributable.

## Branches and pull requests

- Create a **topic branch** from `main` (for example `feature/…`, `fix/…`, `docs/…`).
- Open a **pull request** for every change set; merge only after review.
- **Do not push directly to `main`** except for rare repository maintenance agreed among maintainers.

## Commit authorship

- Use your **real name and email** in Git (`user.name` / `user.email`) so commits match the contributor who did the work.
- Before pushing, review the commit message body. Some local tools append extra `Co-authored-by:` lines; remove any that do not reflect an actual human co-author so GitHub does not list unintended co-authors.

## Signed commits (optional)

If your organization requires signed commits, configure signing locally and keep signing keys under your control.
