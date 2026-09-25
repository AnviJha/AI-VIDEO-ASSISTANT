# AI Video Assistant

AI Video Assistant turns a YouTube video or a local audio/video file into an English transcript, meeting notes, and a searchable chat. The web interface is built with Streamlit. Mistral generates the title and written analysis, Whisper transcribes English audio locally, Sarvam handles the Hinglish option, and Chroma stores transcript chunks for question answering.

## Features

- Accepts a YouTube URL or a local audio/video file path.
- Extracts audio from YouTube videos and converts local media to mono 16 kHz WAV.
- Splits long audio into 10-minute files before transcription.
- Transcribes English with the local Whisper model (default: `small`).
- Transcribes and translates Hinglish audio to English with Sarvam, in 25-second pieces.
- Creates a short meeting title and a bullet-point summary.
- Extracts action items, including owner and deadline when mentioned, key decisions, and unresolved questions.
- Provides a chat interface that answers questions using retrieved transcript sections.
- Shows pipeline progress, the full transcript, analysis cards, and chat history. Chat history can be cleared from the interface.
- Includes both a Streamlit interface and a command-line pipeline.

## Requirements

- Windows, macOS, or Linux.
- Python 3.11 is recommended. Whisper and PyTorch can be sensitive to Python and platform versions.
- FFmpeg installed and available on your `PATH`. `pydub` and `yt-dlp` use the FFmpeg programs to decode and convert media; installing the Python package `ffmpeg-python` alone does not install FFmpeg.
- A Mistral API key for title generation, summaries, extraction, and transcript chat.
- A Sarvam API key only if you select `hinglish`.
- Internet access for YouTube downloads, API calls, and the initial model downloads.

## Setup (Windows PowerShell)

1. Open PowerShell in the project directory.

2. Create and activate a virtual environment:

   ```powershell
   py -3.11 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, open Command Prompt and use `.venv\Scripts\activate.bat`, or run `.venv\Scripts\python.exe` and `.venv\Scripts\streamlit.exe` directly.

3. Install FFmpeg using a package manager, or install it manually and add its `bin` directory to `PATH`. Confirm it is available:

   ```powershell
   ffmpeg -version
   ```

4. Install the Python dependencies. The dependency file in this project is named `requirement.txt` (singular):

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirement.txt
   ```

5. Create a `.env` file in the project root. Add your own keys; do not commit or share this file:

   ```dotenv
   MISTRAL_API_KEY=your_mistral_api_key
   SARVAM_API_KEY=your_sarvam_api_key

   # Optional settings; these are the application defaults.
   WHISPER_MODEL=small
   SARVAM_STT_MODEL=saaras:v2.5
   ```

   `MISTRAL_API_KEY` is required for the analysis features. `SARVAM_API_KEY` is required only for Hinglish transcription. If you only use English, you can omit the Sarvam key.

## Run the Streamlit app

From the project root with the virtual environment active:

```powershell
streamlit run app.py
```

In the browser:

1. Paste a YouTube URL into **YouTube URL or File Path**, or enter the path to a local media file.
2. Select **english** or **hinglish**.
3. Select **Analyse** and wait for the audio, transcription, title, summary, extraction, and RAG steps to finish.
4. Review the title, summary, action items, decisions, and open questions. Expand **Full Transcript** to read the transcript.
5. Enter a question in **Chat with your Meeting** and select **Send**. The answer is based on the transcript chunks retrieved for that question.
6. Select **Clear Chat** to clear the visible conversation.

The first run can take longer because Whisper and the embedding model may need to be downloaded. English Whisper transcription runs locally and may use substantial CPU, memory, and disk space.

## Run from the command line

Run the complete pipeline and then chat with the transcript:

```powershell
python main.py
```

Enter the YouTube URL or local file path, then enter `english` or `hinglish` when prompted.

For a manual smoke check of transcription and analysis (without the RAG chat step):

```powershell
python test.py
```

This script prompts for a source and starts processing only when run directly. It is not an automated test suite.

## How processing works

1. **Audio ingestion:** YouTube audio is downloaded into `downloades/`. Local media is converted to WAV. The audio is divided into 10-minute chunks.
2. **Transcription:** English chunks are sent to Whisper locally. Hinglish chunks are divided into 25-second pieces and sent to Sarvam's speech-to-text-translate API; the returned transcript is English.
3. **Analysis:** Mistral generates a title, a concise bullet-point summary, action items, key decisions, and open questions. Long summaries are processed in text chunks and combined.
4. **Search and chat:** The transcript is split into chunks, embedded with `all-MiniLM-L6-v2`, and stored in the local Chroma database at `vector_db/`. Each new analysis replaces the previous meeting's collection. Chat retrieves up to four relevant transcript chunks and asks Mistral to answer from that context.

Generated WAV files and audio chunks are stored under `downloades/` or alongside the input file. The Chroma database is stored under `vector_db/`. These are local processing data, not exported reports.

## Configuration

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `MISTRAL_API_KEY` | Yes, for analysis and chat | None | Authenticates Mistral calls. |
| `SARVAM_API_KEY` | Only for Hinglish | None | Authenticates Sarvam transcription/translation calls. |
| `WHISPER_MODEL` | No | `small` | Whisper model used for English audio. |
| `SARVAM_STT_MODEL` | No | `saaras:v2.5` | Sarvam model used for Hinglish audio. |

## Troubleshooting

- **Mistral HTTP 429 / rate limit:** This is a limit on the API account or key, not a Python syntax problem. Wait for the limit to reset and check the key's usage and rate limits. Repeated retries cannot restore exhausted quota.
- **Missing API key:** Confirm `.env` is in the project root, the variable name is spelled exactly as shown, and restart Streamlit after changing it.
- **FFmpeg not found or media conversion fails:** Install the FFmpeg executable and make sure `ffmpeg -version` works in the same terminal used to start the app.
- **Local file not found:** Provide a valid path. For paths containing spaces, quotation marks can help when using a command-line prompt.
- **Hinglish transcription fails:** Confirm `SARVAM_API_KEY` is set and the account can access the configured Sarvam speech-to-text-translate model.
- **Whisper first-run delay or memory use:** The selected model is downloaded on first use. A smaller Whisper model can reduce resource use by setting `WHISPER_MODEL` in `.env` (for example, `base` or `tiny`), with a likely reduction in transcription quality.
- **YouTube download fails:** Check the URL, network connection, and whether `yt-dlp` needs updating in the virtual environment (`pip install --upgrade yt-dlp`).

## Project layout

```text
app.py                   Streamlit user interface
main.py                  Command-line pipeline and transcript chat
test.py                  Manual transcription/analysis smoke check
requirement.txt          Python dependencies
core/
  extractor.py           Action items, decisions, and open questions
  rag_engine.py          Transcript question answering
  summarizer.py          Title and summary generation
  transcriber.py         Whisper and Sarvam transcription
  vector_store.py        Transcript embeddings and Chroma storage
utils/
  audio_processor.py     YouTube/local media conversion and chunking
downloades/              Downloaded and temporary audio files
vector_db/               Local Chroma database (created when processing)
```

## Notes

- Keep `.env` private; it contains API credentials.
- API calls may incur charges or be subject to account rate limits.
- The UI's displayed outputs remain in the current Streamlit session. Audio files and the local vector database are stored on disk as described above.
