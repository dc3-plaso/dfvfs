# -*- coding: utf-8 -*-
"""The encryption manager."""


class EncryptionManager(object):
  """Class that implements the encryption manager."""

  _decrypters = {}

  @classmethod
  def DeregisterDecrypter(cls, decrypter):
    """Deregisters a decrypter for a specific encryption method.

    Args:
      decrypter: the decrypter class (encryption.Decrypter).

    Raises:
      KeyError: if the corresponding decrypter is not set.
    """
    encryption_method = decrypter.ENCRYPTION_METHOD.lower()
    if encryption_method not in cls._decrypters:
      raise KeyError(
          u'Decrypter for encryption method: {0:s} not set.'.format(
              decrypter.ENCRYPTION_METHOD))

    del cls._decrypters[encryption_method]

  @classmethod
  def GetDecrypter(
      cls, encryption_method, key=None, block_cipher_mode=None, iv=None,
      segment_size=None):
    """Retrieves the decrypter object for a specific encryption method.

    Args:
      encryption_method: the encryption method identifier.
      key: optional key.
      block_cipher_mode: optional block cipher mode identifier.
      iv: optional initialization vector.
      segment_size: optional segment size

    Returns:
      The decrypter object (instance of encryption.Decrypter) or None if
      the encryption method does not exists.
    """
    encryption_method = encryption_method.lower()
    decrypter = cls._decrypters.get(encryption_method, None)
    if not decrypter:
      return

    return decrypter(
        key=key, block_cipher_mode=block_cipher_mode, iv=iv,
        segment_size=segment_size)

  @classmethod
  def RegisterDecrypter(cls, decrypter):
    """Registers a decrypter for a specific encryption method.

    Args:
      decrypter: the decrypter class (encryption.Decrypter).

    Raises:
      KeyError: if the corresponding decrypter is already set.
    """
    encryption_method = decrypter.ENCRYPTION_METHOD.lower()
    if encryption_method in cls._decrypters:
      raise KeyError(
          u'Decrypter for encryption method: {0:s} already set.'.format(
              decrypter.ENCRYPTION_METHOD))

    cls._decrypters[encryption_method] = decrypter

  @classmethod
  def RegisterDecrypters(cls, decrypters):
    """Registers decrypters.

    The decrypters are identified based on their lower case encryption method.

    Args:
      decrypters: a list of class objects of the decrypters.

    Raises:
      KeyError: if decrypters is already set for the corresponding
                encryption method.
    """
    for decrypters in decrypters:
      cls.RegisterDecrypters(decrypters)

