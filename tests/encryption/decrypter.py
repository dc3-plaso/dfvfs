#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the decrypter object."""

from Crypto.Cipher import blockalgo

from dfvfs.encryption import decrypter
from dfvfs.lib import definitions
from tests.encryption import test_lib


class FakeDecrypter(object):
  """Class that implements a fake PyCrypto decrypter module."""

  @staticmethod
  def new(key, **kwargs):
    return key, kwargs


class PyCryptoDecrypterTestCase(test_lib.DecrypterTestCase):
  """Tests for the PyCrypto based decrypter object."""

  def testInitialization(self):
    """Tests the initializations using different combinations of credentials."""
    decrypter.PyCryptoDecrypter.BLOCK_SIZE = 8
    decrypter.PyCryptoDecrypter._DECRYPTER_MODULE = FakeDecrypter

    # Test valid input.
    test_decrypter = decrypter.PyCryptoDecrypter(
        key=u'This is a key123',
        block_cipher_mode=definitions.BLOCK_CIPHER_MODE_CBC,
        iv=u'This IV!')
    # pylint: disable=unpacking-non-sequence
    key, kwargs = test_decrypter._decrypter
    self.assertEqual(u'This is a key123', key)
    self.assertDictEqual(
        {u'mode': blockalgo.MODE_CBC, u'IV': u'This IV!'}, kwargs)

    test_decrypter = decrypter.PyCryptoDecrypter(
        key=u'This is a key123',
        block_cipher_mode=definitions.BLOCK_CIPHER_MODE_CFB,
        iv=u'This IV!')
    # pylint: disable=unpacking-non-sequence
    key, kwargs = test_decrypter._decrypter
    self.assertEqual(u'This is a key123', key)
    self.assertDictEqual(
        {u'mode': blockalgo.MODE_CFB, u'IV': u'This IV!', u'segment_size': 8},
        kwargs)

    with self.assertRaises(ValueError):
      decrypter.PyCryptoDecrypter(key=None)

    with self.assertRaises(ValueError):
      decrypter.PyCryptoDecrypter(
          key=u'This is a key123', block_cipher_mode=u'bogus')

    # Test invalid segment size.
    with self.assertRaises(ValueError):
      decrypter.PyCryptoDecrypter(
          key=u'This is a key123',
          block_cipher_mode=definitions.BLOCK_CIPHER_MODE_CFB,
          segment_size=2)

    with self.assertRaises(ValueError):
      decrypter.PyCryptoDecrypter(
          key=u'This is a key123',
          block_cipher_mode=definitions.BLOCK_CIPHER_MODE_CBC,
          iv=u'Too large of an IV!')

