# YouTube Video Diarization

This project provides tools for downloading YouTube videos, performing speaker diarization, and transcribing the audio. It leverages state-of-the-art models for accurate speaker identification and transcription.

## Features

- Download audio from YouTube videos
- Perform speaker diarization to identify different speakers in the audio
- Transcribe the audio to text
- Save detailed protocols of speaker segments and their transcriptions

## Requirements

To install the required dependencies, run:

```sh
pip install -r requirements.txt
```

## Usage

### Download and Diarize a Single YouTube Video

To download and process a single YouTube video, run:

```sh
python diarization.py <YouTube_URL> <output_folder>
```

### Batch Processing from a File

To process multiple YouTube URLs from a file, run:

```sh
python diarization.py --file <file_with_urls> <output_folder>
```

## Output

The output will include:
- The downloaded audio file in WAV format
- A JSON file with diarization results
- A text file with detailed protocols of speaker segments and their transcriptions

## Example

```sh
python diarization.py https://www.youtube.com/watch?v=example <output_folder>
```

## Applications

The diarization results can be used for various applications, including:
- Training large language models (LLMs) with speaker-specific data
- Implementing Retrieval-Augmented Generation (RAG) applications for more accurate and context-aware responses

## License

This project is licensed under the MIT License.