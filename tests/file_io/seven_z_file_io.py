#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the 7z extracted file-like object."""

import os
import unittest

from dfvfs.file_io import seven_z_file_io
from dfvfs.path import os_path_spec
from dfvfs.path import seven_z_path_spec
from dfvfs.resolver import context
from tests.file_io import test_lib


class SevenZFileTest(test_lib.SylogTestCase):
  """The unit test for a 7z extracted file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(SevenZFileTest, self).setUp()
    self._resolver_context = context.Context()
    test_file = os.path.join(u'test_data', u'syslog.7z')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._7z_path_spec = seven_z_path_spec.SevenZPathSpec(
        location=u'/syslog', parent=path_spec)

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = seven_z_file_io.SevenZFile(self._resolver_context)
    file_object.open(path_spec=self._7z_path_spec)

    self._TestGetSizeFileObject(file_object)

    file_object.close()

  def testSeek(self):
    """Test the seek functionality."""
    file_object = seven_z_file_io.SevenZFile(self._resolver_context)
    file_object.open(path_spec=self._7z_path_spec)

    self._TestSeekFileObject(file_object)

    file_object.close()

  def testRead(self):
    """Test the read functionality."""
    file_object = seven_z_file_io.SevenZFile(self._resolver_context)
    file_object.open(path_spec=self._7z_path_spec)

    self._TestReadFileObject(file_object)

    file_object.close()


if __name__ == '__main__':
  unittest.main()
