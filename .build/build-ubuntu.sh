#!/bin/bash

pushd $(dirname "$0")

# -----------------------------
# Create cxinventory executable
# -----------------------------
pyinstaller --clean --noconfirm --onefile --nowindow --distpath=../.dist/cxonerepositoryset/ubuntu --workpath=temp --paths=../shared ../cxonerepositoryset/cxonerepositoryset.py
cp ../cxonerepositoryset/src/cxonerepositorysetconfig.yaml ../.dist/cxonerepositoryset/ubuntu/config.yaml
cp ../LICENSE ../.dist/cxonerepositoryset/ubuntu/LICENSE
rm -f -r --interactive=never cxonerepositoryset.spec
rm -f -r --interactive=never temp
tar -czvf ../.dist/cxonerepositoryset-ubuntu64.tar.gz -C ../.dist/cxonerepositoryset/ubuntu .

popd