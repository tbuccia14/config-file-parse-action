# How to contribute to this GitHub Action

## How to contribute

1. Fork this repository (or create a branch directly if you have write access).
2. Create a branch with a descriptive name for your change.
3. Code your changes, add or update tests (`tests/test_parser.py`), and run them locally.
4. Push your branch and open a pull request against `main`, describing the change and, for
   complex changes, linking to test results.
5. Use a Draft pull request if you are not ready for review yet.

> Note: composite actions like this one cannot be triggered directly from a fork when testing via `uses: ./`. To validate changes end-to-end, either work from a branch on this repository (if you have access) or reference your fork explicitly (`uses: <your-fork>/config-file-parse-action@<branch>`) from a separate test workflow.

### Calling actions from third parties

> [!IMPORTANT]
> **Security rule:** how a third-party action is pinned depends on whether its publisher is a
> [verified creator](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions#using-third-party-actions)
> on the GitHub Marketplace (or, for `github/*` actions, officially maintained by GitHub even if
> not published as a Marketplace listing):
>
> - **Verified / GitHub-official** → a mutable version tag is fine:
>   ```yaml
>   uses: some-org/some-action@v1
>   ```
> - **Not verified** → pin to the full commit SHA of the action's latest release, with the
>   human-readable version as a trailing comment:
>   ```yaml
>   uses: some-org/some-action@<commit-sha>  # vx.y.z
>   ```
>
> This repository follows this rule for every action used in its own workflows — see
> [`.github/workflows/`](.github/workflows/) for current examples of each case. When adding a new
> step that calls a third-party action, check its Marketplace listing for the "Verified creator"
> badge before deciding how to pin it, and re-check on every version bump since publishers can
> change.

### Committing your changes

Once your changes are done (including unit tests), you can commit your changes.
We use [Conventional Commits](https://www.conventionalcommits.org/) to enforce rules that allow the next version to be deduced automatically based on [Semantic Versioning 2](https://semver.org/).

> The Conventional Commits specification is a lightweight convention on top of commit messages. It provides an easy set of rules for creating an explicit commit history, which makes it easier to write automated tools on top of.

To ensure commit messages are properly formatted, we rely on [Commitlint](https://commitlint.js.org/), which is configured as a `commit-msg` Git hook.
This means that when committing, the hook will run `commitlint` and reject the commit if it does not comply with the expected [rules](https://github.com/conventional-changelog/commitlint/tree/master/%40commitlint/config-conventional#rules).
Pull requests are also validated with the same rules in CI.

Here is the list of supported _types_:

| Commit Type | Title | Description | Emoji |
| ----------- | ----- | ----------- | ----- |
| build | Build System | Changes that affect the build system or external dependencies | 🛠 |
| chore | Miscellaneous Chores | Changes to the build process or auxiliary tools and libraries such as documentation generation | ♻️ |
| ci | Continuous Integration | Changes to our CI configuration files and scripts | ⚙️ |
| docs | Documentation | Documentation only changes | 📚 |
| feat or feature | Features | A new feature | ✨ |
| fix | Bug Fixes | A bug fix | 🐛 |
| perf | Performance Improvements | A code change that improves performance | 🚀 |
| refactor | Code Refactoring | A code change that neither fixes a bug nor adds a feature | 📦 |
| revert | Reverts | Reverts a previous commit | 🗑 |
| style | Styles | Changes that do not affect the meaning of the code, like formatting | 💎 |
| test | Tests | Adding missing tests or correcting existing tests | 🚨 |

Here is an example of a conventional commit message:

```text
feat(parser): support flattening tuples
^    ^              ^
|    |              |__ Subject
|    |_________________ Scope
|______________________ Type
```

Here is an example of what you should get if `commitlint` reports an error:

```bash
$ git commit -m 'foo: bar'

⧗   input: foo: bar
✖   type must be one of [build, chore, ci, docs, feat, fix, perf, refactor, revert, style, test] [type-enum]

✖   found 1 problems, 0 warnings
ⓘ   Get help: https://github.com/conventional-changelog/commitlint/#what-is-commitlint

husky - commit-msg hook exited with code 1 (error)
```

### Automated GitHub semantic release

The GitHub release creation is automated thanks to the [Semantic Release plugin](https://semantic-release.gitbook.io/semantic-release), triggered manually via the [action-release.yaml](.github/workflows/action-release.yaml) workflow.
We may not release for every commit — for example, a change to NPM `devDependencies` alone typically has no impact on the action itself.

A release is created based on the commit message content:

* A breaking change triggers a **major** version
* A change of type _feat_ triggers a **minor** version
* A change of type _fix_, _perf_, _refactor_ or _revert_ triggers a **patch** version

After a successful release, a new [GitHub release](../../releases), including a tag, is created. The associated _release notes_ are generated by the [Conventional Changelog plugin](https://github.com/conventional-changelog/conventional-changelog), covering all changes since the previous release (not just the commit that triggered the release). A [CHANGELOG.md](./CHANGELOG.md) file is also maintained by the plugin with the generated release notes.

The release workflow additionally moves the major version tag (e.g. `v1`) to point at the new release, so that consumers pinning `uses: tbuccia14/config-file-parse-action@v1` get non-breaking updates automatically.
