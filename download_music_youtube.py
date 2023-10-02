from multiprocessing import Pool, TimeoutError
from threading import Thread
from pytube import YouTube
from pytube import Playlist
import json
import os
from pathlib import Path

def youtube2mp3(url, outdir):
    yt = YouTube(url)
    try:
        video = yt.streams.filter(only_audio=True).first()
    except:
        print(f'Failed downloading: {url} - {yt.title}')
        return
    destination = outdir or '.'
    video.download(output_path=destination, filename=f'{yt.author} - {yt.title}.mp4'.replace('?', '').replace('|', '-'))


def all_urls_from_youtube_playlist(url_playlist):
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



