import os
import tqdm
import json
from download_music_youtube import (  # type: ignore
    sync_from_json,
    yt_to_filename,
    add_tag,
)
from pytubefix import YouTube

OUTDIR = r"C:\BackUp DOK\Extra\music\avi"
JSON_FILE = r"C:\checkouts\youtube-music-downloader\avi_songs_dict.json"


def save(json_data):
    with open(JSON_FILE, "w", encoding="utf-8") as of:
        of.write(json.dumps(json_data, indent=4, ensure_ascii=False))


def read():
    with open(JSON_FILE, encoding="utf-8") as rf:
        return json.load(rf)


def add_tags():
    songs_to_download = read()
    for url, fname in tqdm.tqdm(songs_to_download.items()):
        add_tag(os.path.join(OUTDIR, fname), YouTube(url, use_po_token=True))


def sync_titles():
    songs_to_download = read()
    for url, fname in tqdm.tqdm(songs_to_download.items()):
        yt = YouTube(url, use_po_token=True)
        new_fname = yt_to_filename(yt)
        if new_fname != fname:
            print(f"New fname is different: {new_fname} ||| vs ||| {fname}")
            songs_to_download[url] = new_fname
    if input("Resave after changes? (Y/N)").lower().strip() == "y":
        save(songs_to_download)
    return songs_to_download


def sort_json():
    with open(JSON_FILE, encoding="utf-8") as rf:
        lines = rf.read().split("\n")
        lines = [line for line in lines if line.strip("{").strip("}").strip() != ""]
        lines.sort(key=lambda x: x.split(': "')[1])
    save(json.loads("{" + ",".join([line.rstrip(",") for line in lines]) + "}"))


if __name__ == "__main__":
    sync_from_json(read(), OUTDIR)
