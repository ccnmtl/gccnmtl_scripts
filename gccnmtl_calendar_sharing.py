#!ve/bin/python
"""
A small script to manage gccnmtl calendars

./gccnmtl_calendar_sharing.py -c|--config <path to .ini file of urls and dest names> [-a|--add] [-r|--remove] [-l list] [-h|--help]

Jonah Bossewitch, CTL
https://github.com/ccnmtl/gccnmtl_scripts/README.md

"""


from __future__ import print_function
import httplib2
import os
import sys
import getopt
import ConfigParser

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
from googleapiclient.errors import HttpError
import datetime

SCOPES = 'https://www.googleapis.com/auth/calendar' # read/write acces to calendars
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'gCCNMTL Calendar Sharing'

CALENDAR_ID_SECTION='calendars'
USER_ID_SECTION='emails'

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-gccnmtl-calendars.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


class GCalSharing:

    def __init__(self, config_filename):
        self.service = None
        self.calendars = []
        self.users = []
        service = None
        
        # try opening the config file
        if not(os.access(config_filename, os.R_OK | os.F_OK)):
            print ("Could not open %s\n" % config_filename)
            sys.exit(2)

        # this config file should have a section for calendar ids, and another for valid gapp emails
        # the elements are not name=value pairs, just names
        config = ConfigParser.SafeConfigParser(allow_no_value=True)
        config.read(config_filename)

        try: 
            self.calendars = config.options(CALENDAR_ID_SECTION)
            self.users = config.options(USER_ID_SECTION)
        except:
            print ("Config file is misconfiged. See the README.md for more help")

    def authenticate(self):
        # oauth dance w/ google. Credentials are stored locally after first auth. 
        # this method will open a brower for auth
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        self.service = discovery.build('calendar', 'v3', http=http)

    def list_calendar(self, calendar_id):
        """List the current sharing rules on calendar_id"""
        
        try:
            acl = self.service.acl().list(calendarId=calendar_id).execute()
        except HttpError, err:
          if err.resp.status == 404:
              print ("Calendar %s was not found." % calendar_id )
              return
          else:
              raise
          
        for rule in acl['items']:
            print("%s: %s" % (rule['id'], rule['role']))
            
    def list_all(self):
        """call list_calendar for each calendar in calendars"""
        
        for c in self.calendars:
            self.list_calendar(c)
        
    def add_user(self, calendar_id, user_email):
        """add this user to the calendar as a reader"""
        
        # construct a valid rule object
        # todo: will domains work here? 
        rule = {
            'scope': {
                'type': 'user',
                'value': user_email,
                },
            'role': 'reader'
        }

        try:
            created_rule = self.service.acl().insert(calendarId=calendar_id, body=rule).execute()
        except HttpError, err:
            if err.resp.status == 404:
                print ("The Calendar %s was not found." % calendar_id )
                return
            # this method does not fail if user is already on the calendar. 
            else:
                raise

        print("%s was added to %s (rule: %s)" % (user_email, calendar_id, created_rule['id']))
          
    def add_users(self):
        """call add_user for each users for each calendar in calendars"""
        
        for c in self.calendars:
            for u in self.users:
                self.add_user(c, u)
                
    def remove_user(self, calendar_id, user_email):
        """remove this user from calendar_id"""
    
        rule_id = "user:%s" % user_email
        try:
            self.service.acl().delete(calendarId=calendar_id, ruleId=rule_id).execute()
        except HttpError, err:
            if err.resp.status == 404:
                print ("The Calendar %s was not found." % calendar_id )
                return
            elif err.resp.status == 400:
                print ("The user %s was not found on this calendar (%s)." % (user_email, calendar_id))
                return
            else:
                raise
        print("%s was removed from %s" % (user_email, calendar_id))
    
    def remove_users(self):
        """call add_user for each users for each calendar in calendars"""
        
        for c in self.calendars:
            for u in self.users:
                self.remove_user(c, u)

def main(argv=None):
    """
    parse command line args, read config file, authenticate to google, and dispatch to action function
    """

    if argv == None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "arlc:h", ["add", "remove", "list", "config=", "help"])
        except getopt.error, msg:
            raise Usage(msg)
    except Usage, err:
        print(err.msg, file=sys.stderr)
        print("for help use --help", file=sys.stderr)
        return 2

    if not opts:
        print (__doc__)
        return 2
    
    #import pdb; pdb.set_trace()

    action = None
    arg = None
    config_filename = ""
    for o, a in opts:
        if o == "-l" or o == "--list":
            action = GCalSharing.list_all
        elif o == "-a" or o == "--add":
            action = GCalSharing.add_users
        elif o == "-r" or o == "--remove":
            action = GCalSharing.remove_users
        elif o == "-c" or o == "--config":
            config_filename = a
        elif o == "-h" or o == "--help":
            print (__doc__)
            return 2
        else:            
            print (__doc__)
            return 2

    #make sure an action was specified
    if not action or not config_filename:
        print ("You must specify a config filename AND a single action, --add, --remove or --list")
        print (__doc__)
        return 2

    # construct calendar sharing manager, using config file
    gccnmtl_calendars = GCalSharing(config_filename)

    # authenticate to google - will prompt browswer based oauth
    gccnmtl_calendars.authenticate()

    # finally, call the class method corresponding to the action specified on the command line
    # this was an unbound function, so bind it to our instance
    action(gccnmtl_calendars)

if __name__ == '__main__':
    sys.exit(main())
