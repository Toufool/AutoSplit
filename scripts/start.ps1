param ([string]$p1)
& "$PSScriptRoot/compile_resources.ps1"
python "$PSScriptRoot/../src/AutoSplit.py" $p1
