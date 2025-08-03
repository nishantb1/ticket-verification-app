#!/bin/bash

# Startup script for Render deployment
echo "=== Starting ΔΕΨ Ticket Verifier ==="

# Check if persistent disk is mounted
if [ -d "/var/data" ]; then
    echo "✅ Persistent disk found at /var/data"
    ls -la /var/data/
else
    echo "⚠️  Persistent disk not found at /var/data"
fi

# Check if Tesseract is installed
if command -v tesseract &> /dev/null; then
    echo "✅ Tesseract found: $(tesseract --version | head -n1)"
else
    echo "❌ Tesseract not found"
fi

# Check if poppler-utils is installed
if command -v pdftoppm &> /dev/null; then
    echo "✅ Poppler-utils found"
else
    echo "❌ Poppler-utils not found"
fi

# Set environment variables
export DATABASE_PATH=/var/data/tickets.db
export TESSERACT_CMD=/usr/bin/tesseract

echo "Environment variables:"
echo "DATABASE_PATH=$DATABASE_PATH"
echo "TESSERACT_CMD=$TESSERACT_CMD"

# Start the application
echo "Starting Flask application..."
exec gunicorn app:app --bind 0.0.0.0:$PORT 