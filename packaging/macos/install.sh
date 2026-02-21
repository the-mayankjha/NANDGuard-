#!/bin/bash

# NANDGuard+ macOS Setup Script
APP_NAME="NANDGuard+.app"
PLIST_NAME="com.nandguard.plus.plist"

echo "Setting up NANDGuard+ for macOS..."

# 1. Install App (assuming it's built in dist/)
if [ -d "dist/$APP_NAME" ]; then
    echo "Installing $APP_NAME to /Applications..."
    sudo cp -R "dist/$APP_NAME" /Applications/
else
    echo "Error: $APP_NAME not found in dist/. Please build it first."
    exit 1
fi

# 2. Setup LaunchAgent
echo "Installing LaunchAgent..."
mkdir -p ~/Library/LaunchAgents
cp "packaging/macos/$PLIST_NAME" ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/$PLIST_NAME

echo "Successfully installed NANDGuard+ and enabled auto-start."
