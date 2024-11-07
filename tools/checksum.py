#!/usr/bin/env python3
import hashlib
import argparse

def generate_checksum(file_path: str, checksum_file: str) -> None:
    """generate an MD5 checksum for the file and save it to a checksum file"""
    checksum = hashlib.md5(open(file_path, "rb").read()).hexdigest()
    
    with open(checksum_file, "w") as f:
        f.write(checksum)

    print(f"checksum for {file_path} saved to {checksum_file}")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a SHA-256 checksum for a file")
    parser.add_argument("file", help="Path to the file you want to generate a checksum for")
    parser.add_argument("checksum_file", help="Path to save the generated checksum")
    
    args = parser.parse_args()
    
    generate_checksum(args.file, args.checksum_file)
