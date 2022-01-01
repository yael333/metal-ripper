from __future__ import unicode_literals
import argparse, os, shutil, youtube_dl, metallum, pydub, requests, eyed3, re

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
                    help='the url to the metal archives page')
    parser.add_argument('-d',
                type=str,
                help='the directory to download the album into')
    parser.add_argument('-k',
            action="store_true",
            help='whether to keep the unsplitted album file')
    args = parser.parse_args()

    youtube_url = args.youtube_url
    metal_url = args.m
    directory = args.d if args.d else DEFAULT_DIRECTORY
    keep = args.k

    # if user doesn't supply metal archives url, parse video information to try and find it ourselves
    if not metal_url:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            video = info["entries"][0] if "entries" in info else info

            title  = video["title"]
            video_id = video["id"]
            split = title.split("-")
            if len(split) < 2:
                print("[</3] Video title isn't formatted right...")
                exit()

            # split format: {artist} - {album}
            # remove strings in parentheses to avoid stuff like ({release_year})
            y_artist = re.sub("[\(\[].*?[\)\]]", "", split[0]).strip()
            y_album = re.sub("[\(\[].*?[\)\]]", "", "-".join(split[1:])).strip()

        print(f"[*] Looking for {y_artist} - {y_album} on the Metal Archives")
        search_results = metallum.album_search(y_album, band=y_artist, strict=False)

        if not search_results:
            print("[</3] Couldn't find it, quitting......")
            exit()
        album = search_results[0].get()
        artists = album.bands

    # if user supplied metal archives url, parse the url in order to find the album id
    else:
        album = metallum.album_for_id(metal_url.split("/")[-1])
        artists = album.bands
    
    print(f"[<3] Found album {album.title} by {', '.join([artist.name for artist in artists])}\n\t URL - https://www.metal-archives.com/{album.url}")
    
    # download youtube video
    print("[*] Starting download...")
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=True)
        video = info["entries"][0] if "entries" in info else info
        title  = video["title"].replace(":", "-")
        video_id = video["id"]
    print("[<3] Finished downloading!")

    # get the full album file name and load it
    vid_name = re.sub(r'[/\\:*?"<>|]', '', f"{title}-{video_id}.mp3")
    vid_path = os.path.join(".", vid_name)
    file = pydub.AudioSegment.from_mp3(vid_path)

    # get the new album directory name and create it
    album_name = re.sub(r'[/\\:*?"<>|]', '', f"{', '.join([artist.name for artist in artists])} - {album.title} ({album.year})").strip()
    album_path = os.path.join(directory, album_name )
    os.makedirs(album_path, exist_ok=True)

    # download cover into the new album directory
    with open(os.path.join(album_path, "cover.jpg"), "wb") as f:
        f.write(requests.get(album.cover).content)
    

    # split the full album file into the seperate tracks
    # use tracks durations in order to find the correct splits
    current = 0
    for track in album.tracks:
        track_path = os.path.join(album_path, f"{str(track.number).zfill(2)} {track.full_title}.mp3")
        print(f"{str(track.number).zfill(2)} {track.full_title}")
        duration = track.duration*1000
        end_track = current + duration
        file[current:end_track].export(track_path, format="mp3")
        current = end_track

        # write the metadata into the track
        metadata = eyed3.load(track_path)
        metadata.tag.title = track.full_title
        metadata.tag.artist = track.band.name
        metadata.tag.album = album.title
        metadata.tag.release_date = album.year
        metadata.tag.recording_date = album.year
        metadata.tag.track_num = (track.number, next(t.number for t in album.tracks[::-1] if t.disc_number == track.disc_number))
        metadata.tag.disc_num = (track.disc_number, album.tracks[-1].disc_number)
        metadata.tag.save()
    
    # delete or move the full album file depending on args
    if keep:
        shutil.move(vid_path, os.path.join(album_path, f"{title}-{video_id}.mp3"))
    else:
        os.remove(vid_path)