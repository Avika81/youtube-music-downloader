import functools
from multiprocessing import Pool
from random import randint
import shutil
import tqdm
from yt_dlp import YoutubeDL
import time
from pytubefix import YouTube
from pytubefix import Playlist
from pathlib import Path
import mutagen
import os
import os

_DEBUG = False


def add_tag(file, yt):
    media_file = mutagen.File(file, easy=True)  # type: ignore
    media_file["artist"] = yt.author  # type: ignore
    media_file.save()  # type: ignore


def yt_to_filename(yt):
    title = yt.title
    if "-" not in title and "Topic" in yt.author:
        title = f"{yt.author} - {title}".replace(" - Topic", "")

    return (
        f"{title}.mp3".replace("?", "")
        .replace("|", "-")
        .replace("/", "-")
        .replace("\\", "-")
        .replace(":", " -")
        .replace("*", "")
        .replace('"', "'")
    )


def retry(f, attempts: int = 10):
    @functools.wraps(f)
    def inner(*args, **kwargs):
        if _DEBUG:
            return f(*args, **kwargs)
        time.sleep(randint(0, 3))
        for _ in range(attempts):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                print(f"Failed: {f} - {args} {kwargs} - {repr(e)}")
                time.sleep(randint(0, 20))
        raise Exception(f"Failed: {f} - {args} {kwargs}")

    return inner


def download(url, filename):
    # This api is broken, downloading with YoutubeDL
    # yt.streams.filter(only_audio=True).first().download(
    #     output_path=outdir,
    #     filename=filename,
    #     timeout=10,
    # )
    ydl_opts = {
        "format": "bestaudio/best",
        "extractaudio": True,  # Optional, already implied by next two
        "audioformat": "mp3",  # Convert to mp3
        "outtmpl": filename,
        "quiet": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    shutil.move(f"{filename.replace('.mp4','.mp3')}", filename)


@retry
def youtube2mp3(url: str, outdir: str) -> str:
    yt = YouTube(url, use_po_token=True)
    filename = os.path.join(outdir, yt_to_filename(yt=yt))
    download(url, filename=filename)
    add_tag(filename, yt)
    return filename


def remove_empty_files(songs_to_download, outdir: str) -> None:
    [
        os.remove(os.path.join(outdir, name))
        for name in os.listdir(outdir)
        if os.stat(os.path.join(outdir, name)).st_size == 0
    ]


def remove_old(songs_to_download, outdir: str) -> None:
    for f in [
        os.path.join(outdir, name)
        for name in os.listdir(outdir)
        if name not in songs_to_download.values()
    ]:
        os.remove(f)


def missing(songs_to_download, outdir: str) -> dict:
    ldir = os.listdir(outdir)
    return {url: name for url, name in songs_to_download.items() if name not in ldir}


def sync_from_json(songs_dict: dict[str, str], outdir: str):
    remove_empty_files(songs_dict, outdir=outdir)
    remove_old(songs_dict, outdir=outdir)
    new_songs = missing(songs_dict, outdir=outdir)
    if _DEBUG:
        [youtube2mp3(ns, outdir=outdir) for ns in new_songs.keys()]  # for _DEBUGging
    else:
        with Pool(processes=16) as pool:
            res = pool.imap_unordered(
                functools.partial(youtube2mp3, outdir=outdir), new_songs.keys()
            )

            for _ in tqdm.tqdm(res, total=len(new_songs)):
                pass
    remaining = missing(songs_dict, outdir=outdir)
    assert not remaining, f"Failed to download everything, missing: f{remaining}"


# The playlist api was Not tested recently (use with caution):
def all_urls_from_youtube_playlist(url_playlist: list[str]):
    playlist = Playlist(url_playlist)  # type: ignore
    print("Number Of Videos In playlist: %s" % len(playlist.video_urls))

    urls = []
    for url in playlist:
        urls.append(url)

    return urls


def download_playlist(url, outdir: str):
    for songs_url in all_urls_from_youtube_playlist(url):
        dest_dir = Path(outdir) / Playlist(url).title
        try:
            dest_dir.mkdir()
        except:
            pass
        youtube2mp3(songs_url, dest_dir)
