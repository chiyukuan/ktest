#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

import time
import smtplib
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from kd.util.logger       import getLogger

logger = getLogger(__name__)

class KEmail(object):

    def __init__(self):
        pass

    @staticmethod
    def sendFile(fname, emailTo=[], emailFrom='ray@kodiakdata.com',
            subject='Test Result', stmpSvr='localhost', infos=None):
        if emailTo is None:
            emailTo = []
        date = time.ctime(time.time())
        emailTo.append('ray@kodiakdata.com')

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = emailFrom
        msg['To'] = ';'.join(emailTo)


        text = ""
        html  = '<html><head></head><body><font face="Courier New, Courier, monospace">'
        html += '<style type="text/css" media="screen"> td { padding: 5px 10px; } </style>'

        if infos is not None:
            for pair in infos:
                html += '<h1>%s</h1><ul style="list-style-type:square">' % pair[0]
                for item in pair[1]:
                    html += '<li>%s</li>' %  item
                html += '</ul>'

        html += "<h1>Test Case Detail</h1>"
        iFile = open(fname, 'r')
        html += '<ol type="1">'
        for line in iFile.readlines():
            text += line
            if line.startswith("* "):
                line = re.sub(r"\* (.*) '(.*)' return ", r"\1 '<b>\2</b>' return ", line, 1)
                if   " return OK" in line or " return CONTINU" in line:
                    html += '<li>%s</li>' % line
                elif " return WARNING" in line:
                    html += '<li><font color="DarkOrange">%s</font></li>' % line
                else:
                    html += '<li><font color="red">%s</font></li>' % line
            else:
                html += line + "<br>"
        iFile.close()
        html += '</ul>'
        html += "</font></body></html>"

        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        
        msg.attach(part1)
        msg.attach(part2)
        try:
            server = smtplib.SMTP(stmpSvr) # connect, no login step
            #server.starttls()
            #server.login('ray@kodiakdata.com', 'd3v3l0p@')
        except:
            logger.error('Failed to connect the email server, %s', stmpSvr)
            return False
        failed = server.sendmail(emailFrom, emailTo, msg.as_string())
        server.quit() 
        if failed: # smtplib may raise exceptions
            logger.error("Failed to send mail due to %s", failed)
            return False
        else:
            logger.info("Send '%s' email to %s", subject, emailTo) 
            return True

if __name__ == '__main__':
    ''' Test this module here '''

    print KEmail.sendFile('/home/rkuan/result.log')

