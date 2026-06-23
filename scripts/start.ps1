#! /usr/bin/pwsh

param ([string]$p1)
& "$PSScriptRoot/compile_resources.ps1"
uv run --active --no-sync "$PSScriptRoot/../src/AutoSplit.py" $p1
