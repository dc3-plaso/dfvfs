# -*- coding: utf-8 -*-
"""The Blowfish decrypter object implementation."""

from Crypto.Cipher import Blowfish

from dfvfs.encryption import decrypter
from dfvfs.encryption import manager
from dfvfs.lib import definitions


class BlowfishDecrypter(decrypter.PyCryptoDecrypter):
  """Class that implements a Blowfish decrypter using PyCrypto."""

  ENCRYPTION_METHOD = definitions.ENCRYPTION_METHOD_BLOWFISH
  BLOCK_SIZE = Blowfish.block_size
  KEY_SIZES = Blowfish.key_size

  _DECRYPTER_MODULE = Blowfish


# Register the decrypter with the encryption manager.
manager.EncryptionManager.RegisterDecrypter(BlowfishDecrypter)
