#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from kd.util.logger import getLogger

logger = getLogger(__name__)

class StatsColloct(object):

    def __init__(self, colFields):
        self.colFields = colFields
        self.feedSets  = []
        self.tbl       = None
        self.genValue  = False

    def newFeed(self, key, feed):
        self.genValue = False
        done = False
        for feedSet in self.feedSets:
            if key == feedSet[0]:
                feedSet.append(feed)
                done = True
        if not done:
            self.feedSets.append( [key, feed] )

    def _genTbl(self):
        for feedSet in self.feedSets:
            row = [feedSet[0]]
            row.extend(feedSet[1])
            self.tbl.append(row)
        return

    def htmlTbl(self):
        if not self.genValue:
            self.tbl = []
            self._genTbl()
            self.genValue = True

        tbl = '<br><table><tr style="background: DarkCyan; color: white;">'

        for field in self.colFields:
            tbl += '<th>%s</th>' % field

        tbl += '</tr>'

        evenRow = False
        for row in self.tbl:
            if evenRow:
                tbl += '<tr style="background: Lavender;">'
                evenRow = False
            else:
                tbl += '<tr">'
                evenRow = True

            for idx in range(len(row)):
                col = row[idx]
                if idx == 0:
                    tag = 'td'
                else:
                    tag = 'td'

                if isinstance(col, basestring):
                    if col.endswith(' K') or col.endswith(' M') or \
                       col.endswith(' ms') or col.endswith(' us'):
                        tbl += "<%s align='right'>%s</%s>" % (tag, col, tag)
                    else:
                        tbl += "<%s align='left'>%s</%s>" % (tag, col, tag)
                elif isinstance(col, int):
                    tbl += "<%s align='right'>%d</%s>" % (tag, col, tag)
                else:
                    tbl += "<%s align='right'>%.2f</%s>" % (tag, col, tag)
            tbl += '</tr>'
        tbl += '</table>'
        return tbl

    def __str__(self):
        return self.htmlTbl()

    __repr__ = __str__

if __name__ == '__main__':
    ''' Test this module here '''
    stats = StatsColloct(['Name', 'Val-1', 'Val-2'])
    stats.newFeed('Test1', [100, 101])
    stats.newFeed('Test2', [200, 201])
    stats.newFeed('Test3', [300, 301])

    print stats



