# FORGE_INIT Prompt

This prompt initializes the `.forge/` structure in any project repo. It is non-destructive — it only creates files and folders that don't already exist.

## Usage

Copy the prompt below and send it to Claude Code. It will ask which repository to target.

## Notes

- CLAUDE.md is NOT created by this prompt — it requires manual project-specific setup
- The prompt is idempotent — safe to run multiple times on the same repo
- Existing files are never modified or overwritten
