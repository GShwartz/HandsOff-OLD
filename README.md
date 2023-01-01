# HandsOff
![logo](https://github.com/GShwartz/HandsOff/raw/main/Images/HandsOff_resized.png) <br />
### A small and free <i>Client</i> <-> <i>Server</i> solution for IT & HD specialists.  <br />

### The Idea
Do you love your job but hate the custumer's <b>technophobic</b> nature and unwillingness to cooperate? <br />
<b>ME TOO!</b> <br /><br /> 
This is where <b>HandsOff</b> comes in. <br />
The entire idea behind this solution is that the other side only holds the <b>phone</b> and nothing else<br />
** Maintenance & Update options are unavailable ATM.

---
### Main Features
- Grab Screenshot from the Remote Station
- Run Anydesk On The Remote Station: <br />
  * If anydesk isn't installed on the remote machine, the app downloads, installs & runs it. <br />
- View Remote Station's Last Restart Time
- View Remote Station'sSystem Information
- View & Kill Remote Station's Running Tasks
- Restart Remote Station
- View Remote Station's Files In Local Dir (screenshots, system information and tasks files)
- Update Remote Station's Client
- Run Maintenance On The Remote Station

### Menubar Tools
- Refresh Connections
- Clear Details Window
- Save Connection History
- Restart All Connected Stations
- Update All Connected Stations

---
# Installation #
## Controller ##
* HandsOff runs on Python >= 3.10.8
* Clone Repo
* open CMD, navigate to dir and run pip install -r requirements.txt
* change the ip addr/port according to your wished inside main.py OR <br />
  run python main.py -i [ip] -p [port] <br />
  -- keep in mind you'll have to change the ip address in the client file or run the client the same as you run the server.

## Client ##
### Important!!!
  Remember to use the same IP address and port for both main & client files.
* Navigate to Client Folder
* Run python client.py OR python client -i [ip_to_connect_to] -p [port]
  - you can also setup autorun @startup using registery or creating a bat file inside StartUp folder that runs the client, <br />
  or use the scripts [here](https://github.com/GShwartz/HandsOff/tree/main/Client).

#### the client runs an icon inside system tray, no exit options on purpse.
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

