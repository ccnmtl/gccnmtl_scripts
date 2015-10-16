# gccnmtl_scripts
Scripts for manipulating our GApps using the API

## Usage:

./gccnmtl_calendar_sharing.py [-a --add|-r --remove|-l list]][-c|--config <path to .ini file of urls and dest names>] [-h|--help]


Understanding this script starts with understanding the gapp calendar api:

From https://developers.google.com/google-apps/calendar/quickstart/python

(quickstart.py is included in this repo just to make sure you can get this running)

## Installation
 git clone https://github.com/ccnmtl/gccnmtl_scripts
 cd gccnmt_scripts
 make bootstrap
 
The first time you run this script, it shoudl fire up a browser, where you can authenticate as admin@gccnmtl.columbia.edu. The oauth credentials will be saved locally, so you won't be prompted to do this again.  If you want to clear the auth credentials, type make clean-creds. 
