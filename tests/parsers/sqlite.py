#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the SQLite database parser."""

import unittest

from plaso.parsers import sqlite
# Register plugins.
from plaso.parsers import sqlite_plugins  # pylint: disable=unused-import

from tests.parsers import test_lib


class SQLiteParserTest(test_lib.ParserTestCase):
  """Tests for the SQLite database parser."""

  def testGetPluginNames(self):
    """Tests the GetPluginNames function."""
    all_plugin_names = sqlite.SQLiteParser.GetPluginNames()

    self.assertNotEqual(all_plugin_names, [])

    self.assertTrue(u'skype' in all_plugin_names)
    self.assertTrue(u'chrome_history' in all_plugin_names)
    self.assertTrue(u'firefox_history' in all_plugin_names)

    # Change the calculations of the parsers.
    parser_filter_string = u'chrome_history, firefox_history, -skype'
    plugin_names = sqlite.SQLiteParser.GetPluginNames(
        parser_filter_string=parser_filter_string)

    self.assertEqual(len(plugin_names), 2)
    self.assertFalse(u'skype' in plugin_names)
    self.assertTrue(u'chrome_history' in plugin_names)
    self.assertTrue(u'firefox_history' in plugin_names)

    # Test with a different plugin selection.
    parser_filter_string = u'sqlite, -skype'
    plugin_names = sqlite.SQLiteParser.GetPluginNames(
        parser_filter_string=parser_filter_string)

    # This should result in all plugins EXCEPT the skype one.
    self.assertEqual(len(plugin_names), len(all_plugin_names) - 1)
    self.assertFalse(u'skype' in plugin_names)
    self.assertTrue(u'chrome_history' in plugin_names)
    self.assertTrue(u'firefox_history' in plugin_names)

  def testFileParserChainMaintenance(self):
    """Tests that the parser chain is correctly maintained by the parser."""
    parser = sqlite.SQLiteParser()
    test_file = self._GetTestFilePath([u'contacts2.db'])

    event_queue_consumer = self._ParseFile(parser, test_file)
    event_objects = self._GetEventObjectsFromQueue(event_queue_consumer)
    for event in event_objects:
      chain = event.parser
      self.assertEqual(1, chain.count(u'/'))

  def testQueryDatabaseWithWAL(self):
    """Tests querying a database with the WAL file."""
    database_file = self._GetTestFilePath([u'wal_database.db'])
    wal_file = self._GetTestFilePath([u'wal_database.db-wal'])

    database = sqlite.SQLiteDatabase(u'wal_database.db')
    with open(database_file, u'rb') as database_file_object:
      with open(wal_file, u'rb') as wal_file_object:
        database.Open(database_file_object, wal_file_object=wal_file_object)

    row_results = []
    for row in database.Query(u'SELECT * FROM MyTable'):
      row_results.append((row['Field1'], row['Field2'], str(row['Field3'])))

    expected_results = [
        (u'Committed Text 1', 1, b'None'),
        (u'Committed Text 2', 2, b'None'),
        (u'Modified Committed Text 3', 4, b'None'),
        (u'Committed Text 4', 5, b'None'),
        (u'Committed Text 5', 7, b'None'),
        (u'Committed Text 6', 8, b'None'),
        (u'Committed Text 7', 9, b'None'),
        (u'Unhashable Row 1', 10, b'Binary Text!\x01\x02\x03'),
        (u'Unhashable Row 2', 11, b'More Binary Text!\x01\x02\x03'),
        (u'New Text 1', 12, b'None'),
        (u'New Text 2', 13, b'None')]

    self.assertEqual(expected_results, row_results)

  def testQueryDatabaseWithoutWAL(self):
    """Tests querying a database without the WAL file."""
    database_file = self._GetTestFilePath([u'wal_database.db'])

    database = sqlite.SQLiteDatabase(u'wal_database.db')
    with open(database_file, u'rb') as database_file_object:
      database.Open(database_file_object)

    row_results = []
    for row in database.Query(u'SELECT * FROM MyTable'):
      row_results.append((row['Field1'], row['Field2'], str(row['Field3'])))

    expected_results = [
        (u'Committed Text 1', 1, b'None'),
        (u'Committed Text 2', 2, b'None'),
        (u'Deleted Text 1', 3, b'None'),
        (u'Committed Text 3', 4, b'None'),
        (u'Committed Text 4', 5, b'None'),
        (u'Deleted Text 2', 6, b'None'),
        (u'Committed Text 5', 7, b'None'),
        (u'Committed Text 6', 8, b'None'),
        (u'Committed Text 7', 9, b'None'),
        (u'Unhashable Row 1', 10, b'Binary Text!\x01\x02\x03')]

    self.assertEqual(expected_results, row_results)


if __name__ == '__main__':
  unittest.main()
