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

from datetime import datetime
from urllib.parse import urlparse

def utcnow() -> datetime:
    """Construct a UTC datetime from time.time().
    """
    return datetime.utcnow()

def fmt_github_datetime(dt: datetime) -> str:
    """Generates and returns the datetime in a format accepted by AltStore.

    The format used is the same as the GitHub API: yyyy-mm-ddThh:mm:ss-z
    Ex. 2022-05-25T03:39:23Z

    Returns:
        str: a formatted string containing the date and time.
    """
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def parse_github_datetime(dt: str) -> datetime:
    """Parses a string containing a datetime and returns a Python datetime object.
    
    The string must be using the Github API format: yyyy-mm-ddThh:mm:ss-z
    Ex. 2022-05-25T03:39:23Z

    Args:
        dt (str): a Github API format string containing the date and time

    Returns:
        datetime: a datetime object with the same date and time as the argument
    """
    return datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S%z")

def is_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
    
def flatten_ids(ids: list[str | dict[str, str]], use_keys: bool = True) -> list[str]:
    """Takes a list of mixed data types (str and dict) and converts them all to a list[str] by removing either the key or value of any dict objects.

    Args:
        ids (list[str  |  dict[str, str]]): The list of ids which is either just the `str` id or a `dict` where the `appID` is the key and `bundleID` the value.
        use_keys (bool, optional): If True, the method will flatten the list using the keys of any `dict` objects, rather than their values (disposing of the unused key/value). Defaults to True.

    Returns:
        list[str]: A flattened list of app ids.
    """
    nested_ids = [[id] if isinstance(id, str) else id.keys() if use_keys else id.values() for id in ids] # converts a mixed list of strings and dicts to a flat list using the dict keys or values
    flat_ids = [item for sublist in nested_ids for item in sublist] # flatten list
    return flat_ids

def gen_id_parse_table(ids: list[str | dict[str, str]]) -> dict[str, str] | None:
    """Creates a singular dictionary that combines all the dict objects in `ids`.

    Args:
        ids (list[str | dict[str, str]]): _description_

    Returns:
        dict[str, str] | None: A dict that allows conversion from key:`appID` to value:`bundleID` based on the list of ids given.
    """
    convert_ids = [dic for dic in ids if isinstance(dic, dict)]
    if convert_ids is not None:
        return {k: v for d in convert_ids for k, v in d.items()} # combine into one dict
    return None
