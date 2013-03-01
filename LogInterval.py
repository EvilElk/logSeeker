__author__ = 'elk'

import datetime
import TimeString
import re


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
        self.dateFormat = '%Y-%m-%d %H:%M:%S'  #,%f'
        self.datePattern = re.compile('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')  #,\d+')
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
                milliseconds=TimeString.TimeString().castTimeString(deltaTime)))
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


if __name__ == '__main__':
    import doctest
    doctest.testmod()