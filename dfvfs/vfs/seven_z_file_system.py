# -*- coding: utf-8 -*-
"""The 7z file system implementation."""

import py7zlib

# This is necessary to prevent a circular import.
import dfvfs.vfs.seven_z_file_entry

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import seven_z_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import file_system


class SevenZFileSystem(file_system.FileSystem):
  """Class that implements a file system object using py7zlib."""

  LOCATION_ROOT = u'/'
  TYPE_INDICATOR = definitions.TYPE_INDICATOR_7Z

  def __init__(self, resolver_context):
    """Initializes the file system object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
      encoding: optional file entry name encoding. The default is 'utf-8'.
    """
    super(SevenZFileSystem, self).__init__(resolver_context)
    self._file_object = None
    self._seven_z_file = None

  def _Close(self):
    """Closes the file system object.

    Raises:
      IOError: if the close failed.
    """
    self._seven_z_file = None

    self._file_object.close()
    self._file_object = None

  def _Open(self, path_spec=None, mode='rb'):
    """Opens the file system object defined by path specification.

    Args:
      path_spec: optional path specification (instance of path.PathSpec).
                 The default is None.
      mode: optional file access mode. The default is 'rb' read-only binary.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file system object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if not path_spec.HasParent():
      raise errors.PathSpecError(
          u'Unsupported path specification without parent.')

    file_object = resolver.Resolver.OpenFileObject(
        path_spec.parent, resolver_context=self._resolver_context)

    try:
      self._seven_z_file = py7zlib.Archive7z(file_object)
    except (py7zlib.FormatError, TypeError) as exception:
      raise errors.BackEndError(
          u'Failed to open 7z archive file with error: {0:s}'.format(exception))
    self._file_object = file_object

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec: a path specification (instance of path.PathSpec).

    Returns:
      Boolean indicating if the file entry exists.
    """
    location = getattr(path_spec, u'location', None)

    if (location is None or
        not location.startswith(self.LOCATION_ROOT)):
      return

    if len(location) == 1:
      return True

    seven_z_info = self._seven_z_file.getmember(location[1:])
    return seven_z_info is not None

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec: a path specification (instance of path.PathSpec).

    Returns:
      A file entry (instance of vfs.SevenZFileEntry) or None.
    """
    location = getattr(path_spec, u'location', None)

    if (location is None or
        not location.startswith(self.LOCATION_ROOT)):
      return

    if len(location) == 1:
      return dfvfs.vfs.seven_z_file_entry.SevenZFileEntry(
          self._resolver_context, self, path_spec, is_root=True,
          is_virtual=True)

    seven_z_info = self._seven_z_file.getmember(location[1:])

    if seven_z_info is None:
      return
    return dfvfs.vfs.seven_z_file_entry.SevenZFileEntry(
        self._resolver_context, self, path_spec, seven_z_info=seven_z_info)

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      A file entry (instance of vfs.FileEntry).
    """
    path_spec = seven_z_path_spec.SevenZPathSpec(
        location=self.LOCATION_ROOT, parent=self._path_spec.parent)
    return self.GetFileEntryByPathSpec(path_spec)

  def GetSevenZFile(self):
    """Retrieves the tar file object.

    Returns:
      The tar file object (instance of tarfile.TarFile).
    """
    return self._seven_z_file
