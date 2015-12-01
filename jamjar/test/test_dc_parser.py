#------------------------------------------------------------------------------
# test_dc_parser.py - Test for the -dc parser module
#
# November 2015, Zoe Kelly
#------------------------------------------------------------------------------

"""dc parser tests."""

__all__ = ()


import unittest

from .. import database
from .. import parsers

class DmParserTest(unittest.TestCase):
    """Tests for the jam dm parser"""

    def setUp(self):
        self._db = database.Database()
        self._dc_parser = parsers.DCParser(self._db)

    def tearDown(self):
        self._db = None

    #@@@!

