import pickle
import time
from typing import List, Tuple
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
from collections import Counter


"""
SongClasses
    This file contains classes which define the datatypes of PlayedSong (one song that was played on the radio) and
    SongList (an abstract list of PlayedSongs, ex. all the times 'Symphony' was played or all the songs played on Air1
    within an interval of time).
"""


class PlayedSong:

    def __init__(self, title, artist, album, stationName, timestamp=None):
        self.title = title
        self.artist = artist
        self.album = album
        self.stationName = stationName
        if timestamp:
            self.timestamp = timestamp
        else:
            self.timestamp = time.time()

    def isSameSong(self, other):
        thisDict = self.__dict__.copy()
        otherDict = other.__dict__.copy()
        thisDict['timestamp'] = otherDict['timestamp'] = None
        if thisDict == otherDict:
            return True
        else:
            return False

    def __eq__(self, other):
        return self.isSameSong(other)

    def __hash__(self):
        return hash(self.title + self.artist + self.album)

    def __str__(self):
        return '<%s>' % self.title

    def __repr__(self):
        return "<%s>" % self.title

    def save(self, filename: str):
        with open(filename, 'wb') as fp:
            pickle.dump(self, fp)

    @staticmethod
    def showList(playedSongList):
        strSongs = []
        for song in playedSongList:
            strSongs.append(str(song))
        return '[%s]' % ', '.join(strSongs)


class SongList:

    def __init__(self, songsToAdd: List[PlayedSong]=None):
        self.currentSongIter = 0
        self.songs = []  # type: List[PlayedSong]
        self.n = 0
        if songsToAdd is not None:
            self.add(songsToAdd)

    @staticmethod
    def fromLists(songLists: List['SongList']) -> 'SongList':
        obj = SongList()
        obj.addLists(songLists)
        return obj

    def __repr__(self):
        return '<SongList of %d song%s>' % (self.n, '' if self.n == 1 else 's')

    def __len__(self):
        return self.n

    def __iter__(self):
        return self

    def __next__(self):
        if self.currentSongIter < self.n:
            self.currentSongIter += 1
            return self.songs[self.currentSongIter - 1]
        raise StopIteration

    def showTimeCoverage(self):
        hours = [datetime.fromtimestamp(song.timestamp).hour for song in self.songs]
        plt.hist(hours, 24)
        plt.xlabel('Hour')
        plt.ylabel('Frequency')
        plt.show()

    def timesPlayed(self, song: PlayedSong) -> int:
        return self.songs.count(song)

    def showWhenPlayed(self, byHour: bool=False, byHourAndDay: bool=False, song: PlayedSong=None, title: str=None, artist: str=None):
        # Error checking
        if not (byHour ^ byHourAndDay):
            raise RuntimeError('Need either byHour or byHourAndDay selected')

        # Get data
        if song:
            timestamps = [int(eachSong.timestamp) for eachSong in self.songs if eachSong == song]
        elif title or artist:
            timestamps = [int(eachSong.timestamp) for eachSong in self.select(title=title, artist=artist)]
        else:
            raise RuntimeError('Argument error: pass song object or title and artist data to this function')

        # By hour and day
        if byHourAndDay:
            self._graphTimestampsByTimeOfDay(points=timestamps)

        # By hour
        else:
            adjustedPts = []
            points = Counter([datetime.fromtimestamp(timestamp).hour for timestamp in timestamps])
            for hour in range(24):
                adjustedPts.append(points[hour] / len(self.select(hour=hour)))  # Adjust for lack of coverage for some hours

            plt.bar(range(24), adjustedPts)
            plt.xlabel('Hour')
            plt.ylabel('Frequency')
            plt.title('When is "%s" played?' % (song.title if song else title))
            plt.show()

    def getCaptureIntervals(self) -> List[List[int]]:
        BUFFER_BETWEEN_SONGS = 12 * 60  # 12 minutes is the max time between 1st song start and 2nd song start

        # Our timestamps of all the songs in this list sorted in ascending order
        timestamps = sorted([song.timestamp for song in self.songs])  # type: List[float]

        intervals = []  # type: List[List[int, int]]
        currentInterval = []
        for i in range(len(timestamps)-1):
            # If a new interval is starting
            if not currentInterval:
                currentInterval = [int(timestamps[i]), int(timestamps[i])]  # At the beginning, start and end are the same
            # If an interval has been started and this timestamp is close to its current end
            elif currentInterval[1] + BUFFER_BETWEEN_SONGS > timestamps[i]:  # If the interval's acceptable addition buffer includes this point
                currentInterval[1] = int(timestamps[i])  # Add it to the interval
            # If we need to start a new interval
            else:
                intervals.append(currentInterval)
                currentInterval = []
        intervals.append(currentInterval)

        return intervals

    @staticmethod
    def _timeElapsedAcrossIntervals(intervals: List[List[int]]) -> int:
        timeElapsedSeconds = 0
        for interval in intervals:
            elapsed = interval[1] - interval[0]

            # Error check
            if elapsed < 0:
                raise RuntimeError('Interval is misconfigured')

            timeElapsedSeconds += elapsed
        return timeElapsedSeconds

    def getSongTimestamps(self):
        return [song.timestamp for song in self.songs]

    @staticmethod
    def _daysBetweenDates(date1: datetime, date2: datetime) -> int:
        # TODO Move this method
        A = date1.replace(hour=0, minute=0, second=0, microsecond=0)
        B = date2.replace(hour=0, minute=0, second=0, microsecond=0)
        return (B - A).days

    @staticmethod
    def _graphTimestampsByTimeOfDay(intervals: List[List[int]] = None, points: List[int] = None):
        # Error checks
        if not ((intervals is None) ^ (points is None)):
            raise RuntimeError('Need to input either a list of points or a list of intervals')

        if (points is not None) and (len(points) < 1):
            raise RuntimeError('Need at least one point to graph')

        if (intervals is not None) and (len(intervals) < 1):
            raise RuntimeError('Need at least one interval to graph')

        # Setup X axis
        plt.xlim(1, 25)
        hourLabels = ["%d %s" % (hour if hour < 13 else (hour - 12), "AM" if hour < 13 else "PM") for hour in range(1, 25)]
        plt.xticks(range(1,25), hourLabels, rotation=90)
        plt.xlabel('Hour', fontsize='large')

        # Setup Y axis
        startDay = datetime.fromtimestamp(intervals[0][0]) if intervals is not None else datetime.fromtimestamp(points[0])
        endDay = datetime.fromtimestamp(intervals[-1][1]) if intervals is not None else datetime.fromtimestamp(points[-1])
        nDays = SongList._daysBetweenDates(startDay, endDay)

        dayNames = []
        for i in range(nDays+1):
            thisDayName = (startDay + timedelta(days=i)).strftime('%b %d')
            dayNames.append(thisDayName)
        plt.yticks(range(nDays+1), dayNames[::-1])
        plt.ylabel('Day', fontsize='large')

        # Drawing functions
        def drawInterval(startCoord: Tuple[float, float], endCoord: Tuple[float, float]):
            # If interval spans just one day
            if startCoord[1] == endCoord[1]:
                plt.hlines(startCoord[1], startCoord[0], endCoord[0], lw=5, colors='b')

            # If interval spans multiple days
            else:
                drawInterval(startCoord, (24.0, startCoord[1]))  # Draw line across graph to the end of the line
                drawInterval((1, startCoord[1] - 1), endCoord)
        def drawPoint(coord: Tuple[float, float]):
            plt.scatter(coord[0], coord[1], marker='o', c='b', s=30)

        # Convert to coord system
        if intervals is not None:
            for i, interval in enumerate(intervals):
                ts = datetime.fromtimestamp(interval[0])
                ts2 = datetime.fromtimestamp(interval[1])
                startCoord = (ts.hour + 1 + ts.minute / 60, nDays - SongList._daysBetweenDates(startDay, ts))
                endCoord = (ts2.hour + 1 + ts.minute / 60, nDays - SongList._daysBetweenDates(startDay, ts2))
                drawInterval(startCoord, endCoord)
        elif points is not None:
            for point in points:
                ts = datetime.fromtimestamp(point)
                coord = (ts.hour + 1 + ts.minute / 60, nDays - SongList._daysBetweenDates(startDay, ts))
                drawPoint(coord)

        # Show
        title = 'Intervals of time this song list contains' if points is None else 'The play times of songs in this list'
        plt.title(title, fontsize='large')
        plt.ioff()
        plt.show()

    def showCaptureIntervals(self):
        ints = self.getCaptureIntervals()
        self._graphTimestampsByTimeOfDay(intervals=ints)

    def getCaptureLength(self) -> int:
        ints = self.getCaptureIntervals()
        return self._timeElapsedAcrossIntervals(ints)

    def select(self, title: str=None, artist: str=None, hour: int=None):
        return SongList([song for song in self.songs if
                (title is None or title == song.title) and
                (artist is None or artist == song.artist) and
                (hour is None or hour == datetime.fromtimestamp(song.timestamp).hour)])

    def getUniqueSongs(self) -> List[PlayedSong]:
        return list(set(self.songs))

    def getUniquenessIndex(self):
        return len(self.getUniqueSongs()) / self.n

    def getMostPopular(self, n: int=10):
        if n == 0:
            n = self.n
        indices = self.getPopularityIndices()[:n]
        return [index[0] for index in sorted(indices, reverse=True, key=lambda x:x[1])]

    def add(self, songs: List[PlayedSong]):
        self.songs += [song for song in songs if song is not None]
        self.n += len(songs)

    def addLists(self, songLists: List['SongList']):
        for songList in songLists:
            self.add(songList.songs)

    def getPopularityIndices(self) -> List[Tuple[PlayedSong, float]]:
        uniqueSongs = self.getUniqueSongs()
        output = []
        for unique in uniqueSongs:
            output.append((unique, self.songs.count(unique) / self.n))
        output.sort(key=lambda index: index[1], reverse=True)
        return output

    def getHoursAndSongs(self) -> List[Tuple[int, 'SongList']]:
        return [(hour, self.select(hour=hour)) for hour in range(24)]
