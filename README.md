# Scandir
## This tool creates a report on c:/temp/scandir/scandir.csv of the host, 
## showing the size of every single folder under what is requested 
## on file hosts.json.
##  
## Ex:
## {'022fs01': 'e:/Dept'} -> It will report the size of all folders under e:/Dept
## for the host 022fs01
## 
# Instalation
## 1- Create a python virtual environment:
### python -m venv .venv
## 2- Activate the virtual environment:
### .venv\scripts\activate
## 3- Install the dependencies:
### pip install -r requirements.txt
## 4- Update file hosts.json with the hosts data
## 5- Create a distribution exe file for scandir.py:
### pyinstaller scandir.py --onefile
## 6- Run remote.py file:
### (.venv) c:/fileserver_reports>remote.py
# 
## This script will:
### 1- Update every server added on json file with the latest version of scandir on 
### c:/temp/scandir
### 2- Iterate on every server and run the scandir.exe remotelly.
### 3- scandir will generate file scandir.csv on the same folder as the scandir.exe
### Note: the user running remote.py shoud have read permissions on all the hosts on the hosts.json file.