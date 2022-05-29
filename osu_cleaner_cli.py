#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__prog__ = "osu-cleaner-cli"
__version__ = "0.0.3"
__author__ = "Layerex"
__desc__ = "A simple program on python to remove unneeded files from osu! Songs directory."

import argparse
import glob
import os
import re

extensions = {
    "videos": ("avi", "flv", "mp4", "wmv"),
    "images": ("png", "jpg", "jpeg"),
    "hitsounds": "wav",
    "beatmaps": "osu",
    "storyboards": "osb",
    "skin_initialization_files": "ini",
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
quotation_marks_re = re.compile(r"\"(.*?)\"")


def main():
    parser = argparse.ArgumentParser(
        prog=__prog__,
        description=__desc__,
        epilog="If no arguments or only file path specified, script will start in interactive mode."
    )

    parser.add_argument(
        "working_directory_path",
        metavar="osu_songs_directory",
        type=str,
        nargs="?",
        help="path to your osu! Songs directory",
    )
    parser.add_argument(
        "--delete-videos",
        action="store_true",
    )
    parser.add_argument(
        "--delete-hitsounds",
        action="store_true",
    )
    parser.add_argument(
        "--delete-backgrounds",
        action="store_true",
    )
    parser.add_argument(
        "--delete-skin-elements",
        action="store_true",
    )
    parser.add_argument(
        "--delete-storyboard-elements",
        action="store_true",
    )
    parser.add_argument(
        "--delete-all",
        action="store_true",
    )

    args = parser.parse_args()

    if args.working_directory_path:
        working_directory_path = args.working_directory_path
    else:
        working_directory_path = input("Enter the path to your osu! Songs directory: ")
    os.chdir(working_directory_path)

    # Check if chosen directory is actually osu! Songs directory
    if not os.path.exists(os.path.join(os.pardir, "osu!.exe")):
        if not ask_yes_no(
            "Are you really sure that chosen directory is actually osu! Songs directory"
            "? Incorrect choice of directory may lead to LOSS OF DATA."
        ):
            exit()

    delete_videos = args.delete_videos or args.delete_all
    delete_hitsounds = args.delete_hitsounds or args.delete_all
    delete_backgrounds = args.delete_backgrounds or args.delete_all
    delete_skin_elements = delete_skin_initialization_files = (
        args.delete_skin_elements or args.delete_all
    )
    delete_storyboard_elements = args.delete_storyboard_elements or args.delete_all

    if not (
        delete_videos
        or delete_hitsounds
        or delete_backgrounds
        or delete_skin_elements
        or delete_skin_initialization_files
        or delete_storyboard_elements
    ):
        delete_videos = ask_yes_no(
            "Do you want to delete all videos from your osu! Songs directory?"
        )
        delete_hitsounds = ask_yes_no(
            "Do you want to delete all hitsounds from your osu! Songs directory?"
        )
        delete_backgrounds = ask_yes_no(
            "Do you want to delete all backgrounds from your osu! Songs directory?"
        )
        delete_skin_elements = delete_skin_initialization_files = ask_yes_no(
            "Do you want to delete all skin elements from your osu! Songs directory?"
        )
        delete_storyboard_elements = ask_yes_no(
            "Do you want to delete all storyboards from your osu! Songs directory?"
        )

    # If backgrounds, skin elements and storyboards are deleted we can just delete all images(and
    # skin initialization files(.ini)), which is faster, because there is no need to parse .osu
    # files in that case
    if delete_backgrounds and delete_skin_elements and delete_storyboard_elements:
        delete_images = True
        delete_backgrounds = False
        delete_skin_elements = False
        delete_storyboard_elements = False
    else:
        delete_images = False

    print("Scanning...")
    directories = os.listdir(".")
    files_to_remove = set()
    for directory in directories:
        if os.path.isdir(directory):
            print(os.path.basename(directory))
            os.chdir(directory)
            # Recursively get all files in directory
            files = glob.glob("**/*", recursive=True)
            if files:
                for file in files:
                    file_lowercase = file.lower()
                    if (
                        (
                            delete_videos
                            and file_lowercase.endswith(extensions["videos"])
                        )
                        or (
                            delete_images
                            and file_lowercase.endswith(extensions["images"])
                        )
                        or (
                            delete_hitsounds
                            and file_lowercase.endswith(extensions["hitsounds"])
                        )
                        or (
                            delete_skin_initialization_files
                            and file_lowercase.endswith(
                                extensions["skin_initialization_files"]
                            )
                        )
                        or (
                            delete_skin_elements
                            and os.path.basename(file_lowercase).startswith(skin_file_names)
                            and file.endswith(extensions["images"])
                        )
                    ):
                        files_to_remove.add(os.path.abspath(file))
                    # The code assumes that storyboards are contained only in .osb storyboard files
                    # (those also may be in .osu beatmap files, under [Events] section), so some of
                    # the storyboard files might be occasionally deleted. It can be fixed by adding
                    # additional regex for searching only for backgrounds.
                    # Lines in .osu files specifying backgrounds look like 0,0,"background.png",0,0
                    elif (
                        delete_backgrounds
                        and file_lowercase.endswith(extensions["beatmaps"])
                    ):
                        for extracted_file_path in use_re_on_file(
                            file, quotation_marks_re
                        ):
                            extracted_file_path_lowercase = extracted_file_path.lower()
                            if extracted_file_path_lowercase.endswith(
                                extensions["images"]
                            ) and os.path.isfile(extracted_file_path):
                                files_to_remove.add(
                                    os.path.abspath(extracted_file_path)
                                )
                    elif (
                        delete_storyboard_elements
                        and file_lowercase.endswith(extensions["storyboards"])
                    ):
                        for extracted_file_path in use_re_on_file(
                            file, quotation_marks_re
                        ):
                            extracted_file_path_lowercase = extracted_file_path.lower()
                            if (
                                extracted_file_path_lowercase.endswith(
                                    extensions["images"]
                                )
                                or extracted_file_path_lowercase.endswith(
                                    extensions["videos"]
                                )
                                and os.path.isfile(extracted_file_path)
                            ):
                                files_to_remove.add(
                                    os.path.abspath(extracted_file_path)
                                )
                        files_to_remove.add(os.abspath(file))
            os.chdir("..")
        else:
            files_to_remove.add(os.path.abspath(directory))

    for file_to_remove in files_to_remove:
        print("Removing %s..." % file_to_remove)
        try:
            os.remove(file_to_remove)
        except OSError:
            print("Failed to remove %s." % file_to_remove)


def ask_yes_no(question_string):
    return input("%s (Y/n) " % question_string).lower() in ("y", "yes")


def use_re_on_file(file, regex):
    with open(file, "r", errors="ignore") as file:
        return regex.findall(file.read())


if __name__ == "__main__":
    main()
