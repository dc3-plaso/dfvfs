#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the encoded stream file-like object."""

import os
import unittest

from dfvfs.file_io import encrypted_stream_io
from dfvfs.file_io import os_file_io
from dfvfs.lib import definitions
from dfvfs.path import encrypted_stream_path_spec
from dfvfs.path import os_path_spec
from dfvfs.resolver import context
from tests.file_io import test_lib



class AESEncryptedStreamTest(test_lib.PaddedSyslogTestCase):
  """The unit test for a AES encrypted stream file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = os.path.join(u'test_data', u'syslog.aes')
    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._encrypted_stream_path_spec = (
        encrypted_stream_path_spec.EncryptedStreamPathSpec(
            encryption_method=definitions.ENCRYPTION_METHOD_AES,
            key=u'This is a key123',
            block_cipher_mode=definitions.BLOCK_CIPHER_MODE_CBC,
            iv=u'This is an IV456',
            parent=self._os_path_spec))
    self.padding_size = 1

  def testOpenCloseFileObject(self):
    """Test the open and close functionality using a file-like object."""
    os_file_object = os_file_io.OSFile(self._resolver_context)
    os_file_object.open(path_spec=self._os_path_spec)
    file_object = encrypted_stream_io.EncryptedStream(
        self._resolver_context,
        encryption_method=definitions.ENCRYPTION_METHOD_AES,
        file_object=os_file_object,
        key=u'This is a key123',
        block_cipher_mode=definitions.BLOCK_CIPHER_MODE_CBC,
        iv=u'This is an IV456')
    file_object.open()

    self._TestGetSizeFileObject(file_object)

    file_object.close()
    os_file_object.close()

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = encrypted_stream_io.EncryptedStream(self._resolver_context)
    file_object.open(path_spec=self._encrypted_stream_path_spec)

    self._TestGetSizeFileObject(file_object)

    file_object.close()

  def testSeek(self):
    """Test the seek functionality."""
    file_object = encrypted_stream_io.EncryptedStream(self._resolver_context)
    file_object.open(path_spec=self._encrypted_stream_path_spec)

    self._TestSeekFileObject(file_object)

    file_object.close()

  def testRead(self):
    """Test the read functionality."""
    file_object = encrypted_stream_io.EncryptedStream(self._resolver_context)
    file_object.open(path_spec=self._encrypted_stream_path_spec)

    self._TestReadFileObject(file_object)

    file_object.close()


class BlowfishEncryptedStreamTest(test_lib.PaddedSyslogTestCase):
  """The unit test for a Blowfish encrypted stream file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = os.path.join(u'test_data', u'syslog.blowfish')
    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._encrypted_stream_path_spec = (
        encrypted_stream_path_spec.EncryptedStreamPathSpec(
            encryption_method=definitions.ENCRYPTION_METHOD_BLOWFISH,
            key=u'This is a key123',
            block_cipher_mode=definitions.BLOCK_CIPHER_MODE_CBC,
            iv=u'This IV!',
            parent=self._os_path_spec))
    self.padding_size = 1

  def testOpenCloseFileObject(self):
    """Test the open and close functionality using a file-like object."""
    os_file_object = os_file_io.OSFile(self._resolver_context)
    os_file_object.open(path_spec=self._os_path_spec)
    file_object = encrypted_stream_io.EncryptedStream(
        self._resolver_context,
        encryption_method=definitions.ENCRYPTION_METHOD_BLOWFISH,
        file_object=os_file_object,
        key=u'This is a key123',
        block_cipher_mode=definitions.BLOCK_CIPHER_MODE_CBC,
        iv=u'This IV!')
    file_object.open()

    self._TestGetSizeFileObject(file_object)

    file_object.close()
    os_file_object.close()

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = encrypted_stream_io.EncryptedStream(self._resolver_context)
    file_object.open(path_spec=self._encrypted_stream_path_spec)

    self._TestGetSizeFileObject(file_object)

    file_object.close()

  def testSeek(self):
    """Test the seek functionality."""
    file_object = encrypted_stream_io.EncryptedStream(self._resolver_context)
    file_object.open(path_spec=self._encrypted_stream_path_spec)

    self._TestSeekFileObject(file_object)

    file_object.close()

  def testRead(self):
    """Test the read functionality."""
    file_object = encrypted_stream_io.EncryptedStream(self._resolver_context)
    file_object.open(path_spec=self._encrypted_stream_path_spec)

    self._TestReadFileObject(file_object)

    file_object.close()


class DES3EncryptedStreamTest(test_lib.PaddedSyslogTestCase):
  """The unit test for a Triple DES encrypted stream file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = os.path.join(u'test_data', u'syslog.des3')
    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._encrypted_stream_path_spec = (
        encrypted_stream_path_spec.EncryptedStreamPathSpec(
            encryption_method=definitions.ENCRYPTION_METHOD_DES3,
            key=u'This is a key123',
            block_cipher_mode=definitions.BLOCK_CIPHER_MODE_CBC,
            iv=u'This IV!',
            parent=self._os_path_spec))
    self.padding_size = 1

  def testOpenCloseFileObject(self):
    """Test the open and close functionality using a file-like object."""
    os_file_object = os_file_io.OSFile(self._resolver_context)
    os_file_object.open(path_spec=self._os_path_spec)
    file_object = encrypted_stream_io.EncryptedStream(
        self._resolver_context,
        encryption_method=definitions.ENCRYPTION_METHOD_DES3,
        file_object=os_file_object,
        key=u'This is a key123',
        block_cipher_mode=definitions.BLOCK_CIPHER_MODE_CBC,
        iv=u'This IV!')
    file_object.open()

    self._TestGetSizeFileObject(file_object)

    file_object.close()
    os_file_object.close()

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = encrypted_stream_io.EncryptedStream(self._resolver_context)
    file_object.open(path_spec=self._encrypted_stream_path_spec)

    self._TestGetSizeFileObject(file_object)

    file_object.close()

  def testSeek(self):
    """Test the seek functionality."""
    file_object = encrypted_stream_io.EncryptedStream(self._resolver_context)
    file_object.open(path_spec=self._encrypted_stream_path_spec)

    self._TestSeekFileObject(file_object)

    file_object.close()

  def testRead(self):
    """Test the read functionality."""
    file_object = encrypted_stream_io.EncryptedStream(self._resolver_context)
    file_object.open(path_spec=self._encrypted_stream_path_spec)

    self._TestReadFileObject(file_object)

    file_object.close()


if __name__ == '__main__':
  unittest.main()
