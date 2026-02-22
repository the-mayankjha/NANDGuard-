#!/bin/bash

# NANDGuard+ Linux .deb Build Script
PACKAGE_NAME="nandguard-plus"
VERSION="${1:-1.0.0}"
ARCH="amd64"
BUILD_DIR="packaging/linux/deb_build"

echo "Building .deb package for $PACKAGE_NAME..."

# 1. Create directory structure
mkdir -p $BUILD_DIR/DEBIAN
mkdir -p $BUILD_DIR/usr/bin
mkdir -p $BUILD_DIR/usr/share/applications
mkdir -p $BUILD_DIR/usr/share/pixmaps

# 2. Create Control file
cat <<EOF > $BUILD_DIR/DEBIAN/control
Package: $PACKAGE_NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: $ARCH
Maintainer: NANDGuard Team
Description: AI-Powered Storage Health Monitor
 NANDGuard+ provides proactive background monitoring and 
 failure prediction for NAND storage devices.
EOF

# 3. Copy files (assuming build is in dist/nandguard/linux)
if [ -f "dist/nandguard/linux/NANDGuard+" ]; then
    cp "dist/nandguard/linux/NANDGuard+" $BUILD_DIR/usr/bin/nandguard-plus
else
    echo "Error: Binary dist/nandguard/linux/NANDGuard+ not found."
    exit 1
fi

cp "packaging/linux/nandguard-plus.desktop" $BUILD_DIR/usr/share/applications/
# cp "dashboard/icon.png" $BUILD_DIR/usr/share/pixmaps/nandguard-plus.png

# 4. Build package
DRIVERS_DIR="drivers/linux"
mkdir -p "$DRIVERS_DIR"
dpkg-deb --build $BUILD_DIR "$DRIVERS_DIR/${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"

echo "Package built: $DRIVERS_DIR/${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"
