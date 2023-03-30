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
from pathlib import Path

from altparse.errors import *
from altparse.helpers import fmt_github_datetime, utcnow, parse_github_datetime

# Create a helper class in the namespace that acts as an intermediary to the logging.info to optionally silence the AltSource creation help text
# OR remove the info help text from the model entirely and place in the cli instead

class AltSource:
    class App:
        class Permission:
            _validTypes = ["photos", "camera", "location", "contacts", "reminders", "music", "microphone", "speech-recognition", "background-audio", "background-fetch", "bluetooth", "network", "calendars", "faceid", "siri", "motion"]
            _requiredKeys = ["type", "usageDescription"]
            
            def __init__(self, src: dict[str] | None = None):
                if src is not None:
                    self._src = src
                    if not all(x in src.keys() for x in self._requiredKeys):
                        logging.warning(f"Missing required AltSource.App.Permission keys. Must have both `type` and `usageDescription`.")
                    if "type" in src.keys() and not self.is_valid_type():
                        logging.warning(f"Permission type not found in valid permission types.")
                else:
                    logging.info(f"Brand new AltSource.App.Permission created. Please remember to set the following properties: {self._requiredKeys}")
                    src = {}
            
            def to_dict(self) -> dict[str]:
                ret = self._src.copy()
                ret = {k:v for (k,v) in ret.items() if ret.get(k) is not None}
                return ret
            
            def missing_keys(self) -> list[str]:
                """Checks to see if the Permission has all the required values and returns the missing keys.
                
                Note that if the list is empty, it will evaluate as False.

                Returns:
                    list[str]: The list of required keys that are missing. If the Permission is valid, the list will be empty.
                """
                missing_keys = list()
                for key in self._requiredKeys:
                    if key not in self._src.keys():
                        missing_keys.append(key)
                return missing_keys
            
            def is_valid(self) -> bool:
                """Checks to see if the AltSource.App.Permission is valid and contains all the required information.

                Returns:
                    bool: True if the `Permission` is a valid AltSource.App.Permission.
                """
                return not self.missing_keys() and self.is_valid_type()
            
            def is_valid_type(self) -> bool:
                """Checks to see if the Permission type is valid.

                Returns:
                    bool: True if the listed type is valid
                """
                return self._src.get("type") in self._validTypes
            
            @property 
            def type(self) -> str:
                return self._src.get("type")
            @type.setter
            def type(self, value: str):
                if value in self._validTypes:
                    self._src["type"] = value
                else:
                    raise ValueError("Invalid permission type.")
                
            @property 
            def usageDescription(self) -> str:
                return self._src.get("usageDescription")
            @usageDescription.setter
            def usageDescription(self, value: str):
                self._src["usageDescription"] = value
        # End class Permission
        class Version:
            _requiredKeys = ['version', 'date', 'downloadURL', 'size']
            
            def __init__(self, src: dict[str] | None = None):
                if src is not None:
                    self._src = src
                    if not all(x in src.keys() for x in self._requiredKeys):
                        logging.warning(f"Missing required AltSource.App.Permission keys.")
                else:
                    logging.info(f"Brand new AltSource.App.Version created. Please remember to set the following properties: {self._requiredKeys}")
                    src = {}
            
            def to_dict(self) -> dict[str]:
                ret = self._src.copy()
                ret = {k:v for (k,v) in ret.items() if ret.get(k) is not None}
                return ret
            
            def missing_keys(self) -> list[str]:
                """Checks to see if the Version has all the required values and returns the missing keys.
                
                Note that if the list is empty, it will evaluate as False.

                Returns:
                    list[str]: The list of required keys that are missing. If the Version is valid, the list will be empty.
                """
                missing_keys = list()
                for key in self._requiredKeys:
                    if key not in self._src.keys():
                        missing_keys.append(key)
                return missing_keys
            
            def is_valid(self) -> bool:
                """Checks to see if the AltSource.App.Permission is valid and contains all the required information.

                Returns:
                    bool: True if the `Permission` is a valid AltSource.App.Permission.
                """
                return not self.missing_keys()
            
            @property 
            def version(self) -> str:
                return self._src.get("version")
            @version.setter
            def version(self, value: str):
                self._src["version"] = value
                
            @property 
            def date(self) -> str:
                return self._src.get("date")
            @date.setter
            def date(self, value: str):
                self._src["date"] = value
                
            @property 
            def downloadURL(self) -> str:
                return self._src.get("downloadURL")
            @downloadURL.setter
            def downloadURL(self, value: str):
                self._src["downloadURL"] = value
                
            @property 
            def size(self) -> str:
                return self._src.get("size")
            @size.setter
            def size(self, value: str):
                self._src["size"] = value
                
            @property 
            def sha256(self) -> str:
                return self._src.get("sha256")
            @sha256.setter
            def sha256(self, value: str):
                self._src["sha256"] = value
                
            @property 
            def localizedDescription(self) -> str:
                return self._src.get("localizedDescription")
            @localizedDescription.setter
            def localizedDescription(self, value: str):
                self._src["localizedDescription"] = value

            # Start unofficial AltSource properties
            
            @property 
            def buildVersion(self) -> str:
                return self._src.get("buildVersion")
            @buildVersion.setter
            def buildVersion(self, value: str):
                self._src["buildVersion"] = value
            
            @property 
            def absoluteVersion(self) -> str:
                return self._src.get("absoluteVersion")
            @absoluteVersion.setter
            def absoluteVersion(self, value: str):
                self._src["absoluteVersion"] = value

        # End class Version
        
        _requiredKeys = ["name", "bundleIdentifier", "developerName", "versions", "localizedDescription", "iconURL"]
        
        def __init__(self, src: dict[str] | None = None):
            if src is None:
                logging.info(f"Brand new AltSource.App created. Please remember to set the following properties: {self._requiredKeys}")
                self._src = {
                    "name": "Example App", 
                    "bundleIdentifier": "com.example.app", 
                    "developerName": "Example.com", 
                    "versions": [],
                    "localizedDescription": "An app that is an example.", 
                    "iconURL": "https://example.com/icon.png"
                    }
            else:
                self._src = src
                if "permissions" in src.keys():
                    self._src["permissions"] = [self.Permission(perm) for perm in src["permissions"]]
                if "versions" in src.keys():
                    self._src["versions"] = [AltSource.App.Version(ver) for ver in src["versions"]]
                else: # create the first Version 
                    self._src["versions"] = [AltSource.App.Version({
                        "version": src.get("version"),
                        "date": src.get("versionDate"),
                        "downloadURL": src.get("downloadURL"),
                        "localizedDescription": src.get("versionDescription"),
                        "size": src.get("size"),
                        "sha256": src.get("sha256"),
                        "absoluteVersion": src.get("absoluteVersion")
                    })]
                missing_keys = self.missing_keys()
                if missing_keys:
                    logging.warning(f"Missing required AltSource.App keys: {missing_keys}")
        
        def to_dict(self) -> dict[str]:
            ret = self._src.copy()
            if "permissions" in self._src.keys():
                ret["permissions"] = [perm.to_dict() for perm in self.permissions]
            if "versions" in self._src.keys():
                ret["versions"] = [ver.to_dict() for ver in self.versions]
            ret = {k:v for (k,v) in ret.items() if ret.get(k) is not None}
            return ret
        
        def missing_keys(self) -> list[str]:
            """Checks to see if the App has all the required values and returns the missing keys.
            
            Note that if the list is empty, it will evaluate as False.

            Returns:
                list[str]: The list of required keys that are missing. If the App is valid, the list will be empty.
            """
            missing_keys = list()
            for key in self._requiredKeys:
                if key not in self._src.keys():
                    missing_keys.append(key)
            return missing_keys
        
        def is_valid(self) -> bool:
            """Checks to see if the AltSource.App is valid and contains all the required information.

            Returns:
                bool: True if the `App` is a valid AltSource.App.
            """
            return not self.missing_keys()
        
        def latest_version(self, use_dates: bool = False) -> Version:
            if use_dates:
                return sorted(self.versions, key=lambda x: parse_github_datetime(x.date))[-1]
            return self.versions[0]
        
        def add_version(self, ver: Version):
            versions_list = [ver.version for ver in self.versions]
            if ver.version in versions_list:
                logging.warning("Version already exists in AltSource. Automatically replaced with new one.")
                self.versions[versions_list.index(ver.version)] = ver
            else:
                self.versions.insert(0,ver)
            self._update_old_version_util(ver)
        
        def _update_old_version_util(self, ver: Version):
            """Takes an `AltSource.App.Version` and uses it to update all the original AltStore API 
               properties for managing updates. Utilize this method to maintain backwards compatibility.
            """
            self._src["version"] = ver.version
            self._src["size"] = ver.size
            self._src["downloadURL"] = ver.downloadURL
            self._src["versionDate"] = ver.date
            self._src["versionDescription"] = ver.localizedDescription
        
        @property 
        def name(self) -> str:
            return self._src.get("name")
        @name.setter
        def name(self, value: str):
            self._src["name"] = value
            
        @property 
        def bundleIdentifier(self) -> str:
            return self._src.get("bundleIdentifier")
        @bundleIdentifier.setter
        def bundleIdentifier(self, value: str):
            logging.warning(f"App `bundleIdentifier` changed from {self._src['bundleIdentifier']} to {value}.")
            self._src["bundleIdentifier"] = value
            
        @property 
        def developerName(self) -> str:
            return self._src.get("developerName")
        @developerName.setter
        def developerName(self, value: str):
            self._src["developerName"] = value
            
        @property 
        def subtitle(self) -> str:
            return self._src.get("subtitle")
        @subtitle.setter
        def subtitle(self, value: str):
            self._src["subtitle"] = value
            
        @property 
        def versions(self) -> list[Version]:
            return self._src.get("versions")
        @versions.setter
        def versions(self, value: list[Version]):
            if self.versions is not None:
                logging.warning(f"Entire `versions` section has been replaced for {self.name}.")
            self._src["versions"] = value
            
        @property 
        def version(self) -> str:
            logging.warning(f"Using deprecated v1 AltSource API.")
            return self._src.get("version")
        @version.setter
        def version(self, value: str):
            logging.warning(f"Using deprecated v1 AltSource API.")
            self._src["version"] = value
            
        @property 
        def versionDate(self) -> str:
            logging.warning(f"Using deprecated v1 AltSource API.")
            return self._src.get("versionDate")
        @versionDate.setter
        def versionDate(self, value: str):
            logging.warning(f"Using deprecated v1 AltSource API.")
            self._src["versionDate"] = value
            
        @property 
        def versionDescription(self) -> str:
            logging.warning(f"Using deprecated v1 AltSource API.")
            return self._src.get("versionDescription")
        @versionDescription.setter
        def versionDescription(self, value: str):
            logging.warning(f"Using deprecated v1 AltSource API.")
            self._src["versionDescription"] = value
            
        @property 
        def downloadURL(self) -> str:
            logging.warning(f"Using deprecated v1 AltSource API.")
            return self._src.get("downloadURL")
        @downloadURL.setter
        def downloadURL(self, value: str):
            logging.warning(f"Using deprecated v1 AltSource API.")
            self._src["downloadURL"] = value
            
        @property 
        def localizedDescription(self) -> str:
            return self._src.get("localizedDescription")
        @localizedDescription.setter
        def localizedDescription(self, value: str):
            self._src["localizedDescription"] = value
            
        @property 
        def iconURL(self) -> str:
            return self._src.get("iconURL")
        @iconURL.setter
        def iconURL(self, value: str):
            self._src["iconURL"] = value
            
        @property 
        def tintColor(self) -> str:
            return self._src.get("tintColor")
        @tintColor.setter
        def tintColor(self, value: str):
            self._src["tintColor"] = value
            
        @property 
        def size(self) -> int:
            return self._src.get("size")
        @size.setter
        def size(self, value: int):
            self._src["size"] = value
            
        @property 
        def beta(self) -> bool:
            return self._src.get("beta")
        @beta.setter
        def beta(self, value: bool):
            self._src["beta"] = value
            
        @property 
        def screenshotURLs(self) -> list[str]:
            return self._src.get("screenshotURLs")
        @screenshotURLs.setter
        def screenshotURLs(self, value: list[str]):
            self._src["screenshotURLs"] = value
            
        @property 
        def permissions(self) -> list[Permission]:
            return self._src.get("permissions")
        @permissions.setter
        def permissions(self, value: list[Permission]):
            if self.permissions is not None:
                logging.warning(f"Entire `permissions` section has been replaced for {self.name}.")
            self._src["permissions"] = value
            
        ### Additional properties that are not currently standard in AltSources ###
            
        @property 
        def appID(self) -> str:
            return self._src.get("appID")
        @appID.setter
        def appID(self, value: str):
            if not isinstance(value, str):
                raise ArgumentTypeError("AltSource.App.appID cannot be set to any type other than str.")
            if self._src.get("appID") is not None:
                logging.warning(f"App `appID` changed from {self._src['appID']} to {value}.")
            self._src["appID"] = value
            
    # End class App
    
    class Article:
        _requiredKeys = ["title", "identifier", "caption", "date"]
        
        def __init__(self, src: dict | None = None):
            if src is None:
                logging.info(f"Brand new AltSource.Article created. Please remember to set the following properties: {self._requiredKeys}")
                self._src = {"title": "Example Article Title", "identifier": "com.example.article", "caption": "Provoking example caption.", "date": fmt_github_datetime(utcnow())}
            else:
                self._src = src
                missing_keys = self.missing_keys()
                if missing_keys:
                    logging.warning(f"Missing required AltSource.Article keys: {missing_keys}")
            
        def to_dict(self) -> dict[str]:
            ret = self._src.copy()
            ret = {k:v for (k,v) in ret.items() if ret.get(k) is not None}
            return ret
        
        def missing_keys(self) -> list[str]:
            """Checks to see if the `Article` has all the required values and returns the missing keys.
            
            Note that if the list is empty, it will evaluate as False.

            Returns:
                list[str]: The list of required keys that are missing. If the `Article` is valid, the list will be empty.
            """
            missing_keys = list()
            for key in self._requiredKeys:
                if key not in self._src.keys():
                    missing_keys.append(key)
            return missing_keys
        
        def is_valid(self) -> bool:
            """Checks to see if the AltSource.Article is valid and contains all the required information.

            Returns:
                bool: True if the `Article` is a valid AltSource.Article.
            """
            return not self.missing_keys()
        
        @property 
        def title(self) -> str:
            return self._src.get("title")
        @title.setter
        def title(self, value: str):
            self._src["title"] = value
            
        @property 
        def name(self) -> str:
            return self._src.get("name")
        @name.setter
        def name(self, value: str):
            self._src["name"] = value
            
        @property 
        def newsID(self) -> str:
            return self._src.get("identifier")
        @newsID.setter
        def newsID(self, value: str):
            logging.warning(f"Article `identifier` changed from {self._src['identifier']} to {value}.")
            self._src["identifier"] = value
            
        @property 
        def caption(self) -> str:
            return self._src.get("caption")
        @caption.setter
        def caption(self, value: str):
            self._src["caption"] = value
            
        @property 
        def tintColor(self) -> str:
            return self._src.get("tintColor")
        @tintColor.setter
        def tintColor(self, value: str):
            self._src["tintColor"] = value
            
        @property 
        def imageURL(self) -> str:
            return self._src.get("imageURL")
        @imageURL.setter
        def imageURL(self, value: str):
            self._src["imageURL"] = value
            
        @property 
        def appID(self) -> str:
            return self._src.get("appID")
        @appID.setter
        def appID(self, value: str):
            self._src["appID"] = value
            
        @property 
        def date(self) -> str:
            return self._src.get("date")
        @date.setter
        def date(self, value: str):
            self._src["date"] = value
            
        @property 
        def notify(self) -> bool:
            return self._src.get("notify")
        @notify.setter
        def notify(self, value: bool):
            self._src["notify"] = value
            
        @property 
        def url(self) -> str:
            return self._src.get("url")
        @url.setter
        def url(self, value: str):
            self._src["url"] = value
    # End class Article
    
    _requiredKeys = ["name", "identifier", "apps"]
    
    def __init__(self, src: dict | None = None, path: str | Path | None = None):
        """Create new AltSource object. If a src is included, all properties will be retained regardless of use in a 
            standard AltSource. This will *not* load the data from path. Use the `altsource_from_file` method for that.

        Args:
            src (dict, optional): the direct serialization of an AltSource json file. Defaults to None.
            path (str | Path, optional): the filepath to which a physical version of the AltSource should be stored. Defaults to None.
        """
        if src is None:
            self._src = {"name": "ExampleSourceName", "identifier": "com.example.identifier", "apps": [], "version": 2}
            logging.info(f"Brand new AltSource created. Please remember to set the following properties: {self._requiredKeys}")
        else:
            self._src = src
            self._src["apps"] = [self.App(app) for app in src["apps"]]
            if "news" in self._src.keys():
                self._src["news"] = [self.Article(art) for art in src["news"]]
            self.version = 2 # set current API version
        if path:
            if isinstance(path, str):
                self.path = Path(path)
            self.path = path
        else:
            self.path = None
    
    def to_dict(self) -> dict[str]:
        ret = self._src.copy()
        ret["apps"] = [app.to_dict() for app in self.apps]
        if "news" in self._src.keys():
            ret["news"] = [art.to_dict() for art in self.news]
        ret = {k:v for (k,v) in ret.items() if ret.get(k) is not None}
        return ret
    
    def missing_keys(self) -> list[str]:
        """Checks to see if the `AltSource` has all the required values.
        
        Note that if the list is empty, it will evaluate as False.

        Returns:
            list[str]: The list of required keys that are missing. If the `AltSource` is valid, the list will be empty.
        """
        missing_keys = list()
        for key in self._requiredKeys:
            if key not in self._src.keys():
                missing_keys.append(key)
        return missing_keys
    
    def is_valid(self):
        return not self.missing_keys()
    
    @property 
    def name(self) -> str:
        return self._src.get("name")
    @name.setter
    def name(self, value: str):
        self._src["name"] = value
        
    @property 
    def identifier(self) -> str:
        return self._src.get("identifier")
    @identifier.setter
    def identifier(self, value: str):
        logging.warning(f"Source `identifier` changed from {self._src['identifier']} to {value}.")
        self._src["identifier"] = value
        
    @property 
    def sourceURL(self) -> str:
        return self._src.get("sourceURL")
    @sourceURL.setter
    def sourceURL(self, value: str):
        self._src["sourceURL"] = value
    
    @property 
    def apps(self) -> list[App]:
        return self._src.get("apps")
    @apps.setter
    def apps(self, value: list[App]):
        logging.warning("Entire `apps` section has been replaced.")
        self._src["apps"] = value
        
    @property 
    def news(self) -> list[Article]:
        return self._src.get("news")
    @news.setter
    def news(self, value: list[Article]):
        if self.news is not None:
            logging.warning("Entire `news` section has been replaced.")
        self._src["news"] = value
        
    # Start unofficial AltSource attributes.
    
    @property 
    def sourceIconURL(self) -> str:
        return self._src.get("sourceIconURL")
    @sourceIconURL.setter
    def sourceIconURL(self, value: str):
        self._src["sourceIconURL"] = value
    
    @property 
    def version(self) -> str:
        """Used to declare the AltSource API version.
        """
        return self._src.get("version")
    @version.setter
    def version(self, value: str):
        self._src["version"] = value
# End class AltSource

def altsource_from_file(filepath: Path | str) -> AltSource:
    """Loads an AltSource json into the Python object

    Args:
        filepath (Path | str): the filepath of an AltSource json. Will search for file in current working directory if only given a string
    """
    if not isinstance(filepath, Path):
        try:
            filepath = next(Path.cwd().rglob(filepath))
        except StopIteration:
            raise FileNotFoundError(f"{filepath} not found in current working directory.")
    with open(filepath, "r", encoding="utf-8") as fp:
        return AltSource(json.load(fp), filepath)
