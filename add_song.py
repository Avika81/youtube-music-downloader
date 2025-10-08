from pytubefix import YouTube
import sys
from collections import Counter

from download_music_youtube import yt_to_filename  # type: ignore
from sync import save, read, sort_json  # type: ignore


def remove_duplicates(songs_to_download):
    duplicate_values = [
        k for k, v in Counter(songs_to_download.values()).items() if v > 1
    ]

    for value in duplicate_values:
        for u in songs_to_download:
            if songs_to_download[u] == value:
                songs_to_download.pop(u)
                break


def main():
    url = sys.argv[1]
    songs_data = read()
    if url not in songs_data:
        fname = yt_to_filename(YouTube(url, use_po_token=True))
        if fname not in songs_data.values():
            songs_data[url] = fname
            remove_duplicates(songs_data)
            save(songs_data)
            sort_json()
    else:
        print(f"The song {url} already exists :)")


if __name__ == "__main__":
    main()
