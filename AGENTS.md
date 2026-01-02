# AGENTS.md

Instructions for AI coding agents working on this repository.

**Repository**: https://github.com/jkowall/LivePhish-Downloader

## Project Overview

LivePhish Downloader is a browser-automation tool for downloading LivePhish playlists and Stash content. It uses Selenium for browser automation and captures authenticated stream URLs from network traffic.

### Key Files

- `livephish_browser_downloader.py` - Main script with Selenium automation
- `README.md` - User documentation and installation instructions
- `LICENSE` - Apache 2.0 license

### Tech Stack

- **Language**: Python 3.8+
- **Browser Automation**: Selenium with Chrome/ChromeDriver
- **Dependencies**: selenium, webdriver-manager, requests

## Development Guidelines

### Setting Up

```bash
python3 -m venv venv
source venv/bin/activate
pip install selenium webdriver-manager requests
```

### Code Style

- Follow PEP 8 conventions
- Use descriptive variable and function names
- Add docstrings to functions and classes
- Keep functions focused and modular

## Documentation

**Always update documentation when making changes:**

- Update `README.md` when adding/changing CLI options or features
- Update docstrings in the script when changing function behavior
- Keep usage examples current with actual script behavior
- Update version number in script when making significant changes

## Git & Code Signing

**All commits MUST be GPG signed.**

### Configuration

```bash
# Configure GPG signing for this repository
git config user.signingkey <YOUR_GPG_KEY_ID>
git config commit.gpgsign true
```

### Commit Commands

```bash
# Signed commit (automatic if gpgsign is true)
git commit -m "Your message"

# Explicit signed commit
git commit -S -m "Your message"

# Push to remote
git push origin main
```

### Commit Message Format

Use clear, descriptive commit messages:
- `feat: Add new download progress bar`
- `fix: Handle expired stream URLs gracefully`
- `docs: Update installation instructions`
- `refactor: Simplify track detection logic`

## Testing

Before submitting changes:
1. Test the script runs without errors
2. Verify browser automation works correctly
3. Check that downloads complete successfully

## Legal Considerations

- This tool is for personal use with valid LivePhish subscriptions
- Do not add features that circumvent authentication
- Respect rate limits and terms of service
