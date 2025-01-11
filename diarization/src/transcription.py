import os
import logging
import argparse
from src.youtube_downloader import YouTubeDownloader
import torch
import whisper

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class Transcriber:
    """
    A class to handle transcription of audio files using Whisper.
    """

    def __init__(self, modelname="turbo"):
        """
        Initializes the Transcriber with a specified model.
        """
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
        )
        logging.info(f"Using device: {self.device}")
        self.model = whisper.load_model(modelname)

    def transcribe(self, filename, language="en"):
        """
        Transcribes the given audio file.
        """
        logging.info("Starting transcription...")
        result = self.model.transcribe(filename, fp16=False, language=language)
        transcription_text = result["text"]
        logging.info("Transcription completed.")
        return transcription_text

    def save(self, output_file, transcription_text):
        """
        Saves the transcription text to a file.
        """
        with open(output_file, "w") as text_file:
            text_file.write(transcription_text)
            logging.info(f"Transcription saved to {output_file}")


def main(url, output_folder):
    """
    Main function to handle downloading and transcribing YouTube audio.
    """
    logging.info("Starting YouTube download process.")
    downloader = YouTubeDownloader(url, output_folder)
    audio_file, _ = downloader.download()

    if audio_file:
        logging.info("Download completed. Starting transcription process.")
        transcriber = Transcriber(modelname="turbo")
        output_file = os.path.join(downloader.base_dir, "transcription.txt")
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            logging.info("Transcription file already exists. Reading from file.")
            with open(output_file, "r") as file:
                transcription_text = file.read()
        else:
            transcription_text = transcriber.transcribe(audio_file)
            transcriber.save(output_file, transcription_text)
            logging.info("Transcription completed and saved to file.")

        word_count = len(transcription_text.split())
        logging.info(f"Word count: {word_count}")
    else:
        logging.error("Failed to download the audio file.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube Downloader and Transcriber")
    parser.add_argument("url", type=str, help="The YouTube URL to download")
    parser.add_argument(
        "output_folder", type=str, help="The folder to save the output files"
    )
    args = parser.parse_args()

    main(args.url, args.output_folder)
