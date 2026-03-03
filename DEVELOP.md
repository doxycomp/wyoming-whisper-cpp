# Entwickler-Setup (wyoming-whisper-cpp)

Kurze Anleitung, um das Projekt zu initialisieren und lokal zu entwickeln.

## Repo-Überblick (nach PR #4)

- **wyoming-whisper-cpp**: Wyoming-Protocol-Server, der [whisper.cpp](https://github.com/ggerganov/whisper.cpp) als ASR anbietet.
- **whisper.cpp** ist ein **Git-Submodul** (nicht mehr gebündelt). Build erfolgt über **scikit-build** beim `pip install .` – es gibt keine separate CMake-/Make-Stufe mehr.
- Die Binary **whisper-wyoming** wird mit dem Python-Paket gebaut und in `wyoming_whisper_cpp/bin/` installiert.
- **GPU-Unterstützung**: OpenVINO, Core ML etc. über `CMAKE_ARGS` beim `pip install` (siehe README).

## 1. Projekt initialisieren

### Klonen mit Submodul

```powershell
git clone --recursive https://github.com/doxycomp/wyoming-whisper-cpp.git
cd wyoming-whisper-cpp
```

Falls schon geklont ohne `--recursive`:

```powershell
git submodule update --init --recursive
```

### Virtualenv + Abhängigkeiten

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
```

Unter Linux/macOS:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

**Hinweis:** `pip install -e .` baut über scikit-build das Submodul whisper.cpp und die **whisper-wyoming**-Binary. Dafür werden CMake und ein C++-Compiler benötigt (unter Windows: Visual Studio Build Tools oder „Desktop development with C++“).

### Dev-Tools (optional)

```powershell
pip install -r requirements_dev.txt
```

### GPU-Build (optional)

Laut [README](README.md):

```powershell
# Vulkan
CMAKE_ARGS="-DGGML_VULKAN=1" pip install .

# OpenVINO (Issue #1)
CMAKE_ARGS="-DWHISPER_OPENVINO=1" pip install .

# Core ML (Issue #2, macOS)
CMAKE_ARGS="-DWHISPER_COREML=1" pip install .
```

## 2. Server starten

Es gibt **kein** `--whisper-cpp-dir` mehr; die Binary kommt aus dem Paket.

```powershell
.\.venv\Scripts\Activate.ps1
wyoming-whisper-cpp `
  --model tiny.en-q5_1 `
  --language en `
  --uri 'tcp://0.0.0.0:10300' `
  --data-dir .\local `
  --download-dir .\local
```

Oder mit `python -m`:

```powershell
python -m wyoming_whisper_cpp --model tiny.en-q5_1 --language en --uri 'tcp://0.0.0.0:10300' --data-dir .\local --download-dir .\local
```

Modell-Download nutzt das Script `download-ggml-model.sh` (wird mit dem Paket installiert). Unter Windows ggf. Git Bash oder WSL nötig, oder Modell manuell als `ggml-<model>.bin` in `--data-dir` legen.

## 3. Tests

```powershell
pytest tests\ -v
```

Die Tests erwarten die gebaute **whisper-wyoming**-Binary und das Modell (z.B. `tiny-q5_1`) in `local/`.

## 4. Wo du Features hinzufügen kannst

| Bereich | Ort | Beschreibung |
|--------|-----|--------------|
| CLI / Server-Args | `wyoming_whisper_cpp/__main__.py` | Argumente, URI, Defaults; Aufruf von `bin/whisper-wyoming` |
| Wyoming-Events / Transkription | `wyoming_whisper_cpp/handler.py` | Audio → WAV, Subprocess, Ausgabe verarbeiten |
| Modell-Download | `wyoming_whisper_cpp/download.py` | Modelle, Pfade, `download-ggml-model.sh` |
| Sprachen / Konstanten | `wyoming_whisper_cpp/const.py` | Unterstützte Sprachen |
| C++ Wyoming-Binary | `wyoming/` (wyoming.cpp, CMakeLists.txt) | whisper-wyoming Executable |
| Version | `wyoming_whisper_cpp/VERSION` | Paketversion |

## 5. Code-Qualität (Dev-Requirements)

- **Formatierung:** `black .` / `isort .`
- **Linting:** `flake8`, `pylint`
- **Typen:** `mypy wyoming_whisper_cpp`

---

**PR #4** („Replace bundled whisper.cpp with submodule“) ist eingebunden: whisper.cpp ist ein Submodul, Build läuft über scikit-build, GPU-Optionen über `CMAKE_ARGS`, keine separate Build-Stufe mehr.
