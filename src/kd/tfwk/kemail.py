#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

import smtplib
import logging
from operator             import add
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText

from test_case      import TestCase
from test_set       import TestSet
from kd.util.logger import getLogger
from kd.util.rc_msg import RC, RcMsg


logger = getLogger(__name__)

class KEmail(object):

    def __init__(self):
        self.emailFrom   = 'ray@kodiakdata.com'
        self.stmpSvr     = 'localhost'

        self.text        = ''
        self.html        = ''
        self.dTbl        = ''
        self.dTblEvenRow = True
        self.cRsltKey    = None
        self.cRsltCnt    = 0
        self.cRslt       = None
        self.tRslts      = []

    def addTCase(self, key, tcase):
        ws = tcase.fName.split(":")
        # record test result
        if self.cRsltKey != key:

            self.dTbl += '<tr style="background: SeaGreen; color: white;">' \
                    '<td colspan="6">%s: %s</td></tr>\n' % (ws[0], tcase.desc)
            
            self.cRsltKey = key
            self.cRslt    = [ tcase.desc, 0, 0, 0, 0, 0, 0 ]
            self.cRsltCnt = 1
            self.tRslts.append( self.cRslt )
        else:
            self.cRsltCnt += 1

        self.cRslt[1] += 1
        self.cRslt[6] += (tcase.endTime - tcase.startTime)
        if tcase.needSkip():
            color = "gray"
            self.cRslt[4] += 1
        elif tcase.rcMsg.rc == RC.WARNING:
            color = "DarkOrange"
            self.cRslt[3] += 1
        elif tcase.rcMsg.rc == RC.OK:
            color = "black"
            self.cRslt[2] += 1
        else:
            color = "red"
            self.cRslt[5] += 1

        # print detail table
        if not tcase.needNotify():
            return

        if self.dTblEvenRow:
            self.dTbl       += '<tr style="background: WhiteSmoke;">'
            self.dTblEvenRow = False
        else:
            self.dTbl       += "<tr>"
            self.dTblEvenRow = True

        self.dTbl += '<td><font color="%s">%s</font></td>' % ("black", self.cRsltCnt - 1)
        self.dTbl += '<td><font color="%s"><b>%s</b></font></td>' % (
                        color, tcase.desc.replace("(", "<br>&nbsp;&nbsp;("))
        self.dTbl += '<td><font color="%s">%s</font></td>' % (color, tcase.rcMsg)
        self.dTbl += '<td><font color="%s">%d/%d</font></td>' % (
                        "black",tcase.rIdx, len(tcase.steps) + 2)
        if bool(tcase.notices):
            self.dTbl += '<td><ul style="list-style-type:square">'
            for notice in tcase.notices:
                pStr = notice
                if notice.isPre:
                    self.dTbl += '<pre>%s</pre>\n' % (pStr)
                elif not notice.listItem:
                    self.dTbl += '</ul>%s<ul style="list-style-type:square">' % (notice.desc)
                elif notice.level <= logging.INFO:
                    self.dTbl += '<li>%s</li>\n' % (pStr)
                elif notice.level <= logging.WARNING:
                    self.dTbl += '<li><font color="%s">%s</font></li>\n' % ( "DarkOrange", pStr)
                else:
                    self.dTbl += '<li><font color="%s">%s</font></li>\n' % ( "red", pStr)
            self.dTbl += '</ul></td>\n'
        else:
            self.dTbl += '<td><font color="%s"></font></td>\n' % ("black")
        self.dTbl += '<td><font color="%s">%s</font></td>' % ("black", tcase.timeDuration())
        self.dTbl += '</tr>\n'


    def _getInfoSec(self):
        while True:
            infos = TestCase.getParamEval('email.info')
            bench = TestCase.getParamExactEval('bench')
            if infos is None and bench is None:
                break

            if bench is not None:
                if isinstance( bench,  basestring):
                    bench = [bench]

                if infos is None:
                    infos = ['Test Bench', bench['desc']]
                else:
                    infos.append( ['Test Bench', bench['desc']] )

            for info in infos:
                self.html += '<h1>%s</h1><ul style="list-style-type:square">' % info[0]
                for item in info[1]:
                    self.html += '<li>%s</li>' %  item
                self.html += '</ul>\n'
            break

    def _getSmrySec(self):
        evenRow = False
        total   = ['Total', 0, 0, 0, 0, 0, 0]

        tbl = '<h1>Test Case Summary</h1>' \
              '<table style="font-family: Helvetica Neue, Helvetica, sans-serif">' \
              '<tr style="background: SteelBlue; color: white;">' \
              '<td>Feature</td>' \
              '<td>Test Case #</td>' \
              '<td>OK #</td>' \
              '<td>Warning #</td>' \
              '<td>Skip #</td>' \
              '<td>Error #</td>' \
              '<td>Run Time (min)</td>' \
              '</tr>\n'

        for rslt in self.tRslts:
            if evenRow:
                tbl += '<tr style="background: WhiteSmoke;">'
                evenRow = False
            else:
                tbl += "<tr>"
                evenRow = True

            tbl += '<td>%s</td>' % rslt[0]
            tbl += '<td style="text-align: right;">%d</td>' % rslt[1]
            tbl += '<td style="text-align: right;">%d</td>' % rslt[2]
            tbl += '<td style="text-align: right; color: %s">%d</td>' % (
                    "black" if rslt[3] == 0 else "DarkOrange", rslt[3])
            tbl += '<td style="text-align: right; color: %s">%d</td>' % (
                    "black" if rslt[4] == 0 else "DimGray", rslt[4])
            tbl += '<td style="text-align: right; color: %s">%d</td>' % (
                    "black" if rslt[5] == 0 else "red", rslt[5])
            tbl += '<td style="text-align: right;">%d min</td>' % (rslt[6] / 60)
            tbl += '</tr>\n'
            total = map(add, rslt, total)


        tbl += '<tr style="background: SeaGreen;color: white;">'
        tbl += '<td>%s</td>' % "Total"
        tbl += '<td style="text-align: right;">%d</td>' % total[1]
        tbl += '<td style="text-align: right;">%d</td>' % total[2]
        tbl += '<td style="text-align: right; color: %s">%d</td>' % (
                "black" if total[3] == 0 else "DarkOrange", total[3])
        tbl += '<td style="text-align: right; color: %s">%d</td>' % (
                "black" if total[4] == 0 else "DimGray", total[4])
        tbl += '<td style="text-align: right; color: %s">%d</td>' % (
                "black" if total[5] == 0 else "red", total[5])
        tbl += '<td style="text-align: right;">%d min</td>' % (total[6] / 60)
        tbl += '</tr></table>\n'

        self.html += tbl

    def _genHtmlCtn(self):
        self.html    = '<html><head></head><body><font '\
                       'face="Courier New, Courier, monospace">' \
                       '<style type="text/css" media="screen"> '\
                       'td { padding: 5px 10px; vertical-align: top;} '\
                       '</style>'
        self._getInfoSec()
        self._getSmrySec()

        self.html += '<h1>Test Case Detail</h1>' \
                     '<table style="font-family: Helvetica Neue, Helvetica, sans-serif">' \
                     '<tr style="background: SteelBlue; color: white;">' \
                     '<td>IDX</td>' \
                     '<td>Description</td>' \
                     '<td>Return</td>' \
                     '<td>Run Steps</td>' \
                     '<td>Notes</td>' \
                     '<td>Run Time</td>' \
                     '</tr>\n%s</table>' % (self.dTbl)

        self.html += "</font></body></html>"


    def _getTextCtn(self):
        self.text = 'Test Result only available at html format'

    def send(self, ignoreSend):
        self._genHtmlCtn()
        self._getTextCtn()
        notifyFile = open("%s/notify.html" % TestCase.getWorkDir(), 'w')
        notifyFile.write(self.html)
        notifyFile.close()

        if ignoreSend or not TestCase.checkParam('email.enable', 'True'):
            logger.info("No email notification")
            return

        if TestCase.isForceSkip():
            emailTo = self.emailFrom
        else:
            emailTo = TestCase.getParamEval('email.toList')

        if emailTo is None:
            emailTo = [ self.emailFrom ]
        else:
            emailTo.append( self.emailFrom )

        msg = MIMEMultipart('alternative')
        msg['Subject'] = "[Test Result] %s" % TestCase.testCtx.desc
        msg['From']    = self.emailFrom
        msg['To']      = ';'.join(emailTo)
        
        part1 = MIMEText(self.text, 'plain')
        part2 = MIMEText(self.html, 'html')
        
        msg.attach(part1)
        msg.attach(part2)

        try:
            server = smtplib.SMTP(self.stmpSvr) # connect, no login step
        except:
            logger.error('Failed to connect the email server, %s',
                         self.stmpSvr)
            return False
        failed = server.sendmail(self.emailFrom, emailTo, msg.as_string())
        server.quit() 
        if failed: # smtplib may raise exceptions
            logger.error("Failed to send mail due to %s", failed)
            return False
        else:
            logger.info("Send test result email to %s", emailTo) 
            return True


