"""Utility for downloading models."""
import os
import subprocess
import sys
from pathlib import Path
from typing import Union
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

WHISPER_CPP_MODELS = [
    "tiny",
    "tiny.en",
    "tiny-q5_1",
    "tiny.en-q5_1",
    "base",
    "base.en",
    "base-q5_1",
    "base.en-q5_1",
    "small",
    "small.en",
    "small-q5_1",
    "small.en-q5_1",
    "medium",
    "medium.en",
    "medium-q5_0",
    "medium.en-q5_0",
    "large-v1",
    "large-v2",
    "large-v2-q5_0",
    "large-v3",
    "large-v3-q5_0",
]


def model_name_to_path(model_name: str, dest_dir: Union[str, Path]) -> Path:
    return Path(dest_dir) / f"ggml-{model_name}.bin"


def _download_model_python(model_name: str, dest_dir: Path) -> None:
    """Download ggml model from Hugging Face using Python (works on Windows)."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = dest_dir / f"ggml-{model_name}.bin"
    if dest_file.is_file():
        return

    if "tdrz" in model_name.lower():
        base_url = "https://huggingface.co/akashmjn/tinydiarize-whisper.cpp/resolve/main"
    else:
        base_url = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main"
    url = f"{base_url}/ggml-{model_name}.bin"

    print(f"Downloading {model_name} from {base_url} ...", file=sys.stderr)
    try:
        with urlopen(url) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            chunk_size = 1024 * 1024
            downloaded = 0
            with open(dest_file, "wb") as f:
                while True:
                    chunk = resp.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total and total > 0:
                        pct = 100 * downloaded / total
                        print(f"\r  {downloaded // (1024*1024)} MiB / {total // (1024*1024)} MiB ({pct:.0f}%)", end="", file=sys.stderr)
        if total:
            print(file=sys.stderr)
        print(f"Saved to {dest_file}", file=sys.stderr)
    except (URLError, HTTPError) as e:
        dest_file.unlink(missing_ok=True)
        raise RuntimeError(f"Failed to download {model_name}: {e}") from e


def download_model(
    model_name: str,
    dest_dir: Union[str, Path],
) -> None:
    """Downloads whisper.cpp model (script on Unix, Python on Windows)."""
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)

    if os.name == "nt":
        _download_model_python(model_name, dest_dir)
        return

    # On Unix, try the shell script first (from PATH when installed)
    try:
        subprocess.check_call(
            ["download-ggml-model.sh", str(model_name), str(dest_dir)],
        )
    except (FileNotFoundError, OSError):
        _download_model_python(model_name, dest_dir)
