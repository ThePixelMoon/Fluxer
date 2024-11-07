#!/usr/bin/env python3
import urllib.request
import os
import sys
import tarfile
import hashlib # sha-256

supports_tar_xz = False

def progress_callback(block_num: int, block_size: int, total_size: int) -> None:
    downloaded = block_num * block_size
    if total_size > 0:
        percent = downloaded * 100 / total_size
        sys.stdout.write(f"\rdownloading.. {percent:.2f}%")
        sys.stdout.flush()
        
        if percent >= 100:
            print("\n") # bug fix

def verify_checksum(file_path: str, expected_hash: str) -> bool:
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for block in iter(lambda: f.read(4096), b""):
            sha256.update(block)
    return sha256.hexdigest() == expected_hash

class Manager:
    def __init__(self, host: str) -> None:
        self.host = host
        
    def get_package_url(self, package: str) -> tuple[str, str]:
        extension = ".tar.xz" if supports_tar_xz else ".tar"
        return f"{self.host}packages/{package}{extension}", extension

    def get_checksum_url(self, package: str) -> str:
        extension = ".tar.xz" if supports_tar_xz else ".tar"
        return f"{self.host}packages/{package}{extension}.sha256"

    def extract_package(self, file_path: str, verbose: bool) -> None:
        try:
            mode = "r:xz" if file_path.endswith(".tar.xz") else "r:"
            with tarfile.open(file_path, mode) as tar:
                tar.extractall("installed")
            if verbose:
                print(" - done")
        except (tarfile.TarError, FileNotFoundError) as e:
            print(f"error extracting package '{file_path}': {e}")

    def parse(self, package: str, verbose: bool) -> None:
        url, extension = self.get_package_url(package)
        checksum_url = self.get_checksum_url(package)
        
        if verbose:
            print(f"extension: {extension}")
            print(f"downloading at '{url}'...")

        os.makedirs("installed", exist_ok=True)
        to = os.path.join("installed", f"{package}{extension}")

        try:
            urllib.request.urlretrieve(url, to, reporthook=progress_callback)
        except urllib.error.HTTPError:
            print(f"package {package} not found")
            return 1
        
        if verbose:
            print("done")

        checksum_file = os.path.join("installed", f"{package}{extension}.sha256")
        
        if verbose:
            print(f"downloading at {checksum_url}..")
        
        try:
            urllib.request.urlretrieve(checksum_url, checksum_file, reporthook=progress_callback)
        except urllib.error.HTTPError:
            print(f"checksum file for {package} not found")
            os.remove(to)
            return 1

        if verbose:
            print("done")

        with open(checksum_file, "r") as f:
            expected_hash = f.read().strip()

        if not verify_checksum(to, expected_hash):
            print(f"checksum mismatch for {package}!")
            return 1

        if verbose:
            print("checksum verified")

        self.extract_package(to, verbose)
        os.remove(checksum_file) # cleanup!!