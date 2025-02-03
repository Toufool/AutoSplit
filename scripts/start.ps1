param ([string]$p1)
& "$PSScriptRoot/compile_resources.ps1"
uv run "$PSScriptRoot/../src/AutoSplit.py" $p1
