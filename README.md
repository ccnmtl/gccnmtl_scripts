# gccnmtl_scripts
Scripts for manipulating our GApps using the API

This script is intended for bulk sharing operations on GApps calendars.

Our specific need right now is to share resource calendars form gccnmtl.columbia.edu (owned by admin@gccnmtl.columbia.edu) with every member of the CTL staff in lionmail.  We are doing this to avoid having to share event details publically. W/out explicit sharing of event details, the resource rooms will not auto-accept reservations. With explicit sharing, even free/busy can be private.

## Usage:

./gccnmtl_calendar_sharing.py [-a --add|-r --remove|-l list]][-c|--config <path to .ini file of urls and dest names>] [-h|--help]



## Installation
 git clone https://github.com/ccnmtl/gccnmtl_scripts
 cd gccnmt_scripts
 make bootstrap
 
Before running this script, you will need to download the credentials from the developer console in gccnmtl (https://console.developers.google.com/project/charged-thought-110002), and save them to a file called gccnmtl_scripts/client_secret.json

as described here:

https://developers.google.com/google-apps/calendar/quickstart/python

FYI - (quickstart.py is included in this repo just to make sure you can get this running)

The first time you run this script, it should fire up a browser, where you can authenticate as admin@gccnmtl.columbia.edu. The oauth credentials will be saved locally, so you won't be prompted to do this again.  If you want to clear the auth credentials, type make clean-creds. 
