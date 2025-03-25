# Shell Script  text file containing terminal commands

echo "Starting Audio Setup..."

# Update system
echo "Updating system..."
sudo apt-get update
sudo apt-get upgrade -y

# Install audio and microphone dependencies
echo "Installing dependencies..."
sudo apt-get install -y \
    alsa-utils \
    pulseaudio \
    pulseaudio-utils \
    portaudio19-dev \
    python3-pyaudio \
    python3-pip \
    espeak \
    espeak-ng \
    python3-espeak \
    libespeak1 \
    libespeak-ng1

# Install Python packages
echo "Installing Python packages..."
sudo pip3 install \
    pyaudio \
    wave \
    SpeechRecognition \
    pyttsx3

# Configure audio
echo "Configuring audio..."
# Unmute and set volume
amixer sset 'Master' 100%
amixer sset 'Master' unmute
# If using USB microphone, unmute input
amixer sset 'Capture' 100%
amixer sset 'Capture' cap

# Add user to audio group
sudo usermod -a -G audio $USER

# Test audio setup
echo "Testing audio setup..."

# List audio devices
echo "Available audio devices:"
arecord -l
aplay -l

# Test microphone
echo "Testing microphone..."
python3 test_mic.py

echo "Setup complete!"
echo "If you see your microphone listed and the tests passed, the setup was successful."
echo "If you encountered any errors, please check your microphone connection and try again." 