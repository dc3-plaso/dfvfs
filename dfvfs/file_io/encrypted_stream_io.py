# -*- coding: utf-8 -*-
"""The encrypted stream file-like object implementation."""

import os

from dfvfs.encryption import manager as encryption_manager
from dfvfs.file_io import file_io
from dfvfs.lib import errors
from dfvfs.resolver import resolver


class EncryptedStream(file_io.FileIO):
  """Class that implements a file-like object of a encrypted stream."""

  # The size of the encrypted data buffer.
  _ENCRYPTED_DATA_BUFFER_SIZE = 8 * 1024 * 1024

  def __init__(
      self, resolver_context, encryption_method=None, file_object=None,
      key=None, block_cipher_mode=None, iv=None, segment_size=None):
    """Initializes the file-like object.

       If the file-like object is chained do not separately use the parent
       file-like object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
      encryption_method: optional method used to the encrypt the data.
      file_object: optional parent file-like object. The default is None.
      key: optional key.
      block_cipher_mode: optional block cipher mode identifier.
      iv: optional initialization vector.
      segment_size: optional segment size

    Raises:
      ValueError: if file_object provided but encoding_method is not.
    """
    if file_object is not None and encryption_method is None:
      raise ValueError(
          u'File-like object provided without corresponding encoding method.')

    super(EncryptedStream, self).__init__(resolver_context)
    self._current_offset = 0
    self._decrypted_data = b''
    self._decrypted_block_offset = 0
    self._decrypted_data_size = 0
    self._decrypted_stream_size = None
    self._decrypter = None
    self._encrypted_data = b''
    self._file_size = None
    self._file_object = file_object
    self._realign_offset = True

    self._encryption_method = encryption_method
    self._key = key
    self._block_cipher_mode = block_cipher_mode
    self._iv = iv
    self._segment_size = segment_size

    if file_object:
      self._file_object_set_in_init = True
      self._file_size = file_object.get_size()
    else:
      self._file_object_set_in_init = False

  def _Close(self):
    """Closes the file-like object.

       If the file-like object was passed in the init function
       the encrypted stream file-like object does not control
       the file-like object and should not actually close it.

    Raises:
      IOError: if the close failed.
    """
    if not self._file_object_set_in_init:
      self._file_object.close()
      self._file_object = None

    self._decrypter = None
    self._decrypted_data = b''
    self._encrypted_data = b''

  def _GetDecrypter(self):
    """Gets the decrypter."""
    return encryption_manager.EncryptionManager.GetDecrypter(
        self._encryption_method, key=self._key,
        block_cipher_mode=self._block_cipher_mode, iv=self._iv,
        segment_size=self._segment_size)

  def _Open(self, path_spec=None, mode='rb'):
    """Opens the file-like object.

    Args:
      path_spec: optional path specification (instance of path.PathSpec).
                 The default is None.
      mode: optional file access mode. The default is 'rb' read-only binary.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file-like object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if not self._file_object_set_in_init and not path_spec:
      raise ValueError(u'Missing path specfication.')

    if not self._file_object_set_in_init:
      if not path_spec.HasParent():
        raise errors.PathSpecError(
            u'Unsupported path specification without parent.')

      self._encryption_method = getattr(path_spec, u'encryption_method', None)
      if self._encryption_method is None:
        raise errors.PathSpecError(
            u'Path specification missing encoding method.')

      self._key = getattr(path_spec, u'key', None)
      self._block_cipher_mode = getattr(path_spec, u'block_cipher_mode', None)
      self._iv = getattr(path_spec, u'iv', None)
      self._segment_size = getattr(path_spec, u'segment_size', None)

      try:
        self._decrypter = self._GetDecrypter()
      except ValueError, exception:
        raise errors.PathSpecError(
            u'Unsupported path specification with error: {0:s}'.format(
                exception))

      self._file_object = resolver.Resolver.OpenFileObject(
          path_spec.parent, resolver_context=self._resolver_context)
      self._file_size = self._file_object.get_size()

  def _AlignDecryptedDataOffset(self, file_offset):
    """Aligns the decrypted data with the file offset.

    Args:
      file_offset: the file offset.
    """
    # Reset decrypter.
    self._file_object.seek(0, os.SEEK_SET)
    self._decrypted_data = b''
    self._decrypter = None

    # Decrypt until we have reached the file offset.
    read_data_offset = 0
    while read_data_offset < self._file_size:
      read_count = self._ReadEncryptedData(self._ENCRYPTED_DATA_BUFFER_SIZE)
      if read_count == 0:
        break

      read_data_offset += read_count

      if file_offset < self._decrypted_data_size:
        self._decrypted_block_offset = file_offset
        break

      file_offset -= self._decrypted_data_size

  def _ReadEncryptedData(self, read_size):
    """Reads encrypted data from the file-like object.

    Args:
      read_size: the number of bytes of encrypted data to read.

    Returns:
      The number of bytes of encrypted data read.
    """
    encrypted_data = self._file_object.read(read_size)

    read_count = len(encrypted_data)

    self._encrypted_data += encrypted_data

    # Initialize decrypter on first read.
    if not self._decrypter:
      self._decrypter = self._GetDecrypter()

    self._decrypted_data, self._encrypted_data = (
        self._decrypter.Decrypt(self._encrypted_data))

    self._decrypted_data_size = len(self._decrypted_data)

    return read_count

  # Note: that the following functions do not follow the style guide
  # because they are part of the file-like object interface.

  def read(self, size=None):
    """Reads a byte string from the file-like object at the current offset.

       The function will read a byte string of the specified size or
       all of the remaining data if no size was specified.

    Args:
      size: Optional integer value containing the number of bytes to read.
            Default is all remaining data (None).

    Returns:
      A byte string containing the data read.

    Raises:
      IOError: if the read failed.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    if self._current_offset < 0:
      raise IOError(
          u'Invalid current offset: {0:d} value less than zero.'.format(
              self._current_offset))

    if self._current_offset >= self._file_size:
      return b''

    if self._realign_offset:
      self._AlignDecryptedDataOffset(self._current_offset)
      self._realign_offset = False

    if size is None:
      size = self._file_size
    if self._current_offset + size > self._file_size:
      size = self._file_size - self._current_offset

    decrypted_data = b''

    if size == 0:
      return decrypted_data

    # Read full blocks.
    while size > self._decrypted_data_size:
      decrypted_data += self._decrypted_data[self._decrypted_block_offset:]

      remaining_decrypted_data_size = (
          self._decrypted_data_size - self._decrypted_block_offset)

      self._current_offset += remaining_decrypted_data_size
      size -= remaining_decrypted_data_size

      if self._current_offset >= self._file_size:
        break

      read_count = self._ReadEncryptedData(self._ENCRYPTED_DATA_BUFFER_SIZE)
      self._decrypted_block_offset = 0
      if read_count == 0:
        break

    # Read partial block.
    if size > 0:
      slice_start_offset = self._decrypted_block_offset
      slice_end_offset = slice_start_offset + size

      decrypted_data += (
          self._decrypted_data[slice_start_offset:slice_end_offset])

      self._decrypted_block_offset += size
      self._current_offset += size

    return decrypted_data

  def seek(self, offset, whence=os.SEEK_SET):
    """Seeks an offset within the file-like object.

    Args:
      offset: the offset to seek.
      whence: optional value that indicates whether offset is an absolute
              or relative position within the file. Default is SEEK_SET.

    Raises:
      IOError: if the seek failed.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    if self._current_offset < 0:
      raise IOError(
          u'Invalid current offset: {0:d} value less than zero.'.format(
              self._current_offset))

    if whence == os.SEEK_CUR:
      offset += self._current_offset
    elif whence == os.SEEK_END:
      offset += self._file_size
    elif whence != os.SEEK_SET:
      raise IOError(u'Unsupported whence.')
    if offset < 0:
      raise IOError(u'Invalid offset value less than zero.')

    if offset != self._current_offset:
      self._current_offset = offset
      self._realign_offset = True

  def get_offset(self):
    """Returns the current offset into the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    return self._current_offset

  def get_size(self):
    """Returns the size of the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    return self._file_size
