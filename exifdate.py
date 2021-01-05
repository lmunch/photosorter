#!/usr/bin/env python
"""Add or modify dates in EXIF in image files

bla..
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

def add_metadata(filename, jsonfile):
    exiftool_set_json = exiftool["-json+=%s" % jsonfile, "-overwrite_original", filename]
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
        if "DateTimeOriginal" in j[0]:
            print("SKIP: DateTimeOriginal: %s" % j[0]["DateTimeOriginal"])
            continue
        if "CreateDate" in j[0]:
            print("SKIP: CreateDate: %s" % j[0]["CreateDate"])
            continue
        if "ModifyDate" in j[0]:
            print("SKIP: ModifyDate: %s" % j[0]["ModifyDate"])
            continue

        j[0]["DateTimeOriginal"] = "2017:09:10 16:48:46"
        j[0]["CreateDate"] = "2017:09:10 16:48:46"
        j[0]["ModifyDate"] = "2017:09:10 16:48:46"

        # Set new metadata
        jsonfile = os.path.splitext(filename)[0] + ".json"
        with open(jsonfile, 'w') as fd:
            fd.write(json.dumps(j, indent=4, sort_keys=True))
        add_metadata(filename, jsonfile)
