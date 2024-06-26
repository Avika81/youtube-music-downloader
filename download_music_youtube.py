from pytube import YouTube
from pytube import Playlist
from pathlib import Path


def yt_to_filename(yt):
    return (
        f"{yt.author} - {yt.title}.mp4".replace("?", "")
        .replace("|", "-")
        .replace("/", "-")
    )


def youtube2mp3(url: str, outdir: str) -> None:
    yt = YouTube(url)
    try:
        video = yt.streams.filter(only_audio=True).first()
    except:
        print(f"Failed downloading: {url} - {yt.title}")
        return
    destination = outdir or "."
    filename = yt_to_filename(yt=yt)
    video.download(
        output_path=destination,
        filename=filename,
    )
    return filename


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
