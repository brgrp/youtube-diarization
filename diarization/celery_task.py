import os
import logging
from celery import Celery
from src.youtube_downloader import YouTubeDownloader
from diarization import Diarization
import json

# Configure Celery
app = Celery('celery_task', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')
app.conf.update(
    broker_connection_retry_on_startup=True,
    result_backend='redis://localhost:6379/0',
    task_track_started=True,
    worker_send_task_events=True
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

@app.task(bind=True)
def download_diarize_transcribe(self, url, output_folder):
    """
    Celery task to handle downloading, diarizing, and transcribing YouTube audio.
    """
    try:
        logging.info("Starting YouTube download process.")
        
        # Initialize YouTube downloader
        downloader = YouTubeDownloader(url, output_folder)
        _, wav_audio_file = downloader.download()
        
        if not wav_audio_file:
            raise ValueError("Failed to download the audio file.")

        logging.info("Download completed. Starting diarization process.")
        
        # Initialize diarization process
        diarization = Diarization(wav_audio_file)
        diarization_result = diarization.diarize()

        protocol_json_file = os.path.join(downloader.base_dir, "protocol.json")
        if not os.path.exists(protocol_json_file):
            protocol = diarization.create_protocol(diarization_result)
            
            # Save the protocol as JSON
            with open(protocol_json_file, "w") as json_file:
                json.dump(protocol, json_file, indent=4)
            
            logging.info(f"Protocol saved to {protocol_json_file}.")
        else:
            logging.info("Protocol file already exists.")

        return {"status": "success", "protocol_file": protocol_json_file}
    
    except Exception as e:
        # Handle exceptions and update task state
        logging.error(f"Error in download_diarize_transcribe: {str(e)}")
        self.update_state(state="FAILURE", meta={"exc_message": str(e)})
        return {"status": "failure", "error": str(e)}
