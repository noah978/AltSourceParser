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

import logging
from pathlib import Path

from github3 import login
from github3.exceptions import GitHubError
from github3.repos.release import Release

from altparse.ipautil.model import IPA_Info
from altparse.ipautil.helpers import extract_sha256


def get_or_create_github_release(github_token: str, repo_id: int | None = None, repo_name: str | None = None) -> Release:
    """Gets the github3.py Release object required to upload assets to.
    
    If neither a repo_id or repo_name is provided, a repository will be automatically generated. And if the selected repository does not contain any releases, one will be automatically generated.

    Args:
        github_token (str): Your personal GitHub access token to use the GitHub API.
        repo_id (int | None, optional): The id number of the desired repository. Defaults to None.
        repo_name (str | None, optional): The name of the desired repository. Defaults to None.

    Returns:
        Release: A Release object that can be used to access assets and upload new assets.
    """
    try:
        g_repo, g_release = None, None
        gh = login(token=github_token)
        
        # Use either the repo_id or repo_name to locate the repository, otherwise create a new one
        if repo_id is not None:
            g_repo = gh.repository_with_id(repo_id)
        elif repo_name is not None:
            g_repo = gh.repository(repo_name)
        else:
            g_repo = gh.create_repository("IPA_Uploads", description="This repository is used for uploading IPA files to.", issues=False, has_projects=False, has_wiki=False, auto_init=True)
            
        # If a release doesn't exist, create one. Otherwise grab latest release.
        if len(list(g_repo.releases())) == 0:
            g_release = g_repo.create_release("v0.0", name="IPA Storage Release", body="This release has been automatically generated for the use of uploading IPAs for storage and download by the general public.")
        else:
            g_release = g_repo.latest_release()
    except GitHubError as err:
        logging.error(f"GitHub Authentication failed.")
        logging.error(f"{type(err).__name__}: {str(err)}")
    return g_release

def extract_altstore_metadata(ipa_path: Path | None = None, plist_path: Path | None = None) -> dict[str]:
    """Extracts all relevant ipa metadata from the IPA and its Info.plist and converts it into the format AltStore uses as stored in a dictionary.

    Args:
        ipa_path (Path): Path to the .ipa file.
        plist_path (Path): Path to the Info.plist file.

    Raises:
        InsufficientArgError: Occurs if there were no arguments received.

    Returns:
        dict[str, Any]: Returns a dictionary containing the bundleID, version, and more
    """
    ipa_info = IPA_Info(ipa_path=ipa_path, plist_path=plist_path)
    
    # common metadata
    metadata = {
        "bundleIdentifier": ipa_info.Identifier,
        "version": ipa_info.ShortVersion,
        "buildVersion": ipa_info.Version,
        "appPermissions": extract_permissions(ipa_info=ipa_info)
    }
    
    if ipa_path is not None:
        metadata["size"] = ipa_path.stat().st_size
        metadata["sha256"] = extract_sha256(ipa_path)
    return metadata

def extract_permissions(ipa_info: IPA_Info | None = None, ipa_path: Path | None = None) -> dict[str,list]:
    if ipa_info is None and ipa_path is not None:
        ipa_info = IPA_Info(ipa_path)
    elif ipa_info is None:
        raise ValueError("Not enough information to extract permissions.")
    
    privacy_perms = []
    for k,desc in ipa_info._plist.items():
        if isinstance(k, str) and k.endswith("UsageDescription"):
            privacy_perms.append({
                "name": k[2:k.find("UsageDescription")],
                "usageDescription": desc
            })
            
    permissions = {
        "entitlements": [],
        "privacy": privacy_perms
    }
    return permissions
