Get-Process | Where-Object {$_.ProcessName -eq "flask"} | Stop-Process