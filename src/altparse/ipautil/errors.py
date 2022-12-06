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

class IPAError(Exception):
    """Base exception for all IPA processing errors."""
    pass

class InsufficientArgError(IPAError):
    """Occurs when there are insufficient number of arguments."""
    pass

class FileError(IPAError):
    """Occurs if there are issues when processing files."""
    pass