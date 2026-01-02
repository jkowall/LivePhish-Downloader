#!/usr/bin/env python3
"""
LivePhish Automated Browser Downloader
Automatically clicks through tracks and downloads them.

Repository: https://github.com/jkowall/LivePhish-Downloader
Author: jkowall
License: Apache 2.0
"""

__version__ = "1.2.0"

import sys
import subprocess

def check_dependencies():
    """Check for required dependencies and offer to install them."""
    missing = []
    
    try:
        import selenium
    except ImportError:
        missing.append("selenium")
    
    try:
        import requests
    except ImportError:
        missing.append("requests")
    
    try:
        import webdriver_manager
    except ImportError:
        missing.append("webdriver-manager")
    
    if missing:
        print("=" * 60)
        print("MISSING DEPENDENCIES")
        print("=" * 60)
        print(f"\nThe following packages are not installed: {', '.join(missing)}")
        print("\nHow would you like to proceed?\n")
        print("  1) Install directly with pip (quick, system-wide)")
        print("  2) Create virtual environment and install (recommended)")
        print("  3) Exit and install manually")
        print()
        
        while True:
            response = input("Enter choice [1/2/3]: ").strip()
            
            if response == '1':
                # Direct pip install
                print("\nInstalling dependencies...")
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
                    print("\n✓ Dependencies installed successfully!")
                    print("Please restart the script.\n")
                except subprocess.CalledProcessError as e:
                    print(f"\n✗ Installation failed: {e}")
                    print("Try option 2 (venv) or install manually.\n")
                sys.exit(0)
                
            elif response == '2':
                # Create venv and install
                import os
                venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv")
                
                print(f"\nCreating virtual environment at: {venv_path}")
                try:
                    subprocess.check_call([sys.executable, "-m", "venv", venv_path])
                    print("✓ Virtual environment created!")
                    
                    # Determine python path in venv (use python -m pip for reliability)
                    if sys.platform == "win32":
                        python_path = os.path.join(venv_path, "Scripts", "python")
                        activate_cmd = f"{venv_path}\\Scripts\\activate"
                    else:
                        python_path = os.path.join(venv_path, "bin", "python")
                        activate_cmd = f"source {venv_path}/bin/activate"
                    
                    print(f"\nInstalling dependencies in venv...")
                    subprocess.check_call([python_path, "-m", "pip", "install"] + missing)
                    print("\n✓ Dependencies installed successfully!")
                    print("\nTo use the script, first activate the virtual environment:")
                    print(f"\n    {activate_cmd}")
                    print("\nThen run the script:")
                    print("\n    python livephish_browser_downloader.py\n")
                    
                except subprocess.CalledProcessError as e:
                    print(f"\n✗ Setup failed: {e}")
                    print("Please install manually.\n")
                sys.exit(0)
                
            elif response == '3':
                print("\nTo install manually, run:")
                print(f"\n    pip install {' '.join(missing)}")
                print("\nOr with a virtual environment:")
                print("\n    python3 -m venv venv")
                print("    source venv/bin/activate  # Linux/macOS")
                print("    venv\\Scripts\\activate     # Windows")
                print(f"    pip install {' '.join(missing)}\n")
                sys.exit(1)
                
            else:
                print("Please enter 1, 2, or 3.")

# Check dependencies before importing
check_dependencies()

import json
import os
import time
import re
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

class AutomatedDownloader:
    def __init__(self, output_dir="downloads"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.driver = None
        self.downloaded_urls = set()
    
    def browser_is_open(self):
        """Check if the browser is still open."""
        if not self.driver:
            return False
        try:
            # Try to access the window handle - will fail if browser is closed
            _ = self.driver.window_handles
            return True
        except Exception:
            return False
        
    def setup_browser(self):
        """Initialize browser with network monitoring"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # Enable network logging
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        os.environ['WDM_LOG_LEVEL'] = '0'
        
        print("Initializing browser...")
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        self.driver.set_window_size(1400, 900)
        print("Browser ready!")
    
    def login_only(self):
        """Navigate to login page and wait for user to log in. Returns False if browser closed."""
        login_url = "https://plus.livephish.com/login"
        print(f"\nNavigating to login page: {login_url}")
        
        try:
            self.driver.get(login_url)
        except Exception:
            print("\n✗ Browser was closed. Exiting.")
            return False
        
        print("\n" + "="*60)
        print("PLEASE LOG IN to LivePhish in the browser window")
        print("="*60)
        
        input("\nPress ENTER after you've logged in...")
        
        # Check if browser is still open
        if not self.browser_is_open():
            print("\n✗ Browser was closed. Exiting.")
            return False
        
        return True
    
    def select_stash_tab(self, tab_type="webcasts"):
        """Select a specific tab on the stash page: 'webcasts', 'shows', or 'playlists'."""
        tab_map = {
            "webcasts": ["My webcasts", "webcasts", "Webcasts"],
            "shows": ["Shows and albums", "shows", "Shows", "albums", "Albums"],
            "playlists": ["My playlists", "playlists", "Playlists"]
        }
        
        search_terms = tab_map.get(tab_type, tab_map["webcasts"])
        print(f"\n  Selecting tab: {tab_type}")
        
        # Try to find and click the tab
        for term in search_terms:
            try:
                # Try finding by text content
                elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{term}')]")
                for el in elements:
                    if el.is_displayed():
                        try:
                            el.click()
                            print(f"  ✓ Clicked tab: {term}")
                            time.sleep(2)
                            return True
                        except:
                            continue
            except:
                continue
        
        # Try by aria-label or other attributes
        selectors = [
            f"[aria-label*='{tab_type}' i]",
            f"button:contains('{tab_type}')",
            f"a[href*='{tab_type}']",
            f"[class*='tab'][class*='{tab_type}' i]",
            f"[role='tab']"
        ]
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for el in elements:
                    if el.is_displayed() and tab_type.lower() in el.text.lower():
                        el.click()
                        print(f"  ✓ Clicked tab via selector")
                        time.sleep(2)
                        return True
            except:
                continue
        
        print(f"  ! Could not find tab: {tab_type}, using default view")
        return False
    
    def navigate_to_stash(self, tab_type=None):
        """Navigate to the stash page. Optionally select a specific tab. Returns False if browser closed."""
        stash_url = "https://plus.livephish.com/stash"
        print(f"\nNavigating to your Stash: {stash_url}")
        
        try:
            self.driver.get(stash_url)
        except Exception:
            print("\n✗ Browser was closed. Exiting.")
            return False
            
        time.sleep(3)
        
        if not self.browser_is_open():
            print("\n✗ Browser was closed. Exiting.")
            return False
        
        # Select specific tab if requested
        if tab_type:
            self.select_stash_tab(tab_type)
        
        return True
        
    def login_and_navigate(self):
        """Navigate to login page, log in, and select a playlist. Returns False if browser closed."""
        if not self.login_only():
            return False
        
        if not self.navigate_to_stash():
            return False
        
        print("\n" + "="*60)
        print("Click on your playlist to open it")
        print("="*60)
        
        input("\nPress ENTER when viewing the playlist with track list visible...")
        
        # Check if browser is still open after playlist selection
        if not self.browser_is_open():
            print("\n✗ Browser was closed. Exiting.")
            return False
        
        return True

    def clear_logs(self):
        """Clear performance logs"""
        try:
            self.driver.get_log('performance')
        except:
            pass
            
    def capture_stream_url(self, timeout=15):
        """Monitor network traffic for Akamai streaming URL"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                logs = self.driver.get_log('performance')
                
                for entry in logs:
                    try:
                        message = json.loads(entry['message'])
                        method = message['message']['method']
                        
                        if method == 'Network.requestWillBeSent':
                            params = message['message']['params']
                            request = params['request']
                            url = request.get('url', '')
                            
                            # Look for Akamai streaming URLs (not clips)
                            if ('akamaized.net' in url or 'nugslpmobile' in url):
                                if ('.m4a' in url or '.flac' in url or '.mp3' in url):
                                    if 'clips' not in url and url not in self.downloaded_urls:
                                        return url
                                        
                    except:
                        continue
                        
                time.sleep(0.2)
                
            except Exception as e:
                break
                
        return None
    
    def find_play_buttons(self):
        """Find all play button elements on the page"""
        # Try multiple selectors for play buttons
        selectors = [
            "button[aria-label*='play' i]",
            "button[aria-label*='Play' i]",
            "[data-testid*='play']",
            ".play-button",
            "button.track-play",
            "[class*='play'][class*='button']",
            "svg[class*='play']",
            # Try finding track rows and their play controls
            "[class*='track'] button",
            "[class*='Track'] button",
            "tr button",
            # Generic icon buttons that might be play
            "button svg",
        ]
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"  Found {len(elements)} elements with selector: {selector}")
                    return elements
            except:
                continue
                
        return []

    def find_track_elements(self):
        """Find track row elements that can be clicked to play"""
        # LivePhish-specific selectors first, then generic
        selectors = [
            # LivePhish specific patterns
            "[class*='TrackList'] [class*='item']",
            "[class*='tracklist'] [class*='item']",
            "[class*='track-list'] [class*='row']",
            "[class*='TrackList'] > div",
            "[class*='playlist-tracks'] > div",
            "[class*='PlaylistTracks'] > div",
            # Data attributes
            "[data-trackid]",
            "[data-track-id]", 
            "[data-index]",
            # Table rows
            "table[class*='track'] tbody tr",
            "[class*='tracks'] table tbody tr",
            # List items
            "[class*='track'][class*='list'] li",
            "[class*='Track'][class*='List'] li",
            "ul[class*='track'] > li",
            # Generic rows/items
            "[class*='track-row']",
            "[class*='TrackRow']",
            "[class*='track-item']",
            "[class*='TrackItem']",
            "[class*='trackItem']",
            # Fallback to any element with track in class
            "div[class*='track']:not([class*='list']):not([class*='List'])",
        ]
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if len(elements) > 1:  # We want multiple tracks, not just one
                    print(f"  Found {len(elements)} track elements with: {selector}")
                    return elements
            except:
                continue
        
        # Debug: print page source snippet to help identify structure
        print("\n  DEBUG: Looking for track elements in page...")
        try:
            # Find any element with 'track' in its class
            all_track_elements = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'track') or contains(@class, 'Track')]")
            if all_track_elements:
                print(f"  Found {len(all_track_elements)} elements with 'track' in class:")
                for i, el in enumerate(all_track_elements[:5]):
                    class_name = el.get_attribute('class')
                    tag = el.tag_name
                    print(f"    {i+1}. <{tag}> class='{class_name[:60]}...'")
        except:
            pass
        
        return []
    
    def find_playlist_elements(self):
        """Find all playlist elements on the stash page. Returns list of (element, name) tuples."""
        print("\nLooking for playlist elements...")
        
        # LivePhish stash page selectors for playlists
        selectors = [
            # Playlist cards/items
            "[class*='PlaylistCard']",
            "[class*='playlist-card']",
            "[class*='StashItem']",
            "[class*='stash-item']",
            "[class*='Playlist'] a",
            "[class*='playlist'] a",
            # Grid/list items that might be playlists
            "[class*='stash'] [class*='card']",
            "[class*='Stash'] [class*='Card']",
            "[class*='library'] [class*='item']",
            "[class*='Library'] [class*='Item']",
            # Generic clickable playlist elements
            "a[href*='/playlist/']",
            "a[href*='/stash/']",
            "[data-playlist-id]",
            "[data-playlistid]",
        ]
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"  Found {len(elements)} playlist elements with: {selector}")
                    # Extract name for each playlist
                    playlists = []
                    for el in elements:
                        try:
                            name = el.text.strip().split('\n')[0][:50] if el.text else "Unnamed Playlist"
                            playlists.append((el, name))
                        except:
                            playlists.append((el, "Unnamed Playlist"))
                    return playlists
            except:
                continue
        
        # Debug: try to find any clickable items
        print("\n  DEBUG: Looking for playlist-like elements...")
        try:
            all_playlist_elements = self.driver.find_elements(
                By.XPATH, 
                "//*[contains(@class, 'playlist') or contains(@class, 'Playlist') or contains(@class, 'stash') or contains(@class, 'Stash')]"
            )
            if all_playlist_elements:
                print(f"  Found {len(all_playlist_elements)} elements with playlist/stash in class:")
                for i, el in enumerate(all_playlist_elements[:5]):
                    class_name = el.get_attribute('class') or ''
                    tag = el.tag_name
                    text = el.text[:30] if el.text else '(no text)'
                    print(f"    {i+1}. <{tag}> class='{class_name[:40]}' text='{text}'")
        except:
            pass
        
        return []
    
    def click_element_safely(self, element):
        """Try multiple methods to click an element"""
        try:
            # Try regular click
            element.click()
            return True
        except:
            pass
            
        try:
            # Try JavaScript click
            self.driver.execute_script("arguments[0].click();", element)
            return True
        except:
            pass
            
        try:
            # Try action chains
            ActionChains(self.driver).move_to_element(element).click().perform()
            return True
        except:
            pass
            
        return False

    def download_file(self, url, filename):
        """Download a file from URL"""
        filepath = os.path.join(self.output_dir, filename)
        
        if os.path.exists(filepath):
            print(f"  File already exists: {filename}")
            return True
            
        print(f"  Downloading: {filename}")
        try:
            response = requests.get(url, stream=True, timeout=300)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=65536):
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        mb = downloaded / (1024*1024)
                        print(f"    {mb:.1f} MB ({percent:.1f}%)", end='\r')
            
            mb = downloaded / (1024*1024)
            print(f"\n  ✓ Downloaded: {filename} ({mb:.1f} MB)")
            self.downloaded_urls.add(url)
            return True
            
        except Exception as e:
            print(f"\n  ✗ Download failed: {e}")
            if os.path.exists(filepath):
                os.remove(filepath)
            return False

    def extract_filename(self, url, track_num, track_name=None):
        """Extract or generate filename from URL"""
        # URL format: .../ph251228d1_07_Sigma_Oasis.m4a?...
        match = re.search(r'/(ph\d+[^/]*?)\.(m4a|flac|mp3)', url)
        if match:
            base_name = match.group(1)
            ext = match.group(2)
            # Clean up the name
            name = base_name.replace('_', ' ').replace('  ', ' ')
            return f"{track_num:02d} - {name}.{ext}"
        else:
            ext = "m4a"
            if '.flac' in url:
                ext = "flac"
            elif '.mp3' in url:
                ext = "mp3"
            name = track_name or f"Track"
            return f"{track_num:02d} - {name}.{ext}"
    
    def download_playlist_auto(self):
        """Automatically download all tracks from the playlist"""
        self.setup_browser()
        
        try:
            if not self.login_and_navigate():
                return
            
            # Give page time to fully load
            time.sleep(3)
            
            # Find track elements initially to get count
            print("\nLooking for track elements...")
            tracks = self.find_track_elements()
            
            if not tracks:
                print("Could not find track elements automatically.")
                print("Let's try finding play buttons instead...")
                tracks = self.find_play_buttons()
            
            if not tracks:
                print("\nCould not find tracks automatically.")
                print("Falling back to interactive mode...")
                self.download_interactive()
                return
            
            total_tracks = len(tracks)
            print(f"\nFound {total_tracks} tracks")
            print("="*60)
            print("STARTING AUTOMATED DOWNLOAD")
            print("="*60)
            
            successful = 0
            failed = 0
            track_num = 0
            
            while track_num < total_tracks:
                # Re-find track elements each iteration (they may have changed)
                tracks = self.find_track_elements()
                if not tracks:
                    tracks = self.find_play_buttons()
                
                if track_num >= len(tracks):
                    print(f"Track {track_num + 1} no longer found, stopping...")
                    break
                
                track = tracks[track_num]
                print(f"\n[{track_num + 1}/{total_tracks}] Processing track...")
                
                # Clear previous network logs
                self.clear_logs()
                
                # Try to get track name if visible
                track_name = None
                try:
                    track_name = track.text.split('\n')[0][:50]
                    if track_name:
                        print(f"  Track: {track_name}")
                except:
                    pass
                
                # Scroll element into view
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", track)
                    time.sleep(0.5)
                except:
                    pass
                
                # Double-click to play
                print(f"  Clicking on track...")
                try:
                    ActionChains(self.driver).double_click(track).perform()
                except:
                    if not self.click_element_safely(track):
                        print(f"  ✗ Could not click track {track_num + 1}")
                        failed += 1
                        track_num += 1
                        continue
                
                # Wait for playback to start and capture URL
                print(f"  Waiting for stream URL...")
                time.sleep(2)  # Give player time to initiate
                
                url = self.capture_stream_url(timeout=15)
                
                if url:
                    filename = self.extract_filename(url, track_num + 1, track_name)
                    if self.download_file(url, filename):
                        successful += 1
                    else:
                        failed += 1
                else:
                    print(f"  ✗ No stream URL captured for track {track_num + 1}")
                    failed += 1
                
                track_num += 1
                
                # Brief pause between tracks
                time.sleep(1)
            
            print("\n" + "="*60)
            print(f"DOWNLOAD COMPLETE")
            print(f"  Successful: {successful}")
            print(f"  Failed: {failed}")
            print(f"  Total: {total_tracks}")
            print("="*60)
                
        finally:
            print("\nClosing browser...")
            if self.driver:
                self.driver.quit()

    def download_all_playlists(self, tab_type=None):
        """Download all tracks from all playlists in the stash"""
        self.setup_browser()
        base_output_dir = self.output_dir
        
        try:
            # Login and navigate to stash
            if not self.login_only():
                return
            
            if not self.navigate_to_stash(tab_type=tab_type):
                return
            
            # Find all playlists
            playlists = self.find_playlist_elements()
            
            if not playlists:
                print("\nCould not find any playlists. Please try single playlist mode.")
                print("Run: python livephish_browser_downloader.py")
                return
            
            total_playlists = len(playlists)
            print(f"\nFound {total_playlists} playlists")
            print("="*60)
            print("STARTING DOWNLOAD OF ALL PLAYLISTS")
            print("="*60)
            
            all_results = []
            
            for playlist_idx, (playlist_el, playlist_name) in enumerate(playlists):
                print(f"\n{'='*60}")
                print(f"PLAYLIST [{playlist_idx + 1}/{total_playlists}]: {playlist_name}")
                print("="*60)
                
                # Create subdirectory for this playlist
                safe_name = re.sub(r'[<>:"/\\|?*]', '_', playlist_name).strip()
                if not safe_name:
                    safe_name = f"playlist_{playlist_idx + 1}"
                playlist_dir = os.path.join(base_output_dir, safe_name)
                os.makedirs(playlist_dir, exist_ok=True)
                self.output_dir = playlist_dir
                
                # Re-find playlists (page may have changed)
                if playlist_idx > 0:
                    if not self.navigate_to_stash(tab_type=tab_type):
                        print("  ✗ Could not navigate back to stash")
                        continue
                    time.sleep(2)
                    playlists = self.find_playlist_elements()
                    if playlist_idx >= len(playlists):
                        print(f"  ✗ Playlist {playlist_idx + 1} no longer found")
                        continue
                    playlist_el, _ = playlists[playlist_idx]
                
                # Click on playlist
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", playlist_el)
                    time.sleep(0.5)
                    if not self.click_element_safely(playlist_el):
                        print(f"  ✗ Could not click playlist: {playlist_name}")
                        all_results.append((playlist_name, 0, 0))
                        continue
                except Exception as e:
                    print(f"  ✗ Error clicking playlist: {e}")
                    all_results.append((playlist_name, 0, 0))
                    continue
                
                time.sleep(3)  # Wait for playlist to load
                
                if not self.browser_is_open():
                    print("\n✗ Browser was closed. Exiting.")
                    break
                
                # Find and download tracks
                tracks = self.find_track_elements()
                if not tracks:
                    tracks = self.find_play_buttons()
                
                if not tracks:
                    print(f"  No tracks found in playlist: {playlist_name}")
                    all_results.append((playlist_name, 0, 0))
                    continue
                
                total_tracks = len(tracks)
                print(f"  Found {total_tracks} tracks in this playlist")
                
                successful = 0
                failed = 0
                track_num = 0
                
                while track_num < total_tracks:
                    # Re-find tracks each time (DOM may have changed)
                    tracks = self.find_track_elements()
                    if not tracks:
                        tracks = self.find_play_buttons()
                    
                    if track_num >= len(tracks):
                        print(f"  Track {track_num + 1} no longer found, moving to next playlist...")
                        break
                    
                    track = tracks[track_num]
                    print(f"\n  [{track_num + 1}/{total_tracks}] Processing track...")
                    
                    self.clear_logs()
                    
                    # Get track name
                    track_name = None
                    try:
                        track_name = track.text.split('\n')[0][:50]
                        if track_name:
                            print(f"    Track: {track_name}")
                    except:
                        pass
                    
                    # Click track
                    try:
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", track)
                        time.sleep(0.5)
                        ActionChains(self.driver).double_click(track).perform()
                    except:
                        if not self.click_element_safely(track):
                            failed += 1
                            track_num += 1
                            continue
                    
                    time.sleep(2)
                    url = self.capture_stream_url(timeout=15)
                    
                    if url:
                        filename = self.extract_filename(url, track_num + 1, track_name)
                        if self.download_file(url, filename):
                            successful += 1
                        else:
                            failed += 1
                    else:
                        print(f"    ✗ No stream URL captured")
                        failed += 1
                    
                    track_num += 1
                    time.sleep(1)
                
                all_results.append((playlist_name, successful, failed))
                print(f"\n  Playlist complete: {successful} successful, {failed} failed")
            
            # Final summary
            print("\n" + "="*60)
            print("ALL PLAYLISTS DOWNLOAD COMPLETE")
            print("="*60)
            total_successful = sum(r[1] for r in all_results)
            total_failed = sum(r[2] for r in all_results)
            print(f"\nSummary:")
            for name, succ, fail in all_results:
                print(f"  {name}: {succ} successful, {fail} failed")
            print(f"\nTotal: {total_successful} successful, {total_failed} failed across {len(all_results)} playlists")
            print("="*60)
            
        finally:
            print("\nClosing browser...")
            if self.driver:
                self.driver.quit()

    def download_interactive(self):
        """Fallback interactive mode"""
        track_num = 1
        
        print("\n" + "="*60)
        print("INTERACTIVE MODE")
        print("="*60)
        print("\nFor each track:")
        print("  1. Double-click the track to play")
        print("  2. Press ENTER here")
        print("\nType 'done' when finished")
        print("="*60)
        
        while True:
            self.clear_logs()
            response = input(f"\nTrack #{track_num} - Play track and press ENTER (or 'done'): ")
            
            if response.lower() == 'done':
                print("\n✓ All done!")
                break
            
            url = self.capture_stream_url(timeout=15)
            
            if url:
                filename = self.extract_filename(url, track_num)
                if self.download_file(url, filename):
                    track_num += 1
            else:
                print("  ✗ Could not capture stream URL. Make sure track is playing.")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="LivePhish Automated Downloader")
    parser.add_argument("--output", default="downloads", help="Output directory")
    parser.add_argument("--interactive", action="store_true", help="Use interactive mode")
    parser.add_argument("--all", action="store_true", dest="download_all",
                        help="Download all playlists from your stash")
    parser.add_argument("--type", choices=["webcasts", "shows", "playlists"], default="playlists",
                        dest="stash_type", help="Which stash tab to use (default: playlists)")
    
    args = parser.parse_args()
    
    downloader = AutomatedDownloader(output_dir=args.output)
    
    if args.download_all:
        downloader.download_all_playlists(tab_type=args.stash_type)
    elif args.interactive:
        downloader.setup_browser()
        if not downloader.login_and_navigate():
            return
        downloader.download_interactive()
    else:
        downloader.download_playlist_auto()


if __name__ == "__main__":
    main()
