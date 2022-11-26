# HandsOff #
![logo](https://github.com/GShwartz/HandsOff/raw/main/Images/HandsOff_resized.png) <br />
### A small and free <i>Client</i> <-> <i>Server</i> solution for IT & HD specialists.  <br />

## The Idea ##
Do you love your job but hate the custumer's <b>technophobic</b> nature and unwillingness to cooperate? <br />
<b>ME TOO!</b> <br /><br />
This is where <b>HandsOff</b> comes in. <br />
The entire idea behind this solution is that the other side only holds the <b>phone</b> and nothing else<br />
You can also perform maintenance on the remote station and update the station's client remotely.
* Since this is a pet project I don't have any steady hosting space to hold the exe files so I added a feature <br />
  that allows you to manually enter the new download url which will be published here. <br />

---

### Main Features ###
- Grab Screenshot from the Remote Station
- Run Anydesk On The Remote Station: <br />
  * If anydesk isn't installed on the remote machine, the app downloads and installs & runs it. <br />
- View Remote Station's Last Restart Time
- View Remote Station'sSystem Information
- View & Kill Remote Station's Running Tasks
- Restart Remote Station
- View Remote Station's Files In Local Dir (screenshots, system information and tasks files)
- Update Remote Station's Client
- Run Maintenance On The Remote Station

### Menubar Tools ###
- Refresh Connections
- Clear Details Window
- Save Connection History
- Restart All Connected Stations
- Update All Connected Stations

---
# Installation #
## Controller ##
* HandsOff runs on Python <= 3.10.8
* Clone Repo
* open CMD, navigate to dir and run pip install -r requirements.txt
* run python main.py

## Client ##
* Navigate to Client Folder
* Run python client.py
  - you can also setup autorun @startup using registery or creating a bat file inside StartUp folder that runs the client, <br />
  or use the scripts [here](https://github.com/GShwartz/HandsOff/tree/main/Client).
---


### About
![about](https://github.com/GShwartz/HandsOff/raw/main/Images/POC/about.JPG)

------
### Main Window
![main window](https://github.com/GShwartz/HandsOff/raw/main/Images/POC/main_window.JPG)

------
### Connected Stations
![main window connected stations](https://github.com/GShwartz/HandsOff/raw/main/Images/POC/main_window_connected.JPG)

------
### Screenshot
![screenshot](https://github.com/GShwartz/HandsOff/raw/main/Images/POC/screenshot.JPG)
------

### System Information
![system information](https://github.com/GShwartz/HandsOff/raw/main/Images/POC/sysinfo.JPG)

------
### Tasks
![tasks](https://github.com/GShwartz/HandsOff/raw/main/Images/POC/tasks.JPG)
