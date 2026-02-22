FROM tobix/pyinstaller-windows:python3

# Set working directory
WORKDIR /src

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Command to build and package
# We assume Inno Setup is available in the image or we fallback to zip
CMD ["bash", "-c", "pyinstaller packaging/nandguard_windows.spec --distpath dist/nandguard/windows --noconfirm && (iscc /DAppVersion=$VERSION packaging/windows/nandguard_installer.iss || (mkdir -p drivers/windows && zip -r drivers/windows/NANDGuard+_windows_$VERSION.zip dist/nandguard/windows/))"]
