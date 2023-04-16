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

import plistlib
from pathlib import Path

from altparse.ipautil.helpers import extract_ipa
from altparse.ipautil.errors import InsufficientArgError


class IPA_Info:
    """A wrapper class that makes getting relevant information from the IPAs Info.plist file easier for those who don't have Apple's absurd lingo memorized.
    """
    def __init__(self, ipa_path: Path | None = None, plist_path: Path | None = None, plist: dict | None = None):
        """Encapsulates an IPA to retrieve metadata more easily.

        Processing priority: `plist` > `plist_path` > `ipa_path`. The `ipa_path` and `plist` will be saved for later use to return various aspects of the IPA.
        If any property of the IPA should return None, the IPA simply does not have that property.

        Args:
            ipa_path (Path | None, optional): The Path to the .ipa file. Defaults to None.
            plist_path (Path | None, optional): The Path to the Info.plist file. Defaults to None.
            plist (dict | None, optional): The plist as loaded into a dictionary object. Defaults to None.

        Raises:
            InsufficientArgError: Occurs if there were no arguments received.
        """
        if plist is None:
            if ipa_path is None and plist_path is None:
                raise InsufficientArgError("Not enough arguments supplied to create IPA_Info object.")
            if ipa_path is not None and plist_path is None:
                payload_path = extract_ipa(ipa_path, use_temp_dir=True)
                plist_path = list(payload_path.rglob("Info.plist"))[0] # locate the Info.plist path within the extracted data
            if plist_path is not None:
                with open(plist_path, "rb") as fp:
                    plist = plistlib.load(fp)
        self._ipa_path, self._plist = ipa_path, plist
    
    @property 
    def DisplayName(self) -> str:
        """The name that is shown on the iOS Home Screen.
        """
        return self._plist.get("CFBundleDisplayName")
        
    @property
    def DevelopmentRegion(self) -> str:
        """The development region as determined by the written language used. 
        
        Example: "en"444
        """
        return self._plist.get("CFBundleDevelopmentRegion")
        
    @property 
    def Identifier(self) -> str:
        return self._plist.get("CFBundleIdentifier")
        
    @property 
    def InfoDictionaryVersion(self) -> str:
        """The plist version this data was stored in.
        """
        return self._plist.get("CFBundleInfoDictionaryVersion")
        
    @property 
    def Name(self) -> str:
        return self._plist.get("CFBundleName")
        
    @property 
    def ShortVersion(self) -> str:
        """The most commonly used and more accurate version designed for display to end users.
        """
        return self._plist.get("CFBundleShortVersionString").lstrip("v")
        
    @property 
    def SupportedPlatforms(self) -> list[str]:
        return self._plist.get("CFBundleSupportedPlatforms")
        
    @property 
    def Version(self) -> str:
        """Version that is designed to indicate the internal build version, sometimes only contains one digit or the full version string.
        """
        return self._plist.get("CFBundleVersion")
    
    @property 
    def MinimumOSVersion(self) -> str:
        return self._plist.get("MinimumOSVersion")
    
    @property 
    def NetworkUsageDescription(self) -> str:
        return self._plist.get("NSLocalNetworkUsageDescription")
    
    @property 
    def MicUsageDescription(self) -> str:
        return self._plist.get("NSMicrophoneUsageDescription")
    
    @property 
    def FileSharingEnabled(self) -> bool:
        return self._plist.get("UIFileSharingEnabled", False)