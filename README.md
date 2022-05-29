# osu-cleaner-cli

Script to remove unwanted files from osu! Songs directory. A rewrite of [that](https://github.com/henntix/osu-cleaner) tool, which is not cross-platform and does not work as intended.

## Installation

```bash
pip install osu-cleaner-cli
```

## Usage

```
usage: osu-cleaner-cli [-h] [--delete-videos] [--delete-hitsounds] [--delete-backgrounds] [--delete-skin-elements] [--delete-storyboard-elements] [--delete-all] [osu_songs_directory]

A simple program on python to remove unneeded files from osu! Songs directory.

positional arguments:
  osu_songs_directory   path to your osu! Songs directory

optional arguments:
  -h, --help            show this help message and exit
  --delete-videos
  --delete-hitsounds
  --delete-backgrounds
  --delete-skin-elements
  --delete-storyboard-elements
  --delete-all

If no arguments or only file path specified, script will start in interactive mode.
```
