from scripts.StationInterfaces import *
from typing import List, Union, Dict
import os, time

"""
SongCollection
    This file contains classes and functions that collect PlayedSongs into a format that can be analyzed and graphed.
"""

class StationPlayCollection:

    def __init__(self):
        self.songLists = {}

    def __getstate__(self):
        return {'stationData': dict([(item[0], item[1].songs) for item in self.songLists.items()])}

    def __setstate__(self, state):
        self.songLists = {}
        for stationName in state['stationData']:
            self.songLists[stationName] = SongList(state['stationData'][stationName])

    def __getitem__(self, item) -> SongList:
        return self.songLists[item]

    def __setitem__(self, key: str, value: SongList):
        self.songLists[key] = value

    def add(self, stationName, songs: List[PlayedSong]) -> None:
        # Add first addition
        if self.songLists.get(stationName, None) is None:
            print('[%s] Starting collection with %d song%s' % (stationName, len(songs), '' if len(songs) == 1 else 's'))
            self.songLists[stationName] = SongList(songs)

        # Add to collection if not first addition
        else:
            lastFewSongs = self.songLists[stationName].songs[-6:]
            newSongs = getNewSongs(lastFewSongs, songs)
            print('[%s] Adding %d new song%s' % (stationName, len(newSongs), '' if len(newSongs) == 1 else 's'))
            self.songLists[stationName].add(newSongs)

    def save(self, timestamp: Union[None, int]=None):
        if timestamp is None:
            timestamp = int(time.time())
        with open('data/%d' % timestamp, 'wb+') as fp:
            pickle.dump(self, fp)

    def getStations(self) -> List[str]:
        return list(self.songLists.keys())

    def getAllSongs(self) -> SongList:
        return SongList([song for songList in self.songLists.values() for song in songList.songs])

    @staticmethod
    def restore(timestamp: int):
        filepath = 'data/%d' % timestamp
        if not os.path.exists(filepath):
            raise RuntimeError('Collection does not exist')
        with open(filepath, 'rb') as fp:
            restoredCollection = pickle.load(fp)
        return restoredCollection

    @staticmethod
    def getMostRecentSaved(folder='data/', output=True) -> 'StationPlayCollection':
        """Retrieve the most recently saved collection from a specified folder. Pickle files must be in timestamp format."""

        savedCollections = os.listdir(folder)
        newest = 0
        for collectionName in savedCollections:
            try:
                timestamp = int(collectionName)
                if timestamp > newest:
                    newest = timestamp
            except ValueError:
                continue
        if output: print('[i] Loading newest collection: %s' % datetime.fromtimestamp(newest).strftime('%b %d, %I:%M'))
        return StationPlayCollection.restore(newest)

    def showStats(self) -> None:
        stationNames = self.songLists.keys()
        print('[i] Station Stats:')
        for station in stationNames:
            print('\t%s - %d' % (station, len(self.songLists[station])))


class RadioAnalysis:

    def __init__(self, samples: Dict[str, SongList]):
        self.stationSamples = samples

    def showSongPopularityByHour(self, stationName: str=None) -> None:
        # Collect data
        if stationName is None:
            allSongs = SongList.fromLists(list(self.stationSamples.values()))
        else:
            allSongs = self.stationSamples[stationName]  # Extract one station's songs
        popularityIndex = dict(allSongs.getPopularityIndices())

        # Iterate over 24 hours
        avgPopularityByHour = []
        allHours = list(range(24))
        for hour in allHours:
            songsAtHour = allSongs.select(hour=hour)
            nSongsAtHour = len(songsAtHour)
            hourlyPopularityTotal = sum([popularityIndex[song] for song in songsAtHour.songs]) / nSongsAtHour
            avgPopularityByHour.append(hourlyPopularityTotal)

        plt.bar(allHours, avgPopularityByHour)
        plt.title('During which hour of the day is the most popular music played?')
        plt.xlabel('Hour')
        plt.ylabel('Average popularity index (sum of each song\'s total play frequency per hour)')
        plt.show()


def getNewSongs(laterSongs: List[PlayedSong], earlierSongs: List[PlayedSong]) -> Union[None, List[PlayedSong]]:
    """Combine two PlayedSong lists while respecting the older timestamp values in the laterSongs list."""

    # Get overlapping section
    overlap = set(laterSongs).intersection(set(earlierSongs))
    if overlap != set(earlierSongs[-len(overlap):]):
        print('[-] Error in stitching! Overlap: %s Later: %s Earlier: %s' %
              (PlayedSong.showList(overlap), PlayedSong.showList(laterSongs), PlayedSong.showList(earlierSongs)))

    if not overlap:
        print('[-] No overlap between songs!')
    for item in overlap:
        earlierSongs.remove(item)
    return earlierSongs


def collectSongsFromStations(collection: StationPlayCollection, wait: float=5*60):
    """This function continuously checks the websites of Air1 and K-LOVE for new songs."""

    while True:
        # Retrieve songs from Air1 and KLOVE
        for i in range(2):
            # Add more stations here <---
            writeSongsToCollectionAIR1(collection)
            writeSongsToCollectionKLOVE(collection)
            print('[i] Waiting %d minutes' % (wait / 60))
            time.sleep(wait)

        # Every two additions, save collection
        collection.showStats()
        print('[i] Saving collection (%s)...' % (datetime.now().strftime("%I:%M")), end='')
        collection.save()
        print('saved!')

