#!/bin/bash
# Mochi Haven - Installation Script for RG35xx
# Run this on your handheld to set up the game!

echo "🐱 Installing Mochi Haven..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found! Please install Python first."
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 not found! Installing..."
    sudo apt update && sudo apt install -y python3-pip
fi

# Install pygame
echo "📦 Installing pygame..."
pip3 install pygame

# Create game directory
GAME_DIR="$HOME/mochi_haven"
mkdir -p "$GAME_DIR"

# Copy files
echo "📁 Copying game files..."
cp mochi_haven.py "$GAME_DIR/"
cp README.md "$GAME_DIR/"
cp requirements.txt "$GAME_DIR/"

# Create desktop shortcut (if supported)
if [ -d "$HOME/.local/share/applications" ]; then
    echo "🖥️  Creating desktop shortcut..."
    cat > "$HOME/.local/share/applications/mochi_haven.desktop" << EOF
[Desktop Entry]
Name=Mochi Haven
Comment=Cozy catgirl life sim RPG
Exec=python3 $GAME_DIR/mochi_haven.py
Icon=$GAME_DIR/icon.png
Terminal=false
Type=Application
Categories=Game;
EOF
fi

echo "✅ Installation complete!"
echo ""
echo "🎮 How to play:"
echo "   1. Connect to RG35xx via USB"
echo "   2. Copy the 'mochi_haven' folder to /home/retro/ or /usr/local/bin/"
echo "   3. Run: python3 mochi_haven.py"
echo ""
echo "🐱 Or launch from the menu if desktop file was created!"
echo ""
echo "💾 Save files are stored in: ~/.config/mochi_haven/"
