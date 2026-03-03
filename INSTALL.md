# Installationsanleitung – Wyoming Whisper.cpp

Diese Anleitung beschreibt die Installation für **Linux**, **WSL2** und **Windows** Schritt für Schritt.

---

## Voraussetzungen (alle Plattformen)

- **Python** 3.7 oder neuer  
- **CMake** 3.16 oder neuer  
- **C++-Compiler** (plattformspezifisch, siehe unten)  
- **Git** (mit Submodul-Support)

---

## 1. Linux

### 1.1 Build-Tools und Abhängigkeiten

```bash
# Debian/Ubuntu
sudo apt-get update
sudo apt-get install -y build-essential cmake git python3 python3-venv python3-pip

# Fedora
sudo dnf install -y gcc-c++ cmake git python3 python3-pip

# Arch
sudo pacman -S base-devel cmake git python python-pip
```

### 1.2 Repository klonen (mit Submodul)

```bash
git clone https://github.com/rhasspy/wyoming-whisper-cpp.git --recursive
cd wyoming-whisper-cpp
```

Falls bereits ohne `--recursive` geklont (oder Fehler „not our ref“ beim Submodule-Update):

```bash
git submodule update --init --recursive
```

Bei **„not our ref“ / „Direct fetching of that commit failed“**: siehe Abschnitt **3.2** (Windows), dort gleiche Lösung mit `script/fix-whisper-submodule.sh`.

### 1.3 Virtuelle Umgebung und Paket installieren

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
# oneAPI Base Toolkit installieren, dann:
source /opt/intel/oneapi/setvars.sh
CMAKE_ARGS="-DGGML_SYCL=ON" pip install .
```

**NVIDIA CUDA:**

```bash
CMAKE_ARGS="-DGGML_CUDA=1" pip install .
```

### 1.5 Server starten

```bash
source venv/bin/activate
wyoming-whisper-cpp \
  --model tiny.en-q5_1 \
  --language en \
  --uri 'tcp://0.0.0.0:10300' \
  --data-dir ./data \
  --download-dir ./data
```

Beim ersten Start wird das Modell per Skript in `./data` geladen. Bei Problemen: [Modell manuell herunterladen](https://huggingface.co/ggerganov/whisper.cpp) und als `ggml-<modell>.bin` in `--data-dir` ablegen.

---

## 2. WSL2 (Windows Subsystem for Linux)

Unter WSL2 wird wie unter **Linux** vorgegangen. Die Schritte entsprechen Abschnitt 1.

### 2.1 Build-Tools (in der WSL2-Shell)

```bash
sudo apt-get update
sudo apt-get install -y build-essential cmake git python3 python3-venv python3-pip
```

### 2.2 Klonen, venv, Installation

```bash
git clone https://github.com/rhasspy/wyoming-whisper-cpp.git --recursive
cd wyoming-whisper-cpp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install .
```

### 2.3 Optional: GPU in WSL2

- **Vulkan:** In WSL2 einen Vulkan-Treiber nutzen (z. B. für Intel/AMD/NVIDIA). Je nach Hersteller: Treiber und ggf. `vulkan-utils` in WSL2 installieren, dann:

  ```bash
  CMAKE_ARGS="-DGGML_VULKAN=1" pip install .
  ```

- **CUDA (NVIDIA):** Wenn du NVIDIA GPU in WSL2 nutzt: CUDA-Toolkit in WSL2 installieren, dann:

  ```bash
  CMAKE_ARGS="-DGGML_CUDA=1" pip install .
  ```

### 2.4 Server starten

Wie unter Linux (Abschnitt 1.5):

```bash
source venv/bin/activate
wyoming-whisper-cpp --model tiny.en-q5_1 --language en --uri 'tcp://0.0.0.0:10300' --data-dir ./data --download-dir ./data
```

---

## 3. Windows (nativer Build)

### 3.1 Voraussetzungen installieren

1. **Python 3.7+**  
   Von [python.org](https://www.python.org/downloads/) oder z. B. Microsoft Store. Bei der Installation „Add Python to PATH“ aktivieren.

2. **Visual Studio Build Tools** (C++-Compiler)  
   - [Build Tools für Visual Studio](https://visualstudio.microsoft.com/visual-cpp-build-tools/) herunterladen  
   - Bei der Installation die Workload **„Desktopentwicklung mit C++“** auswählen (enthält MSVC und Windows SDK).

3. **CMake**  
   - Von [cmake.org](https://cmake.org/download/) oder z. B. `winget install Kitware.CMake`  
   - CMake soll in der PATH liegen.

4. **Git**  
   - [git-scm.com](https://git-scm.com/download/win) – für Klonen und (optional) Modell-Download per Git Bash.

### 3.2 Repository klonen (mit Submodul)

In **PowerShell** oder **Eingabeaufforderung**:

```powershell
git clone https://github.com/rhasspy/wyoming-whisper-cpp.git --recursive
cd wyoming-whisper-cpp
```

Falls schon ohne `--recursive` geklont (oder der Ordner `whisper.cpp` leer ist), **vor** `pip install .` ausführen:

```powershell
git submodule update --init --recursive
```

Ohne dieses Submodul schlägt der Build mit „whisper.cpp does not contain a CMakeLists.txt“ fehl.

#### Submodule-Fehler: „not our ref“ / „Direct fetching of that commit failed“

Wenn `git submodule update --init --recursive` mit **„not our ref“** oder **„did not contain … Direct fetching of that commit failed“** abbricht, zeigt das Repo auf einen Commit, den es im Upstream (ggerganov/whisper.cpp) nicht mehr gibt. Submodul auf einen gültigen Stand bringen:

**Windows (PowerShell, im Repo-Root):**

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

Danach wieder `pip install .` ausführen.

### 3.3 Virtuelle Umgebung und Paket installieren

**Wichtig:** Führe `pip install .` in der **Developer PowerShell** bzw. **„x64 Native Tools Command Prompt“** deiner Visual-Studio-Version aus (Startmenü: z. B. „Developer PowerShell for VS 2022“ oder „VS 2026“). Dort sind Compiler und Build-Tools in der PATH – sonst schlägt der Build mit „Visual Studio not found“ oder „Ninja not found“ fehl.

In **PowerShell** (im Projektordner):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install .
```

Falls Ausführungsrichtlinien Fehler machen:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Build-Fehler: „Visual Studio not found“ / „Ninja not found“

- **Lösung 1 – Developer-Umgebung nutzen:**  
  Startmenü → **„Developer PowerShell for VS 2022“** (oder deine Version, z. B. **„Developer PowerShell for VS 2026“**) öffnen. In dieses Fenster wechseln, zum Projektordner (`cd C:\git\...\wyoming-whisper-cpp`), venv aktivieren, dann `pip install .` ausführen.

- **Lösung 2 – Visual Studio 2026 (oder neuer):**  
  scikit-build sucht standardmäßig nur nach VS 2017/2019/2022. Bei **VS 2026** den Generator explizit setzen (CMake 4.2+ für „Visual Studio 18 2026“ nötig):

```powershell
$env:CMAKE_GENERATOR = "Visual Studio 18 2026"
pip install .
```

  Bei **VS 2025** ggf. `"Visual Studio 17 2025"` o. Ä. (Generator-Namen in der [CMake-Doku](https://cmake.org/cmake/help/latest/manual/cmake-generators.7.html) prüfen).

- **Lösung 3 – Ninja:**  
  Ninja installieren (`winget install Ninja-build.Ninja`), dann in der **Developer PowerShell**:

```powershell
$env:CMAKE_GENERATOR = "Ninja"
pip install .
```

### 3.4 Optional: GPU (Vulkan, Intel SYCL, CUDA)

**Vulkan (z. B. Intel Arc / integrierte Intel-GPU):**

```powershell
$env:CMAKE_ARGS="-DGGML_VULKAN=1"
pip install .
```

**Intel SYCL (oneAPI):**  
Intel oneAPI Base Toolkit installieren und die „Intel oneAPI command prompt“ bzw. die oneAPI-Umgebung nutzen, dann z. B.:

```powershell
$env:CMAKE_ARGS="-DGGML_SYCL=ON"
pip install .
```

**NVIDIA CUDA:**

```powershell
$env:CMAKE_ARGS="-DGGML_CUDA=1"
pip install .
```

### 3.5 Modell (unter Windows)

Die automatische Modell-Installation nutzt ein Shell-Skript. Eine der Optionen:

- **Option A – Git Bash:**  
  Git Bash öffnen, in den Projektordner wechseln, venv aktivieren (z. B. `source venv/Scripts/activate`) und den Server wie unten starten. Beim ersten Start wird das Modell heruntergeladen.

- **Option B – Manuell:**  
  Gewünschtes Modell von [Hugging Face (whisper.cpp)](https://huggingface.co/ggerganov/whisper.cpp) herunterladen (z. B. `ggml-tiny.en-q5_1.bin`) und in einen Ordner legen, den du als `--data-dir` angibst.

### 3.6 Server starten

PowerShell (venv aktiviert):

```powershell
.\venv\Scripts\Activate.ps1
wyoming-whisper-cpp --model tiny.en-q5_1 --language en --uri 'tcp://0.0.0.0:10300' --data-dir .\data --download-dir .\data
```

Wenn das Modell bereits in `.\data` liegt (z. B. `ggml-tiny.en-q5_1.bin`), startet der Server ohne Download.

---

## Kurzreferenz: Erster Start nach Installation

| Plattform | venv aktivieren           | Server starten (Beispiel) |
|-----------|---------------------------|----------------------------|
| Linux     | `source venv/bin/activate` | `wyoming-whisper-cpp --model tiny.en-q5_1 --language en --uri 'tcp://0.0.0.0:10300' --data-dir ./data --download-dir ./data` |
| WSL2      | wie Linux                 | wie Linux                  |
| Windows   | `.\venv\Scripts\Activate.ps1` | `wyoming-whisper-cpp --model tiny.en-q5_1 --language en --uri 'tcp://0.0.0.0:10300' --data-dir .\data --download-dir .\data` |

Weitere Optionen: `wyoming-whisper-cpp --help`
