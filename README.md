# Radio Song Analysis

### Contents

- Inspiration
- Setup
- Results
- Project Structure

### Inspiration

This project was inspired by the stereotype that Christian radio stations are in desperate lack of variety. (https://babylonbee.com/news/report-air1-still-top-alternative-good-music is a good example.) I have also noticed that I know almost every song that comes on Air1, which is making me a little sick of the station. But is Air1's lack of variety to blame, or should I blame my over-attention to the music? Am I just listening at the wrong times, or does the variety of music change at certain hours of the day? How does Air1 compare to one of its competitors, KLOVE? The answers to these questions are too infeasible for normal people to find, but I'm not normal: I'm a programmer.

So instead of immediately dismissing Air1 as mindnumbingly repetitive, I will let the data do the judging. Will the stats find Air1 innocent or guilty??? (Spoiler alert: both Air1 *and* KLOVE are **very guilty**.)

### Setup

I figured out that the easiest way to programmatically retrieve the last few songs played on a radio station is through its website. Almost every radio station has a page that lists the last few songs that were played on the radio, so I made some functions to GET and parse that data. To automate this data collection I added a feature to my script where the user can tell the computer to wait a certain amount of time between requests (I decided the best is 5 minutes), and the program will disappear into the background silently grabbing data from the stations they added.

After having accumulated a few days worth of song data, you can also use the same script (`RadioSongAnalysis.py`) to analyze the data. 

(At the moment I have not implemented a command line interface to the program, so users have to write their own Python code using my methods if they want to analyze anything.)

### Numerical Results

I observed the songs played by KLOVE and Air1 over the course of about 10 days to get a decent dataset of songs (around 3500 for each station). Here is what I found:

- KLOVE and Air1 play almost the exact same amount of songs per unit time. TODO
- KLOVE has a larger music collection (the station plays more distinct songs). TODO
- Of the top 40 songs most frequently played at each station, only 7 songs were common to both lists. This means that the songs that the two stations choose to play most frequently are different. You would think that there would be much more overlap between these lists, because the stations would ideally play the newest, most popular songs among people who listen to Contemporary Christian Music (CCM). Surprisingly, their most frequent plays are almost entirely different. This might mean that Christian radio stations play music that is not representative of the  tastes of the CCM audience. (Who knew, right?!)

### Graphical Results

Here is a graph of the times where the song "Symphony" by the artist "Switch" was played on Air1:

![](results/Symphony Play Times (Air1).png)

As you can see, Air1 *loves* to play this song, to my pain. This graph confirms my theory that Air1 plays this song way too much. It's not that I'm choosing the wrong times to listen to the station (or that I'm plain crazy), but that Air1 has a problem.

There are a few points on the graph where the song is "played" almost back-to-back. These are errors in my song-stitching algorithm. Sometimes when the script checks the Air1 recently-added page, it adds a duplicate song. However, these errors are easy to spot.



### Project Structure

```
- scripts
  - SongClasses.py
  - SongCollection.py
  - StationInterfaces.py
- RadioSongAnalysis.py
```

- `RadioSongAnalysis` is the command line interface for this project. It runs in two modes of operation: `collect`, which collects data and can run in the background, and `show`, a command to show statistics about the data.
-  `SongClasses` contains classes which define the datatypes of `PlayedSong` - representing a song that was played on the radio at a certain point in time - and `SongList` - an abstract list of PlayedSongs. This could be all the times 'Symphony' was played or, say, all the songs played on Air1 within an interval of time.
- `SongCollection` contains classes and functions that collect played songs into a format that can be analyzed and graphed. The most important class is `StationPlayCollection`, which contains the list of `PlayedSong`s from all your stations.
- `StationInterfaces` is a collection of functions that act as the interface between a radio station and played songs. They scrape the station's website for recently played songs and fill out the PlayedSong datatype according to the data that the website provides. If you want to add a station to the program, this is where you put the function to scrape its website.

