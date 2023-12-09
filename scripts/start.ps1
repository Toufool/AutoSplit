param ([string]$p1)
& "$PSScriptRoot/compile_resources.ps1"
$python = $IsLinux ? 'python3' : 'python'
&"$python" "$PSScriptRoot/../src/AutoSplit.py" $p1
