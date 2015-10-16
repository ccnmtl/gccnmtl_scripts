#!ve/bin/python
"""
From https://developers.google.com/google-apps/calendar/quickstart/python

Make sure to follow the instructions, and download client_secret.json
"""

from __future__ import print_function
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
from googleapiclient.errors import HttpError
import datetime

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/calendar' # read/write acces to calendars
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'gCCNMTL Calendar Sharing'


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
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatability with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def list_users(service, calendar_id):
    """List the current sharing rules on calendar_id"""
    
    try:
        acl = service.acl().list(calendarId=calendar_id).execute()
    except HttpError, err:
      if err.resp.status == 404:
          print ("Calendar %s was not found." % calendar_id )
          return
      else:
          raise

    for rule in acl['items']:
        print("%s: %s" % (rule['id'], rule['role']))
    
def add_user(service, calendar_id, user_email):
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
        created_rule = service.acl().insert(calendarId=calendar_id, body=rule).execute()
    except HttpError, err:
        if err.resp.status == 404:
          print ("The Calendar %s was not found." % calendar_id )
          return
        # this method does not fail if user is already on the calendar. 
        else:
          raise

    print("%s was added to %s (rule: %s)" % (user_email, calendar_id, created_rule['id']))

def remove_user(service, calendar_id, user_email):
    """remove this user from calendar_id"""
    
    rule_id = "user:%s" % user_email
    try:
        service.acl().delete(calendarId=calendar_id, ruleId=rule_id).execute()
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
    
def main():
    """
    Decides what to do based on command line arguements, and dispatches to appropriate function

    required arguments
    - gccntml calendar id - the calendar you want to operate on
    - verb: add|remove
    - user: the user you want to share/remove from the calendar 
    """
    LEW_603 = 'gccnmtl.columbia.edu_2d31383235333138342d393935@resource.calendar.google.com'
    USER = 'jb2410'
    USER_EMAIL = "%s@columbia.edu" % USER
    
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
 
    list_users(service, LEW_603)

    #add_user(service, LEW_603, USER_EMAIL)
    remove_user(service, LEW_603, USER_EMAIL)

    list_users(service, LEW_603)


if __name__ == '__main__':
    main()
