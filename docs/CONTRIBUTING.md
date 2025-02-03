<!-- This has to be in the repository's root, `docs/`, or `.github/` directory to be picked by github. Read more at: https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors#about-contributing-guidelines -->

# Contributing guidelines

## Python Setup and Building

Refer to the [build instructions](/docs/build%20instructions.md) if you're interested in building the application yourself or running it in Python.  

## Linting and formatting

The project is setup to automatically configure VSCode with the proper extensions and settings. Fixers and formatters will be run on save.  
If you use a different IDE or for some reason cannot / don't want to use the recommended extensions, you can run `scripts/lint.ps1`.
Project configurations for other IDEs are welcome.

If you like to use pre-commit hooks, `.pre-commit-config.yaml` is setup for such uses.

The CI will automatically fix and commit any autofixable issue your changes may have.

## Visual Designer

If you need to make visual changes, run `./scripts/designer.ps1` to quickly open the bundled Qt Designer.
(Can also be downloaded externally as a non-python package)

## Pull Request Guidelines

If your pull request is meant to address an open issue, please link it as part of your Pull Request description. If it would close said issue, please use a [closing keyword](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue#linking-a-pull-request-to-an-issue-using-a-keyword).

Try not to Force Push once your Pull Request is open, unless absolutely necessary. It is easier for reviewers to keep track of reviewed and new changes if you don't. The Pull Request should be squashed-merged anyway.

Your Pull Request has to pass all checks ot be accepted. If it is still a work-in-progress, please [mark it as draft](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/changing-the-stage-of-a-pull-request#converting-a-pull-request-to-a-draft).

## Coding Standards

Most coding standards will be enforced by automated tooling.
As time goes on, project-specific standards and "gotchas" in the frameworks we use will be listed here.

### Keep shipped dependencies and bundle size low

The bigger the bundle, the longer it takes to boot single-file executables. That is because we need to ship everything and the bootloader basically has to extract it all.
Our main use case is a single-file that is as easy to use as possible for the end user.
Keeping install time, build time and bandwith as low as possible is also a nice-to-have.

You should also consider whether the work the dependency is doing is simple enough that you could implement it yourself.

For these reasons, it's important to consider the impacts of adding any new dependency bundled with AutoSplit.

### Magic numbers

Please avoid using magic numbers and prefer constants and enums that have a meaningful name when possible.
If a constant is shared throughout the app, it should live in `src/utils.py`. Unless it is very-specific to a module.
For image shape and channels, please use `utils.ImageShape` and `utils.ColorChannel`.

### Image color format and channels

To avoid image shape mismatch issues, and to keep code simpler, we standardize the image color format to BGRA. This should always be done early in the pipeline, so whatever functionality takes care of obtaining an image should also ensure its color format. You can do so with `cv2.cvtColor` (ie: `cv2.cvtColor(image, cv2.COLOR_RGBA2BGRA)` or `cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)`).

### Split-specific setting overrides

Whenever a split image overrides a default global setting, we add a getter that handles the logic of checking for a split-specific override, then falling back to globals. This avoids repeating the fallback logic in multiple places. See `AutoSpitImage.get_*` methods for examples.

## Testing

None 😦 Please help us create test suites, we lack the time, but we really want (*need!*) them. <https://github.com/Toufool/AutoSplit/issues/216>
