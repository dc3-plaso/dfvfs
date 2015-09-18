#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the file system implementation using the 7z file."""

import os
import unittest

from dfvfs.path import os_path_spec
from dfvfs.path import seven_z_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import seven_z_file_system


class SevenZFileSystemTest(unittest.TestCase):
  """The unit test for the tar file system object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = os.path.join(u'test_data', u'syslog.7z')
    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._seven_z_path_spec = seven_z_path_spec.SevenZPathSpec(
        location=u'/syslog', parent=self._os_path_spec)

  def testOpenAndClose(self):
    """Test the open and close functionality."""
    file_system = seven_z_file_system.SevenZFileSystem(self._resolver_context)
    self.assertNotEqual(file_system, None)

    file_system.Open(path_spec=self._seven_z_path_spec)

    file_system.Close()

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    file_system = seven_z_file_system.SevenZFileSystem(self._resolver_context)
    self.assertNotEqual(file_system, None)

    file_system.Open(path_spec=self._seven_z_path_spec)

    path_spec = seven_z_path_spec.SevenZPathSpec(
        location=u'/syslog', parent=self._os_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = seven_z_path_spec.SevenZPathSpec(
        location=u'/bogus', parent=self._os_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    file_system.Close()

  def testGetFileEntryByPathSpec(self):
    """Test the get entry by path specification functionality."""
    file_system = seven_z_file_system.SevenZFileSystem(self._resolver_context)
    self.assertNotEqual(file_system, None)

    file_system.Open(path_spec=self._seven_z_path_spec)

    path_spec = seven_z_path_spec.SevenZPathSpec(
        location=u'/syslog', parent=self._os_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEqual(file_entry, None)
    self.assertEqual(file_entry.name, u'syslog')

    path_spec = seven_z_path_spec.SevenZPathSpec(
        location=u'/bogus', parent=self._os_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertEqual(file_entry, None)

    file_system.Close()

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    file_system = seven_z_file_system.SevenZFileSystem(self._resolver_context)
    self.assertNotEqual(file_system, None)

    file_system.Open(path_spec=self._seven_z_path_spec)

    file_entry = file_system.GetRootFileEntry()

    self.assertNotEqual(file_entry, None)
    self.assertEqual(file_entry.name, u'')

    file_system.Close()


if __name__ == '__main__':
  unittest.main()
