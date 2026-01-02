# LivePhish Downloader

A browser-automation tool for downloading your LivePhish playlists and Stash content.

## Features

- **Automated Downloads**: Automatically clicks through tracks and captures stream URLs
- **Browser-Based**: Uses Selenium to interact with LivePhish like a real user
- **Network Capture**: Monitors browser traffic to capture authenticated stream URLs
- **Progress Tracking**: Shows download progress for each track
- **Cross-Platform**: Works on macOS, Windows, and Linux

## Prerequisites

- Python 3.8+
- Google Chrome browser
- Active LivePhish subscription

## Installation

### macOS

```bash
# Install Python (if not installed)
brew install python

# Clone the repository
git clone https://github.com/jkowall/LivePhish-Downloader.git
cd LivePhish-Downloader

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install selenium webdriver-manager requests
```

### Linux (Ubuntu/Debian)

```bash
# Install Python and Chrome
sudo apt update
sudo apt install python3 python3-venv python3-pip google-chrome-stable

# Clone the repository
git clone https://github.com/jkowall/LivePhish-Downloader.git
cd LivePhish-Downloader

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install selenium webdriver-manager requests
```

### Linux (Fedora/RHEL)

```bash
# Install Python
sudo dnf install python3 python3-pip

# Install Chrome
sudo dnf install google-chrome-stable

# Clone the repository
git clone https://github.com/jkowall/LivePhish-Downloader.git
cd LivePhish-Downloader

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install selenium webdriver-manager requests
```

### Windows

```powershell
# Install Python from https://www.python.org/downloads/
# Make sure to check "Add Python to PATH" during installation

# Install Chrome from https://www.google.com/chrome/

# Clone the repository (or download ZIP)
git clone https://github.com/jkowall/LivePhish-Downloader.git
cd LivePhish-Downloader

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install selenium webdriver-manager requests
```

## Usage

### macOS / Linux

```bash
source venv/bin/activate
python livephish_browser_downloader.py
```

### Windows

```powershell
venv\Scripts\activate
python livephish_browser_downloader.py
```

### How It Works

1. **Browser opens** → Log in to LivePhish
2. **Navigate to Stash** → Click on your playlist
3. **Press ENTER** → Script automatically downloads all tracks
4. **Done!** → Files saved to `downloads/` folder

### Options

```bash
# Download all playlists automatically
python livephish_browser_downloader.py --all

# Download all from a specific stash tab (webcasts, shows, or playlists)
python livephish_browser_downloader.py --all --type shows

# Custom output directory
python livephish_browser_downloader.py --output my_music

# Interactive mode (manual track selection)
python livephish_browser_downloader.py --interactive
```

When using `--all`, each playlist is saved to its own subdirectory (e.g., `downloads/Winter 2026/`).

## File Naming

Downloaded files are named:
```
01 - ph251228d1 07 Sigma Oasis.m4a
02 - ph251228d1 08 Simple.m4a
```

Format: `{track_num} - {original_filename}.{ext}`

## Troubleshooting

### "Could not find track elements"
- Make sure you're on the playlist page with tracks visible
- Try scrolling to ensure tracks are loaded
- Falls back to interactive mode if needed

### Downloads fail
- Check your internet connection
- Ensure you have an active subscription
- Try running again - the signed URLs may have expired

### Browser doesn't open
- Make sure Chrome is installed
- Check that chromedriver can be installed automatically

### Windows: chromedriver issues
- Run as Administrator if permission errors occur
- Ensure Chrome is up to date

### macOS: Security warning
- If blocked, go to System Preferences → Security & Privacy → Allow

## Legal Disclaimer

This tool is for personal use only. You must have an active LivePhish subscription to download content. Please respect copyright and the terms of service.

## License

Apache 2.0 - See [LICENSE](LICENSE) file
