#!/usr/bin/env python
"""Simple photo and video sorter

This tool bla bla.

Example:
$ ./photosorter.py SRCDIR DESTDIR
"""

import argparse
import hashlib
import os
import pathlib
import shutil
import sys
from datetime import datetime

import exiftool


class CustomHelpFormatter(argparse.ArgumentDefaultsHelpFormatter,
                          argparse.RawDescriptionHelpFormatter):
    pass

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def sorter(srcdir, destdir, move, dryrun):
    for path in pathlib.Path(srcdir).rglob("*"):
        filename = str(path)
        if os.path.isdir(filename):
            continue

        # Get timestamp using exiftool
        if filename.lower().endswith(('.jpg', '.mp4', '.3gp', '.mov')):
            extension = filename.lower()[-3:]
            with exiftool.ExifTool() as et:
                metadata = et.get_metadata(filename)
                if "EXIF:DateTimeOriginal" in metadata:
                    timestamp = metadata["EXIF:DateTimeOriginal"]
                elif "EXIF:ModifyDate" in metadata:
                    timestamp = metadata["EXIF:ModifyDate"]
                elif "QuickTime:CreateDate" in metadata:
                    timestamp = metadata["QuickTime:CreateDate"]
                else:
                    print("SKIP: Date missing %s" % filename)
                    continue
        else:
            print("SKIP: Unknown %s" % filename)
            continue

        # Parse timestamp
        try:
            dateobj = datetime.strptime(timestamp, "%Y:%m:%d %H:%M:%S")
        except:
            print("SKIP: timestamp error (%s)  %s" % (timestamp, filename))
            continue

        # Sanity check year
        if dateobj.year < 1990 or dateobj.year > datetime.now().year:
            print("SKIP: wrong date (%s) %s" % (dateobj.strftime("%Y%m%d_%H%M%S"), filename))
            continue

        # Create destination dir
        new_filepath = os.path.join(destdir, dateobj.strftime("%Y"), dateobj.strftime("%m"))
        if not os.path.isdir(new_filepath):
            pathlib.Path(new_filepath).mkdir(parents=True)

        # Check for duplicates
        for i in range(sys.maxsize):
            new_filename = os.path.join(new_filepath, "%s%s.%s" %
                                        (dateobj.strftime("%Y%m%d_%H%M%S"),
                                        "_%03d" % i if i > 0 else "", extension))
            if os.path.exists(new_filename):
                src_md5 = md5(filename)
                dst_md5 = md5(new_filename)
                if src_md5 == dst_md5:
                    print("SKIP: duplicate %s %s" % (filename, new_filename))
                    new_filename = None
                    if move and not dryrun:
                        os.remove(filename)
                    break
            else:
                break

        # Copy or move file
        if new_filename:
            print("%s -> %s" % (filename, new_filename))
            if not dryrun:
                if move:
                    shutil.move(filename, new_filename)
                else:
                    shutil.copyfile(filename, new_filename)


if __name__ == "__main__":
    description = __doc__.splitlines()[0]
    epilog = "\n".join(__doc__.splitlines()[1:])
    parser = argparse.ArgumentParser(description=description,
                                     epilog=epilog,
                                     formatter_class=CustomHelpFormatter)
    parser.add_argument("-v", "--verbose", default=False, action="store_true",
                        help="Verbose output")
    parser.add_argument("--dryrun", default=False, action="store_true",
                        help="Do not copy/move any files")
    parser.add_argument("--move", default=False, action="store_true",
                        help="Move files instead of copy")
    parser.add_argument("srcdir", metavar="SRCDIR", nargs=1,
                        help="source directory")
    parser.add_argument("destdir", metavar="DESTDIR", nargs=1,
                        help="destination directory")
    args = parser.parse_args()

    if args.verbose:
        print(args)

    srcdir = args.srcdir[0]
    destdir = args.destdir[0]

    if not os.path.isdir(srcdir):
        print("Could not find source directory %s" % srcdir)
        sys.exit(1)

    if not os.path.isdir(destdir):
        print("Could not find destination directory %s" % destdir)
        sys.exit(1)

    os.environ["PATH"] += os.pathsep + "/usr/bin/site_perl"

    sorter(srcdir, destdir, args.move, args.dryrun)
