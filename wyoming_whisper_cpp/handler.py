"""Event handler for clients of the server."""
import argparse
import asyncio
import io
import json
import logging
import re
import wave
from asyncio.subprocess import Process

from wyoming.asr import Transcribe, Transcript
from wyoming.audio import AudioChunk, AudioChunkConverter, AudioStop
from wyoming.event import Event
from wyoming.info import Describe, Info
from wyoming.server import AsyncEventHandler

_LOGGER = logging.getLogger(__name__)

# Regex to strip emojis and similar symbols that are not TTS-friendly (e.g. 👾😊✅)
_EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "\U0001F900-\U0001F9FF"  # supplemental symbols (e.g. 👾)
    "\U00002600-\U000026FF"  # misc symbols (e.g. ✅-like)
    "\U00002700-\U000027BF"  # dingbats (e.g. ✅ ✂)
    "]+",
    flags=re.UNICODE,
)


def _strip_emoji(text: str) -> str:
    """Remove emojis and TTS-unfriendly symbols; collapse spaces left behind."""
    if not text:
        return text
    cleaned = _EMOJI_PATTERN.sub(" ", text)
    return " ".join(cleaned.split())


class WhisperCppEventHandler(AsyncEventHandler):
    """Event handler for clients."""

    def __init__(
        self,
        wyoming_info: Info,
        cli_args: argparse.Namespace,
        model_proc: Process,
        model_proc_lock: asyncio.Lock,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.cli_args = cli_args
        self.wyoming_info_event = wyoming_info.event()
        self.model_proc = model_proc
        self.model_proc_lock = model_proc_lock
        self.audio = bytes()
        self.audio_converter = AudioChunkConverter(
            rate=16000,
            width=2,
            channels=1,
        )
        self._language = self.cli_args.language

    async def handle_event(self, event: Event) -> bool:
        if AudioChunk.is_type(event.type):
            if not self.audio:
                _LOGGER.debug("Receiving audio")

            chunk = AudioChunk.from_event(event)
            chunk = self.audio_converter.convert(chunk)
            self.audio += chunk.audio

            return True

        if AudioStop.is_type(event.type):
            _LOGGER.debug("Audio stopped")
            text = ""
            with io.BytesIO() as wav_io:
                wav_file: wave.Wave_write = wave.open(wav_io, "wb")
                with wav_file:
                    wav_file.setframerate(16000)
                    wav_file.setsampwidth(2)
                    wav_file.setnchannels(1)
                    wav_file.writeframes(self.audio)

                wav_io.seek(0)
                wav_bytes = wav_io.getvalue()

                assert self.model_proc.stdin is not None
                assert self.model_proc.stdout is not None

                if self.model_proc.returncode is not None:
                    _LOGGER.error(
                        "Model process already exited (code=%s). Restart the server.",
                        self.model_proc.returncode,
                    )
                    await self.write_event(Transcript(text="").event())
                    self.audio = bytes()
                    return False

                async with self.model_proc_lock:
                    try:
                        request_str = json.dumps(
                            {"size": len(wav_bytes), "language": self._language}
                        )
                        request_line = f"{request_str}\n".encode("utf-8")
                        self.model_proc.stdin.write(request_line)
                        self.model_proc.stdin.write(wav_bytes)
                        await self.model_proc.stdin.drain()

                        lines = []
                        line = (
                            (await self.model_proc.stdout.readline()).decode().strip()
                        )
                        while line != "<|endoftext|>":
                            if line:
                                lines.append(line)
                            line = (
                                (
                                    await self.model_proc.stdout.readline()
                                ).decode().strip()
                            )

                        # Drop lines that are log/error output from the binary (e.g. OpenVINO
                        # exceptions on stdout) so they are not sent as transcript to the client.
                        # Use narrow patterns so dictated words like "error" or "it failed" pass through.
                        transcript_lines = []
                        for ln in lines:
                            low = ln.lower()
                            if (
                                ln.startswith("whisper_")
                                or ln.startswith("main:")
                                or ln.startswith("ggml_")
                                or ln.startswith("system_info:")
                                or "exception:" in low
                                or "could not open" in low
                                or "failed to init" in low
                                or "failed to open" in low
                            ):
                                _LOGGER.debug("Binary log/error line (not transcript): %s", ln[:200])
                                continue
                            transcript_lines.append(ln)
                        text = " ".join(transcript_lines)
                        text = text.replace("[BLANK_AUDIO]", "").strip()
                        if getattr(self.cli_args, "strip_emoji", False):
                            text = _strip_emoji(text)
                    except (ConnectionResetError, BrokenPipeError, OSError) as e:
                        code = self.model_proc.returncode
                        _LOGGER.error(
                            "Model process died (connection lost). exit_code=%s error=%s. Restart the server. If built with OpenVINO, ensure OpenVINO runtime DLLs are on PATH and encoder model files are in --data-dir.",
                            code,
                            e,
                        )
                        text = ""

                _LOGGER.info(text or "(no text)")

                await self.write_event(Transcript(text=text).event())
                _LOGGER.debug("Completed request")

            # Reset
            self.audio = bytes()
            self._language = self.cli_args.language

            return False

        if Transcribe.is_type(event.type):
            transcribe = Transcribe.from_event(event)
            if transcribe.language:
                self._language = transcribe.language
                _LOGGER.debug("Language set to %s", transcribe.language)
            return True

        if Describe.is_type(event.type):
            await self.write_event(self.wyoming_info_event)
            _LOGGER.debug("Sent info")
            return True

        return True
