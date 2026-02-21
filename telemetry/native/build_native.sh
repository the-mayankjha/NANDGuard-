#!/bin/bash
# Build script for NANDGuard Native Telemetry Bridge

C_FILE="/Users/mayankjha/Documents/Projects/Hackathon/FSEM/NANDGuard/telemetry/native/mac_nvme.c"
OUTPUT="/Users/mayankjha/Documents/Projects/Hackathon/FSEM/NANDGuard/telemetry/native/mac_nvme"

echo "🔨 Building Native Telemetry Bridge..."

clang -framework IOKit -framework CoreFoundation "$C_FILE" -o "$OUTPUT"

if [ $? -eq 0 ]; then
    echo "✅ Native bridge compiled successfully: $OUTPUT"
    chmod +x "$OUTPUT"
else
    echo "❌ Compilation failed."
    exit 1
fi
