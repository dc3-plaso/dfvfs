# -*- coding: utf-8 -*-
"""The AES decrypter object implementation."""

from Crypto.Cipher import AES

from dfvfs.encryption import decrypter
from dfvfs.encryption import manager
from dfvfs.lib import definitions


class AESDecrypter(decrypter.PyCryptoDecrypter):
  """Class that implements a AES decrypter using PyCrypto."""

  ENCRYPTION_METHOD = definitions.ENCRYPTION_METHOD_AES
  BLOCK_SIZE = AES.block_size
  KEY_SIZES = AES.key_size

  _DECRYPTER_MODULE = AES


# Register the decrypter with the encryption manager.
manager.EncryptionManager.RegisterDecrypter(AESDecrypter)
