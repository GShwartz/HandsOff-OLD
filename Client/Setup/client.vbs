Dim WShell
Set WShell = CreateObject("WScript.Shell")
WShell.Run "c:\HandsOff\client.exe", 0
Set WShell = Nothing