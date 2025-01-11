import os
import logging
from youtube_downloader import YouTubeDownloader
from transcription import Transcriber
import torch
from pyannote.core import Segment
from pyannote.audio import Pipeline
from pydub import AudioSegment
import json
from tqdm import tqdm
from pyannote.core import Annotation

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

HUGGING_FACE_TOKEN = "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"

class Diarization:
    def __init__(self, audio_file):
        self.audio_file = audio_file
        logging.info(f"Initializing diarization pipeline for audio file: {audio_file}")
        self.pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1", use_auth_token=HUGGING_FACE_TOKEN
        )
        self.pipeline.to(
            torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        )
        self.transcriber = Transcriber(modelname="turbo")

    def diarize(self):
        logging.info("Starting speaker diarization.")
        diarization_file = os.path.join(
            os.path.dirname(self.audio_file), "diarization.json"
        )

        if os.path.exists(diarization_file):
            logging.info(f"Loading diarization from {diarization_file}.")
            with open(diarization_file, "r") as file:
                diarization = json.load(file)
                annotation = Annotation()
                for segment in diarization:
                    annotation[Segment(segment["start"], segment["end"])] = segment[
                        "speaker"
                    ]
                return annotation

        else:
            diarization = self.pipeline(self.audio_file)
            logging.info("Diarization completed.")
            diarization_data = [
                {"start": turn.start, "end": turn.end, "speaker": speaker}
                for turn, _, speaker in diarization.itertracks(yield_label=True)
            ]
            with open(diarization_file, "w") as file:
                json.dump(diarization_data, file)
            logging.info(f"Diarization saved to {diarization_file}.")

        return diarization

    def create_protocol(self, diarization):
        logging.info("Creating detailed protocol.")
        protocol = []
        for turn, _, speaker in tqdm(
            diarization.itertracks(yield_label=True), desc="Processing segments"
        ):
            logging.info(
                f"Processing segment from {turn.start} to {turn.end} for speaker {speaker}."
            )
            segment_text = self.extract_segment_text(turn, speaker)
            protocol.append(
                {
                    "start": turn.start,
                    "end": turn.end,
                    "speaker": speaker,
                    "text": segment_text,
                }
            )

        logging.info(f"Protocol creation completed.")
        logging.info(f"Protocol: {protocol}")
        return protocol

    def extract_segment_text(self, segment, speaker):
        logging.info(
            f"Extracting text for segment from {segment.start} to {segment.end}."
        )
        # Load the audio file
        audio = AudioSegment.from_file(self.audio_file)
        # Extract the segment
        start_ms = (
            segment.start * 1000
        )  # pyannote uses seconds, pydub uses milliseconds
        end_ms = segment.end * 1000
        audio_segment = audio[start_ms:end_ms]
        # Use the segment start and end time as an identifier for the file names
        segment_identifier = f"{segment.start:.2f}_{segment.end:.2f}".replace(".", "_")

        # Create a directory for the speaker if it doesn't exist
        speaker_dir = os.path.join(
            os.path.dirname(self.audio_file), "speakers", f"{speaker}"
        )
        os.makedirs(speaker_dir, exist_ok=True)

        try:
            # Save the audio segment
            audio_filename = os.path.join(
                speaker_dir, f"segment_{segment_identifier}.wav"
            )
            audio_segment.export(audio_filename, format="wav")
            logging.info(f"Audio segment saved to {audio_filename  }.")
        except Exception as e:
            logging.error(f"Failed to save audio segment: {e}")
            raise e

        # Transcribe the segment
        try:
            transcription_text = self.transcriber.transcribe(audio_filename)
            logging.info(f"Transcription for segment completed.")

            # Save the transcription
            transcript_filename = os.path.join(
                speaker_dir, f"transcript_{segment_identifier}.txt"
            )
            with open(transcript_filename, "w") as transcript_file:
                transcript_file.write(transcription_text)
            logging.info(f"Transcript saved to {transcript_filename}.")
        except Exception as e:
            logging.error(f"Failed to transcribe segment: {e}")
            transcription_text = ""
            raise e

        return transcription_text


def main(url, output_folder):
    """
    Main function to handle downloading, diarizing, and transcribing YouTube audio.
    """
    logging.info("Starting YouTube download process.")
    downloader = YouTubeDownloader(url, output_folder)
    _, wav_audio_file = downloader.download()
    
    if wav_audio_file:
        logging.info("Download completed. Starting diarization process.")
        diarization = Diarization(wav_audio_file)
        diarization_result = diarization.diarize()
        protocol_file = os.path.join(downloader.base_dir, "protocol.txt")
        protocol_json_file = os.path.join(downloader.base_dir, "protocol.json")

        if not os.path.exists(protocol_json_file):
            protocol = diarization.create_protocol(diarization_result)

            with open(protocol_file, "w") as file:
                for entry in protocol:
                    file.write(
                        f"{entry['speaker']} from {entry['start']:.2f} to "
                        f"{entry['end']:.2f}: {entry['text']}\n"
                    )

            # Save the protocol as JSON
            with open(protocol_json_file, "w") as json_file:
                json.dump(protocol, json_file, indent=4)
        else:
            logging.info("Protocol file already exists.")
    else:
        logging.error("Failed to download the audio file.")

# Example usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="YouTube Downloader, Diarization, and Transcription"
    )
    parser.add_argument(
        "url", type=str, nargs='?', help="The YouTube URL to download"
    )
    parser.add_argument(
        "output_folder", type=str, help="The folder to save the output files"
    )
    parser.add_argument(
        "--file", type=str, help="A text file containing multiple YouTube URLs"
    )
    args = parser.parse_args()

    if args.file:
        logging.info(f"Processing URLs from file: {args.file}")
        with open(args.file, 'r') as file:
            urls = file.readlines()
        for url in urls:
            url = url.strip()
            if url:
                logging.info(f"Processing URL: {url} output_folder: {args.output_folder}")
                main(url, args.output_folder)
    elif args.url:
        logging.info(f"Processing single URL: {args.url}")
        main(args.url, args.output_folder)
    else:
        logging.error(
            "You must provide either a YouTube URL or a file containing URLs."
        )
    
