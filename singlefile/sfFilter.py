__author__ = 'elk'


import datetime
import re
import sys
from math import log


class LogIntervalsException(Exception):
    pass


class IncorrectTimeFormatError(ValueError, LogIntervalsException):

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class TimeString():

    def __init__(self):
        self.__suffixMapH__ = {'ms': 1, 's': 1000, 'm': 60000, 'h': 3600000}
        self.__timeChunkRegEx = re.compile('(?P<timeCount>\d+\.?\d*)+(?P<timeSuffix>[msh]+)')
        self.__timeStringRegEx = re.compile('(\d+\s?[m,s,h]{1,2})\s*')

    def castTimeChunkBySuffix(self, timeWithSuffix):
        matcher = self.__timeChunkRegEx.search(timeWithSuffix)
        if matcher:
            return int(matcher.group('timeCount')) * self.__suffixMapH__[matcher.group('timeSuffix')]
        else:
            return None

    def castTimeString(self, timeString):
        resultedTimeChunk = 0
        matcher = self.__timeStringRegEx.findall(timeString)
        if matcher:
            for timeChunk in matcher:
                castedTime = self.castTimeChunkBySuffix(timeChunk.replace(" ", ""))
                if castedTime:
                    resultedTimeChunk += castedTime
        return resultedTimeChunk


class LogInterval():

    def __init__(self, startTime, finTime=None, deltaTime='+1m'):
        self.dateFormat = '%Y-%m-%d %H:%M:%S'
        self.datePattern = re.compile('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')
        self.isIntoInterval = False
        if deltaTime[0] == "+":
            self.deltaSign = 1
        elif deltaTime[0] == "-":
            self.deltaSign = -1
        deltaTime = deltaTime[1:]

        if self.datePattern.match(startTime):
            self.startTime = datetime.datetime.strptime(startTime, self.dateFormat)
        else:
            msg = "{time} not matches {timeFormat}".format(time=startTime, timeFormat=self.dateFormat)
            raise IncorrectTimeFormatError(msg)

        if not finTime:
            self.finTime = self.startTime + (self.deltaSign * datetime.timedelta(
                milliseconds=TimeString().castTimeString(deltaTime)))
        elif self.datePattern.match(finTime):
            self.finTime = datetime.datetime.strptime(finTime, self.dateFormat)
        else:
            msg = "{time} not matches {timeFormat}".format(time=finTime, timeFormat=self.dateFormat)
            raise IncorrectTimeFormatError(msg)

        if self.deltaSign == -1:
            self.startTime, self.finTime = (self.finTime, self.startTime)
        elif self.deltaSign == 1:
            pass
        else:
            raise ValueError('Incorrect delta sign')

    def getStartTime(self):
        return self.startTime.isoformat(' ').replace('.', ',')

    def getFinTime(self):
        return  self.finTime.isoformat(' ').replace('.', ',')

    def __str__(self):
        return 'start time: {start}\nfinish time: {finish}'.format(start=self.startTime, finish=self.finTime)

    def __del__(self):
        del self


class LogSeeker():

    def __init__(self, filePath, tStartDate, tFinDate):

        self.dateRe = re.compile(
            '(?P<dateTime>\d{4}-\d{2}-\d{2} (?P<hours>\d{2}):(?P<minutes>\d{2}):(?P<seconds>\d{2})).*'
        )

        tStartMatcher = self.dateRe.match(tStartDate)
        tFinMatcher = self.dateRe.match(tFinDate)
        if tStartMatcher and tFinMatcher:
            self.tStartH = tStartMatcher.group('hours')
            self.tStartM = tStartMatcher.group('minutes')
            self.tStartS = tStartMatcher.group('seconds')
            self.tFinH = tFinMatcher.group('hours')
            self.tFinM = tFinMatcher.group('minutes')
            self.tFinS = tFinMatcher.group('seconds')
        else:
            raise ValueError('inappropriate date format')
        self.currentOffset = 0
        self.tStartDate = tStartDate
        self.tFinDate = tFinDate
        self.logFd = open(filePath, 'rb')
        self.size, self.cLimit = self.__seekSize__(self.logFd)
        self.startOffset = self.__seekLog__(self.tStartH, self.tStartM, self.tStartS)
        self.finOffset = self.__seekLog__(self.tFinH, self.tFinM, self.tFinS)
        self.logFd.close()

    def __seekSize__(self, fileFd):
        start = fileFd.tell()
        fileFd.seek(0, 0)
        fileFd.seek(0, 2)
        size = fileFd.tell()
        limit = round(log(size, 2)) + 1.0
        fileFd.seek(0, start)
        return float(size), limit

    def __seekLog__(self, tH, tM, tS):
        logOffset = int(self.size / 2)
        bisect = logOffset
        cCounter = 0

        while True:
            if logOffset < 0:
                logOffset = 0
            self.logFd.seek(logOffset, 0)
            self.logFd.readline()
            cOffset = self.logFd.tell()
            ln = self.logFd.readline().decode()
            sMatcher = self.dateRe.match(ln)

            if bisect >= 2:
                bisect = int(bisect / 2)
            else:
                bisect = 1

            cCounter += 1

            if sMatcher:
                if (sMatcher.group('hours') == tH and
                   (sMatcher.group('minutes') == tM) and
                   (-1 <= (int(sMatcher.group('seconds')) - int(tS)) <= 0) or 
                   (cCounter >= self.cLimit) or 
                   (logOffset == 0 or logOffset == self.size)):
                    return cOffset
                if sMatcher.group('hours') > tH:
                    logOffset -= bisect
                elif sMatcher.group('hours') < tH:
                    logOffset += bisect
                elif sMatcher.group('hours') == tH and sMatcher.group('minutes') > tM:
                    logOffset -= bisect
                elif sMatcher.group('hours') == tH and sMatcher.group('minutes') < tM:
                    logOffset += bisect
                elif (sMatcher.group('hours') == tH and
                     (sMatcher.group('minutes') == tM) and
                     (int(sMatcher.group('seconds')) - int(tS) > 0)):
                    logOffset -= bisect
                elif (sMatcher.group('hours') == tH and
                     (sMatcher.group('minutes') == tM) and
                     (int(sMatcher.group('seconds')) - int(tS) < -1)):
                    logOffset += bisect
            else:
                while True:
                    curPos = self.logFd.tell()
                    nLine = self.logFd.readline().decode()
                    if self.dateRe.match(nLine):
                        logOffset = curPos
                        break
                    else:
                        pass

    def getStartOffset(self):
        return self.startOffset

    def getFinOffset(self):
        return self.finOffset


USAGE = 'python log_filter \'start time\' \'time increment\'|\'fin time\' [filename]'
options = {'start': sys.argv[1], 'fin': sys.argv[2]}
datePattern = re.compile('(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})')
interval = None
if len(sys.argv) != 4:
    print(USAGE)
elif len(sys.argv) == 4:
    options['file'] = sys.argv[3]
elif len(sys.argv) < 3:
    print(USAGE)

if datePattern.match(options['start']):
    if datePattern.match(options['fin']):
        interval = LogInterval(startTime=(options['start']), finTime=options['fin'])
    elif re.match('(\+|\-)\d+\S+', options['fin']):
        interval = LogInterval(startTime=(options['start']), deltaTime=options['fin'])
    else:
        print('err 2')
else:
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
