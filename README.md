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

**Windows:** Install the [Vulkan SDK](https://vulkan.lunarg.com/sdk/home#windows) first so CMake finds Vulkan and **glslc**. Then open a new terminal and run the install. See [INSTALL.md](INSTALL.md) if you get "Could NOT find Vulkan".

### Intel GPUs

- **Vulkan (recommended on Windows):** Works with the normal MSVC build; no extra toolchain:
  ``` sh
  CMAKE_ARGS="-DGGML_VULKAN=1" pip install .
  ```
- **SYCL (oneAPI):** Native Intel acceleration. Requires the **Intel DPC++ compiler (icx)** – on Windows, use the **Intel oneAPI Command Prompt** and e.g. `CMAKE_GENERATOR=Ninja` and `CMAKE_ARGS="-DGGML_SYCL=ON"`. Without the oneAPI environment you get "C++ compiler lacks SYCL support"; use Vulkan or build from the oneAPI prompt. See [INSTALL.md](INSTALL.md).

### Other backends

- **Core ML (macOS):** `CMAKE_ARGS="-DWHISPER_COREML=1" pip install .`
- **OpenVINO:** `CMAKE_ARGS="-DWHISPER_OPENVINO=1" pip install .`
- **CUDA (NVIDIA):** `CMAKE_ARGS="-DGGML_CUDA=1" pip install .`

### Flash Attention

When using **CUDA** or **Metal**, you can enable Flash Attention at runtime for faster inference. Start the server with:

```sh
wyoming-whisper-cpp ... --flash-attn
```

Or pass it through: `--whisper-cpp-args "--flash-attn"`. Flash Attention support is included in CUDA/Metal builds of whisper.cpp (v1.6+).
