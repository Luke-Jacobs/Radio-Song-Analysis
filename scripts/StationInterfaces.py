from scripts.SongClasses import *
import requests, json
from bs4 import BeautifulSoup
from http.client import RemoteDisconnected

"""
StationInterfaces
    These functions are the interface between a radio station and PlayedSongs. They scrape the station's website for 
    recently played songs and fill out the PlayedSong datatype according to the data that the website provides.
"""

# URLs of radio stations
AIR1_URL_RECENTLY_PLAYED = "https://www.air1.com/listen/recently-played"
KLOVE_URL_RECENTLY_PLAYED = "http://c.kloveair1.com/Services/Broadcast.asmx/GetRecentSongsLimit?siteId=1&limit=5&RemoveTags=true&format=json"
KISS_URL_RECENTLY_PLAYED = "https://1035kissfm.iheart.com/music/"
FISH_URL_RECENTLY_PLAYED = "'https://thefishoc.com/lastsongs'"


def getRecentlyPlayedAIR1() -> List[PlayedSong]:
    """Get a list of Songs played."""

    # Output
    songsProcessed = []

    # Get page
    try:
        page = requests.get(AIR1_URL_RECENTLY_PLAYED, timeout=5)
    except requests.exceptions.Timeout:
        print('[-] Timeout getting Air1 songs.')
        return []

    # Parse HTML
    try:
        parser = BeautifulSoup(page.text, 'html.parser')
        recently_played = parser.find('div', attrs={'class': 'recently-played-wrapper'})
        songsRaw = recently_played.findAll('div', attrs={'class': 'song-wrapper'})
    except AttributeError:
        return []

    # Iterate through the extracted HTML sections
    titles = []
    for song in songsRaw:
        data = [field.strip() for field in song.text.replace('\r', '').split('\n') if field.strip()]
        title, artist, album = data
        if title not in titles:
            # print('PlayedSong:\n\ttitle: %s\n\tartist: %s\n\talbum: %s\n' % (title, artist, album))
            titles.append(title)
            songsProcessed.append(PlayedSong(title, artist, album, 'Air1'))

    return songsProcessed
def writeSongsToCollectionAIR1(collection):
    try:
        moreSongs = getRecentlyPlayedAIR1()
        collection.add('Air1', moreSongs)
    except RemoteDisconnected:
        print('[-] Error: RemoteDisconnected from Air1, continuing anyways')


def getRecentlyPlayedKLOVE() -> List[PlayedSong]:
    # Output
    processedSongs = []

    # Get and parse JSON response
    try:
        jsonPage = requests.get(KLOVE_URL_RECENTLY_PLAYED)
    except requests.exceptions.Timeout:
        print('[-] Timeout getting KLOVE songs.')
        return []
    obj = json.loads(jsonPage.text[1:-2])

    # Get the fields from JSON
    data = obj.get('d')
    titles = []
    for song in data:
        title = song.get('Title')
        artist = song.get('Artist')
        album = song.get('Album')
        if title is None or title in titles:
            continue
        titles.append(title)
        timestamp = int(song.get('StartDate')[6:-2]) / 1000
        # print('PlayedSong:\n\ttitle: %s\n\tartist: %s\n\talbum: %s\ntimestamp: %d\n' %
        #       (title, artist, album, timestamp))
        processedSongs.append(PlayedSong(title, artist, album, 'KLOVE', timestamp=timestamp))

    return processedSongs
def writeSongsToCollectionKLOVE(collection):
    try:
        moreSongs = getRecentlyPlayedKLOVE()
        collection.add('KLOVE', moreSongs)
    except RemoteDisconnected:
        print('[-] Error: RemoteDisconnected from KLOVE, continuing anyways')


def getRecentlyPlayedKISS() -> List[PlayedSong]:
    # Get webpage
    page = None
    try:
        page = requests.get(KISS_URL_RECENTLY_PLAYED, timeout=5)
    except requests.exceptions.Timeout:
        print('[-] Timeout getting KISS songs.')

    # Parse HTML
    parser = BeautifulSoup(page.text, 'html.parser')
    songsHTML = parser.find('ol', attrs={'class': 'component-playlist-items on-demand-target thumbs-target'})
    if songsHTML is None:
        print('[-] Could not parse KISS recently played page.')
    songsHTML = songsHTML.findAll('li', attrs={'class': 'playlist-track-container ondemand-track'})

    # Iterate through songs
    output = []
    for songHTML in songsHTML:
        fields = songHTML.find('figcaption')
        titleHTML, artistHTML = fields.findAll('a')
        title = titleHTML.text
        artist = artistHTML.text
        dateStr = fields.find('time').attrs['datetime'][:-6]
        timestamp = datetime.strptime(dateStr, "%Y-%m-%d %H:%M:%S").timestamp()
        output.append(PlayedSong(title, artist, '?', 'KISS', timestamp=timestamp))
    return output
def writeSongsToCollectionKISS(collection):
    try:
        moreSongs = getRecentlyPlayedKISS()
        collection.add('KISS', moreSongs)
    except RemoteDisconnected:
        print('[-] Error: RemoteDisconnected from KISS, continuing anyways')


def getRecentlyPlayedFISH() -> List[PlayedSong]:
    # Get page
    page = None
    try:
        page = requests.get('https://thefishoc.com/lastsongs')
    except requests.exceptions.Timeout:
        print('[-] Timeout getting the FISH songs.')

    # Parse HTML
    parser = BeautifulSoup(page.text, 'html.parser')
    tableHTML = parser.find('table', attrs={'class': 'table-data'})

    # Iterate through the table rows
    songs = []
    for row in tableHTML.findAll('tr')[1:]:
        fields = [item.text for item in row.findAll('td')]
        title, artist, timeStr = fields

        # Timestamp from time on page
        if len(timeStr.split(':')[0]) == 1:
            timeStr = "0" + timeStr
        timestamp = datetime.now()
        dt = datetime.strptime(timeStr, '%I:%M %p')
        timestamp = timestamp.replace(minute=dt.minute, hour=dt.hour+3).timestamp()

        songs.append(PlayedSong(title, artist, '?', 'FISH', timestamp=timestamp))
        # print(title, timestamp)

    return songs
def writeSongsToCollectionFISH(collection):
    try:
        moreSongs = getRecentlyPlayedFISH()
        collection.add('FISH', moreSongs)
    except RemoteDisconnected:
        print('[-] Error: RemoteDisconnected from FISH, continuing anyways')
