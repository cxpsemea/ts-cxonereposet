@echo off
pushd "%~dp0"

:: -----------------------------
:: Create cxinventory executable
:: -----------------------------
create-version-file ..\cxoneflow\src\cxonerepositorysetmanifestwindows.yaml --outfile cxonerepositorysetmanifestwindows.txt
pyinstaller --clean --noconfirm --onefile --nowindow --distpath=..\.dist\cxonerepositoryset\windows --workpath=temp --paths=..\shared --version-file=cxonerepositorysetmanifestwindows.txt --icon=..\shared\imaging\icon.ico ..\cxonerepositoryset\cxonerepositoryset.py
copy ..\cxonerepositoryset\src\cxonerepositorysetconfig.yaml ..\.dist\cxonerepositoryset\windows\config.yaml
copy ..\LICENSE ..\.dist\cxonerepositoryset\windows\LICENSE
del cxonerepositorysetmanifestwindows.txt
del cxonerepositoryset.spec
rmdir /s /q temp
powershell Compress-Archive -Force -CompressionLevel Optimal -Path ..\.dist\cxonerepositoryset\windows\* ..\.dist\cxonerepositoryset-win64.zip

popd
