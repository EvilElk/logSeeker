__author__ = 'elk'

import re


class LogSeeker():

    def __init__(self, filePath, tStartDate, tFinDate):

        self.dateRe = re.compile(
            '(?P<dateTime>\d{4}-\d{2}-\d{2} (?P<hours>\d{2}):(?P<minutes>\d{2}):(?P<seconds>\d{2})).*'  #,(?P<msecs>\d+)).*'
        )

        tStartMatcher = self.dateRe.match(tStartDate)
        tFinMatcher = self.dateRe.match(tFinDate)
        if tStartMatcher and tFinMatcher:
            self.tStartH = tStartMatcher.group('hours')
            self.tStartM = tStartMatcher.group('minutes')
            self.tStartS = tStartMatcher.group('seconds')
            #self.tStartMs = tStartMatcher.group('msecs')
            self.tFinH = tFinMatcher.group('hours')
            self.tFinM = tFinMatcher.group('minutes')
            self.tFinS = tFinMatcher.group('seconds')
            #self.tFinMs = tFinMatcher.group('msecs')
        else:
            raise ValueError('inappropriate date format')
        self.currentOffset = 0
        self.tStartDate = tStartDate
        self.tFinDate = tFinDate
        self.logFd = open(filePath, 'rb')
        self.size = self.__seekSize__(self.logFd)
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
            if bisect >= 2:
                bisect /= 2
            else:
                bisect = 1

            sMatcher = self.dateRe.match(ln)

            if sMatcher:
                ###
                #print(bisect, logOffset)
                #print(tH, tM, tS)
                #print(sMatcher.group('hours'), sMatcher.group('minutes'), sMatcher.group('seconds'))
                #print()
                ###
                if (sMatcher.group('hours') == tH and
                   (sMatcher.group('minutes') == tM) and
                   (-1 <= (int(sMatcher.group('seconds')) - int(tS)) <= 0)or
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
                    nLine = self.logFd.readline()
                    if self.dateRe.match(nLine):
                        self.logFd.seek(curPos)
                        break
                    else:
                        pass

    def getStartOffset(self):
        return self.startOffset

    def getFinOffset(self):
        return self.finOffset

    # def getAvgStringSize(self):
    #     return  self.avgStringSize
