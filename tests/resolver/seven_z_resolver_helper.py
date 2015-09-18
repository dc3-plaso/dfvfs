#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the 7z resolver helper implementation."""

import unittest

from dfvfs.resolver import seven_z_resolver_helper
from tests.resolver import test_lib


class TarResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the tar resolver helper implementation."""

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    resolver_helper_object = seven_z_resolver_helper.SevenZResolverHelper()
    self._TestNewFileObject(resolver_helper_object)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    resolver_helper_object = seven_z_resolver_helper.SevenZResolverHelper()
    self._TestNewFileSystem(resolver_helper_object)


if __name__ == '__main__':
  unittest.main()
