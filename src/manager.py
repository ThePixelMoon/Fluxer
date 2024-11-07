#!/usr/bin/env python3
import urllib.request
import os
import sys
import tarfile
import hashlib

supports_tar_xz = False

def progress_callback(block_num: int, block_size: int, total_size: int) -> None:
    """progress bar"""
    downloaded = block_num * block_size
    if total_size > 0:
        percent = (downloaded / total_size) * 100
        percent = min(percent, 100)
        sys.stdout.write(f"\rdownloading.. {percent:.2f}%")
        sys.stdout.flush()
        
        if percent == 100:
            print("\n") # bug fix
            return

def verify_checksum(package_path: str, checksum_file_path: str) -> bool:
    """just compare 2 hashes, duh"""
    p_hash = hashlib.md5(open(package_path, "rb").read()).hexdigest()
    c_hash = open(checksum_file_path, "r").read()
    
    return p_hash == c_hash

class Manager:
    def __init__(self, host: str) -> None:
        """..."""
        self.host = host
        
    def get_package_url(self, package: str) -> tuple[str, str]:
        """gets a package link"""
        extension = ".tar.xz" if supports_tar_xz else ".tar"
        return f"{self.host}packages/{package}{extension}", extension

    def get_checksum_url(self, package: str) -> str:
        """gets a .md5 file link"""
        extension = ".tar.xz" if supports_tar_xz else ".tar"
        return f"{self.host}packages/{package}{extension}.md5"

    def extract_package(self, file_path: str, verbose: bool) -> None:
        """literally extracts the downloaded archive"""
        try:
            mode = "r:xz" if file_path.endswith(".tar.xz") else "r:"
            # ^ if tar then r: if tar.xz then r:xz
            
            with tarfile.open(file_path, mode) as tar:
                tar.extractall("installed")
            
            if verbose:
                print("done")
        except (tarfile.TarError, FileNotFoundError) as e:
            print(f"error extracting package '{file_path}': {e}")

    def parse(self, package: str, verbose: bool) -> None:
        """the downloading, extracting, matching cycle"""
        url, extension = self.get_package_url(package) # get the link
        checksum_url = self.get_checksum_url(package)  # get the link again
        
        if verbose:
            print(f"extension: {extension}")
            print(f"downloading at '{url}'...")

        os.makedirs("installed", exist_ok=True)
        to = os.path.join("installed", f"{package}{extension}")

        # download the .tar(.xz if added) file
        try:
            urllib.request.urlretrieve(url, to, reporthook=progress_callback)
        except urllib.error.HTTPError:
            print(f"package {package} not found")
            return 1
        
        if verbose: print("done")
        
        checksum_file = os.path.join("installed", f"{package}{extension}.md5")
        # ^ prepare the checksum file path
        
        if verbose: print(f"downloading at {checksum_url}..")
        
        # get the .md5 file
        try:
            urllib.request.urlretrieve(checksum_url, checksum_file, reporthook=progress_callback)
        except urllib.error.HTTPError:
            print(f"checksum file for {package} not found")
            os.remove(to)
            return 1

        if verbose:
            print("done")
            
        # if checksum not match, remove file
        if not verify_checksum(to, checksum_file):
            print(f"checksum mismatch for {open(checksum_file, "rb").read()}!")
            if verbose:
                print(f"expected: {open(checksum_file, "r").read()}")
            
            os.remove(to)
            os.remove(checksum_file)
            
            return 1

        if verbose:
            print("checksum verified")

        self.extract_package(to, verbose)
        os.remove(checksum_file)
        os.remove(to)
