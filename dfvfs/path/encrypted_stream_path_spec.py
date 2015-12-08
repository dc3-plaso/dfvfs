# -*- coding: utf-8 -*-
"""The encrypted stream path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class EncryptedStreamPathSpec(path_spec.PathSpec):
  """Class that implements the encoded stream path specification."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_ENCRYPTED_STREAM

  def __init__(
      self, encryption_method=None, key=None, block_cipher_mode=None,
      iv=None, segment_size=None, parent=None, **kwargs):
    """Initializes the path specification object.

       Note that the encoded stream path specification must have a parent.

    Args:
      encryption_method: optional method used to the encode the data.
                       The default is None.
      key: optional key.
      block_cipher_mode: optional block cipher mode identifier.
      iv: optional initialization vector.
      segment_size: optional segment size
      parent: optional parent path specification (instance of PathSpec).
              The default is None.
      kwargs: a dictionary of keyword arguments depending on the path
              specification.

    Raises:
      ValueError: when encoding method or parent are not set.
    """
    if not encryption_method or not parent:
      raise ValueError(u'Missing encoding method or parent value.')

    super(EncryptedStreamPathSpec, self).__init__(parent=parent, **kwargs)
    self.encryption_method = encryption_method
    self.key = key
    self.block_cipher_mode = block_cipher_mode
    self.iv = iv
    self.segment_size = segment_size

  @property
  def comparable(self):
    """Comparable representation of the path specification."""
    string_parts = [u'encryption_method: {0:s}'.format(self.encryption_method)]

    if self.key is not None:
      string_parts.append(u'key: {0!s}'.format(self.key))
    if self.block_cipher_mode:
      string_parts.append(
          u'block cipher mode: {0:s}'.format(self.block_cipher_mode))
    if self.iv is not None:
      string_parts.append(u'IV: {0!s}'.format(self.iv))
    if self.segment_size is not None:
      string_parts.append(u'segment size: {0:d}'.format(self.segment_size))

    return self._GetComparable(sub_comparable_string=u', '.join(string_parts))


# Register the path specification with the factory.
factory.Factory.RegisterPathSpec(EncryptedStreamPathSpec)
