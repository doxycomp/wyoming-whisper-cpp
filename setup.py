#!/usr/bin/env python3
import os
from pathlib import Path

import setuptools
from skbuild import setup
from setuptools import find_packages

this_dir = Path(__file__).parent
whisper_cpp_cmake = this_dir / "whisper.cpp" / "CMakeLists.txt"
if not whisper_cpp_cmake.is_file():
    raise SystemExit(
        "whisper.cpp submodule is missing or not initialized.\n"
        "Run in the repo root: git submodule update --init --recursive\n"
        "Then run: pip install ."
    )

requirements = []
requirements_path = this_dir / "requirements.txt"
if requirements_path.is_file():
    with open(requirements_path, "r", encoding="utf-8") as requirements_file:
        requirements = requirements_file.read().splitlines()

module_name = "wyoming_whisper_cpp"
module_dir = this_dir / module_name
data_files = []

version_path = module_dir / "VERSION"
data_files.append(version_path)
version = version_path.read_text(encoding="utf-8").strip()

# Add scikit-build as a build requirement
setup_requires = ["scikit-build", "cmake>=3.16"]

# On Windows, allow overriding the CMake generator (e.g. for VS 2026: "Visual Studio 18 2026")
cmake_args = [
    "-DBUILD_SHARED_LIBS=OFF",
    "-DWHISPER_BUILD_STATIC=ON",
    "-DWHISPER_BUILD_EXAMPLES=OFF",
    "-DWHISPER_BUILD_TESTS=OFF",
]
if os.name == "nt" and os.environ.get("CMAKE_GENERATOR"):
    cmake_args.extend(["-G", os.environ["CMAKE_GENERATOR"], "-A", "x64"])

# If building with OpenVINO, help CMake find it when only INTEL_OPENVINO_DIR is set (e.g. after setupvars.bat)
env_cmake_args = os.environ.get("CMAKE_ARGS", "")
if "WHISPER_OPENVINO=1" in env_cmake_args and "OpenVINO_DIR" not in env_cmake_args:
    intel_ov = os.environ.get("INTEL_OPENVINO_DIR")
    if intel_ov:
        ov_cmake = Path(intel_ov) / "runtime" / "cmake"
        if ov_cmake.is_dir():
            cmake_args.append(f"-DOpenVINO_DIR={ov_cmake.resolve()}")
        else:
            ov_cmake_alt = Path(intel_ov) / "cmake"
            if ov_cmake_alt.is_dir():
                cmake_args.append(f"-DOpenVINO_DIR={ov_cmake_alt.resolve()}")

# -----------------------------------------------------------------------------

setup(
    name=module_name,
    version=version,
    description="Wyoming Server for whisper.cpp",
    url="http://github.com/rhasspy/wyoming-whisper-cpp",
    author="Michael Hansen",
    author_email="mike@rhasspy.org",
    license="MIT",
    packages=find_packages(),
    package_data={module_name: [str(p.relative_to(module_dir)) for p in data_files]},
    install_requires=requirements,
    setup_requires=setup_requires,
    cmake_install_dir=module_name,
    cmake_args=cmake_args,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Text Processing :: Linguistic",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="rhasspy wyoming whisper stt",
    scripts=["whisper.cpp/models/download-ggml-model.sh"],
    entry_points={
        "console_scripts": ["wyoming-whisper-cpp = wyoming_whisper_cpp.__main__:run"]
    },
)
