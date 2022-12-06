"""
Project: altparse
Module: tests
Created Date: 05 Dec 2022
Author: Noah Keck
:------------------------------------------------------------------------------:
MIT License
Copyright (c) 2022
:------------------------------------------------------------------------------:
"""

import os
import sys
import logging

# required for testing in an environment without altparse installed as a package
sys.path.insert(0, './src')
sys.path.insert(1, './src/altparse')

from altparse.ipautil import get_or_create_github_release

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

try:
    g_token = os.environ["GITHUB_TOKEN"]
    g_repo_id = 132412341 # enter the github release by its API id
    g_release = get_or_create_github_release(g_token, repo_id=g_repo_id) # gets the github release as a Python obj
except KeyError as err:
    logging.error(f"Could not find GitHub Token.")
    logging.error(f"{type(err).__name__}: {str(err)}")
