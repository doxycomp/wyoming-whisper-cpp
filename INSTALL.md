# Installation Guide – Wyoming Whisper.cpp

This guide describes installation for **Linux**, **WSL2**, and **Windows** step by step.

---

## Prerequisites (all platforms)

- **Python** 3.7 or newer  
- **CMake** 3.16 or newer  
- **C++ compiler** (platform-specific; see below)  
- **Git** (with submodule support)

---

## 1. Linux

### 1.1 Build tools and dependencies

```bash
# Debian/Ubuntu
sudo apt-get update
sudo apt-get install -y build-essential cmake git python3 python3-venv python3-pip

# Fedora
sudo dnf install -y gcc-c++ cmake git python3 python3-pip

# Arch
sudo pacman -S base-devel cmake git python python-pip
```

### 1.2 Clone repository (with submodule)

```bash
git clone https://github.com/rhasspy/wyoming-whisper-cpp.git --recursive
cd wyoming-whisper-cpp
```

If you already cloned without `--recursive` (or get "not our ref" when updating the submodule):

```bash
git submodule update --init --recursive
```

For **"not our ref" / "Direct fetching of that commit failed"**: see **Section 3.2** (Windows); the same fix applies using `script/fix-whisper-submodule.sh`.

### 1.3 Virtual environment and package install

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install .
```

### 1.4 Optional: GPU (Vulkan, Intel SYCL, NVIDIA CUDA)

**Vulkan (AMD, Intel, NVIDIA):**

```bash
CMAKE_ARGS="-DGGML_VULKAN=1" pip install .
```

**Intel SYCL (oneAPI):**

```bash
# Install oneAPI Base Toolkit, then:
source /opt/intel/oneapi/setvars.sh
CMAKE_ARGS="-DGGML_SYCL=ON" pip install .
```

**NVIDIA CUDA:**

```bash
CMAKE_ARGS="-DGGML_CUDA=1" pip install .
```

### 1.5 Start the server

```bash
source venv/bin/activate
wyoming-whisper-cpp \
  --model tiny.en-q5_1 \
  --language en \
  --uri 'tcp://0.0.0.0:10300' \
  --data-dir ./data \
  --download-dir ./data
```

On first run the model is downloaded via script into `./data`. If that fails: [download the model manually](https://huggingface.co/ggerganov/whisper.cpp) and place it as `ggml-<model>.bin` in your `--data-dir`.

---

## 2. WSL2 (Windows Subsystem for Linux)

On WSL2, follow the **Linux** steps. The procedure matches Section 1.

### 2.1 Build tools (in WSL2 shell)

```bash
sudo apt-get update
sudo apt-get install -y build-essential cmake git python3 python3-venv python3-pip
```

### 2.2 Clone, venv, install

```bash
git clone https://github.com/rhasspy/wyoming-whisper-cpp.git --recursive
cd wyoming-whisper-cpp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install .
```

### 2.3 Optional: GPU in WSL2

- **Vulkan:** Use a Vulkan driver in WSL2 (e.g. for Intel/AMD/NVIDIA). Install the driver and optionally `vulkan-utils` in WSL2, then:

  ```bash
  CMAKE_ARGS="-DGGML_VULKAN=1" pip install .
  ```

- **CUDA (NVIDIA):** If using an NVIDIA GPU in WSL2, install the CUDA toolkit in WSL2, then:

  ```bash
  CMAKE_ARGS="-DGGML_CUDA=1" pip install .
  ```

### 2.4 Start the server

Same as Linux (Section 1.5):

```bash
source venv/bin/activate
wyoming-whisper-cpp --model tiny.en-q5_1 --language en --uri 'tcp://0.0.0.0:10300' --data-dir ./data --download-dir ./data
```

---

## 3. Windows (native build)

### 3.1 Install prerequisites

1. **Python 3.7+**  
   From [python.org](https://www.python.org/downloads/) or e.g. Microsoft Store. Enable "Add Python to PATH" during installation.

2. **Visual Studio Build Tools** (C++ compiler)  
   - Download [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)  
   - During setup, select the **"Desktop development with C++"** workload (includes MSVC and Windows SDK).

3. **CMake**  
   - From [cmake.org](https://cmake.org/download/) or e.g. `winget install Kitware.CMake`  
   - CMake should be on your PATH.

4. **Git**  
   - [git-scm.com](https://git-scm.com/download/win) – for cloning and (optionally) model download via Git Bash.

### 3.2 Clone repository (with submodule)

In **PowerShell** or **Command Prompt**:

```powershell
git clone https://github.com/rhasspy/wyoming-whisper-cpp.git --recursive
cd wyoming-whisper-cpp
```

If you already cloned without `--recursive` (or the `whisper.cpp` folder is empty), run this **before** `pip install .`:

```powershell
git submodule update --init --recursive
```

Without this submodule, the build fails with "whisper.cpp does not contain a CMakeLists.txt".

#### Submodule error: "not our ref" / "Direct fetching of that commit failed"

If `git submodule update --init --recursive` fails with **"not our ref"** or **"did not contain … Direct fetching of that commit failed"**, the repo is pointing at a commit that no longer exists in upstream (ggerganov/whisper.cpp). Fix the submodule to a valid ref:

**Windows (PowerShell, in repo root):**

```powershell
.\script\fix-whisper-submodule.ps1
git add whisper.cpp
git commit -m "fix: point whisper.cpp submodule to v1.8.3"
```

**Linux/macOS:**

```bash
chmod +x script/fix-whisper-submodule.sh
./script/fix-whisper-submodule.sh
git add whisper.cpp
git commit -m "fix: point whisper.cpp submodule to v1.8.3"
```

Then run `pip install .` again.

### 3.3 Virtual environment and package install

**Important:** Run `pip install .` from **Developer PowerShell** or **"x64 Native Tools Command Prompt"** for your Visual Studio version (Start menu: e.g. "Developer PowerShell for VS 2022" or "VS 2026"). That ensures the compiler and build tools are on PATH; otherwise you may get "Visual Studio not found" or "Ninja not found".

In **PowerShell** (in the project folder):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install .
```

If execution policy causes errors:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Build error: "Visual Studio not found" / "Ninja not found"

- **Fix 1 – Use developer environment:**  
  Open **"Developer PowerShell for VS 2022"** (or your version, e.g. **"Developer PowerShell for VS 2026"**) from the Start menu. In that window, go to the project folder (`cd C:\path\to\wyoming-whisper-cpp`), activate venv, then run `pip install .`.

- **Fix 2 – Visual Studio 2026 (or newer):**  
  scikit-build looks for VS 2017/2019/2022 by default. For **VS 2026** set the generator explicitly (CMake 4.2+ required for "Visual Studio 18 2026"):

```powershell
$env:CMAKE_GENERATOR = "Visual Studio 18 2026"
pip install .
```

  For **VS 2025** you may need `"Visual Studio 17 2025"` etc. (check [CMake docs](https://cmake.org/cmake/help/latest/manual/cmake-generators.7.html) for generator names).

- **Fix 3 – Ninja:**  
  Install Ninja (`winget install Ninja-build.Ninja`), then in **Developer PowerShell**:

```powershell
$env:CMAKE_GENERATOR = "Ninja"
pip install .
```

#### Build error: "No module named 'skbuild'"

Build dependencies (scikit-build, cmake) must be installed **before** `pip install .`. Run once:

```powershell
pip install -r requirements.txt
```

Then run `pip install .` again (with CMAKE_GENERATOR and CMAKE_ARGS if needed).

#### Build error: "Could not find a package configuration file provided by OpenVINO"

You have `WHISPER_OPENVINO=1` in `CMAKE_ARGS` (or `CMAKE_ARGS` from a previous session), but the OpenVINO toolkit is not installed or CMake cannot find it.

- **To build without OpenVINO:** Unset or clear `CMAKE_ARGS` and install again. For Vulkan only, set e.g. `$env:CMAKE_ARGS = "-DGGML_VULKAN=1"` (and do not include `-DWHISPER_OPENVINO=1`). Then run `pip install .` again.
- **To build with OpenVINO:** Install the [OpenVINO toolkit](https://github.com/openvinotoolkit/openvino/releases), run its `setupvars.bat` (or `setupvars.sh` on Linux), then set `OpenVINO_DIR` to the directory containing `OpenVINOConfig.cmake` and run `pip install .` with `CMAKE_ARGS="-DWHISPER_OPENVINO=1"`.

#### Build error: "Could NOT find Vulkan (missing: Vulkan_LIBRARY Vulkan_INCLUDE_DIR glslc)"

A Vulkan build on Windows requires the **Vulkan SDK**:

1. Download and install the **Vulkan SDK** from [LunarG](https://vulkan.lunarg.com/sdk/home#windows).
2. Open a **new** Developer PowerShell (or new terminal) so the **VULKAN_SDK** environment variable is set (the installer often sets it automatically, e.g. `C:\VulkanSDK\1.3.296.0`).
3. If CMake still cannot find Vulkan, set `VULKAN_SDK` manually, e.g. `$env:VULKAN_SDK = "C:\VulkanSDK\1.3.296.0"` (adjust to your install path), then run `pip install .` again.

#### Build error: "FileTracker FTK1011" / "The system cannot find the path specified" (Vulkan build)

The Vulkan build creates very deep directory trees (e.g. `_skbuild\...\vulkan-shaders-gen-prefix\...`). On Windows the **path length** can exceed the 260-character limit and MSBuild reports FTK1011.

- **Fix 1 – Use a short project path (recommended):**  
  Clone the repo into a short path and build there, e.g.:
  ```powershell
  cd C:\
  git clone https://github.com/rhasspy/wyoming-whisper-cpp.git --recursive w
  cd w
  # create venv, set CMAKE_GENERATOR + CMAKE_ARGS, pip install .
  ```
  Example: `C:\w` instead of a long path like `C:\Users\...\wyoming-whisper-cpp`.

- **Fix 2 – Enable long paths in Windows:**  
  [Enable long paths](https://learn.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation#enable-long-paths-in-windows-10-version-1607-and-later) (Group Policy or Registry `LongPathsEnabled = 1`), then reboot and run the build again.

### 3.4 Optional: GPU (Vulkan, Intel SYCL, CUDA)

**Vulkan (e.g. Intel Arc / integrated Intel GPU):**

On Windows this requires the **Vulkan SDK** (CMake needs Vulkan libs, headers, and the **glslc** shader compiler). See "Could NOT find Vulkan" above.

```powershell
$env:CMAKE_ARGS="-DGGML_VULKAN=1"
pip install .
```

**Intel SYCL (oneAPI):**  
SYCL requires the **Intel DPC++ compiler (icx)**, not MSVC. In a normal PowerShell with Visual Studio the build fails with "C++ compiler lacks SYCL support".

- **Easier for Intel GPU:** Use **Vulkan** instead of SYCL (see above; works with MSVC).
- **SYCL anyway:** Open "Intel oneAPI 2024 command prompt for Intel 64" (or newer) from the Start menu, then in the project folder use Ninja and the Intel compiler:
  ```powershell
  $env:CMAKE_GENERATOR = "Ninja"
  $env:CMAKE_ARGS = "-DGGML_SYCL=ON"
  pip install .
  ```
  In the oneAPI prompt `CC=icx` and `CXX=icpx` are usually set; CMake will then use the Intel compiler for SYCL.

**NVIDIA CUDA:**

```powershell
$env:CMAKE_ARGS="-DGGML_CUDA=1"
pip install .
```

### 3.5 Model (on Windows)

Automatic model download uses a shell script. Options:

- **Option A – Git Bash:**  
  Open Git Bash, go to the project folder, activate venv (e.g. `source venv/Scripts/activate`) and start the server as below. On first run the model will be downloaded.

- **Option B – Manual:**  
  Download the desired model from [Hugging Face (whisper.cpp)](https://huggingface.co/ggerganov/whisper.cpp) (e.g. `ggml-tiny.en-q5_1.bin`) and put it in a folder you use as `--data-dir`.

### 3.6 Start the server

PowerShell (with venv activated):

```powershell
.\venv\Scripts\Activate.ps1
wyoming-whisper-cpp --model tiny.en-q5_1 --language en --uri 'tcp://0.0.0.0:10300' --data-dir .\data --download-dir .\data
```

If the model is already in `.\data` (e.g. `ggml-tiny.en-q5_1.bin`), the server starts without downloading.

---

## Quick reference: First run after install

| Platform | Activate venv           | Start server (example) |
|----------|--------------------------|--------------------------|
| Linux    | `source venv/bin/activate` | `wyoming-whisper-cpp --model tiny.en-q5_1 --language en --uri 'tcp://0.0.0.0:10300' --data-dir ./data --download-dir ./data` |
| WSL2     | same as Linux            | same as Linux             |
| Windows  | `.\venv\Scripts\Activate.ps1` | `wyoming-whisper-cpp --model tiny.en-q5_1 --language en --uri 'tcp://0.0.0.0:10300' --data-dir .\data --download-dir .\data` |

More options: `wyoming-whisper-cpp --help`
