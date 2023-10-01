from pytube import YouTube
from pytube import Playlist
import json
import os
from pathlib import Path

def youtube2mp3(url,outdir):
    yt = YouTube(url)
    try:
        video = yt.streams.filter(only_audio=True).first()
    except:
        print(f'Failed downloading: {url} - {yt.title}')
        return
    destination = outdir or '.'
    out_file = video.download(output_path=destination)
    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'
    os.rename(out_file, new_file)
    print(yt.title + " has been successfully downloaded.")


def all_urls_from_youtube_playlist(url_playlist):
    # Retrieve URLs of videos from playlist
    playlist = Playlist(url_playlist)
    print('Number Of Videos In playlist: %s' % len(playlist.video_urls))

    urls = []
    for url in playlist:
        urls.append(url)

    return urls


def download_playlist(url,outdir):
    for songs_url in all_urls_from_youtube_playlist(url):
        dest_dir = Path(outdir) / Playlist(url).title
        try:
            dest_dir.mkdir()
        except:
            pass
        youtube2mp3(songs_url, dest_dir)


with open('songs.json') as rf:
    songs_to_download = json.load(rf)

# if __name__ == "__main__":
download_playlist(
    url=r"https://www.youtube.com/watch?v=gl1aHhXnN1k&list=PLcc2EHxL-4QRSjIQfFWNX3zasjT76drjq",
    outdir=r"./ariana_grande"
    )

    # for url in songs_to_download:
    #     try:
    #         youtube2mp3(url, r"C:\Temp\2023-09-26\songs")
    #     except Exception as e:
    #         print(f'Failed to download url {url}')
