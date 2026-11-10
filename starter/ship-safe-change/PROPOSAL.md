# Proposed change: deployment name from the environment

Prepared with an AI coding assistant. Review it before it is committed.

## Claims

1. `status_message()` now reads the deployment name from the `DEPLOY_ENV` environment variable.
2. The local `.env` file can no longer be committed by accident.

## Acceptance criteria

- Given `DEPLOY_ENV=staging`, `status_message()` returns exactly `staging: ready`.
- With `DEPLOY_ENV` unset, `status_message()` returns exactly `development: ready`.
- `.env` is matched by `.gitignore` and is never tracked.
