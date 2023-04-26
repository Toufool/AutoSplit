<!-- This has to in the repository's root, `docs/`, or `.github/` directory to be picked by github. Read more at: https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors#about-contributing-guidelines -->

# Contributing guidelines

## Python Setup and Building

Refer to the [build instructions](/docs/build%20instructions.md) if you're interested in building the application yourself or running it in Python.  

## Linting and formatting

The project is setup to automatically configure VSCode witht he proper extensions and settings. Linters and formatters will be run on save.  
If you use a different IDE or for some reason cannot / don't want to use the recommended extensions, you can run `scripts/lint.ps1`.

If you like to use pre-commit hooks, `.pre-commit-config.yaml` is setup for such uses.

The CI will automatically fix and commit any autofixable issue your changes may have.

## Pull Request Guidelines

If your pull request is meant to address an open issue, please link it as part of your Pull Request description. If it would close said issue, please use a [closing keyword](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue#linking-a-pull-request-to-an-issue-using-a-keyword).

Try not to Force Push once your Pull Request is open, unless absolutely necessary. It is easier for reviewers to keep track of reviewed and new changes if you don't. The Pull Request should be squashed-merged anyway.

Your Pull Request has to pass all checks ot be accepted. If it is still a work-in-progress, please [mark it as draft](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/changing-the-stage-of-a-pull-request#converting-a-pull-request-to-a-draft).

## Coding Standards

Most coding standards will be enforced by automated tooling.
As time goes on, project-specific standards and "gotchas" in the frameworks we use will be listed here.

## Testing

None 😦 Please help us create test suites, we lack the time, but we really want (need!) them. <https://github.com/Toufool/AutoSplit/issues/216>
