# YouTube Diarization

This project provides tools for downloading YouTube videos, performing speaker diarization, and transcribing the audio. It leverages state-of-the-art models for accurate speaker identification and transcription.

## Features

- Download audio from YouTube videos
- Perform speaker diarization to identify different speakers in the audio
- Transcribe the audio to text
- Save detailed protocols of speaker segments and their transcriptions

## Tools and Models Used

### Transcription

For transcription, we use the Whisper turbo model from OpenAI. Whisper is a general-purpose speech recognition model that is trained on a large dataset of diverse audio.

### Downloading Audio

For downloading audio from YouTube, we use the `pytubefix` library.

### Diarization

For speaker diarization, we use the `pyannote.audio` library. `pyannote.audio` is a toolkit for speaker diarization that provides pre-trained models for speaker identification and segmentation.

## Requirements

To install the required dependencies, run:

```sh
uv sync
```

### Setting Up Environment Variables

You need to set the `HUGGING_FACE_TOKEN` environment variable. You can do this by adding the following line to your shell configuration file (e.g., `.bashrc`, `.zshrc`):

```sh
export HUGGING_FACE_TOKEN=<your_hugging_face_token>
```

### Setting Up Redis (Optional)

To use Celery, you need to have Redis installed and running. You can install Redis using Homebrew:

```sh
brew install redis
```

Start the Redis server:

```sh
brew services start redis
```

### Setting Up Flower (Optional)

To monitor Celery tasks, you can use Flower. Install Flower using pip:

```sh
uv add flower
```

### Running Flower and Celery Workers (Optional)

To monitor Celery tasks and run Celery workers, follow these steps:

1. **Start the Flower server**:
    ```sh
    uv run celery -A diarization.celery_task flower --port=5555
    ```

    Access the Flower dashboard by navigating to `http://localhost:5555` in your web browser.

2. **Start the Celery worker**:
    ```sh
    uv run celery -A diarization.celery_task worker --loglevel=info -P threads
    ```

### Installing ffmpeg

To convert the audio to WAV format, you need to have `ffmpeg` installed. You can install `ffmpeg` using Homebrew:

```sh
brew install ffmpeg
```

## Usage

### Download and Diarize a Single YouTube Video

To download and process a single YouTube video, run:

```sh
uv run diarization.py <YouTube_URL> <output_folder>
```

### Batch Processing from a File

To process multiple YouTube URLs from a simple text file (one link per line), run:

```sh
uv run diarization.py --file <file_with_urls> <output_folder>
```

### Running Celery Tasks (Optional)

To run Celery tasks for downloading and transcribing, start the Celery worker:

```sh
uv run celery -A diarization.celery_task worker --loglevel=info -P threads
```

Then, you can call the task from your code:

```python
from diarization.celery_task import download_and_transcribe

result = download_and_transcribe.delay(<YouTube_URL>, <output_folder>)
print(result.get())
```

### Running the Streamlit App with Celery Tasks

To run the Streamlit app for a user-friendly interface, use the following command:

```sh
uv run streamlit run streamlit_app.py
```

## Output

The output will include:
- The downloaded audio file in WAV format
- A JSON file with diarization results
- A text file with detailed protocols of speaker segments and their transcriptions

## Example

```sh
uv run diarization.py https://www.youtube.com/watch?v=example <output_folder>
```

## Applications

The diarization results can be used for various applications, including:
- Training large language models (LLMs) with speaker-specific data
- Implementing Retrieval-Augmented Generation (RAG) applications for more accurate and context-aware responses

## License

This project is licensed under the MIT License.