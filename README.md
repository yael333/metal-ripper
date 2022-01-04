# metal-ripper-discogs
A fork of metal-ripper that uses discogs as a database. Provide it a YouTube video of an album or EP and it will download it and, using Discogs data, split it into properly tagged and titled tracks.

## Dependencies and Requirements
* Python.
* These packages, using `pip`: youtube_dl, pydub, requests, eyed3, discogs_client.
* A Discogs account. 
* A Discogs [user key](https://www.discogs.com/settings/developers). You must enter this in the 'token' value in line 5 of the python file. This is needed to perform a "search" in the discogs API.

## Usage
`python metal-ripper-discogs.py [youtube album video]`.
Use the tag -m if you want to use your own Discogs page.
Use `python metal-ripper-discogs.py -h` for the full options.

## Note
Like the original program, this is meant to assist with the retreival and cataloguing of rare, out-of-print music using YouTube and Discogs. I do not encourage the use of this tool to violate copyright.
