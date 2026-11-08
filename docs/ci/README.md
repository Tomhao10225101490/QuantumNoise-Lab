# Optional GitHub Actions workflow

Local validation completed successfully: 50 pytest tests, compilation and Ruff. The included verify.yml is a ready-to-enable CI template.

The first public push was rejected because the existing GitHub OAuth credential does not have the workflow scope. To publish the complete project without requesting broader credentials, the workflow is stored here instead of .github/workflows. It is therefore not active remote CI.

To enable it later using an account credential authorized to modify Actions workflows, copy this file to .github/workflows/verify.yml and push that change. No CI success is claimed until an actual Actions run completes.
