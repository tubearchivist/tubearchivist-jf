## Tube Archivist Jellyfin Integration
Import your Tube Archivist media folder into Jellyfin

![home screenshot](assets/screenshot-home.png?raw=true "Jellyfin Home")

This is a proof of concept, looking for feedback. For the time being, only use it for your testing environment, *not* for your main Jellyfin server. This requires Tube Archivist *unstable* builds for API compatibility.

## Core functionality
- Import each YouTube channel as a TV Show
- Each year will become a Season of that Show
- Load artwork and additional metadata into Jellyfin

## How does that work?
At the core, this links the two APIs together: This first queries the Jellyfin API for YouTube videos for any videos that don't have metadata to then populate the required fields from Tube Archivist. Then as a secondary step this will transfer the artwork.

This doesn't depend on any additional Jellyfin plugins, that is a stand alone solution.

This is a *one way* sync, syncing metadata from TA to Jellyfin. This syncs in particular:
- Video title
- Video description
- Video date published
- Channel name
- Channel description

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
    - Then this script will populate the metadata.

3. Backdrops
    - In your Jellyfin installation under > *Settings* > *Display* > enable *Backdrops* for best channel art viewing experience.

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


## Migration problems
To import an existing Tube Archivist archive created with v0.3.4 or before, there are a few manual steps needed. These issues are fixed with videos and channels indexed with v0.3.5 and later.

Apply these fixes *before* importing the archive.

**Permissions**  
Fix folder permissions not owned by the correct user. Navigate to the `ta_video_path` and run:

```bash
sudo chown -R $UID:$GID .
```


**Channel Art**  
Tube Archivist v0.3.5 adds additional art work to the channel metadata. To trigger an automatic refresh of your old channels open a Python shell within the *tubearchivist* container:

```bash
docker exec -it tubearchivist python
```

Then execute these lines to trigger a background task for a full metadata refresh for all channels.

```python
from home.src.es.connect import IndexPaginate
from home.tasks import check_reindex

query = {"query": {"match_all": {}}}
all_channels = IndexPaginate("ta_channel", query).get_results()
reindex = {"channel": [i["channel_id"] for i in all_channels]}
check_reindex.delay(data=reindex)
```
