=========
 Spazzer
=========

spazzer is a web application for sharing your music collection.

basically I wanted the ability to expose my music collection via http rather than file shares that I forget to turn off later etc....

jinzora2 really aggravates me, and so I wrote my own using jqueryui, sqlite, sqlalchemy, mutagen and pyramid. 

there's just enough ui to be able to drill down by artist to albums and either download track by track, or the album as a zip file.


there's also a paster command that can be used to periodically scan your collection and scrape the metadata. currently only looks for mp3 and flac, but can easily be extended to support whatever mutagen supports.





