# TODO - Jira Autofix Extension

## High Priority

- [ ] **Duplicate Comment Prevention**
  - Check for existing PR comments on Jira ticket before adding a new one
  - Option: Update existing comment instead of creating duplicates

- [ ] **Workspace File Path Issue**
  - `/setrepo` fails when trying to write outside workspace
  - Make path handling more robust by always writing to workspace root

- [ ] **Smarter Branch Handling**
  - Detect existing remote branches for the same issue
  - Reuse/update existing branch OR use unique naming to avoid conflicts

## Medium Priority

- [ ] **Existing Directory Handling**
  - When clone fails (dir exists), pull latest changes instead of using stale copy
  - Ensure local copy is in sync with remote

- [ ] **Skip Redundant Work on Same Issue**
  - Detect existing open PR for the same issue early in the workflow
  - Ask user: "PR #X already exists for this issue. Update it or create new?"

## Nice to Have

- [ ] **Test Coverage Detection**
  - Add note in PR body when no automated tests are detected/run

- [ ] **Cleanup of Working Directories**
  - Clean up old working directories after PR is merged

## Work in Progress

- [ ] **External Extension Integration**
  - Integration with `security` and `code-review` extensions (currently using native/built-in review)
