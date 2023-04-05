## Tube Archivist Jellyfin Integration
Import your Tube Archivist media folder into Jellyfin

![home screenshot](assets/screenshot-home.png?raw=true "Jellyfin Home")

This is a proof of concept, expect bugs, for the time being, only use it for your testing environment, *not* for your main Jellyfin server. This requires Tube Archivist *unstable* builds for API compatibility.

## Core functionality
- Import each YouTube channel as a TV Show
- Each year will become a Season of that Show
- Load artwork and additional metadata into Jellyfin

## How does that work?
At the core, this links the two APIs together: This first queries the Jellyfin API for YouTube videos the goes to look up the required metadata in the Tube Archivist API. Then as a secondary step this will transfer the artwork as indexed from Tube Archivist.

This doesn't depend on any additional Jellyfin plugins, that is a stand alone solution.

## Setup Jellyfin
0. Add the Tube Archivist **/youtube** folder as a media folder for Jellyfin.
    - IMPORTANT: This needs to be mounted as **read only** aka `ro`, otherwise this will mess up Tube Archivist.

Example Jellyfin setup:
```yml
jellyfin:
  image: jellyfin/jellyfin
  container_name: jellyfin
  restart: unless-stopped
  network_mode: host
  volumes:
    - ./volume/jellyfin/config:/config
    - ./volume/jellyfin/cache:/cache
    - ./volume/tubearchivist/youtube:/media/youtube:ro  # note :ro at the end
```

1. Add a new media library to your Jellyfin server for your Tube Archivist videos, required options:
    - Content type: `Shows`
    - Displayname: `YouTube`
    - Folder: Root folder for Tube Archivist videos
    - Deactivate all Metadata downloaders
    - Automatically refresh metadata from the internet: `Never`
    - Deactivate all Image fetchers

2. Let Jellyfin complete the library scan
    - This works best if Jellyfin has found all media files and Tube Archivist isn't currently downloading.
    - At first, this will add all channels as a Show with a single Season 1.
    - Then this script will populate the metadata

## Install Standalone
1. Install required libraries for your environment, e.g.
```bash
pip install -r requirements.txt
```
2. rename/copy *config.sample.json* to *config.json*.
3. configure these keys:
	- `ta_video_path`: Absolute path of your /youtube folder from Tube Archivist
	- `ta_url`: Full URL where Tube Archivist is reachable
	- `ta_token`: Tube Archivist API token, accessible from the settings page
	- `jf_url`: Full URL where Jellyfin is reachable
	- `jf_token`: Jellyfin API token

Then run the script with python, e.g.
```python
python main.py
```

## Install with Docker
Coming soon...
