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
from abc import ABC
from functools import total_ordering
from pathlib import Path

from packaging import version

from altparse.errors import *
from altparse.helpers import (all_class_properties, fmt_github_datetime,
                              parse_github_datetime, utcnow, equal_ignore_order)
from altparse.ipautil.helpers import download_temp_ipa, extract_sha256 
from altparse.ipautil.core import extract_permissions

# Create a helper class in the namespace that acts as an intermediary to the logging.info to optionally silence the AltSource creation help text
# OR remove the info help text from the model entirely and place in the cli instead


class Base(ABC):
    _src = {}
    _required_keys = []
    _deprecated_keys = []
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            for key in all_class_properties(self.__class__):
                if key in self._deprecated_keys: continue
                value = getattr(self, key)
                other_value = getattr(other, key)
                if isinstance(value, list) and equal_ignore_order(value, other_value): return False
                elif getattr(self, key) != getattr(other, key): return False
            return True
        return NotImplemented

    def __iter__(self):
        for key in all_class_properties(self.__class__):
            if key in self._deprecated_keys: continue
            value = getattr(self, key)
            if value is None: continue
            if isinstance(value, list) and len(value)>0 and issubclass(value[0].__class__, Base): 
                yield (key, [dict(item) for item in value])
            elif issubclass(value.__class__, Base):  yield (key, dict(value))
            else: yield (key, value)
            
    def __str__(self):
        return str(dict(self))

class AltSource(Base):
    class App(Base):
        
        class Permissions(Base):
            class Entitlement(Base):
                _required_keys = ["name"]
                
                def __init__(self, src: dict[str] | None = None):
                    if src is not None:
                        self._src = src
                        
                        missing_keys = self.missing_keys()
                        if missing_keys:
                            logging.warning(f"Missing required AltSource.App.Entitlement keys: {missing_keys}")
                    else:
                        logging.info(f"Brand new AltSource.App.Entitlement created. Please remember to set the following properties: {self._required_keys}")
                        self._src = {}
                
                def to_dict(self) -> dict[str]:
                    ret = self._src.copy()
                    ret = {k:v for (k,v) in ret.items() if ret.get(k) is not None}
                    return ret
                
                def missing_keys(self) -> list[str]:
                    """Checks to see if the Entitlement has all the required values and returns the missing keys.
                    
                    Note that if the list is empty, it will evaluate as False.

                    Returns:
                        list[str]: The list of required keys that are missing. If the Entitlement is valid, the list will be empty.
                    """
                    missing_keys = list()
                    for key in self._required_keys:
                        if key not in self._src.keys():
                            missing_keys.append(key)
                    return missing_keys
                
                def is_valid(self) -> bool:
                    """Checks to see if the AltSource.App.Entitlement is valid and contains all the required information.

                    Returns:
                        bool: True if the `Entitlement` is a valid AltSource.App.Entitlement.
                    """
                    return not self.missing_keys()
                
                @property 
                def name(self) -> str:
                    return self._src.get("name")
                @name.setter
                def name(self, value: str):
                    self._src["name"] = value
            # End class Entitlement
            class Privacy(Base):
                # this is not an all-inclusive list, but is the most common privacy permissions that an app can request / utilize
                _valid_types = ["BluetoothAlways", "BluetoothPeripheral", "Calendars", "Reminders", "Camera", "Microphone", "Contacts", "FaceID", "DesktopFolder", "DocumentsFolder", "DownloadsFolder", "NetworkVolumes", "RemovableVolumes", "FileProviderDomain", "GKFriendList", "HealthClinicalHealthRecordsShare", "HealthShare", "HealthUpdate", "HomeKit", "LocationAlwaysAndWhenInUse", "Location", "LocationWhenInUse", "LocationAlways", "AppleMusic", "Motion", "FallDetection", "LocalNetwork", "NearbyInteraction", "NearbyInteractionAllowOnce", "NFCReader", "PhotoLibraryAdd", "PhotoLibrary", "UserTracking", "AppleEvents", "SystemAdministration", "SensorKit", "Siri", "SpeechRecognition", "VideoSubscriberAccount", "Identity"]
                _required_keys = ["name", "usageDescription"]
                
                def __init__(self, src: dict[str] | None = None):
                    if src is not None:
                        self._src = src
                        missing_keys = self.missing_keys()
                        if missing_keys:
                            logging.warning(f"Missing required AltSource.App.Permissions.Privacy keys: {missing_keys}")
                        if not self.is_valid_type():
                            logging.warning(f"Privacy name not found in valid types.")
                    else:
                        logging.info(f"Brand new AltSource.App.Permissions.Privacy created. Please remember to set the following properties: {self._required_keys}")
                        self._src = {}
                
                def to_dict(self) -> dict[str]:
                    ret = self._src.copy()
                    ret = {k:v for (k,v) in ret.items() if ret.get(k) is not None}
                    return ret
                
                def missing_keys(self) -> list[str]:
                    """Checks to see if the PrivacyPermission has all the required values and returns the missing keys.
                    
                    Note that if the list is empty, it will evaluate as False.

                    Returns:
                        list[str]: The list of required keys that are missing. If the PrivacyPermission is valid, the list will be empty.
                    """
                    missing_keys = list()
                    for key in self._required_keys:
                        if key not in self._src.keys():
                            missing_keys.append(key)
                    return missing_keys
                
                def is_valid(self) -> bool:
                    """Checks to see if the AltSource.App.PrivacyPermission is valid and contains all the required information.

                    Returns:
                        bool: True if the `PrivacyPermission` is a valid AltSource.App.PrivacyPermission.
                    """
                    return not self.missing_keys()
                
                def is_valid_type(self) -> bool:
                    """Checks to see if the PrivacyPermission name is a valid type.

                    Returns:
                        bool: True if the listed name is valid
                    """
                    return self.name in self._valid_types
                
                @property 
                def name(self) -> str:
                    return self._src.get("name")
                @name.setter
                def name(self, value: str):
                    if value not in self._valid_types:
                        logging.warning("PrivacyPermission name is not found in the list of valid types.")
                    self._src["name"] = value
                    
                @property 
                def usageDescription(self) -> str:
                    return self._src.get("usageDescription")
                @usageDescription.setter
                def usageDescription(self, value: str):
                    self._src["usageDescription"] = value
            # End class Privacy
            
            _required_keys = []
            
            def __init__(self, src: dict[str,list] | None = None):
                if src is not None:
                    self._src = src
                    if "entitlements" in src.keys():
                        self._src["entitlements"] = [AltSource.App.Permissions.Entitlement(title) for title in src["entitlements"]]
                    if "privacy" in src.keys():
                        self._src["privacy"] = [AltSource.App.Permissions.Privacy(perm) for perm in src["privacy"]]
                        
                    missing_keys = self.missing_keys()
                    if missing_keys:
                        logging.warning(f"Missing required AltSource.App.Permissions keys: {missing_keys}")
                else:
                    logging.info(f"Brand new AltSource.App.Permissions created. Please remember to add all the entitlements and privacy permissions that your app uses.")
                    self._src = {
                        "entitlements": [],
                        "privacy": []
                    }
            
            def to_dict(self) -> dict[str]:
                ret = self._src.copy()
                if "entitlements" in self._src.keys():
                    ret["entitlements"] = [title.to_dict() for title in self.entitlements]
                if "privacy" in self._src.keys():
                    ret["privacy"] = [perm.to_dict() for perm in self.privacy]
                ret = {k:v for (k,v) in ret.items() if ret.get(k) is not None}
                return ret
            
            def missing_keys(self) -> list[str]:
                """Checks to see if the Permissions has all the required values and returns the missing keys.
                
                Note that if the list is empty, it will evaluate as False.

                Returns:
                    list[str]: The list of required keys that are missing. If the Permissions is valid, the list will be empty.
                """
                missing_keys = list()
                for key in self._required_keys:
                    if key not in self._src.keys():
                        missing_keys.append(key)
                return missing_keys
            
            def is_valid(self) -> bool:
                """Checks to see if the AltSource.App.Permissions is valid and contains all the required information.

                Returns:
                    bool: True if the `Permissions` is a valid AltSource.App.Permissions.
                """
                return not self.missing_keys()
            
            @property 
            def entitlements(self) -> list[Entitlement]:
                return self._src.get("entitlements",[])
            @entitlements.setter
            def entitlements(self, value: list[Entitlement]):
                if self.entitlements is not None:
                    logging.warning(f"Entire `entitlements` section has been replaced.")
                self._src["entitlements"] = value
                
            @property 
            def privacy(self) -> list[Privacy]:
                return self._src.get("privacy",[])
            @privacy.setter
            def privacy(self, value: list[Privacy]):
                if self.privacy is not None:
                    logging.warning(f"Entire `privacy` section has been replaced.")
                self._src["privacy"] = value
        # End class Permissions
        
        @total_ordering
        class Version(Base):
            _required_keys = ['version', 'date', 'downloadURL', 'size']
            
            def __init__(self, src: dict[str] | None = None):
                if src is not None:
                    self._src = src
                    missing_keys = self.missing_keys()
                    if missing_keys:
                        logging.warning(f"Missing required AltSource.App.Version keys: {missing_keys}")
                else:
                    logging.info(f"Brand new AltSource.App.Version created. Please remember to set the following properties: {self._required_keys}")
                    src = {
                        "version": "",
                        "date": "",
                        "downloadURL": "",
                        "size": 0
                    }
            
            def __lt__(self, other):
                if isinstance(other, self.__class__):
                    if self.absoluteVersion is not None and other.absoluteVersion is not None:
                        if version.parse(self.absoluteVersion) < version.parse(other.absoluteVersion): return True
                        else: return False
                    
                    if (version.parse(self.version) < version.parse(other.version)): return True
                    
                    if (version.parse(self.version) == version.parse(other.version) and 
                        self.buildVersion is not None and other.buildVersion is not None and 
                        version.parse(self.buildVersion) < version.parse(other.buildVersion)): return True
                    
                    return False
                return NotImplemented
            
            def __gt__(self, other):
                if isinstance(other, self.__class__):
                    if (self.absoluteVersion is not None and other.absoluteVersion is not None and 
                        version.parse(self.absoluteVersion) > version.parse(other.absoluteVersion)): return True
                    
                    if (version.parse(self.version) > version.parse(other.version)): return True
                    
                    if (version.parse(self.version) == version.parse(other.version) and 
                        self.buildVersion is not None and other.buildVersion is not None and 
                        version.parse(self.buildVersion) > version.parse(other.buildVersion)): return True
                    
                    return False
                return NotImplemented
            
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
                for key in self._required_keys:
                    if key not in self._src.keys():
                        missing_keys.append(key)
                return missing_keys
            
            def is_valid(self) -> bool:
                """Checks to see if the AltSource.App.Permission is valid and contains all the required information.

                Returns:
                    bool: True if the `Permission` is a valid AltSource.App.Permission.
                """
                return not self.missing_keys()
            
            def calculate_sha256(self, ipa_path: Path | None = None):
                """Calculates the sha256 hash based on the downloadURL or passed `ipa_path` argument and sets the property.
                """
                if ipa_path is None and self.downloadURL is not None: 
                    ipa_path = download_temp_ipa(self.downloadURL)
                if ipa_path is not None:
                    self.sha256 = extract_sha256(ipa_path)
            
            ### Unofficial property ###
            @property 
            def absoluteVersion(self) -> str:
                return self._src.get("absoluteVersion")
            @absoluteVersion.setter
            def absoluteVersion(self, value: str):
                self._src["absoluteVersion"] = value
        
            @property 
            def version(self) -> str:
                return self._src.get("version")
            @version.setter
            def version(self, value: str):
                self._src["version"] = value
                
            @property 
            def buildVersion(self) -> str:
                return self._src.get("buildVersion")
            @buildVersion.setter
            def buildVersion(self, value: str):
                self._src["buildVersion"] = value
                
            @property 
            def date(self) -> str:
                return self._src.get("date")
            @date.setter
            def date(self, value: str):
                self._src["date"] = value
                
            @property 
            def localizedDescription(self) -> str:
                return self._src.get("localizedDescription")
            @localizedDescription.setter
            def localizedDescription(self, value: str):
                self._src["localizedDescription"] = value
                
            @property 
            def downloadURL(self) -> str:
                return self._src.get("downloadURL")
            @downloadURL.setter
            def downloadURL(self, value: str):
                self._src["downloadURL"] = value
                
            @property 
            def size(self) -> int:
                return self._src.get("size")
            @size.setter
            def size(self, value: int):
                self._src["size"] = value
                
            @property 
            def sha256(self) -> str:
                return self._src.get("sha256")
            @sha256.setter
            def sha256(self, value: str):
                self._src["sha256"] = value
                
            @property 
            def minOSVersion(self) -> str:
                return self._src.get("minOSVersion")
            @minOSVersion.setter
            def minOSVersion(self, value: str):
                self._src["minOSVersion"] = value
                
            @property 
            def maxOSVersion(self) -> str:
                return self._src.get("maxOSVersion")
            @maxOSVersion.setter
            def maxOSVersion(self, value: str):
                self._src["maxOSVersion"] = value
            
        # End class Version
        
        _required_keys = ["name", "bundleIdentifier", "developerName", "versions", "localizedDescription", "iconURL"]
        _deprecated_keys = ["version", "versionDate", "versionDescription", "downloadURL", "size", "permissions"]
        
        def __init__(self, src: dict[str] | None = None):
            if src is not None:
                self._src = src
                if "appPermissions" in src.keys():
                    self._src["appPermissions"] = AltSource.App.Permissions(src["appPermissions"])
                if "versions" in src.keys():
                    self._src["versions"] = [AltSource.App.Version(ver) for ver in src["versions"]]
                else: # create the first Version by attempting to convert from old AltSource API
                    self._src["versions"] = [AltSource.App.Version({
                        "version": src.get("version"),
                        "date": src.get("versionDate"),
                        "downloadURL": src.get("downloadURL"),
                        "localizedDescription": src.get("versionDescription"),
                        "size": src.get("size")
                    })]
                    
                missing_keys = self.missing_keys()
                if missing_keys:
                    logging.warning(f"Missing required AltSource.App keys: {missing_keys}")
            else:
                logging.info(f"Brand new AltSource.App created. Please remember to update the following properties: {self._required_keys}")
                self._src = {
                    "name": "Example App",
                    "appID": "com.example.app", 
                    "bundleIdentifier": "com.example.app", 
                    "developerName": "Example.com", 
                    "versions": [AltSource.App.Version()],
                    "localizedDescription": "An app that is an example.",
                    "iconURL": "https://example.com/icon.png",
                    "appPermissions": AltSource.App.Permissions({
                        "entitlements": [],
                        "privacy": []
                    })
                }
        
        def to_dict(self) -> dict[str]:
            ret = self._src.copy()
            if "appPermissions" in self._src.keys():
                ret["appPermissions"] = self.appPermissions.to_dict()
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
            for key in self._required_keys:
                if key not in self._src.keys():
                    missing_keys.append(key)
            return missing_keys
        
        def is_valid(self) -> bool:
            """Checks to see if the AltSource.App is valid and contains all the required information.

            Returns:
                bool: True if the `App` is a valid AltSource.App.
            """
            valid_versions = self.versions is not None and len(self.versions) > 1 and all([version.is_valid() for version in self.versions])
            
            # Allow for old AltSource v1 API to be used
            if not valid_versions:
                valid_versions = self._src.get("version") is not None and self._src.get("downloadURL") is not None and self._src.get("versionDate") is not None
            
            valid_perms = self.appPermissions is None or self.appPermissions.is_valid()
            return valid_versions and valid_perms and not self.missing_keys()
        
        def latest_version(self, use_dates: bool = False) -> Version:
            if use_dates:
                return sorted(self.versions, key=lambda x: parse_github_datetime(x.date))[-1]
            return self.versions[0]
        
        def add_version(self, ver: Version):
            versions_list = [(ver.version,ver.buildVersion) for ver in self.versions]
            if (ver.version,ver.buildVersion) in versions_list:
                logging.warning(f"Version already exists in {self.name}. Automatically replaced with new one.")
                self.versions[versions_list.index((ver.version,ver.buildVersion))] = ver
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
        def screenshotURLs(self) -> list[str]:
            return self._src.get("screenshotURLs")
        @screenshotURLs.setter
        def screenshotURLs(self, value: list[str]):
            self._src["screenshotURLs"] = value
        
        @property 
        def versions(self) -> list[Version]:
            return self._src.get("versions",[])
        @versions.setter
        def versions(self, value: list[Version]):
            if self.versions is not None:
                logging.warning(f"Entire `versions` section has been replaced for {self.name}.")
            self._src["versions"] = value
            
        @property 
        def appPermissions(self) -> Permissions:
            return self._src.get("appPermissions")
        @appPermissions.setter
        def appPermissions(self, value: Permissions):
            self._src["appPermissions"] = value
            
        @property 
        def beta(self) -> bool:
            return self._src.get("beta")
        @beta.setter
        def beta(self, value: bool):
            self._src["beta"] = value
            
        ### Deprecated properties ###
        
        @property 
        def permissions(self) -> list[dict]:
            logging.warning(f"Using deprecated v1 AltSource API.")
            return self._src.get("permissions")
        @permissions.setter
        def permissions(self, value: list[dict]):
            logging.warning(f"Using deprecated v1 AltSource API.")
            self._src["permissions"] = value
        
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
        def size(self) -> int:
            logging.warning(f"Using deprecated v1 AltSource API.")
            return self._src.get("size")
        @size.setter
        def size(self, value: int):
            logging.warning(f"Using deprecated v1 AltSource API.")
            self._src["size"] = value
            
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
    
    class Article(Base):
        _required_keys = ["title", "identifier", "caption", "date"]
        
        def __init__(self, src: dict | None = None):
            if src is None:
                logging.info(f"Brand new AltSource.Article created. Please remember to set the following properties: {self._required_keys}")
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
            for key in self._required_keys:
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
        def identifier(self) -> str:
            return self._src.get("identifier")
        @identifier.setter
        def identifier(self, value: str):
            logging.warning(f"Article `identifier` changed from {self._src['identifier']} to {value}.")
            self._src["identifier"] = value
            
        @property 
        def caption(self) -> str:
            return self._src.get("caption")
        @caption.setter
        def caption(self, value: str):
            self._src["caption"] = value
            
        @property 
        def date(self) -> str:
            return self._src.get("date")
        @date.setter
        def date(self, value: str):
            self._src["date"] = value
            
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
            
        @property 
        def appID(self) -> str:
            return self._src.get("appID")
        @appID.setter
        def appID(self, value: str):
            self._src["appID"] = value
    # End class Article
    
    _required_keys = ["name", "identifier", "apps"]
    
    def __init__(self, src: dict | None = None, path: str | Path | None = None):
        """Create new AltSource object. If a src is included, all properties will be retained regardless of use in a 
            standard AltSource. This will *not* load the data from path. Use the `altsource_from_file` method for that.

        Args:
            src (dict, optional): the direct serialization of an AltSource json file. Defaults to None.
            path (str | Path, optional): the filepath to which a physical version of the AltSource should be stored. Defaults to None.
        """
        if src is not None:
            self._src = src
            self._src["apps"] = [self.App(app) for app in src.get("apps", [])]
            if "news" in self._src.keys():
                self._src["news"] = [self.Article(art) for art in src["news"]]
            self.apiVersion = "v2" # set current API version
            
            missing_keys = self.missing_keys()
            if missing_keys:
                logging.warning(f"Missing required AltSource keys: {missing_keys}")
        else:
            self._src = {"name": "ExampleSourceName", "identifier": "com.example.identifier", "apps": [], "version": 2}
            logging.info(f"Brand new AltSource created. Please remember to set the following properties: {self._required_keys}")
            
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
        for key in self._required_keys:
            if key not in self._src.keys():
                missing_keys.append(key)
        return missing_keys
    
    def is_valid(self):
        """Checks to see if the AltSource is valid and contains all the required information.

            Returns:
                bool: True if object is a valid AltSource.
        """
        valid_apps = all([app.is_valid() for app in self.apps])
        valid_news = self.news is None or all([article.is_valid() for article in self.news])
        return valid_apps and valid_news and not self.missing_keys()
    
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
        
    ### Unofficial AltSource property ###
    @property 
    def apiVersion(self) -> str:
        """Used to declare the AltSource API version."""
        return self._src.get("apiVersion")
    @apiVersion.setter
    def apiVersion(self, value: str):
        self._src["apiVersion"] = value
    
    @property 
    def subtitle(self) -> str:
        return self._src.get("subtitle")
    @subtitle.setter
    def subtitle(self, value: str):
        self._src["subtitle"] = value
        
    @property 
    def description(self) -> str:
        return self._src.get("description")
    @description.setter
    def description(self, value: str):
        self._src["description"] = value
        
    @property 
    def iconURL(self) -> str:
        return self._src.get("iconURL")
    @iconURL.setter
    def iconURL(self, value: str):
        self._src["iconURL"] = value
    
    @property 
    def headerURL(self) -> str:
        return self._src.get("headerURL")
    @headerURL.setter
    def headerURL(self, value: str):
        self._src["headerURL"] = value
        
    @property 
    def website(self) -> str:
        return self._src.get("website")
    @website.setter
    def website(self, value: str):
        self._src["website"] = value
        
    @property 
    def tintColor(self) -> str:
        return self._src.get("tintColor")
    @tintColor.setter
    def tintColor(self, value: str):
        self._src["tintColor"] = value
        
    @property 
    def featuredApps(self) -> list[str]:
        return self._src.get("featuredApps")
    @featuredApps.setter
    def featuredApps(self, value: list[str]):
        self._src["featuredApps"] = value
    
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
        
    @property 
    def userinfo(self) -> dict:
        return self._src.get("userinfo")
    @userinfo.setter
    def userinfo(self, value: dict):
        self._src["userinfo"] = value
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
    
def update_props_from_new_version(app: AltSource.App, new_ver: AltSource.App.Version):
    if new_ver.sha256 is None or app.appPermissions is None:
        ipa_path = download_temp_ipa(new_ver.downloadURL)
        if ipa_path is None:
            logging.warning(f"Broken download link for {app.name} ({new_ver.version}) prevented updating IPA based properties.")
            return
        logging.debug(f"Updating {app.name} sha256 checksum.")
        new_ver.calculate_sha256(ipa_path)
        logging.debug(f"Collecting {app.name} entitlements and privacy permissions.")
        app.appPermissions = AltSource.App.Permissions(extract_permissions(ipa_path=ipa_path))
