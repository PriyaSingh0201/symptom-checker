# utils/voice.py – Server-side stub for voice input
# Voice recognition is handled entirely client-side via the
# Web Speech API (SpeechRecognition / webkitSpeechRecognition).
# This file is kept as a placeholder for any future server-side
# audio processing (e.g. Whisper API integration).


def transcribe_audio(audio_bytes: bytes) -> str:
    """
    Placeholder: transcribe audio bytes to text.
    Currently voice input is processed in the browser (Web Speech API).
    """
    raise NotImplementedError(
        "Server-side transcription not yet implemented. "
        "Use the browser Speech Recognition API instead."
    )
