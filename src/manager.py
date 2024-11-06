# manager.py
import urllib.request
import sys, os, tarfile

supports_tar_xz = False

def progress_callback(block_num: int, block_size: int, total_size: int) -> None:
    downloaded = block_num * block_size
    if total_size > 0:
        percent = downloaded * 100 / total_size
        sys.stdout.write(f"\rdownloading.. {percent:.2f}%")
        sys.stdout.flush()

class Manager:
    def __init__(self, host: str) -> None:
        self.host = host

    def parse(self, package: str, verbose: bool) -> None:
        if supports_tar_xz == False:
            url = f"{self.host}packages/{package}.tar"
            extension = ".tar"
        else:
            url = f"{self.host}packages/{package}.tar.xz"
            extension = ".tar.xz"

        if verbose:
            print(f"downloading at '{url}'...")
        
        os.makedirs("installed", exist_ok=True)
        to = os.path.join("installed", f"{package}{extension}")

        try:
            urllib.request.urlretrieve(url, to, reporthook=progress_callback) # download
        except urllib.error.HTTPError:
            print(f"package {package} not found")
            return 1
        
        if verbose:
            print(" - downloaded")

        if extension == ".tar.xz": # extracting time..
            with tarfile.open(to, "r:xz") as tar:
                tar.extractall("installed")
        else:
            with tarfile.open(to, "r:") as tar:
                tar.extractall("installed")

        if verbose:
            print("extracted")