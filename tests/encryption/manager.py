#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the encryption manager."""

import unittest

from dfvfs.encryption import aes_decrypter
from dfvfs.encryption import decrypter
from dfvfs.encryption import manager
from dfvfs.lib import definitions


class TestDecrypter(decrypter.Decrypter):
  """Class that implements a test decrypter."""

  ENCRYPTION_METHOD = u'test'

  def __init__(
      self, key=None, block_cipher_mode=None, iv=None, segment_size=None):
    """Initializes the decrypter object.

    Args:
      key: optional key.
      block_cipher_mode: optional block cipher mode identifier.
      iv: optional initialization vector.
      segment_size: optional segment size.
    """
    super(TestDecrypter, self).__init__()

  def Decrypt(self, encrypted_data):
    """Decode the encrypted data.

    Args:
      encrypted_data: a byte string containing the encrypted data.

    Returns:
      A tuple containing a byte string of the decrypted data and
      the remaining encrypted data.
    """
    return b'', b''


class EncryptionManagerTest(unittest.TestCase):
  """Class to test the encryption manager."""

  def testDecrypterRegistration(self):
    """Tests the DeregisterDecrypter and DeregisterDecrypter functions."""
    # pylint: disable=protected-access
    number_of_decrypters = len(manager.EncryptionManager._decrypters)

    manager.EncryptionManager.RegisterDecrypter(TestDecrypter)
    self.assertEqual(
        len(manager.EncryptionManager._decrypters),
        number_of_decrypters + 1)

    with self.assertRaises(KeyError):
      manager.EncryptionManager.RegisterDecrypter(TestDecrypter)

    manager.EncryptionManager.DeregisterDecrypter(TestDecrypter)
    self.assertEqual(
        len(manager.EncryptionManager._decrypters), number_of_decrypters)

  def testGetDecrypter(self):
    """Function to test the GetDecrypter function."""
    decoder_object = manager.EncryptionManager.GetDecrypter(
        definitions.ENCRYPTION_METHOD_AES,
        key=u'This is a key123',
        block_cipher_mode=definitions.BLOCK_CIPHER_MODE_CBC,
        iv=u'This is an IV456')
    self.assertIsInstance(decoder_object, aes_decrypter.AESDecrypter)

    decoder_object = manager.EncryptionManager.GetDecrypter(u'bogus')
    self.assertEqual(decoder_object, None)


if __name__ == '__main__':
  unittest.main()
