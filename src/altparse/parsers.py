"""
Project: altparse
Module: altparse
Created Date: 01 Dec 2022
Author: Noah Keck
:------------------------------------------------------------------------------:
MIT License
Copyright (c) 2022
:------------------------------------------------------------------------------:
"""

import json
import logging
import re
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Callable

import requests
from packaging import version

from altparse.core import AltSource
from altparse.errors import *
from altparse.helpers import *
from altparse.ipautil import *
from altparse.ipautil.helpers import *


class BaseParser(ABC):
    @abstractmethod
    def get_apps(self, ids: list[str]) -> list[AltSource.App]:
        """Takes a provided list of ids that are `str` provided that `appID` is intended to be equal to `bundleIdentifier` or are type `dict` in the case that they are not the same value. The dict key will be the id being parsed from the other source, assumably the `bundleIdentifier` (but if an `appID` does exist, it will prioritize that) and the predetermined `appID` will be the value. It will then ensure every app has a unique `appID` before returning the list of Apps. This allows the user to change the appID of an app when they parse it.
        """
        raise NotImplementedError
    def get_news(self, ids: list[str]) -> list[AltSource.Article]:
        raise NotImplementedError

class AltSourceParser:
    """A parser that allows the collection the apps and news articles from an AltSource.
    """
    def __init__(self, filepath: Path | str, **kwargs):
        """
        Args:
            filepath (Path | str): The location of the source to be parsed, strings can be a url or filepath.

        Raises:
            ArgumentTypeError: Occurs if the filepath is not of the accepted types or contains an invalid filepath or url.
        """
        if isinstance(filepath, Path) and filepath.exists():
            with open(filepath, "r", encoding="utf-8") as fp:
                self.src = AltSource(json.load(fp))
        elif isinstance(filepath, str) and is_url(filepath):
            self.src = AltSource(requests.get(filepath).json())
        else:
            try:
                path = Path(filepath)
                with open(path, "r", encoding="utf-8") as fp:
                    self.src = AltSource(json.load(fp))
            except Exception as err:
                raise ArgumentTypeError("Filepath must be a path-like object or a url.")

        if not self.src.is_valid():
            raise AltSourceError("Invalid source formatting.")

    def parse_apps(self, ids: list[str | dict[str, str]] | None = None) -> list[AltSource.App]:
        """Takes a provided list of ids that are `str` provided that `appID` is intended to be equal to `bundleIdentifier` or are type `dict` in the case that they are not the same value. The dict key will be the id being parsed from the other source, assumably the `bundleIdentifier` (but if an `appID` does exist, it will prioritize that) and the predetermined `appID` will be the value. It will then ensure every app has a unique `appID` before returning the list of Apps. This allows the user to change the appID of an app when they parse it.

        Args:
            ids (list[str | dict] | None, optional): _description_. Defaults to None.

        Returns:
            list[AltSource.App]: _description_
        """
        
        processed_apps: list[AltSource.App] = list()
        processed_keys: list[AltSource.App] = list()
        fetch_ids = flatten_ids(ids)
        id_conv_tbl = gen_id_parse_table(ids)
        
        for app in self.src.apps:
            if app.is_valid():
                id = app.appID or app.bundleIdentifier
                if id in processed_keys: # appID / bundleID already exists in list of apps processed (meaning there's a duplicate)
                    index = processed_keys.index(id)
                    if version.parse(processed_apps[index].versions[0].version) > version.parse(app.versions[0].version):
                        continue
                    else:
                        processed_apps[index] = app
                elif ids is None or id in fetch_ids:
                    processed_apps.append(app)
                else:
                    continue # app is not going to be included
                
                if app.appID is None:
                    if ids is None or id in ids:
                        app.appID = app.bundleIdentifier
                    else:
                        app.appID = id_conv_tbl[app.bundleIdentifier]
                        
                processed_keys.append(id)
            else:
                logging.warning(f"Failed to parse invalid app: {app.name}")
            
        # determine if any listed keys were not found in the source
        if len(processed_keys) < len(fetch_ids):
            missing_ids = set([pid for pid in fetch_ids if pid not in processed_keys])
            logging.warning(f"Requested ids not found in AltSource ({self.src.name}): {missing_ids}")
        return processed_apps

    def parse_news(self, ids: list[str] | None = None) -> list[AltSource.Article]:
        processed_news = list()
        if self.src.news is None:
            return processed_news
        for article in self.src.news:
            if article.is_valid():
                if ids is None:
                    processed_news.append(article)
                elif article.newsID in ids:
                    processed_news.append(article)
        return processed_news

class Unc0verParser:
    def __init__(self, url: str = "https://unc0ver.dev/releases.json", ver_parse: Callable = lambda x: x.lstrip("v"), prefer_date: bool = False, **kwargs):
        """Create a new Unc0verParser object that can be used to generate an AltSource.App using the Unc0ver team's personal json release data.

        Args:
            url (str): Link to the Unc0ver API releases json. Defaults to "https://unc0ver.dev/releases.json".
            ver_parse (_type_, optional): A lambda function used as a preprocessor to the listed tag_version before comparing to the stored version. Defaults to lambda x:x.lstrip("v").
            prefer_date (bool, optional): Utilizes the published date to determine if there is an update. Defaults to False.
        """
        self.prefer_date, self.ver_parse = prefer_date, ver_parse
        releases = requests.get(url).json()

        # alter the release tags to match altstore version tags
        releases = [{k: ver_parse(v) if k == "tag_name" else v for (k, v) in x.items()} for x in releases]

        if prefer_date:
            self.data = sorted(releases, key=lambda x: parse_github_datetime(x["published_at"]))[-1] # only grab the most recent release
        else:
            self.data = sorted(releases, key=lambda x: version.parse(x["tag_name"]))[-1] # only grab the release with the highest version

    @property
    def version(self) -> str:
        return self.data["tag_name"]

    @property
    def versionDate(self) -> str:
        return self.data["published_at"]

    @property
    def versionDescription(self) -> str:
        return "# " + self.data["name"] + "\n\n" + self.data["body"]

    def get_asset_metadata(self) -> dict[str]:
        """Returns a dictionary containing the downloadURL, size, bundleID, version
        """
        download_url = "https://unc0ver.dev" + self.data["browser_download_url"]
        ipa_path = download_tempfile(download_url)
        metadata = extract_altstore_metadata(ipa_path)
        metadata["downloadURL"] = download_url
        return metadata

class GithubParser:
    def __init__(self, url: str | None = None, repo_author: str | None = None, repo_name: str | None = None, ver_parse: Callable = lambda x: x.lstrip("v"), include_pre: bool = False, prefer_date: bool = False, asset_regex: str = r".*\.ipa", extract_twice: bool = False, upload_ipa_repo: Release | None = None, **kwargs):
        """Create a new GithubParser object that can be used to generate an AltSource.App.
        
        Supply either the api url explicitly or the repo_author and repo_name to automatically find the api url.

        Args:
            url (str | None, optional): Link to the GitHub API json. Defaults to None.
            repo_author (str | None, optional): The repo owner's username. Defaults to None.
            repo_name (str | None, optional): The name of the repo that contains the releases. Defaults to None.
            ver_parse (_type_, optional): A lambda function used as a preprocessor to the listed GitHub tag_version before comparing to the stored version. Defaults to lambda x:x.lstrip("v").
            include_pre (bool, optional): Flag to allow the inclusion of pre-releases, additional changes to `ver_parse` may be required. Defaults to False.
            prefer_date (bool, optional): Utilizes the GitHub published date to determine if there is an update. Defaults to False.
            asset_regex (str, optional): The regex used to match the IPA asset on the releases. Defaults to r".*\.ipa".
            extract_twice (bool, optional): Set True if the IPA has been enclosed in a zip file for distribution. Defaults to False.
            upload_ipa_repo (Release | None, optional): A github3.py Release object used to upload the ipa. Defaults to None.

        Raises:
            GitHubError: If there was an issue using the GitHub API to get the release info.
        """
        self.asset_regex, self.extract_twice, self.upload_ipa_repo, self.prefer_date = asset_regex, extract_twice, upload_ipa_repo, prefer_date
        if url is not None:
            releases = requests.get(url).json()
        elif repo_author is not None and repo_name is not None:
            releases = requests.get("https://api.github.com/repos/{0}/{1}/releases".format(repo_author, repo_name)).json()
        else:
            raise ValueError("Either the api url or both the repo name and author are required.")
        if isinstance(releases, dict):
            if releases.get("message") == "Not Found":
                raise GitHubError("Github Repo not found.")
            elif releases.get("message").startswith("API rate limit exceeded"):
                raise GitHubError("Github API rate limit has been exceeded for this hour.")
            else:
                raise GitHubError("Github API issue: " + releases.get("message"))

        #### Helper methods ####
        def match_asset(release):
            assets = list(filter(lambda x: re.fullmatch(self.asset_regex, x["name"]), release["assets"])) # filters assets to match asset_regex
            asset = sorted(assets, key=lambda x: parse_github_datetime(x["updated_at"]))[-1] # gets most recently updated ipa
            release["asset"] = asset # set asset in the release to only be most recently IPA found
            
        def alter_tag_names(releases: list):
            for index, release in enumerate(releases):
                alter_tag_name(release)
                ver = version.parse(release["tag_name"])
                if isinstance(ver, version.LegacyVersion):
                    logging.warning(f"Invalid version removed: {ver.base_version}")
                    releases.pop(index)

        def alter_tag_name(release: dict):
            release["tag_name"] = ver_parse(release["tag_name"])
        
        #### Parse the correct release ####
        if not include_pre:
            releases = list(filter(lambda x: x.get("prerelease") != True, releases)) # filter out prereleases
        if len(releases)==0:
            raise AltSourceError("No matching releases found.")
        if prefer_date:
            # narrow down assets for all releases to make checking the asset timestamp easier
            for x in releases: match_asset(x)
            self.data = sorted(releases, key=lambda x: parse_github_datetime(x["asset"]["updated_at"]))[-1] # only grab the most recent release
            alter_tag_name(self.data)
        else:
            # alter the github release tags to match AltStore version tags
            # strip out any invalid versions
            alter_tag_names(releases)
            self.data = sorted(releases, key=lambda x: version.parse(x["tag_name"]))[-1] # only grab the release with the highest version
            match_asset(self.data)

    @property
    def version(self) -> str:
        return self.data["tag_name"]

    @property
    def versionDate(self) -> str:
        return self.data["asset"]["updated_at"]

    @property
    def versionDescription(self) -> str:
        return "# " + self.data["name"] + "\n\n" + self.data["body"]

    def get_asset_metadata(self) -> dict[str]:
        """Processes the most recently released ipa to get various internal metadata.

        Returns:
            dict: A dictionary containing the downloadURL, size, bundleID, version, and more.
        """
        download_url = self.data["asset"]["browser_download_url"]

        ipa_path = download_tempfile(download_url)
        payload_path = extract_ipa(ipa_path, self.extract_twice)
        if self.extract_twice:
            ipa_path = payload_path.parent / "temp2.ipa"
        plist_path = list(payload_path.rglob("Info.plist"))[0] # locate the Info.plist path within the extracted data
        metadata = extract_altstore_metadata(ipa_path=ipa_path, plist_path=plist_path)
        
        # Uploads the ipa to a separate GitHub repository after its been processed
        if self.upload_ipa_repo is not None:
            download_url = upload_ipa_github(ipa_path, self.upload_ipa_repo, name=metadata["bundleIdentifier"], ver=metadata["version"])
        
        metadata["downloadURL"] = download_url
        return metadata

class Parser(Enum):
    ALTSOURCE = AltSourceParser
    GITHUB = GithubParser
    UNC0VER = Unc0verParser
