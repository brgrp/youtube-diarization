import os
import logging
from datetime import datetime
from pytubefix import YouTube
from pytubefix.cli import on_progress
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class YouTubeDownloader:
    """
    A class to download audio from YouTube videos and convert it to WAV format.
    """

    def __init__(self, url, output_folder):
        """
        Initializes the YouTubeDownloader with a URL and output folder.
        """
        self.output_folder = output_folder
        self.yt = YouTube(url, on_progress_callback=on_progress)
        self.date_str = datetime.now().strftime("%Y%m%d")
        sanitized_title = self._sanitize_title(self.yt.title)
        self.base_dir = os.path.join(
            self.output_folder, f"{self.date_str}_{sanitized_title}"
        )
        os.makedirs(self.base_dir, exist_ok=True)
        self.save_meta()
        logging.info(f"Initialized YouTubeDownloader with URL: {url}")

    def _sanitize_title(self, title):
        """
        Sanitizes the video title to create a valid directory name.
        """
        return "".join(c if c.isalnum() or c == "_" else "_" for c in title)

    def save_meta(self):
        """
        Saves the YouTube link and meta information to a JSON file in the output directory.
        """

        meta_info = {
            "URL": self.yt.watch_url,
            "Title": self.yt.title,
            "Description": self.yt.description,
        }

        meta_file = os.path.join(self.base_dir, "meta_info.json")
        with open(meta_file, "w") as file:
            json.dump(meta_info, file, indent=4)
        logging.info(f"Meta information saved to {meta_file}")

    def download(self):
        """
        Downloads the audio from the YouTube video and converts it to WAV format.
        """
        try:
            logging.info(f"Video title: {self.yt.title}")
            logging.info(f"Video Descriptions: {self.yt.description}")
            ys = self.yt.streams.get_audio_only()

            file_title = self._sanitize_title(self.yt.title)
            
            audio_path = os.path.join(self.base_dir, f"{file_title}_audio.m4a")
            wav_audio_path = os.path.join(self.base_dir, f"{file_title}_audio.wav")

            if not os.path.exists(audio_path):
                ys.download(
                    output_path=self.base_dir, filename=f"{file_title}_audio.m4a"
                )
                logging.info("Audio downloaded successfully.")
            else:
                logging.warning("Audio file already exists.")

            if not os.path.exists(wav_audio_path):
                logging.info(f"Converting {audio_path} to {wav_audio_path}")
                self._convert_to_wav(audio_path, wav_audio_path)
            else:
                logging.warning("WAV audio file already exists.")
            return audio_path, wav_audio_path
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return None, None

    def _convert_to_wav(self, audio_path, wav_audio_path):
        """
        Converts the downloaded audio file to WAV format.
        """
        try:
            os.system(f"ffmpeg -i {audio_path} {wav_audio_path}")
            logging.info("Audio converted to WAV format successfully.")
        except Exception as e:
            logging.error(f"Failed to convert audio to WAV format: {e}")


# Example usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="YouTube Downloader")
    parser.add_argument("url", type=str, help="The YouTube URL to download")
    parser.add_argument(
        "output_folder", type=str, help="The folder to save the output files"
    )
    args = parser.parse_args()

    downloader = YouTubeDownloader(args.url, args.output_folder)
    downloader.download()
