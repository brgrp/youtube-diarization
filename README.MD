# YouTube Video Diarization

This project provides tools for downloading YouTube videos, performing speaker diarization, and transcribing the audio. It leverages state-of-the-art models for accurate speaker identification and transcription.

## Features

- Download audio from YouTube videos
- Perform speaker diarization to identify different speakers in the audio
- Transcribe the audio to text
- Save detailed protocols of speaker segments and their transcriptions

## Requirements
The uv package is needed. For installation see [GitHub](https://github.com/astral-sh/uv)

To install the required dependencies, run:

```sh
uv sync
```

### Setting Up Redis

To use Celery, you need to have Redis installed and running. You can install Redis using Homebrew:

```sh
brew install redis
```

Start the Redis server:

```sh
brew services start redis
```

### Setting Up Flower

To monitor Celery tasks, you can use Flower. Install Flower using pip:

```sh
pip install flower
```

### Running Flower and Celery Workers

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

## Usage

### Download and Diarize a Single YouTube Video

To download and process a single YouTube video, run:

```sh
uv run diarization.py <YouTube_URL> <output_folder>
```

### Batch Processing from a File

To process multiple YouTube URLs from a file, run:

```sh
uv run diarization.py --file <file_with_urls> <output_folder>
```

### Running Celery Tasks

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