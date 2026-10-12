# GitHub Workflow

## Issues

Issues represent units of work and use the same vocabulary as Conventional Commits.

Examples:

- `feat: add user registration`
- `fix: reject duplicated usernames`
- `docs: update architecture`

Templates are provided in `.github/ISSUE_TEMPLATE/`.

## Pull Requests

PR titles must follow Conventional Commits.

Examples:

```text
feat(user): add user registration
fix(store): prevent ID reuse
docs(readme): document build requirements
refactor(menu): split input handling
```

The workflow `.github/workflows/conventional.yml` validates the title and applies a matching `type: ...` label.

## Labels

Labels are provisioned by `.github/workflows/labels.yml`.

### Type

`type: feat`, `type: fix`, `type: docs`, `type: style`, `type: refactor`, `type: perf`, `type: test`, `type: build`, `type: ci`, `type: chore`, `type: revert`, `type: breaking`

### Status

`status: ready`, `status: in-progress`, `status: needs-review`, `status: blocked`, `status: done`

### Area

`area: core`, `area: terminal`, `area: persistence`, `area: security`, `area: documentation`

## Semantic versioning

The release workflow derives Git tags from Conventional Commit history and creates a GitHub Release using the matching `CHANGELOG.md` section. Existing non-SemVer tags such as `ui-v1` are ignored:

```text
BREAKING CHANGE or type!:  -> MAJOR
feat:                     -> MINOR
fix/perf/refactor/...:    -> PATCH
```

Tags use:

```text
vMAJOR.MINOR.PATCH
```

The workflow runs on pushes to `main`. It only creates a new tag when new Conventional Commit messages exist since the previous SemVer tag. Manually pushed `vMAJOR.MINOR.PATCH` tags also publish a release from the matching changelog section.

## GitHub Projects

Recommended Project view:

| Status | Purpose |
|---|---|
| Backlog | Planned work |
| Ready | Ready to implement |
| In Progress | Active work |
| Review | Awaiting review |
| Done | Completed |

Recommended fields:

- Status
- Priority
- Type
- Area
- Milestone

The repository does not hard-code a Project ID. This keeps the repository portable between personal, organization and future Project boards.

To automate Project addition later, configure a repository/project identifier and extend the workflow with the Projects v2 API.

## Branches

Suggested branch names:

```text
feat/user-registration
fix/id-generation
refactor/menu
docs/architecture
test/user-store
```

## Merge policy

Preferred merge method:

- Squash merge for feature/fix PRs.
- PR title becomes the resulting Conventional Commit.
- Avoid merge commits when the history is intended to drive semantic versioning.
