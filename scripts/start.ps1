param ([string]$p1)
& "$PSScriptRoot/compile_resources.ps1"
python3 "$PSScriptRoot/../src/AutoSplit.py" $p1
