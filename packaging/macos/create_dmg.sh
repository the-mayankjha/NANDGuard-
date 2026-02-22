#!/bin/bash

# NANDGuard+ Professional DMG Creator
# Uses hdiutil (native macOS) to create a professional drag-and-drop DMG

APP_NAME="NANDGuard+"
VERSION="${1:-1.0.0}"
DMG_NAME="${APP_NAME}_${VERSION}.dmg"
APP_BUNDLE="dist/nandguard/mac/${APP_NAME}.app"
STAGING_DIR="packaging/macos/dmg_staging"
DRIVERS_DIR="drivers/macos"

echo "Creating Professional DMG for ${APP_NAME}..."

# 1. Cleanup
rm -rf "$STAGING_DIR"
mkdir -p "$DRIVERS_DIR"
rm -f "$DRIVERS_DIR/$DMG_NAME"
mkdir -p "$STAGING_DIR"

# 2. Copy App
if [ -d "$APP_BUNDLE" ]; then
    echo "Staging $APP_BUNDLE..."
    cp -R "$APP_BUNDLE" "$STAGING_DIR/"
else
    echo "Error: $APP_BUNDLE not found. Please build with PyInstaller first."
    exit 1
fi

# 3. Create Applications symlink
ln -s /Applications "$STAGING_DIR/Applications"

# 4. Create base DMG
echo "Generating base disk image..."
hdiutil create -volname "${APP_NAME} Installer" -srcfolder "$STAGING_DIR" -ov -format UDZO "packaging/macos/raw.dmg"

# 5. Finalize DMG (Compressed and Read-Only)
echo "Finalizing DMG..."
hdiutil convert "packaging/macos/raw.dmg" -format UDZO -o "$DRIVERS_DIR/$DMG_NAME"
rm "packaging/macos/raw.dmg"

echo "Professional DMG created: $DMG_NAME"
# Note: Further aesthetic refinements (backgrounds, icons positions) 
# usually require AppleScript which is environment-dependent.
