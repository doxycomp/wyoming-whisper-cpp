"""Ensure OpenVINO encoder files exist; run conversion from whisper.cpp when missing."""
import logging
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

_LOGGER = logging.getLogger(__name__)

# Model names supported by convert-whisper-to-openvino.py (strip quantization for mapping)
_OPENVINO_MODEL_NAMES = frozenset({
    "tiny", "tiny.en", "base", "base.en", "small", "small.en",
    "medium", "medium.en", "large-v1", "large-v2", "large-v3", "large-v3-turbo",
})


def _model_stem_to_openvino_name(stem: str) -> Optional[str]:
    """Map ggml model stem to name accepted by convert-whisper-to-openvino.py."""
    # stem is e.g. "ggml-large-v3" or "ggml-large-v3-q5_0"
    name = stem
    if name.startswith("ggml-"):
        name = name[5:]
    # Strip quantization suffix so large-v3-q5_0 -> large-v3
    for suffix in ("-q5_0", "-q5_1", "-q8_0", "-q8_1"):
        if name.endswith(suffix):
            name = name[: -len(suffix)]
            break
    return name if name in _OPENVINO_MODEL_NAMES else None


def _find_convert_script() -> Optional[Path]:
    """Locate whisper.cpp/models/convert-whisper-to-openvino.py (repo or package layout)."""
    # Package dir: .../wyoming_whisper_cpp/__init__.py -> parent is package root
    package_dir = Path(__file__).resolve().parent
    # Repo root may be parent of package dir (when running from source)
    for root in (package_dir.parent, package_dir.parent.parent):
        script = root / "whisper.cpp" / "models" / "convert-whisper-to-openvino.py"
        if script.is_file():
            return script
    return None


def ensure_openvino_encoder(model_path: Path, data_dir: Path) -> bool:
    """
    If the OpenVINO encoder files for the model are missing, try to generate them
    by running whisper.cpp's convert-whisper-to-openvino.py. Returns True if
    encoder exists or was created, False otherwise (no script, conversion failed, or unsupported model).
    """
    model_path = model_path.resolve()
    data_dir = data_dir.resolve()
    stem = model_path.stem  # e.g. ggml-large-v3
    encoder_xml = data_dir / f"{stem}-encoder-openvino.xml"
    if encoder_xml.is_file():
        return True

    openvino_name = _model_stem_to_openvino_name(stem)
    if not openvino_name:
        _LOGGER.debug(
            "OpenVINO encoder auto-convert: model %s not in supported list, skipping",
            stem,
        )
        return False

    script = _find_convert_script()
    if not script:
        _LOGGER.debug(
            "OpenVINO encoder auto-convert: script not found (whisper.cpp/models/), skipping"
        )
        return False

    script_dir = script.parent
    _LOGGER.info(
        "OpenVINO encoder for %s missing; running conversion (this may take a few minutes). Requires: pip install openvino torch openai-whisper",
        stem,
    )
    try:
        proc = subprocess.run(
            [sys.executable, str(script), "--model", openvino_name],
            cwd=script_dir,
            capture_output=True,
            text=True,
            timeout=600,
        )
        if proc.returncode != 0:
            _LOGGER.warning(
                "OpenVINO conversion failed (exit %s). Install deps: pip install openvino torch openai-whisper. %s",
                proc.returncode,
                (proc.stderr or proc.stdout or "")[:400],
            )
            return False

        # Script writes to its own dir (ggml-{openvino_name}-encoder-openvino.*); copy to data_dir with our stem
        generated_xml = script_dir / f"ggml-{openvino_name}-encoder-openvino.xml"
        generated_bin = script_dir / f"ggml-{openvino_name}-encoder-openvino.bin"
        dest_xml = data_dir / f"{stem}-encoder-openvino.xml"
        dest_bin = data_dir / f"{stem}-encoder-openvino.bin"
        if generated_xml.is_file():
            shutil.copy2(generated_xml, dest_xml)
            _LOGGER.info("Copied OpenVINO encoder XML to %s", dest_xml)
        if generated_bin.is_file():
            shutil.copy2(generated_bin, dest_bin)
            _LOGGER.info("Copied OpenVINO encoder BIN to %s", dest_bin)
        return dest_xml.is_file()
    except subprocess.TimeoutExpired:
        _LOGGER.warning("OpenVINO conversion timed out")
        return False
    except Exception as e:
        _LOGGER.warning("OpenVINO conversion error: %s", e)
        return False
