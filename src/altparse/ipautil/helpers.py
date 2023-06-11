"""
Project: altparse
Module: ipautil
Created Date: 05 Dec 2022
Author: Noah Keck
:------------------------------------------------------------------------------:
MIT License
Copyright (c) 2022
:------------------------------------------------------------------------------:
"""

import atexit
import hashlib
import logging
import os
import re
import shutil
from pathlib import Path
from tempfile import mkdtemp
from zipfile import ZipFile, is_zipfile

import requests
from github3.repos.release import Release

from altparse.ipautil.errors import FileError


def cleanup_tempdir(fp: Path):
    try:
        if fp.is_dir():
            shutil.rmtree(fp.as_posix())
        else:
            os.remove(fp.as_posix())
    except FileNotFoundError as err:
        logging.debug(f"File not found in temporary directory: {str(fp)}")
    except Exception as err:
        logging.warning(f"Unable to cleanup files in temporary directory: {str(fp)} due to {err.__class__}")

def download_temp_ipa(download_url: str) -> Path | None:
    """Downloads ipa file to a temporary directory. If a file cannot be downloaded or is not an IPA, it returns None.

    Args:
        download_url (str): The url of the file to be downloaded.

    Returns:
        Path: The Path obj pointing to the downloaded file.
    """
    tempdir = Path(mkdtemp())
    atexit.register(cleanup_tempdir, tempdir)
    filename = "temp"
    r = requests.get(download_url)
    with open(tempdir / filename, "wb") as file:
        file.write(r.content)
    try:
        open(tempdir / filename, "rb")
    except OSError as err:
        logging.error("Could not find/open downloaded file.")
        return None
    if not is_zipfile(filename):
        logging.error("Downloaded file is not an IPA file.")
        return None
    return tempdir / filename

def extract_sha256(ipa_path: Path) -> str:
    sha256_hash = hashlib.sha256()
    with open(ipa_path,"rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096),b""):
            sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

def extract_ipa(ipa_path: Path, extract_twice: bool = False, use_temp_dir: bool = False) -> Path | Path:
    """Extracts the ipa data into a directory.

    If you are extracting twice, the normal .ipa file will be located in the parent directory of the returned path with the name "temp2.ipa".
    
    Args:
        ipa_path (Path): The Path to the ipa file.
        extract_twice (bool, optional): Set True if the ipa file is compressed in a zip file. Defaults to False.
        use_temp_dir (bool, optional): Uses a temporary directory to extract to instead of the same directory as the ipa. Defaults to False.

    Raises:
        FileError: If there was an issue processing the zipped files.

    Returns:
        Path: A Path object pointing to the extracted IPA contents (the "Payload" folder).
    """
    if use_temp_dir:
        dest_path = Path(mkdtemp())
        atexit.register(cleanup_tempdir, dest_path)
    else:
        dest_path = ipa_path.parent
        atexit.register(cleanup_tempdir, ipa_path / "Payload")
    if extract_twice:
        with ZipFile(ipa_path, "r") as zip:
            ipa_path = dest_path / "temp2.ipa"
            r = re.compile(r".*\.ipa")
            files = list(filter(r.match, zip.namelist()))
            if len(files) == 1:
                file = files[0]
            elif len(files > 1):
                raise FileError(str(ipa_path), "More files than just an IPA in the zip file.")
            else:
                raise FileError(str(ipa_path), "No IPA files found in the zip file.")
            data = zip.read(file)
            ipa_path.write_bytes(data)
        
    with ZipFile(ipa_path, "r") as ipa:
        ipa.extractall(path=dest_path)
    dest_path = dest_path / "Payload"
    if not dest_path.exists():
        raise FileError("Invalid IPA file does not have a Payload folder inside.")
    return dest_path

def upload_ipa_github(ipa_path: Path, github_release: Release, name: str | None = None, ver: str | None = None) -> str:
    """Uses github3.py package to upload IPA to the specified Release using the GitHub API.
    
    The name and version are concatenated to make the github release asset name, otherwise the filename from the ipa_path is used.

    Args:
        ipa_path (Path): Path to the ipa to be uploaded.
        github_release (Release): github3.py Release object that will be used as the location to upload to.
        name (str): The filename to be used on the uploaded ipa (do not include the .ipa extension).
        ver (str): The version to be concatenated to the end of the filename on the uploaded ipa.

    Returns:
        str: The download url for the uploaded IPA.
    """
    with open(ipa_path, "rb") as file:
        label = f"{name}-{ver}.ipa" if name is not None and ver is not None else ipa_path.name
        uploaded_asset = github_release.upload_asset(content_type="application/octet-stream", name=label, asset=file)
    return uploaded_asset.browser_download_url