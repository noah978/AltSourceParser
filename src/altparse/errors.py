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

class AltSourceError(Exception):
    """Base exception for AltSource parsing."""
    pass

class GitHubError(AltSourceError):
    """Occurs when there is an error accessing the GitHub API."""
    pass

class ArgumentTypeError(AltSourceError):
    """Occurs when an argument is not of the correct type."""
    pass

class InsufficientArgsError(AltSourceError):
    """Occurs when there are not enough arguments passed."""
    pass