#!/usr/bin/env python3
import urllib.request
import os
import sys
import json
import tarfile
import hashlib
from colors import Colors

SUPPORTS_TAR_XZ = False

def verbose_print(text: str, verbose: bool) -> str:
    """if verbose then print"""
    if verbose:
        print(f"[VERBOSE] {text}")
    return text

def progress_callback(block_num: int, block_size: int, total_size: int) -> None:
    """progress bar"""
    downloaded = block_num * block_size
    if total_size > 0:
        percent = (downloaded / total_size) * 100
        percent = min(percent, 100)
        sys.stdout.write(f"\r{Colors.CYAN}downloading.. {percent:.2f}%{Colors.RESET}")
        sys.stdout.flush()
        
        if percent == 100:
            print("\n") # bug fix
            return

def verify_checksum(package_path: str, checksum_file_path: str) -> bool:
    """just compare 2 hashes, duh"""
    with open(package_path, "rb") as f:
        p_hash = hashlib.sha256(f.read()).hexdigest()


    with open(checksum_file_path, "r", encoding="utf-8") as f:
        c_hash = f.read()
    
    return p_hash == c_hash

class Manager:
    """the manager(tm)"""
    def __init__(self, host: str) -> None:
        """..."""
        self.host = host
        
    def get_package_url(self, package: str) -> tuple[str, str]:
        """gets a package link"""
        extension = ".tar.xz" if SUPPORTS_TAR_XZ else ".tar"
        return f"{self.host}packages/{package}{extension}", extension

    def get_checksum_url(self, package: str) -> str:
        """gets a .sha256 file link"""
        extension = ".tar.xz" if SUPPORTS_TAR_XZ else ".tar"
        return f"{self.host}packages/{package}{extension}.sha256"

    def extract_package(self, file_path: str, verbose: bool) -> None:
        """literally extracts the downloaded archive"""
        try:
            mode = "r:xz" if file_path.endswith(".tar.xz") else "r:"
            # ^ if tar then r: if tar.xz then r:xz
            
            with tarfile.open(file_path, mode) as tar:
                tar.extractall("installed")
            
            verbose_print(f"{Colors.GREEN}done{Colors.RESET}", verbose)
            
        except (tarfile.TarError, FileNotFoundError) as e:
            print(f"error extracting package '{file_path}': {e}")

    def find_package(self, package_name: str) -> None:
        """search for a package and list available options"""
        search_url = f"{self.host}list.json" # should work
        try:
            response = urllib.request.urlopen(search_url)
            data = json.loads(response.read())
            package_list = data.get("packages", [])
            
            found_packages = [pkg for pkg in package_list if package_name.lower() in pkg.lower()]
            
            if found_packages:
                print("found the following packages:")
                for pkg in found_packages:
                    print(f"- {pkg}")
            else:
                print(f"no packages found matching '{package_name}'")
        except urllib.error.HTTPError:
            print(f"{Colors.RED}error accessing package list{Colors.RESET}")

    def download_file(self, url: str, dest: str, verbose: bool) -> None:
        """downloads a file from the given URL to the specified destination"""
        try:
            urllib.request.urlretrieve(url, dest, reporthook=progress_callback)
            verbose_print(f"{Colors.GREEN}done{Colors.RESET}", verbose)
        except urllib.error.HTTPError:
            print(f"{Colors.RED}error downloading '{url}'{Colors.RESET}")
            raise

    def download_package(self, package: str, verbose: bool) -> str:
        """downloads the package file"""
        url, extension = self.get_package_url(package)
        package_path = os.path.join("installed", f"{package}{extension}")
        
        verbose_print(f"{Colors.CYAN}downloading package from {url}...{Colors.RESET}", verbose)

        self.download_file(url, package_path, verbose)
        return package_path

    def download_checksum(self, package: str, verbose: bool) -> str:
        """downloads the checksum file for the package"""
        checksum_url = self.get_checksum_url(package)
        checksum_path = os.path.join("installed", f"{package}.sha256")
        
        verbose_print(f"{Colors.CYAN}downloading checksum from {checksum_url}...{Colors.RESET}", verbose)

        self.download_file(checksum_url, checksum_path, verbose)
        return checksum_path

    def verify_and_cleanup(self, package_path: str, checksum_path: str, verbose: bool) -> bool:
        """verifies checksum and removes files if mismatch"""
        if not verify_checksum(package_path, checksum_path):
            print(f"{Colors.RED}checksum mismatch{Colors.RESET}")
            with open(checksum_path, 'r', encoding='utf-8') as f:
                verbose_print(f"expected: {f.read()}", verbose)
                
            os.remove(package_path)
            os.remove(checksum_path)
            # ^ remove the fucking files, part 2
            
            return False

        verbose_print(f"{Colors.GREEN}checksum verified{Colors.RESET}", verbose)
        
        return True

    def parse(self, package: str, verbose: bool) -> None:
        """the downloading, extracting, matching cycle"""
        os.makedirs("installed", exist_ok=True)
        
        try:
            package_path = self.download_package(package, verbose)
            checksum_path = self.download_checksum(package, verbose)
            
            # verify checksum
            if not self.verify_and_cleanup(package_path, checksum_path, verbose):
                return 1
            
            self.extract_package(package_path, verbose)
        
        finally:
            # finally clean up files
            if os.path.exists(package_path):
                os.remove(package_path)
            if os.path.exists(checksum_path):
                os.remove(checksum_path)