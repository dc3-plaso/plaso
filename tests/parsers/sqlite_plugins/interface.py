#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tets for the SQLite plugin interface."""

import unittest

from plaso.parsers import sqlite
from plaso.parsers.sqlite_plugins import interface
from tests.parsers.sqlite_plugins import test_lib


class BogusSQLitePlugin(interface.SQLitePlugin):

  NAME = u'bogus'

  QUERIES = [(u'SELECT Field1, Field2 FROM MyTable', u'ParseMyTableRow')]

  REQUIRED_TABLES = frozenset([u'MyTable'])

  def __init__(self):
    self.results = []

  def ParseMyTableRow(
      self, parser_mediator, row, query=None, cache=None, database=None,
      **unused_kwargs):
    """Parses a MyTable row.

    Args:
      parser_mediator: A parser mediator object (instance of ParserMediator).
      row: The row resulting from the query.
      query: Optional query string. The default is None.
      cache: A cache object (instance of SQLiteCache).
      database: A database object (instance of SQLiteDatabase).
    """
    from_wal = parser_mediator.GetFileEntry().path_spec.location.endswith(
        u'-wal')
    self.results.append(((row['Field1'], row['Field2']), from_wal))


class SQLiteInterfaceTest(test_lib.SQLitePluginTestCase):
  """Tests for the SQLite plugin interface."""

  def testProcessWithWAL(self):
    """Test the Process function on a database with WAL file."""
    bogus_plugin = BogusSQLitePlugin()
    database_file = self._GetTestFilePath([u'wal_database.db'])
    wal_file = self._GetTestFilePath([u'wal_database.db-wal'])

    cache = sqlite.SQLiteCache()
    self._ParseDatabaseFileWithPlugin(
        bogus_plugin, database_file, cache=cache, wal_path=wal_file)

    expected_results = [
        ((u'Committed Text 1', 1), False),
        ((u'Committed Text 2', 2), False),
        ((u'Deleted Text 1', 3), False),
        ((u'Committed Text 3', 4), False),
        ((u'Committed Text 4', 5), False),
        ((u'Deleted Text 2', 6), False),
        ((u'Committed Text 5', 7), False),
        ((u'Committed Text 6', 8), False),
        ((u'Committed Text 7', 9), False),
        ((u'Modified Committed Text 3', 4), True),
        ((u'New Text 1', 10), True),
        ((u'New Text 2', 11), True),
        ((u'New Text 3', 12), True)]

    self.assertEqual(expected_results, bogus_plugin.results)

  def testProcessWithoutWAL(self):
    """Test the Process function on a database without WAL file."""
    bogus_plugin = BogusSQLitePlugin()
    database_file = self._GetTestFilePath([u'wal_database.db'])

    cache = sqlite.SQLiteCache()
    self._ParseDatabaseFileWithPlugin(bogus_plugin, database_file, cache=cache)

    expected_results = [
        ((u'Committed Text 1', 1), False),
        ((u'Committed Text 2', 2), False),
        ((u'Deleted Text 1', 3), False),
        ((u'Committed Text 3', 4), False),
        ((u'Committed Text 4', 5), False),
        ((u'Deleted Text 2', 6), False),
        ((u'Committed Text 5', 7), False),
        ((u'Committed Text 6', 8), False),
        ((u'Committed Text 7', 9), False)]

    self.assertEqual(expected_results, bogus_plugin.results)


if __name__ == '__main__':
  unittest.main()