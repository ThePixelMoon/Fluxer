#!/usr/bin/env python3
import argparse as ap
from manager import *

LINK = "https://raw.githubusercontent.com/ThePixelMoon/Fluxer/refs/heads/main/"
#      ^ the package manager file URL

if __name__ == "__main__":
    parser = ap.ArgumentParser(description="a free-to-use package manager")
    parser.add_argument('package', type=str, help="the package to install or search for")
    parser.add_argument('--find', action='store_true', help="search for a package")
    parser.add_argument('--verbose', action='store_true', help="enable verbose output")
    
    args = parser.parse_args()
    mgr = Manager(LINK)

    if args.find:
        mgr.find_package(args.package)
    else:
        mgr.parse(args.package, args.verbose)
