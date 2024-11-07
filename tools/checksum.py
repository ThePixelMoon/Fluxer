#!/usr/bin/env python3
import hashlib
import argparse

def generate_checksum(file_path: str, checksum_file: str) -> None:
    """create a checksum for a file because i can"""
    checksum = hashlib.md5(open(file_path, "rb").read()).hexdigest()
    
    with open(checksum_file, "w") as f:
        f.write(checksum)

    print(f"checksum for {file_path} saved to {checksum_file}")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="generate an MD5 checksum for a file")
    parser.add_argument("file", help="file path")
    parser.add_argument("checksum_file", help="path to save")
    
    args = parser.parse_args()
    
    generate_checksum(args.file, args.checksum_file)
