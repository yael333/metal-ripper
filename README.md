# metal-ripper-discogs
A fork of metal-ripper that uses discogs as a database. 

## About
Downloads a provided album from YouTube with metadata and track splits retrieved from Discogs.

## Dependencies and Requirements
* These packages, using `pip`: youtube_dl, pydub, requests, eyed3, discogs_client.
* A Discogs account. 
* A Discogs [user key](https://www.discogs.com/settings/developers). You must enter this in the 'token' value in line 5 of the python file. This is needed to perform a "search" in the discogs API.

## Usage
`python metal-ripper-discogs.py [youtube album video]`.
Use the tag -m if you want to use your own Discogs page.
Use `python metal-ripper-discogs.py -h` for the full options.

## Note
Like the original program, this is meant to assist with the retreival and cataloguing of rare, out-of-print music using YouTube and Discogs. I do not encourage the use of this tool to violate copyright.
