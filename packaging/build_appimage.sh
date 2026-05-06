#!/usr/bin/env bash
# =============================================================================
# build_appimage.sh — Build LocalTorrent as a Linux AppImage
# =============================================================================
# Requirements:
#   pip install pyinstaller
#   wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
#   chmod +x appimagetool-x86_64.AppImage
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
APPDIR="${ROOT_DIR}/packaging/AppDir"
DIST_DIR="${ROOT_DIR}/dist"

echo "==> [1/5] Setting up build environment..."
command -v python3 >/dev/null 2>&1 || { echo "ERROR: python3 not found"; exit 1; }

# Use a venv to avoid system-managed Python restrictions (Arch, Ubuntu 23+)
VENV_DIR="${ROOT_DIR}/.venv-build"
if [ ! -d "${VENV_DIR}" ]; then
    echo "    Creating build venv at ${VENV_DIR}..."
    python3 -m venv "${VENV_DIR}"
fi
# shellcheck disable=SC1090
source "${VENV_DIR}/bin/activate"

# Install / upgrade PyInstaller inside venv
pip install --quiet --upgrade pyinstaller
echo "    PyInstaller $(pyinstaller --version) ready."

# Find appimagetool (either in PATH or in packaging/)
APPIMAGETOOL=""
if command -v appimagetool >/dev/null 2>&1; then
    APPIMAGETOOL="appimagetool"
elif [ -f "${SCRIPT_DIR}/appimagetool-x86_64.AppImage" ]; then
    APPIMAGETOOL="${SCRIPT_DIR}/appimagetool-x86_64.AppImage"
else
    echo "WARNING: appimagetool not found. Downloading..."
    wget -q "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage" \
        -O "${SCRIPT_DIR}/appimagetool-x86_64.AppImage"
    chmod +x "${SCRIPT_DIR}/appimagetool-x86_64.AppImage"
    APPIMAGETOOL="${SCRIPT_DIR}/appimagetool-x86_64.AppImage"
fi

echo "==> [2/5] Building PyInstaller binary..."
cd "${ROOT_DIR}"
python3 -m PyInstaller localtorrent.spec --clean --noconfirm

BINARY="${DIST_DIR}/localtorrent"
if [ ! -f "${BINARY}" ]; then
    echo "ERROR: PyInstaller did not produce ${BINARY}"
    exit 1
fi
echo "    Binary: ${BINARY} ($(du -sh "${BINARY}" | cut -f1))"

echo "==> [3/5] Preparing AppDir..."
# Copy binary into AppDir
cp "${BINARY}" "${APPDIR}/localtorrent"
chmod +x "${APPDIR}/localtorrent"
chmod +x "${APPDIR}/AppRun"

# Copy icon (SVG → PNG fallback handled by appimagetool)
if [ -f "${APPDIR}/localtorrent.svg" ]; then
    echo "    Using SVG icon."
elif [ -f "${APPDIR}/localtorrent.png" ]; then
    echo "    Using PNG icon."
else
    echo "    WARNING: No icon found in AppDir. AppImage will be built without one."
fi

echo "==> [4/5] Building AppImage..."
mkdir -p "${DIST_DIR}"
APPIMAGE_OUT="${DIST_DIR}/LocalTorrent-x86_64.AppImage"

ARCH=x86_64 "${APPIMAGETOOL}" "${APPDIR}" "${APPIMAGE_OUT}"
chmod +x "${APPIMAGE_OUT}"

echo "==> [5/5] Done!"
echo ""
echo "    AppImage: ${APPIMAGE_OUT}"
echo "    Size:     $(du -sh "${APPIMAGE_OUT}" | cut -f1)"
echo ""
echo "    Run it with:  ${APPIMAGE_OUT} gui"
