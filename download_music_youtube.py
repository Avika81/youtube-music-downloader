import joblib
from multiprocessing import Pool, TimeoutError
from threading import Thread
from pytube import YouTube
from pytube import Playlist
from pathlib import Path

memory = joblib.Memory('./.cache', verbose=0)

def _youtube2mp3(url: str, outdir: str) -> None:
    yt = YouTube(url)
    try:
        video = yt.streams.filter(only_audio=True).first()
    except:
        print(f"Failed downloading: {url} - {yt.title}")
        return
    destination = outdir or "."
    filename = f"{yt.author} - {yt.title}.mp4".replace("?", "").replace("|", "-").replace("/", "-")
    video.download(
        output_path=destination,
        filename=filename,
    )
    return filename
youtube2mp3 = memory.cache(_youtube2mp3)

def all_urls_from_youtube_playlist(url_playlist):
    playlist = Playlist(url_playlist)
    print("Number Of Videos In playlist: %s" % len(playlist.video_urls))

    urls = []
    for url in playlist:
        urls.append(url)

    return urls


def download_playlist(url, outdir):
    for songs_url in all_urls_from_youtube_playlist(url):
        dest_dir = Path(outdir) / Playlist(url).title
        try:
            dest_dir.mkdir()
        except:
            pass
        youtube2mp3(songs_url, dest_dir)
