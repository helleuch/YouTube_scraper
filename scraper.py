import argparse
import os
import pathlib
from typing import Tuple

import librosa
import moviepy.editor as mp
import validators
from loguru import logger
from pydub import AudioSegment
from pytube import Channel
from tqdm import tqdm
from tqdm.notebook import tqdm


def export_audio(source_folder: str, destination_folder: str, export_wav: bool = True) -> Tuple[str, str]:
    """
    Exports audio from videos contained in a folder to mp3 and optionally wav formats.
    :param source_folder:
    :param destination_folder:
    :param export_wav: set to True if a wav output is expected.
    :return:
    """

    mp3_path = os.path.join(destination_folder, "mp3")
    wav_path = ""
    pathlib.Path(mp3_path).mkdir(parents=True, exist_ok=True)

    if export_wav:
        wav_path = os.path.join(destination_folder, "wav")
        pathlib.Path(wav_path).mkdir(parents=True, exist_ok=True)

    logger.info(f"Exporting audio from {source_folder} to {destination_folder}...")

    for file in (pbar := tqdm(os.listdir(source_folder))):
        base_file_name = file.split(".mp4")[0]

        mp3_file_name = os.path.join(mp3_path, f"{base_file_name}.mp3")
        pbar.set_description(f"File: {file} || Exporting mp3")
        mp.VideoFileClip(os.path.join(source_folder, file)).audio.write_audiofile(mp3_file_name, verbose=False,
                                                                                  logger=None)

        if export_wav:
            wav_file_name = os.path.join(wav_path, f"{base_file_name}.wav")
            pbar.set_description(f"File: {file} || Exporting wav")
            AudioSegment.from_mp3(mp3_file_name).export(wav_file_name, format="wav")

    logger.success("Audio export completed.")
    return mp3_path, wav_path


def compile_data_information(path: str) -> dict:
    """
    Compiles some information about a directory.
    :param path: directory to be inspected
    :return: dict of info
    """
    duration = 0
    count = 0
    size = 0

    for file in (os.listdir(path)):
        d = librosa.get_duration(filename=os.path.join(path, file))
        size += os.path.getsize(os.path.join(path, file))
        duration += d
        count += 1

    data_info = {"total_duration": duration,
                 "avg_duration": duration / count,
                 "total_size_mb": round(size / (1024 * 1024), 3)}

    return data_info


def scrape_channel(url: str) -> str:
    """
    Downloads all the videos of a given YouTube channel.
    :param url: URL of the YouTube channel.
    :return: Directory in which the videos were saved.
    """
    channel = Channel(url)
    logger.info(f"Scraping channel {channel.channel_name}")

    output_path = os.path.join("downloads",f"scraped_{channel.channel_name}".replace(" ", "_").strip())
    pathlib.Path(output_path).mkdir(parents=True, exist_ok=True)

    with open(f"downloaded_{output_path}.log", 'w') as log:
        for video in (pbar := tqdm(channel.videos)):
            pbar.set_description(f"Downloading {video.video_id}")
            video.streams.first().download(output_path=output_path)
            log.write(video.watch_url + "\n")

    logger.success("Video download completed.")
    return output_path


def parse_str_arg(file_path: str, default_value: str) -> str:
    """
    Will read an str arg and return its value. A default value is supplied if the arg is None.
    :param file_path: str
    :param default_value: str
    :return: str
    """
    if file_path is None:
        return default_value
    else:
        return file_path


def get_channel_from_file(file_path: str) -> str:
    """
    Will open and read the specified file and return the contained URL if valid.
    :raises ValueError if the URL is invalid.
    :param file_path: path of the file to be opened.
    :return: str
    """
    with open(file_path, 'r') as file:
        url = file.readline()
        if validators.url(url):
            return url
        else:
            raise ValueError("The specified URL is invalid")


def main(arguments: dict):
    logger.info(f"Launching scraper with parameters: {arguments}")
    logger.warning(
        "This script requires a modification of the pytube library source code to account for the new channel links with the \"@\" symbol. ")

    if arguments.file:
        file = parse_str_arg(arguments.path, "link.txt")
        url = get_channel_from_file(file)

    elif arguments.channel is not None and validators.url(arguments.channel):
        url = arguments.channel

    else:
        logger.error("No valid URL supplied. Exiting program...")
        exit(1)

    video_dir = scrape_channel(url)
    _, wav_folder = export_audio(source_folder=video_dir, destination_folder=video_dir, export_wav=True)
    if wav_folder != "":
        logger.info({f"Data information: {compile_data_information(wav_folder)}"})

    logger.success("Data scraping completed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download all videos from a given YouTube channel.')
    parser.add_argument('-c', '--channel', help='Youtube channel URL')
    parser.add_argument('-f', '--file', action='store_true',
                        help='Put the channel URL inside a file named link.txt, by default')
    parser.add_argument('-p', '--path',
                        help='Name of the file where the channel link is stored. if not specified, the default name is link.txt')
    args = parser.parse_args()

    main(args)
