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
        
        Example: "en"
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
    
    # Usage Descriptions
    @property 
    def BluetoothAlwaysUsageDescription(self) -> str:
        return self._plist.get("NSBluetoothAlwaysUsageDescription")
    @property 
    def BluetoothPeripheralUsageDescription(self) -> str:
        return self._plist.get("NSBluetoothPeripheralUsageDescription")
    @property 
    def CalendarsUsageDescription(self) -> str:
        return self._plist.get("NSCalendarsUsageDescription")
    @property 
    def RemindersUsageDescription(self) -> str:
        return self._plist.get("NSRemindersUsageDescription")
    @property 
    def CameraUsageDescription(self) -> str:
        return self._plist.get("NSCameraUsageDescription")
    @property 
    def MicrophoneUsageDescription(self) -> str:
        return self._plist.get("NSMicrophoneUsageDescription")
    @property 
    def ContactsUsageDescription(self) -> str:
        return self._plist.get("NSContactsUsageDescription")
    @property 
    def FaceIDUsageDescription(self) -> str:
        return self._plist.get("NSFaceIDUsageDescription")
    @property 
    def DesktopFolderUsageDescription(self) -> str:
        return self._plist.get("NSDesktopFolderUsageDescription")
    @property 
    def DocumentsFolderUsageDescription(self) -> str:
        return self._plist.get("NSDocumentsFolderUsageDescription")
    @property 
    def DownloadsFolderUsageDescription(self) -> str:
        return self._plist.get("NSDownloadsFolderUsageDescription")
    @property 
    def NetworkVolumesUsageDescription(self) -> str:
        return self._plist.get("NSNetworkVolumesUsageDescription")
    @property 
    def RemovableVolumesUsageDescription(self) -> str:
        return self._plist.get("NSRemovableVolumesUsageDescription")
    @property 
    def FileProviderDomainUsageDescription(self) -> str:
        return self._plist.get("NSFileProviderDomainUsageDescription")
    @property 
    def GKFriendListUsageDescription(self) -> str:
        return self._plist.get("NSGKFriendListUsageDescription")
    @property 
    def HealthClinicalHealthRecordsShareUsageDescription(self) -> str:
        return self._plist.get("NSHealthClinicalHealthRecordsShareUsageDescription")
    @property 
    def HealthShareUsageDescription(self) -> str:
        return self._plist.get("NSHealthShareUsageDescription")
    @property 
    def HealthUpdateUsageDescription(self) -> str:
        return self._plist.get("NSHealthUpdateUsageDescription")
    @property 
    def HomeKitUsageDescription(self) -> str:
        return self._plist.get("NSHomeKitUsageDescription")
    @property 
    def LocationAlwaysAndWhenInUseUsageDescription(self) -> str:
        return self._plist.get("NSLocationAlwaysAndWhenInUseUsageDescription")
    @property 
    def LocationUsageDescription(self) -> str:
        return self._plist.get("NSLocationUsageDescription")
    @property 
    def LocationWhenInUseUsageDescription(self) -> str:
        return self._plist.get("NSLocationWhenInUseUsageDescription")
    @property 
    def LocationAlwaysUsageDescription(self) -> str:
        return self._plist.get("NSLocationAlwaysUsageDescription")
    @property 
    def AppleMusicUsageDescription(self) -> str:
        return self._plist.get("NSAppleMusicUsageDescription")
    @property 
    def MotionUsageDescription(self) -> str:
        return self._plist.get("NSMotionUsageDescription")
    @property 
    def FallDetectionUsageDescription(self) -> str:
        return self._plist.get("NSFallDetectionUsageDescription")
    @property 
    def LocalNetworkUsageDescription(self) -> str:
        return self._plist.get("NSLocalNetworkUsageDescription")
    @property 
    def NearbyInteractionUsageDescription(self) -> str:
        return self._plist.get("NSNearbyInteractionUsageDescription")
    @property 
    def NearbyInteractionAllowOnceUsageDescription(self) -> str:
        return self._plist.get("NSNearbyInteractionAllowOnceUsageDescription")
    @property 
    def NFCReaderUsageDescription(self) -> str:
        return self._plist.get("NFCReaderUsageDescription")
    @property 
    def PhotoLibraryAddUsageDescription(self) -> str:
        return self._plist.get("NSPhotoLibraryAddUsageDescription")
    @property 
    def PhotoLibraryUsageDescription(self) -> str:
        return self._plist.get("NSPhotoLibraryUsageDescription")
    @property 
    def UserTrackingUsageDescription(self) -> str:
        return self._plist.get("NSUserTrackingUsageDescription")
    @property 
    def AppleEventsUsageDescription(self) -> str:
        return self._plist.get("NSAppleEventsUsageDescription")
    @property 
    def SystemAdministrationUsageDescription(self) -> str:
        return self._plist.get("NSSystemAdministrationUsageDescription")
    @property 
    def SensorKitUsageDescription(self) -> str:
        return self._plist.get("NSSensorKitUsageDescription")
    @property 
    def SiriUsageDescription(self) -> str:
        return self._plist.get("NSSiriUsageDescription")
    @property 
    def SpeechRecognitionUsageDescription(self) -> str:
        return self._plist.get("NSSpeechRecognitionUsageDescription")
    @property 
    def VideoSubscriberAccountUsageDescription(self) -> str:
        return self._plist.get("NSVideoSubscriberAccountUsageDescription")
    @property 
    def IdentityUsageDescription(self) -> str:
        return self._plist.get("NSIdentityUsageDescription")
    
    
    @property 
    def FileSharingEnabled(self) -> bool:
        return self._plist.get("UIFileSharingEnabled", False)