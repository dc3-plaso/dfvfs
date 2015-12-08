# -*- coding: utf-8 -*-
"""The decrypter object interface."""

import abc
from Crypto.Cipher import blockalgo

from dfvfs.lib import definitions


class Decrypter(object):
  """Class that implements the decrypter object interface."""

  @abc.abstractmethod
  def __init__(
      self, key=None, block_cipher_mode=None, iv=None, segment_size=None):
    """Initializes the decrypter object.

    Args:
      key: optional key.
      block_cipher_mode: optional block cipher mode identifier.
      iv: optional initialization vector.
      segment_size: optional segment size.
    """

  @abc.abstractmethod
  def Decrypt(self, encrypted_data):
    """Decodes the encoded data.

    Args:
      encrypted_data: a byte string containing the encoded data.

    Returns:
      A tuple containing a byte string of the decoded data and
      the remaining encoded data.
    """


class PyCryptoDecrypter(Decrypter):
  """Class that implements the decrypter object interface using PyCrypto."""

  BLOCK_CIPHER_MODES = {
      definitions.BLOCK_CIPHER_MODE_CBC : blockalgo.MODE_CBC,
      definitions.BLOCK_CIPHER_MODE_CFB : blockalgo.MODE_CFB,
      definitions.BLOCK_CIPHER_MODE_ECB : blockalgo.MODE_ECB,
      definitions.BLOCK_CIPHER_MODE_OFB : blockalgo.MODE_OFB}

  BLOCK_SIZE = 1
  KEY_SIZES = None

  _DECRYPTER_MODULE = None

  def __init__(
      self, key=None, block_cipher_mode=None, iv=None, segment_size=None):
    """Initializes the decrypter object.

    Args:
      key: optional key.
      block_cipher_mode: optional block cipher mode identifier.
      iv: optional initialization vector.
      segment_size: optional segment size.
    """
    super(PyCryptoDecrypter, self).__init__()
    self._ciphertext_multiple = 1
    self._decrypter = None
    kwargs = {}

    if key is None:
      raise ValueError(u'Missing secret key.')

    if self.KEY_SIZES is not None and len(key) not in self.KEY_SIZES:
      raise ValueError(u'Invalid key size.')

    if iv is not None:
      if len(iv) != self.BLOCK_SIZE:
        raise ValueError(u'Invalid IV size.')
      kwargs[u'IV'] = iv

    if block_cipher_mode:
      if block_cipher_mode not in self.BLOCK_CIPHER_MODES:
        raise ValueError(
            u'Invalid block cipher mode: {0:s}'.format(block_cipher_mode))
      kwargs[u'mode'] = self.BLOCK_CIPHER_MODES[block_cipher_mode]

      if block_cipher_mode in [
          definitions.BLOCK_CIPHER_MODE_CBC, definitions.BLOCK_CIPHER_MODE_ECB,
          definitions.BLOCK_CIPHER_MODE_OFB]:
        self._ciphertext_multiple = self.BLOCK_SIZE
      elif block_cipher_mode == definitions.BLOCK_CIPHER_MODE_CFB:
        if not segment_size:
          segment_size = 8
        if segment_size % 8 != 0:
          raise ValueError(u'Segment size must be a multiple of 8.')
        self._ciphertext_multiple = segment_size / 8
        kwargs[u'segment_size'] = segment_size

    if self._DECRYPTER_MODULE:
      self._decrypter = self._DECRYPTER_MODULE.new(key, **kwargs)

  def Decrypt(self, encrypted_data):
    """Decrypt the encrypted data.

    Args:
      encrypted_data: a byte string containing the encrypted data.

    Returns:
      A tuple containing a byte string of the decrypted data and
      the remaining encrypted data.
    """
    index_split = -(len(encrypted_data) % self._ciphertext_multiple)
    if index_split:
      remaining_encrypted_data = encrypted_data[index_split:]
      encrypted_data = encrypted_data[:index_split]
    else:
      remaining_encrypted_data = b''

    decrypted_data = self._decrypter.decrypt(encrypted_data)

    return decrypted_data, remaining_encrypted_data

