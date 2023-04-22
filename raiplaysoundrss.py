from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from datetime import datetime
import mimetypes
import logging
from email.utils import format_datetime

import requests
from feedgen.feed import FeedGenerator


logger = logging.getLogger("raiplayrss")


@dataclass
class AudiobookEpisodes:
    id: str
    title: str
    description: str
    logo: str
    url: str
    audio_url: str
    audio_mime: str
    audio_length: int
    audio_duration: str
    date: datetime


@dataclass
class Audiobook:
    id: str
    title: str
    url: str
    logo: str
    date: datetime
    episodes: list[AudiobookEpisodes]


def load_audiobook(name: str):
    baseurl = "https://www.raiplaysound.it/"
    audiobook_url = baseurl + "/audiolibri/" + name
    response = requests.get(audiobook_url + ".json")
    response.raise_for_status()
    audiobook_json = response.json()
    audiobook_id = audiobook_json["uniquename"]
    audiobook_logo = baseurl + "/" + audiobook_json["podcast_info"]["image"]
    audiobook_title = audiobook_json["podcast_info"]["title"]
    audiobook_date = datetime.strptime(
        (
            audiobook_json["podcast_info"]["create_date"] +
            " " +
            audiobook_json["podcast_info"]["create_time"]
        ),
        "%d-%m-%Y %H:%M",
    )
    episodes = []
    for episode in audiobook_json["block"]["cards"]:
        audio_url = episode["audio"]["url"]
        # The User-agent is required to avoid HTTP 403 response.
        response = requests.head(audio_url, allow_redirects=True, headers={
            "User-agent": "Mozilla/5.0",
        })
        response.raise_for_status()
        audio_mime = response.headers["content-type"]
        audio_length = int(response.headers["content-length"])
        audiobookEpisode = AudiobookEpisodes(
            id=episode["uniquename"],
            title=episode["audio"]["title"],
            description=episode["description"],
            logo=baseurl + "/" + episode["image"],
            url=baseurl + "/" + episode["weblink"],
            audio_url=audio_url,
            audio_mime=audio_mime,
            audio_length=audio_length,
            audio_duration=episode["audio"]["duration"],
            date=datetime.strptime(
                (
                    episode["create_date"] +
                    " " +
                    episode["create_time"]
                ),
                "%d-%m-%Y %H:%M",
            )
        )
        episodes.append(audiobookEpisode)

    audiobook = Audiobook(
        id=audiobook_id,
        url=audiobook_url,
        logo=audiobook_logo,
        title=audiobook_title,
        date=audiobook_date,
        episodes=episodes,
    )

    return audiobook


def convert_to_rss(audiobook: Audiobook):
    fg = FeedGenerator()
    fg.load_extension('podcast')
    fg.id(audiobook.id)
    fg.title(audiobook.title)
    fg.description("Audiobook")
    fg.author(name="RAI")
    fg.link(href=audiobook.url)
    fg.logo(audiobook.logo)
    fg.language("it")
    fg.pubDate(format_datetime(audiobook.date))
    for index, episode in enumerate(audiobook.episodes):
        fe = fg.add_entry()
        fe.id(episode.id)
        fe.title(episode.title)
        fe.description(episode.description)
        fe.link(href=episode.url)
        fe.enclosure(
            url=episode.audio_url,
            type=episode.audio_mime,
            length=str(episode.audio_length),
        )
        fe.podcast.itunes_duration(episode.audio_duration)
        fe.pubDate(format_datetime(episode.date))

    return fg.rss_str(pretty=True)


def do_download_rss(args: Namespace):
    audiobook = load_audiobook(args.audiobook_name)
    rss = convert_to_rss(audiobook)
    with open(args.output_rss_path, "wb") as fp:
        fp.write(rss)


def do_download_audio(args: Namespace):
    audiobook = load_audiobook(args.audiobook_name)
    for index, episode in enumerate(audiobook.episodes):
        logger.info(f"Downloading episode #{index}: {episode.audio_url}")
        # The User-agent is required to avoid HTTP 403 response.
        response = requests.get(episode.audio_url, allow_redirects=True, headers={
            "User-agent": "Mozilla/5.0",
        })
        response.raise_for_status()
        suffix = mimetypes.guess_extension(
            response.headers["content-type"].split(";")[0].strip()
        )
        outputfile = f"{args.output_dir}/{index}{suffix}"
        with open(outputfile, "wb") as fp:
            fp.write(response.content)


if __name__ == '__main__':
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()
    download_rss = subparsers.add_parser("download-rss", help="Download RSS feed")
    download_rss.add_argument("audiobook_name")
    download_rss.add_argument("output_rss_path")
    download_rss.set_defaults(func=do_download_rss)
    download_audio = subparsers.add_parser("download-audio", help="Download audio files")
    download_audio.add_argument("audiobook_name")
    download_audio.add_argument("output_dir")
    download_audio.set_defaults(func=do_download_audio)

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    args.func(args)

