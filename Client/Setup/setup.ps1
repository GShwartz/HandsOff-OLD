$dst_path = 'C:\HandsOff'

$clientEXE = '.\client.exe'
$clientBAT = '.\client.bat'
$clientVBS = '.\client.vbs'
$clientPNG = '.\client.png'
$clientICO = '.\client.ico'
$updaterEXE = '.\updater.exe'
$reqsTXT = '.\requirements.txt'

$clientEXE_outpath = "$dst_path\client.exe"
$clientBAT_outpath = "$dst_path\client.bat"
$clientPNG_outpath = "$dst_path\client.png"
$clientVBS_outpath = "$dst_path\client.vbs"
$clientICO_outpath = "$dst_path\client.ico"
$updaterEXE_outpath = "$dst_path\updater.exe"
$reqsTXT_outpath = "$dst_path\requirements.txt"

# Python Vars
$python_version = "3.11.2"
$python_url = "https://www.python.org/ftp/python/3.11.2/python-3.11.2-amd64.exe"

# Windows startup folder for all users
$startup_path = "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp"

# Start installation
Write-Host "Installing HandsOff Client..."

# Create local folder
Write-Host "Creating Dir HandsOff..."
New-Item -ItemType Directory -Force -Path "C:\HandsOff"

$python_post_version = & python -V 2>&1
Write-Host "$python_post_version"

# Copy files
Copy-Item $clientEXE -Destination $clientEXE_outpath -Force
Copy-Item $clientBAT -Destination $clientBAT_outpath -Force
Copy-Item $clientVBS -Destination $clientVBS_outpath -Force
Copy-Item $clientPNG -Destination $clientPNG_outpath -Force
Copy-Item $clientICO -Destination $clientICO_outpath -Force
Copy-Item $updaterEXE -Destination $updaterEXE_outpath -Force
Copy-Item $reqsTXT -Destination $reqsTXT_outpath -Force

# Install python requirements
pip install -r ".\requirements.txt"

# Create Defender Exclusion for EXE File
Write-Host "Creating an Exclusion for Windows Defender..."
Add-MpPreference -ExclusionPath "$dst_path"

# Print Out Defender's Exclusion List
Get-MpPreference | Select-Object -Property ExclusionPath
Write-Host "Done!"

# Set Autorun in Registry
$registry_path = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run'
$registry_name = 'HandsOff'
$registry_value = 'c:\HandsOff\client.bat'

Write-Host "Setting up persistence..."
$persistence = Set-Itemproperty -Path $registry_path -Name $registry_name -Value $registry_value -Force
Write-Host "Done."

# Open Port 55400 For Incoming & Outgoing Traffic
Write-Host "Opening Port 55400..."
New-NetFirewallRule -DisplayName "Allow Incoming Port 55400 For HandsOff" -Direction Inbound -Profile Any -Action Allow -LocalPort 55400 -Protocol TCP
New-NetFirewallRule -DisplayName "Allow Outgoing Port 55400 For HandsOff" -Direction Outbound -Profile Any -Action Allow -LocalPort 55400 -Protocol TCP
Write-Host "Done!"

Write-Host "Installation completed, cleaning up..."
Remove-Item $python_outpath

# Run client
#Write-Host "Running client..."
#wscript "C:\Peach\client.vbs"