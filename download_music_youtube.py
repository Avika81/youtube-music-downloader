import functools
from multiprocessing import Pool
from pytubefix import YouTube
from pytubefix import Playlist
from pathlib import Path
import mutagen
import os
import os
import tqdm


def add_tag(file, yt):
    media_file = mutagen.File(file, easy=True)
    media_file["artist"] = yt.author
    media_file.save()


def yt_to_filename(yt):
    title = yt.title
    if "-" not in title and "Topic" in yt.author:
        title = f"{yt.author} - {title}".replace(" - Topic", "")

    return (
        f"{title}.mp4".replace("?", "")
        .replace("|", "-")
        .replace("/", "-")
        .replace("\\", "-")
        .replace(":", " -")
        .replace("*", "")
    )


def youtube2mp3(url: str, outdir: str) -> None:
    yt = YouTube(url, use_po_token=True)
    try:
        video = yt.streams.filter(only_audio=True).first()
    except Exception:
        print(f"Failed downloading: {url} - {yt.title}")
        raise
    destination = outdir or "."
    filename = yt_to_filename(yt=yt)
    video.download(
        output_path=destination,
        filename=filename,
        timeout=3,
    )
    add_tag(filename, yt)
    return filename


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
    remove_old(songs_dict, outdir=outdir)
    new_songs = missing(songs_dict, outdir=outdir)
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
    playlist = Playlist(url_playlist)
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
