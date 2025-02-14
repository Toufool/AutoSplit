$qt6_applications_path = uv run --active python -c 'import qt6_applications; print(qt6_applications.__path__[0])'

& "$qt6_applications_path/Qt/bin/designer" `
  "$PSScriptRoot/../res/design.ui" `
  "$PSScriptRoot/../res/about.ui" `
  "$PSScriptRoot/../res/settings.ui" `
  "$PSScriptRoot/../res/update_checker.ui"
