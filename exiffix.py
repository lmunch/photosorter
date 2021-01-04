#!/usr/bin/env python
"""Fixes broken EXIF in image files

WARNING: you must customize the fixes needed before using tool

This tool get EXIF information as JSON, changes the information according to
your customizations and writes new EXIF information to the file.
"""

import argparse
import json
import os
import pathlib
import shutil
import sys
from datetime import datetime
from plumbum.cmd import exiftool, md5sum


class CustomHelpFormatter(argparse.ArgumentDefaultsHelpFormatter,
                          argparse.RawDescriptionHelpFormatter):
    pass


def get_metadata(filename):
    """Get EXIF metadata in JSON format using ExifTool"""
    exiftool_get_json = exiftool["-j", filename]
    try:
        metadata = json.loads(exiftool_get_json())
    except Exception as e:
        print("SKIP: Error getting metadata for %s: %s" % (filename, str(e)))
        return None
    return metadata

def set_metadata(filename, jsonfile):
    exiftool_set_json = exiftool["-all=", "-json=%s" % jsonfile, "-overwrite_original", filename]
    try:
        exiftool_set_json()
    except Exception as e:
        print("Error setting for %s: %s" % (filename, str(e)))

if __name__ == "__main__":
    description = __doc__.splitlines()[0]
    epilog = "\n".join(__doc__.splitlines()[1:])
    parser = argparse.ArgumentParser(description=description,
                                     epilog=epilog,
                                     formatter_class=CustomHelpFormatter)
    parser.add_argument("imgfiles", metavar="FILE", nargs="+",
                        help="imge files")
    args = parser.parse_args()

    for filename in args.imgfiles:
        j = get_metadata(filename)
        if not j:
            continue

        # Customize below to fix broken EXIF info
        if "EXIF:DateTimeOriginal" in j[0]:
            print("Skip %s" % filename)
            continue
        print("Fixing %s" % filename)
        if "ExifTool:Warning" in j[0]:
            del j[0]["ExifTool:Warning"]
        if "ISO" in j[0] and j[0]["ISO"] == "":
            del j[0]["ISO"]
        if "UserComment" in j[0]:
            del j[0]["UserComment"]
        if "Comment" in j[0]:
            del j[0]["Comment"]
        if "DateTimeOriginal" not in j[0]:
            j[0]["DateTimeOriginal"] = j[0]["ModifyDate"]
        if "CreateDate" not in j[0]:
            j[0]["CreateDate"] = j[0]["ModifyDate"]

        # Set new metadata
        jsonfile = os.path.splitext(filename)[0] + ".json"
        with open(jsonfile, 'w') as fd:
            fd.write(json.dumps(j, indent=4, sort_keys=True))
        set_metadata(filename, jsonfile)
