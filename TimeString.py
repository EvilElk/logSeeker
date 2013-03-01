__author__ = 'elk'

import re


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

if __name__ == '__main__':
    import doctest
    doctest.testmod()