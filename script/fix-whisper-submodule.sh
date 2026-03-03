#!/bin/sh
# Fix whisper.cpp submodule when "not our ref" or fetch fails.
# Run from repo root: ./script/fix-whisper-submodule.sh
# Then: git add whisper.cpp && git commit -m "fix: point whisper.cpp submodule to v1.8.3"

set -e
cd "$(dirname "$0")/.."
SUBMODULE_PATH="whisper.cpp"
WHISPER_REF="v1.8.3"

if [ -d "$SUBMODULE_PATH" ]; then
  echo "Removing existing whisper.cpp ..."
  rm -rf "$SUBMODULE_PATH"
fi

if [ -d ".git/modules/whisper.cpp" ]; then
  echo "Removing .git/modules/whisper.cpp ..."
  rm -rf .git/modules/whisper.cpp
fi

echo "Cloning whisper.cpp and checking out $WHISPER_REF ..."
if ! git clone --depth 1 --branch "$WHISPER_REF" https://github.com/ggerganov/whisper.cpp.git whisper.cpp; then
  echo "Clone with branch failed. Cloning default and checking out tag..."
  git clone https://github.com/ggerganov/whisper.cpp.git whisper.cpp
  cd whisper.cpp
  git fetch --tags
  git checkout "$WHISPER_REF"
  cd ..
fi

echo "Done. To update the repo's submodule pointer, run:"
echo "  git add whisper.cpp"
echo "  git commit -m \"fix: point whisper.cpp submodule to $WHISPER_REF\""
