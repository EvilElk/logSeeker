__author__ = 'elk'

import sys
import LogInterval
import re
from LogSeek import LogSeeker

USAGE = 'python log_filter \'start time\' \'time increment\'|\'fin time\' [filename]'
options = {'start': sys.argv[1], 'fin': sys.argv[2]}
datePattern = re.compile('(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})')
interval = None
if len(sys.argv) == 3:
    options['logfd'] = sys.stdin
elif len(sys.argv) == 4:
    options['file'] = sys.argv[3]
elif len(sys.argv) < 3:
    print(USAGE)

if datePattern.match(options['start']):
    if datePattern.match(options['fin']):
        interval = LogInterval.LogInterval(startTime=(options['start']), finTime=options['fin'])
    elif re.match('(\+|\-)\d+\S+', options['fin']):
        interval = LogInterval.LogInterval(startTime=(options['start']), deltaTime=options['fin'])
    else:
        print('err 2')
        sys.exit(2)
else:
    print('err 1')
    sys.exit(1)


inside = False


def writeToSTDOUT(line):
    try:
        sys.stdout.write(line)
    except IOError:
        sys.exit(0)

if 'file' in options:
    logFilter = LogSeeker(options['file'], interval.getStartTime(), interval.getFinTime())
    startOffset = logFilter.getStartOffset()
    finOffset = logFilter.getFinOffset()
    logFd = open(options['file'], 'rb')
    logFd.seek(startOffset)
    rSize = finOffset - startOffset
    while True:
        if rSize == 0:
            logFd.close()
            sys.exit(0)
        elif rSize < 1024:
            writeToSTDOUT(logFd.read(rSize))
            logFd.close()
            sys.exit(0)
        else:
            writeToSTDOUT(logFd.read(1024))
            rSize -= 1024
    inside = False
else:
    pass

for line in options['logfd']:
    matcher = datePattern.match(line)
    if matcher:
        currentDate = matcher.group(1)
        if interval.isStartPoint(currentDate) and not inside:
            writeToSTDOUT(line)
            inside = True
        elif interval.isFinPoint(currentDate) and inside:
            writeToSTDOUT(line)
            inside = False
            break
        elif inside:
            writeToSTDOUT(line)
    elif inside:
        writeToSTDOUT(line)
options['logfd'].close()
