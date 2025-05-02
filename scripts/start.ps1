#! /usr/bin/pwsh

param ([string]$p1)
& "$PSScriptRoot/compile_resources.ps1"
uv run --active "$PSScriptRoot/../src/AutoSplit.py" $p1
