@echo off
for /r "packages" %%f in (*.tar) do (
    echo generating checksum for %%f
    python tools\checksum.py "%%f" "%%f.sha256"
)
echo done