# -*- coding: utf-8 -*-
"""The Triple DES decrypter object implementation."""

from Crypto.Cipher import DES3

from dfvfs.encryption import decrypter
from dfvfs.encryption import manager
from dfvfs.lib import definitions


class DES3Decrypter(decrypter.PyCryptoDecrypter):
  """Class that implements a Triple DES decrypter using PyCrypto."""

  ENCRYPTION_METHOD = definitions.ENCRYPTION_METHOD_DES3
  BLOCK_SIZE = DES3.block_size
  KEY_SIZES = DES3.key_size

  _DECRYPTER_MODULE = DES3


# Register the decrypter with the encryption manager.
manager.EncryptionManager.RegisterDecrypter(DES3Decrypter)
