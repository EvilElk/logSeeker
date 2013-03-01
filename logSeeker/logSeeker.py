__author__ = 'elk'

import re
import datetime
import sys


class TimeString():

    def __init__(self):
        """
        initiate cast map and regexp to parse time string
        """
        self.__suffixMapH__ = {'ms': 1, 's': 1000, 'm': 60000, 'h': 3600000}
        self.__timeChunkRegEx = re.compile('(?P<timeCount>\d+\.?\d*)+(?P<timeSuffix>[msh]+)')
        self.__timeStringRegEx = re.compile('(\d+\s?[m,s,h]{1,2})\s*')

    def castTimeChunkBySuffix(self, timeWithSuffix):
        """
        returns time in milliseconds from time string with suffix:

        >>> TimeString().castTimeChunkBySuffix('10ms')
        10

        >>> TimeString().castTimeChunkBySuffix('10s')
        10000

        """
        matcher = self.__timeChunkRegEx.search(timeWithSuffix)
        if matcher:
            return int(matcher.group('timeCount')) * self.__suffixMapH__[matcher.group('timeSuffix')]
        else:
            return None

    def castTimeString(self, timeString):

        """
        cast time string to milliseconds:

        >>> TimeString().castTimeString('10m 11s 13ms')
        611013

        >>> TimeString().castTimeString('10m')
        600000

        >>> TimeString().castTimeString('11s 13ms')
        11013

        :param timeString:
        :return:
        """
        resultedTimeChunk = 0
        matcher = self.__timeStringRegEx.findall(timeString)
        if matcher:
            for timeChunk in matcher:
                castedTime = self.castTimeChunkBySuffix(timeChunk.replace(" ", ""))
                if castedTime:
                    resultedTimeChunk += castedTime
        return resultedTimeChunk

    def convertTimeChunkToTimeString(self, chunk, suffix):
        if chunk < 0:
            raise ValueError('time chunk cannot be negative value')
        else:
            pass
            #TODO get cast algorithm from "dive int o python3"
        pass


class LogIntervalsException(Exception):
    pass


class IncorrectTimeFormatError(ValueError, LogIntervalsException):

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class LogInterval():

    def __init__(self, startTime, finTime=None, deltaTime='+1m'):

        """
        Creates LogInterval object to determine start time and fin time in logfile
        :param startTime: log start point marker
        :param finTime: log fin point marker
        :param deltaTime: allows to set interval in +10m manner
        def __init__(self,startTime,finTime=None,deltaTime='+1m'):
        startTime and finTime format is iso format '%Y-%m-%d %H:%M:%S,%f', i.e. 2013-01-22 19:36:42,158
        """
        self.dateFormat = '%Y-%m-%d %H:%M:%S,%f'
        self.datePattern = re.compile('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+')
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

    def isStartPoint(self, currentTimeStamp):

        """
        test function - determines start of the interval
        :param currentTimeStamp: String representing date and time from log
        :return: Boolean
        :raise: IncorrectTimeFormatError if IncorrectTimeFormatError doesn't correspond to iso format

        >>> interval = LogInterval('2013-01-22 19:36:42,158', deltaTime='-15m')

        >>> interval.isStartPoint('2013-01-22 19:30:42,158')
        True

        >>> interval.isStartPoint('2013-01-22 19:38:42,158')
        False



        """
        if self.datePattern.match(currentTimeStamp):
            if currentTimeStamp >= self.startTime.isoformat(sep=' ').replace('.', ',') and not self.isIntoInterval:
                self.isIntoInterval = True
                return True
            else:
                return False
        else:
            msg = "{time} not matches {timeFormat}".format(time=currentTimeStamp, timeFormat=self.dateFormat)
            raise IncorrectTimeFormatError(msg)

    def isFinPoint(self, currentTimeStamp):

        """
        test function - determines end of the interval
        :param currentTimeStamp: string representing date and time from log
        :return: Boolean
        :raise: IncorrectTimeFormatError if IncorrectTimeFormatError doesn't correspond to iso format

        >>> interval = LogInterval('2013-01-22 19:36:42,158', deltaTime='-15m')

        >>> interval.isStartPoint('2013-01-22 19:30:42,158')
        True

        >>> interval.isFinPoint('2013-01-22 19:36:42,159')
        True

        >>> interval.isFinPoint('2013-01-22 19:39:42,158')
        False


        """
        if self.datePattern.match(currentTimeStamp):
            if currentTimeStamp >= self.finTime.isoformat(sep=' ').replace('.', ',') and self.isIntoInterval:
                self.isIntoInterval = False
                return True
            else:
                return False
            pass
        else:
            msg = "{time} not matches {timeFormat}".format(time=currentTimeStamp, timeFormat=self.dateFormat)
            raise IncorrectTimeFormatError(msg)

    def getStartTime(self):
        return self.startTime.isoformat(' ').replace('.', ',')

    def getFinTime(self):
        return  self.finTime.isoformat(' ').replace('.', ',')

    def __str__(self):

        """
        string representation for object
        useful with print(object)
        :return: String
        """
        return 'start time: {start}\nfinish time: {finish}'.format(start=self.startTime, finish=self.finTime)

    def __del__(self):
        del self


class LogSeeker():

    def __init__(self, filePath, tStartDate, tFinDate):

        self.dateRe = re.compile(
            '(?P<dateTime>\d{4}-\d{2}-\d{2} (?P<hours>\d{2}):(?P<minutes>\d{2}):(?P<seconds>\d{2}),(?P<msecs>\d+)).*'
        )

        tStartMatcher = self.dateRe.match(tStartDate)
        tFinMatcher = self.dateRe.match(tFinDate)
        if tStartMatcher and tFinMatcher:
            self.tStartH = tStartMatcher.group('hours')
            self.tStartM = tStartMatcher.group('minutes')
            self.tStartS = tStartMatcher.group('seconds')
            self.tStartMs = tStartMatcher.group('msecs')
            self.tFinH = tFinMatcher.group('hours')
            self.tFinM = tFinMatcher.group('minutes')
            self.tFinS = tFinMatcher.group('seconds')
            self.tFinMs = tFinMatcher.group('msecs')
        else:
            raise ValueError('inappropriate date format')
        self.currentOffset = 0
        self.tStartDate = tStartDate
        self.tFinDate = tFinDate
        self.logFd = open(filePath, 'rb')
        self.size = self.__seekSize__(self.logFd)
        #self.avgStringSize = 0
        self.startOffset = self.__seekLog__(self.tStartH, self.tStartM, self.tStartS)
        self.finOffset = self.__seekLog__(self.tFinH, self.tFinM, self.tFinS)
        self.logFd.close()

    def __seekSize__(self, fileFd):
        start = fileFd.tell()
        fileFd.seek(0, 0)
        fileFd.seek(0, 2)
        size = fileFd.tell()
        fileFd.seek(0, start)
        return size

    def __seekLog__(self, tH, tM, tS):
        logOffset = int(self.size / 2)
        bisect = logOffset
        while True:
            if logOffset < 0:
                logOffset = 0
            self.logFd.seek(logOffset, 0)
            self.logFd.readline()
            cOffset = self.logFd.tell()
            ln = self.logFd.readline()
            #sCount = 0
            #self.avgStringSize = (self.avgStringSize + self.logFd.tell() - cOffset) / (sCount + 1)
            if bisect >= 2:
                bisect /= 2
            else:
                bisect = 1

            sMatcher = self.dateRe.match(ln)

            if sMatcher:
                if (sMatcher.group('hours') == tH and
                        (sMatcher.group('minutes') == tM) and
                        (-59 < (int(sMatcher.group('seconds')) - int(tS)) <= 0)or
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
            else:
                while True:
                    curPos = self.logFd.tell()
                    nLine = self.logFd.readline()
                    if self.dateRe.match(nLine):
                        self.logFd.seek(curPos)
                        break
                    else:
                        pass

    def getStartOffset(self):
        return self.startOffset

        # def getFinOffset(self):
        #     return self.finOffset

        # def getAvgStringSize(self):
        #     return  self.avgStringSize


options = {'start': sys.argv[1], 'fin': sys.argv[2]}

datePattern = re.compile('(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+).*')
interval = None
if len(sys.argv) < 4:
    options['logfd'] = sys.stdin
else:
    options['file'] = sys.argv[3]


if datePattern.match(options['start']):
    if datePattern.match(options['fin']):
        interval = LogInterval(startTime=options['start'], finTime=options['fin'])
    elif re.match('(\+|\-)\d+\S+', options['fin']):
        interval = LogInterval(startTime=options['start'], deltaTime=options['fin'])
    else:
        print('err 2')
        sys.exit(1)
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
    print(interval.getStartTime(), interval.getFinTime())
    logFilter = LogSeeker(options['file'], interval.getStartTime(), interval.getFinTime())
    startOffset = logFilter.getStartOffset()
    options['logfd'] = open(options['file'], 'rb')
    options['logfd'].seek(startOffset)
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
