#!/bin/bash

pushd $(dirname "$0")

# -------------------------------
# GITHUB runner don't support ARM
# GitHub workflow sends "GITHUB-RUNNER"
# parameter if a macos runner is used
# -------------------------------

# -------------------------------------
# Put icon icns file in the same folder
# -------------------------------------
cp ../shared/imaging/icon.icns icon.icns

# -----------------------------
# Create cxinventory executable
# -----------------------------
pyinstaller --clean --noconfirm --onefile --nowindow --distpath=../.dist/cxonerepositoryset/macos ---workpath=temp --paths=../shared --icon=icon.icns ../cxonerepositoryset/cxonerepositoryset.py
cp ../cxonerepositoryset/src/cxonerepositorysetconfig.yaml ../.dist/cxonerepositoryset/macos/config.yaml
cp ../LICENSE ../.dist/cxonerepositoryset/macos/LICENSE
rm -f -r --interactive=never cxonerepositoryset.spec
rm -f -r --interactive=never temp
tar -czvf ../.dist/cxonerepositoryset-macos.tar.gz -C ../.dist/cxonerepositoryset/macos .

popd