#!/bin/bash

pushd $(dirname "$0")

# -----------------------------
# Create cxinventory executable
# -----------------------------
pyinstaller --clean --noconfirm --onefile --nowindow --distpath=../.dist/cxonerepositoryset/alpine --workpath=temp --paths=../shared ../cxonerepositoryset/cxonerepositoryset.py
cp ../cxonerepositoryset/src/cxonerepositorysetconfig.yaml ../.dist/cxonerepositoryset/alpine/config.yaml
cp ../LICENSE ../.dist/cxonerepositoryset/alpine/LICENSE
rm -f -r cxonerepositoryset.spec
rm -f -r temp
tar -czvf ../.dist/cxonerepositoryset-alpine64.tar.gz -C ../.dist/cxonerepositoryset/alpine .

popd