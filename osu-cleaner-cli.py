#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# __name__ = "osu-cleaner-cli"
__version__ = "1.0.0"
__author__ = "Layerex"
__doc__ = "A simple program on python to remove unneeded files from osu! Songs folder"
__usage__ = "Usage: %s [-h --help] [-v --version] [<path to the osu songs directory> [--delete-videos] \
[--delete-hitsounds] [--delete-backgrounds] [--delete-skin-elements] [--delete-storyboard-elements]]"

import os
import re
import glob
from sys import argv

extensions = {
    "videos": ("avi", "flv", "mp4", "wmv"),
    "images": ("png", "jpg", "jpeg"),
    "hitsounds": "wav",
    "beatmaps": "osu",
    "storyboards": "osb",
    "skin_initialization_files": "ini"
}

skin_file_names = (
    "cursor",
    "hit",
    "lighting",
    "particle",
    "sliderpoint",
    "approachcircle",
    "followpoint",
    "hitcircle",
    "reversearrow",
    "slider",
    "default-",
    "spinner-",
    "sliderscorepoint",
    "taiko",
    "pippidon",
    "fruit-",
    "lighting",
    "scorebar-",
    "score-",
    "selection-mod-",
    "comboburst",
    "menu-button-background",
    "multi-skipped",
    "play-",
    "star2",
    "inputoverlay-",
    "scoreentry-",
    "ready",
    "count",
    "go.png",
    "section-fail",
    "section-pass",
    "ranking-",
    "pause-",
    "fail-background",
)

# Regular expression that extracts everything within quotation marks
quotation_marks_re = re.compile(r'\"(.*?)\"')


def main():
    working_directory_path = ""
    delete_videos = False
    delete_images = False
    delete_hitsounds = False
    delete_backgrounds = False
    delete_skin_elements = False
    delete_storyboard_elements = False
    delete_skin_initialization_files = False
    interactive_mode = False

    if len(argv) >= 2:
        working_directory_path = argv[1]
        os.chdir(working_directory_path)
    if len(argv) < 2:
        interactive_mode = True
    elif len(argv) == 2:
        if argv[1] in {"-v", "--version"}:
            print(__version__)
            exit(0)
        if argv[1] in {"-h", "--help"}:
            print(__usage__ % argv[0])
            exit(0)
        interactive_mode = True
    else:
        for arg in range(2, len(argv)):
            if argv[arg] == "--delete-videos":
                delete_videos = True
            elif argv[arg] == "--delete-hitsounds":
                delete_hitsounds = True
            elif argv[arg] == "--delete-backgrounds":
                delete_backgrounds = True
            elif argv[arg] == "--delete-skin-elements":
                delete_skin_elements = True
            elif argv[arg] == "--delete-storyboard-elements":
                delete_storyboard_elements = True

    if interactive_mode:
        if len(argv) < 2:
            working_directory_path = input("Enter the path to your osu! songs folder: ")
        os.chdir(working_directory_path)
        delete_videos = ask_yes_no("Do you want to delete all videos from your osu! songs folder?")
        delete_hitsounds = ask_yes_no("Do you want to delete all hitsounds from your osu! songs folder?")
        delete_backgrounds = ask_yes_no("Do you want to delete all backgrounds from your osu! songs folder?")
        delete_skin_elements = \
            ask_yes_no("Do you want to delete all skin elements from your osu! songs folder?")
        delete_storyboard_elements = ask_yes_no("Do you want to delete all storyboards from your osu! songs folder?")

    if delete_skin_elements:
        delete_skin_initialization_files = True
    # If backgrounds, skin elements and storyboards are deleted we can just delete all images(and skin initialization
    # files(.ini)), which is faster, because there is no need to parse .osu files in that case
    if delete_backgrounds and delete_skin_elements and delete_storyboard_elements:
        delete_images = True
    if delete_images:
        delete_backgrounds = False
        delete_skin_elements = False
        delete_storyboard_elements = False

    print("Scanning...")
    directories = os.listdir(".")
    files_to_remove = set()
    for directory in directories:
        if os.path.isdir(directory):
            print(os.path.basename(directory))
            os.chdir(directory)
            # Recursively getting all files in the directory
            files = glob.glob(glob.escape(os.getcwd()) + '/**/*.*', recursive=True)
            if not files == []:
                for file in files:
                    file_lowercase = file.lower()
                    if (file_lowercase.endswith(extensions["videos"]) and delete_videos) \
                            or (file_lowercase.endswith(extensions["images"]) and delete_images) \
                            or (file_lowercase.endswith(extensions["hitsounds"]) and delete_hitsounds) \
                            or (file_lowercase.endswith(extensions["storyboards"]) and delete_storyboard_elements) \
                            or (file_lowercase.endswith(extensions["skin_initialization_files"])
                                and delete_skin_initialization_files) \
                            or (os.path.basename(file_lowercase).startswith(skin_file_names)
                                and file.endswith(extensions["images"]) and delete_skin_elements):
                        files_to_remove.add(os.path.abspath(file))
                    # The code assumes that storyboards are contained only in .osb storyboard files
                    # (those also may be in .osu beatmap files, under [Events] section), so some of the
                    # storyboard files might be occasionally deleted. It can be fixed by adding additional
                    # regex for searching only for backgrounds.
                    # Lines in .osu files specifying backgrounds look like 0,0,"background.png",0,0
                    elif file_lowercase.endswith(extensions["beatmaps"]) and delete_backgrounds:
                        for extracted_file_path in use_re_on_file(file, quotation_marks_re):
                            extracted_file_path_lowercase = extracted_file_path.lower()
                            if extracted_file_path_lowercase.endswith(extensions["images"]) \
                                    and os.path.isfile(extracted_file_path):
                                files_to_remove.add(os.path.abspath(extracted_file_path))
                    elif file_lowercase.endswith(extensions["storyboards"]) and delete_storyboard_elements:
                        for extracted_file_path in use_re_on_file(file, quotation_marks_re):
                            extracted_file_path_lowercase = extracted_file_path.lower()
                            if extracted_file_path_lowercase.endswith(extensions["images"]) \
                                    or extracted_file_path_lowercase.endswith(extensions["videos"]) \
                                    and os.path.isfile(extracted_file_path):
                                files_to_remove.add(os.path.abspath(extracted_file_path))
            os.chdir("..")
        else:
            files_to_remove.add(os.path.abspath(directory))

    # Probably it would be worth adding an additional loop just to remove all empty directories after

    for file_to_remove in files_to_remove:
        print("Removing %s..." % file_to_remove)
        try:
            os.remove(file_to_remove)
        except OSError:
            print("Failed to remove %s" % file_to_remove)


def ask_yes_no(question_string):
    return input("%s (Y/n) " % question_string)[0] in {"Y", "y"}


def use_re_on_file(file, regex):
    with open(file, "r", errors="ignore") as file:
        return regex.findall(file.read())


if __name__ == "__main__":
    main()
