"""
Project: altparse
Module: tests
Created Date: 30 Nov 2022
Author: Noah Keck
:------------------------------------------------------------------------------:
MIT License
Copyright (c) 2022
:------------------------------------------------------------------------------:
"""

import sys
import unittest

# required for testing in an environment without altparse installed as a package
sys.path.insert(0, './src')
sys.path.insert(1, './src/altparse')

from altparse import AltSource


class TestDivideByThree(unittest.TestCase):

	def test_create_altsource(self):
		return True

unittest.main()
