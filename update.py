import sys
import os
import time
import requests
import datetime
import winsound
import webbrowser
import subprocess
import py7zr
from urllib.parse import urlparse

seven_zip_dir = os.path.join('7-ZipPortable', 'App', '7-Zip') # Directory for portable 7-Zip
seven_zip_executable = os.path.join(seven_zip_dir, '7z.exe') # path to 7z.exe
seven_zip_archive = "7z_portable.7z" # The bundled portable 7-Zip archive
finished_seven_zip_dir = os.path.exists('7-ZipPortable') # Check if this directory exists, to remove it using shutil

# Function to extract the portable 7-Zip if not already present
def extract_portable_7zip():
    if not os.path.exists(seven_zip_executable):
        print("Portable 7-Zip not found. Extracting...")
        os.makedirs(seven_zip_dir, exist_ok=True)
        try:
            # Extract the portable 7-Zip archive using py7zr
            with py7zr.SevenZipFile(seven_zip_archive, 'r') as archive:
                archive.extractall(seven_zip_dir)
            print("Portable 7-Zip extracted successfully.")
        except Exception as e:
            print(f"Failed to extract portable 7-Zip: {e}")
            raise

# Function to extract a .7z file using the portable 7-Zip
def extract_with_7zip(file_to_extract):
    try:
        # Ensure the portable 7-Zip exists
        if not os.path.exists(seven_zip_executable):
            raise FileNotFoundError(f"7-Zip executable not found at {seven_zip_executable}")

        # Use the portable 7-Zip to extract the file
        subprocess.run([seven_zip_executable, 'x', file_to_extract, '-o.'], check=True)
        print(f"Extraction of {file_to_extract} complete.")
    except subprocess.CalledProcessError as e:
        print(f"Extraction failed: {e}")
        raise
    except Exception as e:
        print(f"Error: {e}")
        raise

extract_portable_7zip()
str_update_manifest_fname = "lastupdate.txt";
str_release_fname = "release.7z";

cwd = os.getcwd();
dirname = os.path.basename(cwd);
if dirname.lower() != "sourcemods":
    print("** Please place me in the Sourcemods directory, and run again! **");
    winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS);
    time.sleep(10);
    sys.exit();

repo_url = "https://github.com/xjiro/releasetest"

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
    api = f"https://api.github.com/repos/{username}/{repo}/releases/latest"
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

with requests.get(release['assets'][0]['browser_download_url'], stream=True) as r:
    r.raise_for_status()
    with open(str_release_fname, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

# unzip release.7z
extract_with_7zip(str_release_fname)

print(f"Update complete !")
webbrowser.open('steam://install/<appid>')

# clean up
import shutil
os.unlink(str_release_fname)
shutil.rmtree(finished_seven_zip_dir)
print(f"Directory '{finished_seven_zip_dir}' and its contents have been removed.")

# update the release info
with open(str_update_manifest_fname, 'w') as f:
    f.write(str(published_unix))