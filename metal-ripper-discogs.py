#from __future__ import unicode_literals
import argparse, os, sys, shutil, youtube_dl, discogs_client, pydub, requests, eyed3, re

# discogs auth for search
token = ''
discogs = discogs_client.Client('metal-ripper/0.1', user_token=token)

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

DEFAULT_DIRECTORY = "."

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Rip some metal off youtube.')
    parser.add_argument('youtube_url',
                        metavar='youtube_url',
                        type=str,
                        help='the url to the youtube video')
    parser.add_argument('-m',
                    type=str,
                    help='the url to the discogs page')
    parser.add_argument('-d',
                type=str,
                help='the directory to download the album into')
    parser.add_argument('-k',
            action="store_true",
            help='whether to keep the unsplitted album file')
    args = parser.parse_args()

    youtube_url = args.youtube_url
    discogs_url = args.m
    directory = args.d if args.d else DEFAULT_DIRECTORY
    keep = args.k

    # if user doesn't supply discogs url, parse video information to try and find it ourselves
    if not discogs_url:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            video = info["entries"][0] if "entries" in info else info

            title  = video["title"]
            video_id = video["id"]
            split = title.split("-")
            if len(split) < 2:
                print("[</3] Video title isn't formatted right...")
                sys.exit()

            # split format: {artist} - {album}
            # remove strings in parentheses to avoid stuff like ({release_year})
            y_artist = re.sub("[\(\[].*?[\)\]]", "", split[0]).strip()
            y_album = re.sub("[\(\[].*?[\)\]]", "", "-".join(split[1:])).strip()

        print(f"[*] Looking for {y_artist} - {y_album} on Discogs")
        search_results = discogs.search(y_album, type='release', artist=y_artist)
        if not search_results:
            print("[</3] Couldn't find it, quitting......")
            sys.exit()

        album = search_results[0]

    # if user supplied discogs url, parse the url in order to find the album id
    else:
        url = discogs_url.split("/")[-1]
        master = discogs.master(url.split("-")[0])
        if not master:
            print("[</3] Couldn't find it, quitting......")
            sys.exit()
        album = master.main_release
    
    print(f"[<3] Found album {album.title} by {', '.join([artist.name for artist in album.artists])}\n\t Discogs id - {album.id}")
    
    # download youtube video
    print("[*] Starting download...")
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=True)
        video = info["entries"][0] if "entries" in info else info
        title  = video["title"].replace(":", "-")
        video_id = video["id"]
    print("[<3] Finished downloading!")

    # get the full album file name and load it
    vid_name = next(filter(lambda s: video_id in s, os.listdir(".")))
    vid_path = os.path.join(".", vid_name)
    file = pydub.AudioSegment.from_mp3(vid_path)

    # get the new album directory name and create it
    album_name = re.sub(r'[/\\:*?"<>|]', '', f"{', '.join([artist.name for artist in album.artists])} - {album.title} ({album.year})").strip()
    album_path = os.path.join(directory, album_name )
    os.makedirs(album_path, exist_ok=True)

    # download cover into the new album directory
    with open(os.path.join(album_path, "cover.jpg"), "wb") as f:
        f.write(requests.get(album.images[0]['uri']).content)


    # split the full album file into the seperate tracks
    # use tracks durations in order to find the correct splits
    current = 0
    trackNum = 1
    for track in album.tracklist:

        # check if track length is empty
        if track.duration == '':
            print("[</3] No track lengths on Discogs, exiting....")
            sys.exit()


        track_path = os.path.join(album_path, f"{str(track.position).zfill(2)} {track.title}.mp3")
        print(f"Track: {str(track.position).zfill(2)} {track.title}")
        duration = sum([a*b for a,b in zip([60,1], map(int,track.duration.split(':')))])*1000        
        end_track = int(current) + int(duration)
        file[current:end_track].export(track_path, format="mp3")
        current = end_track

        # write the metadata into the track
        metadata = eyed3.load(track_path)
        metadata.tag.title = track.title
        metadata.tag.artist = ', '.join([artist.name for artist in album.artists])
        metadata.tag.album = album.title
        metadata.tag.release_date = album.year
        metadata.tag.recording_date = album.year
        metadata.tag.track_num = trackNum
        trackNum += 1
        metadata.tag.save()

    # delete or move the full album file depending on args
    if keep:
        shutil.move(vid_path, os.path.join(album_path, f"{title}-{video_id}.mp3"))
    else:
        os.remove(vid_path)
