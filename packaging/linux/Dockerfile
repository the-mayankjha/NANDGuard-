FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    binutils \
    dpkg-dev \
    libglib2.0-0 \
    libgl1-mesa-glx \
    libqt6gui6 \
    libqt6widgets6 \
    zip \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /src

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir pyinstaller -r requirements.txt

# Command to build and package
CMD ["bash", "-c", "pyinstaller packaging/nandguard.spec --distpath dist/nandguard/linux --noconfirm && bash packaging/linux/build_deb.sh $VERSION"]
