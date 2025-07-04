#!/usr/bin/env python3
"""
CLI tool to test all parts of the PC Builder project: backend, frontend, and scraper.
- Checks backend container and API
- Checks frontend dev server
- Checks S3/CSV data
- Optionally runs the scraper
"""
import subprocess  # nosec B404 - Used with validation and security controls
import requests
import sys
import time
import shutil
import os.path

# ANSI color codes
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"

BACKEND_URL = "http://localhost:8000/graphic-cards"
FRONTEND_URL = "http://localhost:4200"

def cprint(msg, color=RESET, emoji=""):
    print(f"{color}{emoji} {msg}{RESET}")

def check_backend():
    cprint("[Test] Checking backend container...", CYAN, "🐳")
    docker_running = False
    try:
        # Ensure docker exists before running command
        if shutil.which("docker"):
            out = subprocess.check_output(["docker", "ps"], text=True)  # nosec
            if "pc-builder-backend-dev" in out:
                cprint("[OK] Backend container is running.", GREEN, "✅")
                docker_running = True
            else:
                cprint("[INFO] Backend container not running, checking direct Python execution...", YELLOW, "ℹ️")
        else:
            cprint("[INFO] Docker command not found in PATH", YELLOW, "ℹ️")
    except Exception as e:
        cprint(f"[INFO] Docker not available or error: {e}", YELLOW, "ℹ️")
    
    cprint("[Test] Checking backend API response...", CYAN, "🔌")
    try:
        resp = requests.get(BACKEND_URL, timeout=5)
        if resp.status_code == 200 and isinstance(resp.json(), list):
            if docker_running:
                cprint(f"[OK] Backend API (Docker) returned {len(resp.json())} cards.", GREEN, "✅")
            else:
                cprint(f"[OK] Backend API (Python) returned {len(resp.json())} cards.", GREEN, "✅")
            if not resp.json():
                cprint("[WARN] Backend API returned an empty list. Check S3 CSV data.", YELLOW, "⚠️")
            return True
        else:
            cprint(f"[FAIL] Backend API error: {resp.status_code}", RED, "❌")
            return False
    except Exception as e:
        cprint(f"[FAIL] Could not connect to backend API: {e}", RED, "❌")
        return False

def check_frontend():
    cprint("[Test] Checking frontend dev server...", CYAN, "🌐")
    try:
        resp = requests.get(FRONTEND_URL, timeout=5)
        if resp.status_code == 200:
            cprint("[OK] Frontend dev server is running.", GREEN, "✅")
            return True
        else:
            cprint(f"[FAIL] Frontend server error: {resp.status_code}", RED, "❌")
            return False
    except Exception as e:
        cprint(f"[FAIL] Could not connect to frontend: {e}", RED, "❌")
        return False

def check_scraper():
    cprint("[Test] Running scraper (dry run)...", CYAN, "🕷️")
    try:
        # Validate paths before execution
        scraper_dir = "pc-builder/pc-builder-scraper"
        if os.path.isdir(scraper_dir):
            # Using sys.executable ensures we use the correct Python interpreter
            out = subprocess.check_output([  # nosec
                sys.executable, "-m", "scraper.main"
            ], cwd=scraper_dir, text=True, timeout=60)
            cprint("[OK] Scraper ran successfully.", GREEN, "✅")
            return True
        else:
            cprint(f"[FAIL] Scraper directory not found: {scraper_dir}", RED, "❌")
            return False
    except Exception as e:
        cprint(f"[FAIL] Scraper failed: {e}", RED, "❌")
        return False

def check_images():
    cprint("[Test] Checking image retrieval...", CYAN, "🖼️")
    try:
        resp = requests.get(BACKEND_URL, timeout=5)
        if resp.status_code != 200 or not resp.json():
            cprint("[FAIL] Cannot get graphics cards for image testing", RED, "❌")
            return False
        
        cards = resp.json()
        images_tested = 0
        images_working = 0
        
        for card in cards[:5]:
            if card.get('imageUrl'):
                image_url = card['imageUrl']
                if 'cdn-images/' in image_url:
                    filename = image_url.split('cdn-images/')[-1]
                    test_url = f"http://localhost:8000/images/{filename}"
                    try:
                        img_resp = requests.get(test_url, timeout=5, allow_redirects=True)
                        images_tested += 1
                        if img_resp.status_code == 200:
                            images_working += 1
                            cprint(f"[OK] Image {filename}: {img_resp.status_code}", GREEN, "🟢")
                        else:
                            cprint(f"[WARN] Image {filename}: {img_resp.status_code}", YELLOW, "🟡")
                    except Exception as e:
                        images_tested += 1
                        cprint(f"[WARN] Image {filename}: Error {e}", YELLOW, "🟡")
        
        if images_tested == 0:
            cprint("[WARN] No images found to test", YELLOW, "⚠️")
            return True
        
        success_rate = images_working / images_tested
        cprint(f"[INFO] Image test results: {images_working}/{images_tested} working ({success_rate:.1%})", BLUE, "📊")
        
        if success_rate >= 0.5:
            cprint("[OK] Image retrieval is working", GREEN, "✅")
            return True
        else:
            cprint("[FAIL] Too many image retrieval failures", RED, "❌")
            return False
            
    except Exception as e:
        cprint(f"[FAIL] Could not test images: {e}", RED, "❌")
        return False

def main():
    cprint("=== PC Builder Project Test CLI ===", MAGENTA, "🚀")
    all_ok = True
    if not check_backend():
        all_ok = False
    if not check_frontend():
        all_ok = False
    if not check_images():
        all_ok = False
    # Uncomment to test scraper as part of the flow
    # if not check_scraper():
    #     all_ok = False
    if all_ok:
        cprint("\n[ALL OK] All main components are running and responding.", GREEN, "🎉")
    else:
        cprint("\n[SOME FAILURES] See above for details.", RED, "💥")

if __name__ == "__main__":
    main()
