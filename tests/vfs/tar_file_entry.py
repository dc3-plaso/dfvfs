#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the file entry implementation using the tarfile."""

import os
import unittest

from dfvfs.path import os_path_spec
from dfvfs.path import tar_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import tar_file_entry
from dfvfs.vfs import tar_file_system


class TARFileEntryTest(unittest.TestCase):
  """The unit test for the TAR extracted file entry object."""

  def _assertSubFileEntries(self, file_entry, expected_sub_file_entry_names):
    """Helper function that asserts the sub file entries.

    Args:
      file_entry (FileEntry): file entry.
      sub_file_entry_names (list[str]): sub file entry names.
    """
    sub_file_entry_names = []
    for sub_file_entry in file_entry.sub_file_entries:
      sub_file_entry_names.append(sub_file_entry.name)

    self.assertEqual(
        len(sub_file_entry_names), len(expected_sub_file_entry_names))
    self.assertEqual(
        sorted(sub_file_entry_names), sorted(expected_sub_file_entry_names))

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = os.path.join(u'test_data', u'syslog.tar')
    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._tar_path_spec = tar_path_spec.TARPathSpec(
        location=u'/syslog', parent=self._os_path_spec)

    self._file_system = tar_file_system.TARFileSystem(self._resolver_context)
    self._file_system.Open(self._tar_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()

  def testIntialize(self):
    """Test the initialize functionality."""
    file_entry = tar_file_entry.TARFileEntry(
        self._resolver_context, self._file_system, self._tar_path_spec)

    self.assertIsNotNone(file_entry)

  def testGetParentFileEntry(self):
    """Tests the GetParentFileEntry function."""
    path_spec = tar_path_spec.TARPathSpec(
        location=u'/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()

    self.assertIsNotNone(parent_file_entry)

    self.assertEqual(parent_file_entry.name, u'')

  def testGetStat(self):
    """Tests the GetStat function."""
    path_spec = tar_path_spec.TARPathSpec(
        location=u'/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    stat_object = file_entry.GetStat()

    self.assertIsNotNone(stat_object)
    self.assertEqual(stat_object.type, stat_object.TYPE_FILE)
    self.assertEqual(stat_object.size, 1247)

    self.assertEqual(stat_object.mode, 256)
    self.assertEqual(stat_object.uid, 151107)
    self.assertEqual(stat_object.gid, 5000)

    self.assertEqual(stat_object.mtime, 1343166324)
    self.assertFalse(hasattr(stat_object, u'mtime_nano'))

  def testIsFunctions(self):
    """Test the Is? functions."""
    path_spec = tar_path_spec.TARPathSpec(
        location=u'/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertFalse(file_entry.IsRoot())
    self.assertFalse(file_entry.IsVirtual())
    self.assertTrue(file_entry.IsAllocated())

    self.assertFalse(file_entry.IsDevice())
    self.assertFalse(file_entry.IsDirectory())
    self.assertTrue(file_entry.IsFile())
    self.assertFalse(file_entry.IsLink())
    self.assertFalse(file_entry.IsPipe())
    self.assertFalse(file_entry.IsSocket())

    path_spec = tar_path_spec.TARPathSpec(
        location=u'/', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertTrue(file_entry.IsRoot())
    self.assertTrue(file_entry.IsVirtual())
    self.assertTrue(file_entry.IsAllocated())

    self.assertFalse(file_entry.IsDevice())
    self.assertTrue(file_entry.IsDirectory())
    self.assertFalse(file_entry.IsFile())
    self.assertFalse(file_entry.IsLink())
    self.assertFalse(file_entry.IsPipe())
    self.assertFalse(file_entry.IsSocket())

  def testSubFileEntries(self):
    """Test the sub file entries iteration functionality."""
    path_spec = tar_path_spec.TARPathSpec(
        location=u'/', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_sub_file_entries, 1)

    self._assertSubFileEntries(file_entry, [u'syslog'])

    # Test on a tar file that has missing directory entries.
    test_file = os.path.join(u'test_data', u'missing_directory_entries.tar')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    path_spec = tar_path_spec.TARPathSpec(location=u'/', parent=path_spec)

    file_system = tar_file_system.TARFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)
    file_system.Open(path_spec)

    file_entry = file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_sub_file_entries, 2)

    self._assertSubFileEntries(
        file_entry, [u'File System', u'Non Missing Directory Entry'])

    for sub_file_entry in file_entry.sub_file_entries:
      # The "File System" and its sub-directories have missing entries within
      # the tar file, but still should be found due to the AssetManifest.plist
      # file found within the directories.
      if sub_file_entry.name == u'File System':
        self._assertSubFileEntries(sub_file_entry, [u'Recordings'])
        for sub_sub_file_entry in sub_file_entry.sub_file_entries:
          self._assertSubFileEntries(
              sub_sub_file_entry, [u'AssetManifest.plist'])
      else:
        self._assertSubFileEntries(sub_file_entry, [u'test_file.txt'])

    file_system.Close()

  def testDataStreams(self):
    """Test the data streams functionality."""
    path_spec = tar_path_spec.TARPathSpec(
        location=u'/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 1)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [u''])

    path_spec = tar_path_spec.TARPathSpec(
        location=u'/', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 0)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [])

  def testGetDataStream(self):
    """Tests the GetDataStream function."""
    path_spec = tar_path_spec.TARPathSpec(
        location=u'/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_stream_name = u''
    data_stream = file_entry.GetDataStream(data_stream_name)
    self.assertIsNotNone(data_stream)
    self.assertEqual(data_stream.name, data_stream_name)

    data_stream = file_entry.GetDataStream(u'bogus')
    self.assertIsNone(data_stream)


if __name__ == '__main__':
  unittest.main()
