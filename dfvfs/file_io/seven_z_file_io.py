# -*- coding: utf-8 -*-
"""The 7z extracted file-like object implementation."""

import os
import tempfile

from dfvfs.file_io import os_file_io
from dfvfs.resolver import resolver


class SevenZFile(os_file_io.OSFile):
  """Class that implements a file-like object using py7zlib."""

  def __init__(self, resolver_context):
    """Initializes the file-like object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
    """
    super(SevenZFile, self).__init__(resolver_context)
    # TODO: For now we are going to cache the temp file ourselves until
    # the cache feature provides this functionality.
    self._temp_file_name = None

  def _Close(self):
    """Closes the file-like object.

       If the file-like object was passed in the init function
       the data range file-like object does not control the file-like object
       and should not actually close it.

    Raises:
      IOError: if the close failed.
    """
    super(SevenZFile, self)._Close()

    try:
      os.remove(self._temp_file_name)
    except (OSError, IOError):
      pass
    self._temp_file_name = None

  def _Open(self, path_spec=None, mode='rb'):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec: optional the path specification (instance of path.PathSpec).
                 The default is None.
      mode: optional file access mode. The default is 'rb' read-only binary.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file-like object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if not path_spec:
      raise ValueError(u'Missing path specification.')

    file_system = resolver.Resolver.OpenFileSystem(
      path_spec, resolver_context=self._resolver_context)

    file_entry = file_system.GetFileEntryByPathSpec(path_spec)
    if not file_entry:
      file_system.Close()
      raise IOError(u'Unable to retrieve file entry.')

    self._file_system = file_system

    seven_z_info = file_entry.GetSevenZInfo()

    # Move data to a temporary file so we have seek and read size features.
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
      self._temp_file_name = temp_file.name
      temp_file.write(seven_z_info.read())

    self._file_object = open(self._temp_file_name, mode=mode)
    self._size = seven_z_info.size
