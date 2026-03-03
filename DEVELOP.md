# Developer setup (wyoming-whisper-cpp)

Short guide to initialize the project and develop locally.

## Repo overview (after PR #4)

- **wyoming-whisper-cpp**: Wyoming protocol server that exposes [whisper.cpp](https://github.com/ggerganov/whisper.cpp) as ASR.
- **whisper.cpp** is a **Git submodule** (no longer bundled). The build runs via **scikit-build** on `pip install .` – there is no separate CMake/Make step.
- The **whisper-wyoming** binary is built with the Python package and installed into `wyoming_whisper_cpp/bin/`.
- **GPU support**: OpenVINO, Core ML, etc. via `CMAKE_ARGS` at `pip install` (see README).

## 1. Initialize the project

### Clone with submodule

```powershell
git clone --recursive https://github.com/rhasspy/wyoming-whisper-cpp.git
cd wyoming-whisper-cpp
```

If you already cloned without `--recursive`:

```powershell
git submodule update --init --recursive
```

### Virtualenv and dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
```

On Linux/macOS:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

**Note:** `pip install -e .` builds the whisper.cpp submodule and the **whisper-wyoming** binary via scikit-build. You need CMake and a C++ compiler (on Windows: Visual Studio Build Tools or "Desktop development with C++").

### Dev tools (optional)

```powershell
pip install -r requirements_dev.txt
```

### GPU build (optional)

See [README](README.md):

```powershell
# Vulkan
CMAKE_ARGS="-DGGML_VULKAN=1" pip install .

# OpenVINO (Issue #1)
CMAKE_ARGS="-DWHISPER_OPENVINO=1" pip install .

# Core ML (Issue #2, macOS)
CMAKE_ARGS="-DWHISPER_COREML=1" pip install .
```

## 2. Run the server

There is **no** `--whisper-cpp-dir` anymore; the binary comes from the package.

```powershell
.\.venv\Scripts\Activate.ps1
wyoming-whisper-cpp `
  --model tiny.en-q5_1 `
  --language en `
  --uri 'tcp://0.0.0.0:10300' `
  --data-dir .\local `
  --download-dir .\local
```

Or with `python -m`:

```powershell
python -m wyoming_whisper_cpp --model tiny.en-q5_1 --language en --uri 'tcp://0.0.0.0:10300' --data-dir .\local --download-dir .\local
```

Model download uses the `download-ggml-model.sh` script (installed with the package). On Windows you may need Git Bash or WSL, or place the model manually as `ggml-<model>.bin` in `--data-dir`.

## 3. Tests

```powershell
pytest tests\ -v
```

Tests expect the built **whisper-wyoming** binary and a model (e.g. `tiny-q5_1`) in `local/`.

## 4. Where to add features

| Area | Location | Description |
|------|----------|-------------|
| CLI / server args | `wyoming_whisper_cpp/__main__.py` | Arguments, URI, defaults; invocation of `bin/whisper-wyoming` |
| Wyoming events / transcription | `wyoming_whisper_cpp/handler.py` | Audio → WAV, subprocess, output handling |
| Model download | `wyoming_whisper_cpp/download.py` | Models, paths, `download-ggml-model.sh` |
| Languages / constants | `wyoming_whisper_cpp/const.py` | Supported languages |
| C++ Wyoming binary | `wyoming/` (wyoming.cpp, CMakeLists.txt) | whisper-wyoming executable |
| Version | `wyoming_whisper_cpp/VERSION` | Package version |

## 5. Code quality (dev requirements)

- **Formatting:** `black .` / `isort .`
- **Linting:** `flake8`, `pylint`
- **Types:** `mypy wyoming_whisper_cpp`

---

**PR #4** ("Replace bundled whisper.cpp with submodule") is merged: whisper.cpp is a submodule, build is via scikit-build, GPU options via `CMAKE_ARGS`, no separate build stage.
