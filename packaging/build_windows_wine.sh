#!/usr/bin/env bash
# =============================================================================
# build_windows_wine.sh — Cross-compile LocalTorrent.exe on Linux using Wine
# =============================================================================
# Requirements:
#   sudo pacman -S wine   (Arch)
#   OR: sudo apt install wine (Ubuntu/Debian)
#
# This script downloads a portable Windows Python into Wine and uses it to
# run PyInstaller, producing a genuine Windows .exe without needing a VM.
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
WINE_DIR="${ROOT_DIR}/.wine-build"
PYTHON_VERSION="3.12.10"
PYTHON_EMBED_URL="https://www.python.org/ftp/python/${PYTHON_VERSION}/python-${PYTHON_VERSION}-embed-amd64.zip"
PIP_URL="https://bootstrap.pypa.io/get-pip.py"

export WINEARCH=win64
export WINEPREFIX="${WINE_DIR}/wineprefix"
export WINEDEBUG=-all   # Suppress Wine debug noise

echo "==> [1/6] Checking Wine..."
command -v wine >/dev/null 2>&1 || {
    echo "ERROR: wine not found."
    echo "  Arch:   sudo pacman -S wine"
    echo "  Ubuntu: sudo apt install wine"
    exit 1
}
wine --version

echo "==> [2/6] Setting up Wine prefix..."
mkdir -p "${WINEPREFIX}"
wineboot --init 2>/dev/null || true

echo "==> [3/6] Downloading Windows Python ${PYTHON_VERSION} (embeddable)..."
PYTHON_DIR="${WINE_DIR}/python"
mkdir -p "${PYTHON_DIR}"
PYTHON_ZIP="${WINE_DIR}/python-embed.zip"

if [ ! -f "${PYTHON_ZIP}" ]; then
    wget -q "${PYTHON_EMBED_URL}" -O "${PYTHON_ZIP}"
fi
unzip -q -o "${PYTHON_ZIP}" -d "${PYTHON_DIR}"

# Enable site-packages in embedded Python
PTH_FILE="${PYTHON_DIR}/python312._pth"
if [ -f "${PTH_FILE}" ]; then
    sed -i 's/#import site/import site/' "${PTH_FILE}"
fi

echo "==> [4/6] Installing pip + PyInstaller in Wine Python..."
GET_PIP="${WINE_DIR}/get-pip.py"
if [ ! -f "${GET_PIP}" ]; then
    wget -q "${PIP_URL}" -O "${GET_PIP}"
fi

WINE_PYTHON="wine ${PYTHON_DIR}/python.exe"
${WINE_PYTHON} "${GET_PIP}" --quiet
${WINE_PYTHON} -m pip install --quiet pyinstaller

echo "==> [5/6] Building Windows EXE with PyInstaller..."
cd "${ROOT_DIR}"
${WINE_PYTHON} -m PyInstaller localtorrent.spec --clean --noconfirm

EXE="${ROOT_DIR}/dist/localtorrent.exe"
if [ ! -f "${EXE}" ]; then
    echo "ERROR: PyInstaller did not produce ${EXE}"
    exit 1
fi

# Rename for clarity
mv "${EXE}" "${ROOT_DIR}/dist/LocalTorrent-Windows.exe"

echo "==> [6/6] Done!"
echo ""
echo "    EXE:  ${ROOT_DIR}/dist/LocalTorrent-Windows.exe"
echo "    Size: $(du -sh "${ROOT_DIR}/dist/LocalTorrent-Windows.exe" | cut -f1)"
echo ""
echo "    Copy this file to a Windows machine and run it directly."
