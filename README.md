# GitHub Release Updater

Make an `update.exe` that checks github for new releases and updates the current directory if behind.

## Setup
1. Have python3
2. [Download](https://github.com/xjiro/githubreleaseupdater/archive/refs/heads/master.zip) and extract this repo
3. Run `pip install -Ur requirements.txt`

## Configuration
- Set `repo_url` in `update.py`
- Run `.\build.cmd`
- Copy `update.exe` to your project you want to auto update

## Usage Details
- Will only grab the first release artifact
- Expects that artifact to be a zip
- Creates and maintains an `update.txt` with the latest releases' publish timestamp

### Downsides
I might fix these issues later if necessary
- Simply overwrites files (watch out for user configurations, default saves)
- Will redudantly download and overwrite unchanged files (no file hashing or manifest usage)
- Doesn't support architecture selection
- No configuration for installation paths
- Windows only

## License
This project is licensed under the MIT License.
