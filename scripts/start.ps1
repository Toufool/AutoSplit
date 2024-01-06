param ([string]$p1)
& "$PSScriptRoot/compile_resources.ps1"
$python = $IsWindows ? 'python' : 'python3'
&"$python" "$PSScriptRoot/../src/AutoSplit.py" $p1
