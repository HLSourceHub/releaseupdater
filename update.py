import sys
import os
import time
import requests
import datetime
import winsound
from urllib.parse import urlparse

str_update_manifest_fname = "lastupdate.txt";
str_release_fname = "release.zip";

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

# unzip release.zip
import zipfile
with zipfile.ZipFile(str_release_fname, 'r') as zip_ref:
    zip_ref.extractall('.')

print(f"Update complete !")

# clean up
os.remove(str_release_fname)

# update the release info
with open(str_update_manifest_fname, 'w') as f:
    f.write(str(published_unix))