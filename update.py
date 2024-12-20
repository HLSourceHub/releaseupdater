import sys
import os
import time
import requests
import datetime
import winsound
import webbrowser
import subprocess
import zipfile
import urllib.request
from urllib.parse import urlparse

str_update_manifest_fname = "lastupdate.txt"
str_release_fname = "release.7z"
seven_zip_dir = ('7-ZipPortable')  # Directory for portable 7-Zip
seven_zip_executable = os.path.join(seven_zip_dir, '7-ZipPortable', 'App', '7-Zip', '7z.exe')  # path to 7z.exe
seven_zip_archive = "7z_portable.zip"  # The bundled portable 7-Zip archive

cwd = os.getcwd()
dirname = os.path.basename(cwd)
if dirname.lower() != "sourcemods":
    print("** Please place me in the Sourcemods directory, and run again! **")
    winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
    time.sleep(10)
    sys.exit()

repo_url = "https://github.com/<user>/<repo>/"

parsed_url = urlparse(repo_url)
path_parts = parsed_url.path.strip('/').split('/')
username, repo = path_parts[-2:]

# get the last update we performed
latest = 0
try:
    with open(str_update_manifest_fname, 'r') as f:
        latest = int(f.read())
except:
    with open(str_update_manifest_fname, 'w+') as f:
        f.write(str(latest))

# get the most recent release from github repo
def get_release():
    api = f"https://api.github.com/repos/<user>/<repo>/releases/latest"
    response = requests.get(api)
    if response.status_code == 200:
        return response.json()
    return None

release = None
try:
    release = get_release()
except Exception as e:
    pass

if not release:
    print("Failed to get release info")
    sys.exit(0)

# check if the latest release is newer than the last checked
published = datetime.datetime.strptime(release['published_at'], '%Y-%m-%dT%H:%M:%SZ')
published_unix = int(published.timestamp())

if published_unix <= latest:
    print("We are up to date!")
    sys.exit(0)

print(f"New release from {published}, updating...")

# Download the .7z release
with requests.get(release['assets'][0]['browser_download_url'], stream=True) as r:
    r.raise_for_status()
    with open(str_release_fname, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:  # Ensure non-empty chunks
                f.write(chunk)

# Function to check if the file has finished downloading based on file size
def is_file_complete(file_path, check_interval=2, max_retries=30):
    last_size = -1
    retries = 0
    while retries < max_retries:
        current_size = os.path.getsize(file_path)
        if current_size == last_size:  # If the file size hasn't changed
            print(f"File is complete, size: {current_size} bytes")
            return True
        last_size = current_size
        print(f"Checking file size: {current_size} bytes...")
        time.sleep(check_interval)  # Wait for a short interval before checking again
        retries += 1
    print("Error: The release file was not downloaded completely.")
    return False

# Make sure the file is completely downloaded before proceeding
if not is_file_complete(str_release_fname):
    sys.exit(1)

# Function to extract the portable 7-Zip if not already present
def extract_portable_7zip():
    if not os.path.exists(seven_zip_executable):
        print("Portable 7-Zip not found. Downloading...")
        try:
            # Extract the portable 7-Zip archive using zipfile
            urllib.request.urlretrieve("https://github.com/HLSourceHub/releaseupdater/raw/refs/heads/hl2_7z/7z_portable.zip", "7z_portable.zip")
            with zipfile.ZipFile("7z_portable.zip", 'r') as archive:
                archive.extractall(seven_zip_dir)
            print("Portable 7-Zip downloaded successfully.")
        except Exception as e:
            print(f"Failed to download portable 7-Zip: {e}")
            raise

# Function to extract a .7z file using the portable 7-Zip
def extract_with_7zip(file_to_extract):
    try:
        if not os.path.exists(seven_zip_executable):
            raise FileNotFoundError(f"7-Zip executable not found at {seven_zip_executable}")

        print(f"Attempting to extract {file_to_extract}...")
        # Use the portable 7-Zip to extract the file and wait for completion
        result = subprocess.run([seven_zip_executable, 'x', file_to_extract, '-o.'], check=True)
        print("Extraction complete.")
        return result
    except subprocess.CalledProcessError as e:
        print(f"Extraction failed: {e}")
        raise
    except Exception as e:
        print(f"An error occurred during extraction: {e}")
        raise

# Now call the extraction process, but only after confirming the file is complete
extract_portable_7zip()  # Only download the portable 7-Zip if needed
extract_with_7zip(str_release_fname)  # Extract the .7z file after confirming download completion

print(f"Update complete!")

webbrowser.open('steam://install/<appid>')

# clean up
import shutil
os.unlink(str_release_fname)
os.unlink(seven_zip_archive)
shutil.rmtree(seven_zip_dir)
print(f"Directory '{seven_zip_dir}' and its contents have been removed.")

# update the release info
with open(str_update_manifest_fname, 'w') as f:
    f.write(str(published_unix))
