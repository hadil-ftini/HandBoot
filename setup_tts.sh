#!/bin/bash

echo "Starting TTS Setup..."

# Update system
echo "Updating system..."
sudo apt-get update
sudo apt-get upgrade -y

# Install dependencies
echo "Installing dependencies..."
sudo apt-get install -y \
    espeak \
    espeak-ng \
    python3-espeak \
    libespeak1 \
    libespeak-ng1 \
    portaudio19-dev \
    python3-pip \
    python3-pyaudio \
    libttspico-utils

# Install Python packages
echo "Installing Python packages..."
sudo pip3 install pyttsx3

# Configure audio
echo "Configuring audio..."
amixer sset 'Master' 100%
amixer sset 'Master' unmute

# Create test directory
mkdir -p ~/tts_test

# Test espeak directly
echo "Testing espeak..."
espeak "Testing speech synthesis"

# Test Python TTS
echo "Testing Python TTS..."
python3 test_tts.py

echo "Setup complete!"
echo "If you hear audio, the installation was successful." 