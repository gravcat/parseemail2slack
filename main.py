#!/usr/bin/env python
#
# Very basic example of using Python 3 and IMAP to iterate over emails in a
# gmail folder/label.  This code is released into the public domain.
#
# This script is example code from this blog post:
# http://www.voidynullness.net/blog/2013/07/25/gmail-email-with-python-via-imap/
#
# This is an updated version of the original -- modified to work with Python 3.4.
#
import sys
import imaplib
import getpass
import email
import email.header
import datetime
import time
import json
from slacker import Slacker

with open('var/secrets.json') as secrets_file:
    secrets = json.load(secrets_file)

EMAIL_ACCOUNT = secrets['EMAIL_ACCOUNT']
# Use 'INBOX' to read inbox.  Note that whatever folder is specified, 
# after successfully running this script all emails in that folder 
# will be marked as read.
EMAIL_FOLDER = secrets['EMAIL_FOLDER']
EMAIL_PASSWORD = secrets['EMAIL_PASSWORD']
SLACK_TOKEN = secrets['SLACK_TOKEN']
SLACK_CHANNEL = secrets['SLACK_CHANNEL']
slack = Slacker(SLACK_TOKEN)

def process_mailbox(M):
    """
    Do something with emails messages in the folder.  
    For the sake of this example, print some headers.
    """

    rv, data = M.search(None, "ALL")
    if rv != 'OK':
        print("No messages found!")
        return

    for num in data[0].split():
        rv, data = M.fetch(num, '(RFC822)')
        if rv != 'OK':
            print("ERROR getting message", num)
            return

        # preserved for debugging
        msg = email.message_from_bytes(data[0][1])
        #hdr = email.header.make_header(email.header.decode_header(msg['Subject']))
        #subject = str(hdr)
        #print('Message %s: %s' % (num, subject))
        #print('Raw Date:', msg['Date'])
        
        # get body, perform a split to cut off email subscription info and other extraneous stuff
        body = msg.get_payload().split('--')[0].split('STOP')[0]
        print(body)
        print("Sending data to slack channel:", SLACK_CHANNEL, "at", datetime.datetime.now())
        slack.chat.post_message(SLACK_CHANNEL, body, "stockbot", ":satellite:")
        print("Marking message as deleted on mailbox")
        M.store(num, '+FLAGS', '\\Deleted')

M = imaplib.IMAP4_SSL('imap.gmail.com')

try:
    #rv, data = M.login(EMAIL_ACCOUNT, getpass.getpass())
    rv, data = M.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
except imaplib.IMAP4.error:
    print ("LOGIN FAILED!!! ")
    sys.exit(1)

print(rv, data)

while True:
    rv, mailboxes = M.list()
    #if rv == 'OK':
    #    print("Mailboxes:")
    #    print(mailboxes)

    rv, data = M.select(EMAIL_FOLDER)
    if rv == 'OK':
        #print("Processing mailbox...\n")
        process_mailbox(M)
        M.close()
    else:
        print("ERROR: Unable to open mailbox ", rv)

    #M.logout()
    time.sleep(180)