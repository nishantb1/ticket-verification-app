#!/bin/bash
# Build script for Render deployment

echo "Installing Python dependencies..."
pip install -r requirements-deploy.txt

echo "Installing Node.js dependencies..."
cd frontend
npm install

echo "Building React frontend..."
npm run build

echo "Build completed successfully!"