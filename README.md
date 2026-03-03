# Wyoming Whisper.cpp

[Wyoming protocol](https://github.com/rhasspy/wyoming) server for the [whisper.cpp](https://github.com/ggerganov/whisper.cpp) speech to text system.

## Local Install

**Ausführliche Anleitung für Linux, WSL2 und Windows:** [INSTALL.md](INSTALL.md)

Install dependencies:

```sh
sudo apt-get install build-essential cmake
```

Clone the repository and set up Python virtual environment:

``` sh
git clone https://github.com/rhasspy/wyoming-whisper-cpp.git --recursive
cd wyoming-whisper-cpp
python -m venv venv
# Linux / WSL2:
source venv/bin/activate
# Windows (PowerShell):
# .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install .
```

Run a server anyone can connect to:
```sh
wyoming-whisper-cpp \
  --model tiny.en-q5_1 \
  --language en \
  --uri 'tcp://0.0.0.0:10300' \
  --data-dir ./data \
  --download-dir ./data
```

## Docker Image

``` sh
docker run -it -p 10300:10300 -v /path/to/local/data:/data rhasspy/wyoming-whisper-cpp \
    --data-dir /data --model tiny.en-q5_1 --language en
```

[Source](https://github.com/rhasspy/wyoming-addons/tree/master/whisper-cpp)

## Platforms: Linux, WSL2, Windows

| Platform | Supported | Notes |
|----------|-----------|--------|
| **Linux** | Yes | Native. Use `source venv/bin/activate`; Vulkan/SYCL/CUDA as documented. |
| **WSL2** | Yes | Same as Linux. For GPU: install Vulkan/GPU stack in WSL2 (e.g. Intel/AMD/NVIDIA drivers for WSL2). |
| **Windows** | Yes | Use `.venv\Scripts\Activate.ps1`; the server uses `whisper-wyoming.exe`. Run `pip install .` from **Developer PowerShell** (VS Build Tools). For **Visual Studio 2026**: `$env:CMAKE_GENERATOR="Visual Studio 18 2026"; pip install .` See [INSTALL.md](INSTALL.md) for details. |

Build requirements: Python 3.7+, CMake 3.16+, and a C++ compiler (e.g. GCC/clang on Linux/WSL2, Visual Studio Build Tools on Windows).

## GPU Support

To build with GPU support, pass the relevant CMake flags to the install command.

### Vulkan (AMD, Intel, NVIDIA)

Works on Intel Arc and Intel integrated GPUs with Vulkan drivers:

``` sh
CMAKE_ARGS="-DGGML_VULKAN=1" pip install .
```

### Intel GPUs (native via SYCL/oneAPI)

For native Intel GPU acceleration (Arc, integrated, Data Center Max/Flex), use SYCL. Requires [Intel oneAPI Base Toolkit](https://www.intel.com/content/www/us/en/developer/tools/oneapi/base-toolkit.html) and (on Windows) Intel DPC++/icx compiler:

``` sh
# Linux (typical)
source /opt/intel/oneapi/setvars.sh
CMAKE_ARGS="-DGGML_SYCL=ON" pip install .

# Windows: use Intel oneAPI environment, then e.g.:
# set CMAKE_ARGS=-DGGML_SYCL=ON
# pip install .
```

### Other backends

- **Core ML (macOS):** `CMAKE_ARGS="-DWHISPER_COREML=1" pip install .`
- **OpenVINO:** `CMAKE_ARGS="-DWHISPER_OPENVINO=1" pip install .`
- **CUDA (NVIDIA):** `CMAKE_ARGS="-DGGML_CUDA=1" pip install .`
