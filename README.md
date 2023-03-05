# HandsOff
![logo](https://github.com/GShwartz/HandsOff/raw/main/Images/HandsOff_resized.png) <br />
### A small and free <i>Client</i> <-> <i>Server</i> solution for IT & HD specialists.  <br />

### The Idea
Do you love your job but hate the customer's <b>technophobic</b> nature and unwillingness to cooperate? <br />
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
- Run Maintenance On The Remote Station (WiP)

### Menubar Tools
- Refresh Connections
- Clear Details Window
- Save Connection History
- Restart All Connected Stations
- Update All Connected Stations

---
## Usage ##
Just 'python3 main.py -i <IP> -p <PORT> on the machine you want to act as the C&C. <br />
on the client side, download the client DIR (or clone the repo), install requirements (pip install -r /path/to/requirements.txt) <br />
last step is to type 'python3 client.py' or run the client.bat file. <br />

------
### Main Window
![main window](https://raw.githubusercontent.com/GShwartz/HandsOff/main/Images/POC.jpg)


